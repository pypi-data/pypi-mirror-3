#!/usr/bin/env python

# Firelet - Distributed firewall management.
# Copyright (C) 2010 Federico Ceratto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argparse import ArgumentParser
#import daemon
from beaker.middleware import SessionMiddleware
import bottle
from bottle import abort, route, static_file, run, view, request
from bottle import debug as bottle_debug
from collections import defaultdict
from datetime import datetime
#import lockfile
from logging.handlers import TimedRotatingFileHandler
from setproctitle import setproctitle
from sys import exit
import time

from confreader import ConfReader
from mailer import Mailer
from flcore import Alert, GitFireSet, DemoGitFireSet, Users, clean
from flmap import draw_png_map, draw_svg_map
from flutils import flag, extract_all, get_rss_channels

from bottle import HTTPResponse, HTTPError

import logging
log = logging.getLogger()
log.success = log.info

#TODO: add API version number
#TODO: full rule checking upon Save
#TODO: move fireset editing in flcore
#TODO: setup three roles
#TODO: store a local copy of the deployed confs
#              - compare in with the fetched conf
#              - show it on the webapp

#TODO: new rule creation

#TODO: Reset not working, temporily disabled - FireSet files must be read on
# each client request
#TODO: localhost and local networks autosetup

app = bottle.app()

# Setup Python error logging
class LoggedHTTPError(bottle.HTTPResponse):
    """Log a full traceback"""
    def __init__(self, code=500, output='Unknown Error', exception=None,
            traceback=None, header=None):
        super(bottle.HTTPError, self).__init__(output, code, header)
        log.error("""Internal error '%s':\n  Output: %s\n  Header: %s\n  %s \
--- End of traceback ---""" % (exception, output, header, traceback))

    def __repr__(self):
        ts = datetime.now()
        return "%s: An error occourred and has been logged." % ts

bottle.HTTPError = LoggedHTTPError


# Global variables

def success(s):
    """Bound method for the "log" instance, used to display success messages
    to the user
    """
    log.info(s, extra={'web_log_level': 'success'})

log.success = success

class WebLogHandler(logging.Handler):
    """Log messages and store them to be displayed to the user
    Inherits from logging.Handler
    """
    def __init__(self):
        logging.Handler.__init__(self)
        self._msg_buffer = []

    def emit(self, record):
        """Add a log message to the internal circular buffer"""
        lvl = record.levelname.lower()
        if lvl == 'debug':
            return
        elif lvl in ('error', 'critical'):
            lvl = 'alert'
        elif getattr(record, 'web_log_level', None) == 'success':
            lvl = 'success'

        text = record.msg
        if len(text) > 200:
            text = "%s [...see logfile]" % text[:200]

        tstamp = time.strftime("%H:%M:%S", time.gmtime(record.created))
        msg = (lvl, tstamp, text)

        self._msg_buffer.append(msg)
        if len(self._msg_buffer) > 20:
            self._msg_buffer.pop(0)

    def get_msgs(self):
        return self._msg_buffer


web_log_handler = WebLogHandler()

# Miscellaneous functions

def ack(s=None):
    """Acknowledge successful processing and returns ajax confirmation."""
    if s:
        log.success(s)
    return {'ok': True}

def ret_warn(s=None):
    """Generate warn message and returns ajax 'ok: False'."""
    if s:
        log.warn(s)
    return {'ok': False}

def ret_alert(s=None):
    """Generate alert message and returns ajax 'ok: False'."""
    if s:
        log.error(s)
    return {'ok': False}

def pg(name, default=''):
    """Retrieve an element from a POST request"""
    s = request.POST.get(name, default)[:64]
    return clean(s).strip()

def pg_list(name, default=''):
    """Retrieve a serialized (comma-separated) list from a POST request.
    Duplicated and empty elements are removed
    """
    s = request.POST.get(name, default)
    li = clean(s).strip().split(',')
    item_set = set(li)
    if '' in item_set:
        item_set.remove('')
    return list(item_set)

def int_pg(name, default=None):
    """Retrieve an element from a POST request and returns it as an integer"""
    v = request.POST.get(name, default)
    if v == '':
        return None
    try:
        return int(v)
    except:
        raise Exception, "Expected int as POST parameter, got string: '%s'." % v

def pcheckbox(name):
    """Retrieve a checkbox status from a POST request generated by serializeArray() and returns '0' or '1' """
    if name in request.POST:
        return '1'
    return '0'


# # #  web services  # # #


# #  authentication  # #

def _require(role='readonly'):
    """Ensure the user has the required role (or higher).
    Order is: admin > editor > readonly
    """
    m = {'admin': 15, 'editor': 10, 'readonly': 5}
    s = bottle.request.environ.get('beaker.session')
    if not s:
        log.warn("User needs to be authenticated.")
        #TODO: not really explanatory in a multiuser session.
        raise Alert, "User needs to be authenticated."
    myrole = s.get('role', None)
    if not myrole:
        raise Alert, "User needs to be authenticated."
    if m[myrole] >= m[role]:
        return
    log.info("An account with '%s' level or higher is required." % repr(role))
    raise Exception


@bottle.route('/login')
@bottle.route('/login', method='POST')
def login():
    """Log user in if authorized"""
    s = bottle.request.environ.get('beaker.session')
    if 'username' in s:  # user is authenticated <--> username is set
        log.info("Already logged in as \"%s\"." % s['username'])
        return {'logged_in': True}
    user = pg('user', '')
    pwd = pg('pwd', '')
    try:
        users.validate(user, pwd)
        role = users._users[user][0]
        log.success("User %s with role %s logged in." % (user, role))
        s['username'] = user
        s['role'] = role
        s.save()
        bottle.redirect('/')
    except (Alert, AssertionError), e:
        log.warn("Login denied for \"%s\": %s" % (user, e))
        log.debug("Login denied for \"%s\": %s" % (user, e))
        bottle.redirect('/')

@bottle.route('/logout')
def logout():
    """Log user out"""
    _require()
    s = bottle.request.environ.get('beaker.session')
    u = s.get('username', None)
    if u:
        log.info('User %s logged out.' % u)
    s.delete()
    bottle.redirect('/')

#
#class WebApp(object):
#
#def __init__(self, conf):
#    self.conf = conf
#    self.messages = []

@bottle.route('/messages')
@view('messages')
def messages():
    """Populate log message pane"""
    _require()
    return dict(messages=web_log_handler.get_msgs())

@bottle.route('/')
@view('index')
def index():
    """Serve main page"""
    s = bottle.request.environ.get('beaker.session')
    logged_in = True if s and 'username' in s else False

    try:
        title = conf.title
    except:
        title = 'test'
    return dict(msg=None, title=title, logged_in=logged_in)

# #  tables interaction  # #
#
# GETs are used to list all table contents
# POSTs are used to make changes or to populate editing forms
# POST "verbs" are sent using the "action" key, and the "rid" key
# specifies the target:
#   - delete
#   - moveup/movedown/enable/disable   see ruleset()
#   - edit: updates an element if rid is not null, otherwise creates
#             a new one

@bottle.route('/ruleset')
@view('ruleset')
def ruleset():
    """Serve ruleset tab"""
    _require()
    return dict(rules=enumerate(fs.rules))

@bottle.route('/ruleset', method='POST')
def ruleset():
    """Make changes on a rule."""
    _require('editor')
    action = pg('action', '')
    rid = int_pg('rid')
    assert rid is not None, "Item number not provided"
    try:
        if action == 'delete':
            item = fs.fetch('rules', rid)
            name = item.name
            fs.delete('rules', rid)
            return ack("Rule %s deleted." % name)
        elif action == 'moveup':
            fs.rules.moveup(rid)
            return ack("Rule moved up.")
        elif action == 'movedown':
            fs.rules.movedown(rid)
            return ack("Rule moved down.")
        elif action == 'enable':
            fs.rules.enable(rid)
            return ack("Rule %d enabled." % rid)
        elif action == 'disable':
            fs.rules.disable(rid)
            return ack("Rule %d disabled." % rid)
        elif action == "save":
            fields = ('name', 'src', 'src_serv', 'dst', 'dst_serv', 'desc')
            d = dict((f, pg(f)) for f in fields)
            d['enabled'] = flag(pg('enabled'))
            d['action'] = pg('rule_action')
            d['log_level'] = pg('log')
            fs.rules.update(d, rid=pg('rid'), token=pg('token'))
        elif action == "newabove":
            action = "create new rule above"
            d = {}
            fs.rules.add(d, rid=rid)
        elif action == "newbelow":
            action = "create new rule below"
            d = {}
            fs.rules.add(d, rid=rid+1)
        else:
            log.error('Unknown action requested: "%s"' % action)
    except Exception, e:
        log.error("Unable to %s rule n. %s - %s" % (action, rid, e))
        abort(500)

@bottle.route('/ruleset_form', method='POST')
@view('ruleset_form')
def ruleset_form():
    """Generate an inline editing form for a rule"""
    _require()
    rid = int_pg('rid')
    rule = fs.rules[rid]
    services = ['*'] + [s.name for s in fs.services]
    objs = ["%s:%s" % (h.hostname, h.iface) for h in fs.hosts] + \
        [hg.name for hg in fs.hostgroups] + \
        [n.name for n in fs.networks]
    return dict(rule=rule, rid=rid, services=services, objs=objs)

@bottle.route('/sib_names', method='POST')
def sib_names():
    """Return a list of all the available siblings for a hostgroup being created or edited.
    Used in the ajax form."""
    _require()
    sib_names = fs.list_sibling_names()
    return dict(sib_names=sib_names)

@bottle.route('/hostgroups')
@view('hostgroups')
def hostgroups():
    """Generate the HTML hostgroups table"""
    _require()
    return dict(hostgroups=enumerate(fs.hostgroups))

@bottle.route('/hostgroups', method='POST')
def hostgroups():
    """Add/edit/delete a hostgroup"""
    _require('editor')
    action = pg('action', '')
    rid = int_pg('rid')
    try:
        if action == 'delete':
            item = fs.fetch('hostgroups', rid)
            name = item.name
            fs.delete('hostgroups', rid)
            return ack("Hostgroup %s deleted." % name)
        elif action == 'save':
            childs = pg_list('siblings')
            d = {'name': pg('name'),
                    'childs': childs}
            if rid == None:     # new item
                fs.hostgroups.add(d)
                return ack('Hostgroup %s added.' % d['name'])
            else:                     # update item
                fs.hostgroups.update(d, rid=rid, token=pg('token'))
                return ack('Hostgroup %s updated.' % d['name'])
        elif action == 'fetch':
            item = fs.fetch('hostgroups', rid)
            return item.attr_dict()
        else:
            log.error('Unknown action requested: "%s"' % action)
    except Exception, e:
        log.error("Unable to %s hostgroup n. %s - %s" % (action, rid, e))
        abort(500)

@bottle.route('/hosts')
@view('hosts')
def hosts():
    """Serve hosts tab"""
    _require()
    return dict(hosts=enumerate(fs.hosts))

@bottle.route('/hosts', method='POST')
def hosts():
    """Add/edit/delete a host"""
    _require('editor')
    action = pg('action', '')
    rid = int_pg('rid')
    try:
        if action == 'delete':
            h = fs.fetch('hosts', rid)
            name = h.hostname
            fs.delete('hosts', rid)
            log.success("Host %s deleted." % name)
        elif action == 'save':
            d = {}
            for f in ('hostname', 'iface', 'ip_addr', 'masklen'):
                d[f] = pg(f)
            for f in ('local_fw', 'network_fw', 'mng'):
                d[f] = pcheckbox(f)
            d['routed'] = pg_list('routed')
            if rid == None:     # new host
                fs.hosts.add(d)
                return ack('Host %s added.' % d['hostname'])
            else:   # update host
                fs.hosts.update(d, rid=rid, token=pg('token'))
                return ack('Host %s updated.' % d['hostname'])
        elif action == 'fetch':
            h = fs.fetch('hosts', rid)
            d = h.attr_dict()
            for x in ('local_fw', 'network_fw', 'mng'):
                d[x] = int(d[x])
            return d
        else:
            raise Exception, 'Unknown action requested: "%s"' % action
    except Exception, e:
        log.error("Unable to %s host n. %s - %s" % (action, rid, e))
        abort(500)



@bottle.route('/net_names', method='POST')
def net_names():
    """Serve networks names"""
    _require()
    nn = [n.name for n in fs.networks]
    return dict(net_names=nn)

@bottle.route('/networks')
@view('networks')
def networks():
    """Generate the HTML networks table"""
    _require()
    return dict(networks=enumerate(fs.networks))

@bottle.route('/networks', method='POST')
def networks():
    """Add/edit/delete a network"""
    _require('editor')
    action = pg('action', '')
    rid = int_pg('rid')
    try:
        if action == 'delete':
            item = fs.fetch('networks', rid)
            name = item.name
            fs.delete('networks', rid)
            log.success("Network %s deleted." % name)
        elif action == 'save':
            d = {}
            for f in ('name', 'ip_addr', 'masklen'):
                d[f] = pg(f)
            if rid == None:     # new item
                fs.networks.add(d)
                return ack('Network %s added.' % d['name'])
            else:                     # update item
                fs.networks.update(d, rid=rid, token=pg('token'))
                return ack('Network %s updated.' % d['name'])
        elif action == 'fetch':
            item = fs.fetch('networks', rid)
            return item.attr_dict()
        else:
            log.error('Unknown action requested: "%s"' % action)
    except Exception, e:
        log.error("Unable to %s network n. %s - %s" % (action, rid, e))
        abort(500)



@bottle.route('/services')
@view('services')
def services():
    """Generate the HTML services table"""
    _require()
    return dict(services=enumerate(fs.services))

@bottle.route('/services', method='POST')
def services():
    """Add/edit/delete a service"""
    _require('editor')
    action = pg('action', '')
    rid = int_pg('rid')
    try:
        if action == 'delete':
            item = fs.fetch('services', rid)
            name = item.name
            fs.delete('services', rid)
            log.success("service %s deleted." % name)
        elif action == 'save':
            d = {'name': pg('name'),
                    'protocol': pg('protocol')}
            if d['protocol'] in ('TCP', 'UDP'):
                d['ports'] = pg('ports')
            elif d['protocol'] == 'ICMP':
                d['ports'] = pg('icmp_type')
            else:
                d['ports'] = ''
            if rid == None:     # new item
                fs.services.add(d)
                return ack('Service %s added.' % d['name'])
            else:                     # update item
                fs.services.update(d, rid=rid, token=pg('token'))
                return ack('Service %s updated.' % d['name'])
        elif action == 'fetch':
            item = fs.fetch('services', rid)
            return item.attr_dict()
        else:
            log.error('Unknown action requested: "%s"' % action)
    except Exception, e:
        log.error("Unable to %s service n. %s - %s" % (action, rid, e))
        abort(500)


# management commands

@bottle.route('/manage')
@view('manage')
def manage():
    """Serve manage tab"""
    _require()
    s = bottle.request.environ.get('beaker.session')
    myrole = s.get('role', '')
    cd = True if myrole == 'admin' else False
    return dict(can_deploy=cd)

@bottle.route('/save_needed')
def save_needed():
    """Serve fs.save_needed() output"""
    _require()
    return {'sn': fs.save_needed()}

@bottle.route('/save', method='POST')
def savebtn():
    """Save configuration"""
    _require()
    msg = pg('msg', '')
    if not fs.save_needed():
        ret_warn('Save not needed.')
    log.info("Commit msg: \"%s\". Saving configuration..." % msg)
    saved = fs.save(msg)
    ack("Configuration saved: \"%s\"" % msg)
    s = bottle.request.environ.get('beaker.session')
    username = s.get('username', None)
    mailer.send_msg(
        sbj="Configuration saved by %s" % username,
        body_txt="Commit msg: %s" % msg
    )

@bottle.route('/reset', method='POST')
def resetbtn():
    """Reset configuration"""
    _require()
    if not fs.save_needed():
        ret_warn('Reset not needed.')
    log.info("Resetting configuration changes...")
    fs.reset()
    ack('Configuration reset.')

@bottle.route('/api/1/check', method='POST')
@view('rules_diff_table')
def checkbtn():
    """Check configuration"""
    _require()
    log.info('Configuration check started...')
    try:
        diff_dict = fs.check(stop_on_extra_interfaces=conf.stop_on_extra_interfaces)
        log.success('Configuration check successful.')
        return dict(diff_dict=diff_dict, error=None)
    except (Alert, AssertionError), e:
        log.error("Check failed: %s" % e)
        return dict(diff_dict={}, error="Check failed: %s" % e)

@bottle.route('/api/1/deploy', method='POST')
def deploybtn():
    """Deploy configuration"""
    _require('admin')
    log.info('Configuration deployment started...')
    try:
        fs.deploy(stop_on_extra_interfaces=conf.stop_on_extra_interfaces)
        ack('Configuration deployed.')
        s = bottle.request.environ.get('beaker.session')
        username = s.get('username', None)
        mailer.send_msg(
            sbj="Configuration deployed by %s" % username,
            body_txt="Configuration deployed by %s" % username
        )
    except (Alert, AssertionError), e:
        ret_alert("Deployment failed: %s" % e)

@bottle.route('/api/1/get_compiled_rules')
def get_compiled_rules():
    """Compile rules and return them to the requester"""
    _require('admin')
    log.info('Compiling firewall rules...')
    try:
        comp_rules = fs.get_compiled_rules()
        ack('Rules compiled')
        return dict(rules=comp_rules, ok=True)
    except Alert, e:
        return ret_alert("Compilation failed: %s" % e)



@bottle.route('/api/1/version_list')
@view('version_list')
def version_list():
    """Serve version list"""
    _require()
    li = fs.version_list()
    return dict(version_list=li)

@bottle.route('/api/1/version_diff', method='POST')
@view('version_diff')
def version_diff():
    """Serve version diff"""
    _require()
    cid = pg('commit_id') #TODO validate cid?
    li = fs.version_diff(cid)
    if li:
        return dict(li=li)
    return dict(li=(('(No changes.)', 'title')))

@bottle.route('/api/1/rollback', method='POST')
def rollback():
    """Rollback configuration"""
    _require('admin')
    cid = pg('commit_id') #TODO validate cid?
    log.info("Rolling back to commit ID %s" % cid)
    fs.rollback(commit_id=cid)
    ack("Configuration rolled back.")

# serving static files

@bottle.route('/static/:filename#[a-zA-Z0-9_\.?\/?]+#')
def static(filename):
    """Serve static content"""
    bottle.response.headers['Cache-Control'] = 'max-age=3600, public'
    if filename == 'rss.png':
        return static_file(filename, 'static')
    # Authenticated users contents:
    _require()
    if filename == '/jquery-ui.js':
        return static_file('jquery-ui/jquery-ui.js',
            '/usr/share/javascript/') #TODO: support other distros
    elif filename == 'jquery.min.js':
        return static_file('jquery/jquery.min.js', '/usr/share/javascript/')
    elif filename == 'jquery-ui.custom.css': #TODO: support version change
        return static_file('jquery-ui/css/smoothness/jquery-ui-1.7.2.custom.css',
            '/usr/share/javascript/')
    else:
        return static_file(filename, 'static')


@bottle.route('/favicon.ico')
def favicon():
    static_file('favicon.ico', 'static')

@bottle.route('/map') #FIXME: the SVG map is not shown inside the jQuery tab.
def flmap():
    return """<img src="map.png" width="700px" style="margin: 10px">"""

@bottle.route('/map.png')
def flmap_png():
    bottle.response.content_type = 'image/png'
    return draw_png_map(fs)

@bottle.route('/svgmap')
def flmap_svg():
    bottle.response.content_type = 'image/svg+xml'
    return draw_svg_map(fs)

#TODO: provide PNG fallback for browser without SVG support?
#TODO: html links in the SVG map

# RSS feeds

@bottle.route('/rss')
@view('rss_index')
def rss_index():
    """Return RSS index page"""
    # FIXME: available to non-authenticated users - also, trying to fetch the
    # rss.png icon generates an auth Alert.
    return dict()


@bottle.route('/rss/:channel')
@view('rss')
def rss_channels(channel=None):
    """Generate RSS feeds for different channels"""
    # TODO: RSS feeds are available to non-authenticated users
    # make the feed enabled/disabled by conf
    bottle.response.content_type = 'application/rss+xml'
    if channel.endswith('.xml') or channel.endswith('.rss'):
        channel = channel[:-4]
    if conf.public_url:
        url = conf.public_url.rstrip('/') + '/rss'
    else:
        url = "https://%s:%s/rss" % (conf.listen_address, conf.listen_port)

    return get_rss_channels(channel, url, msg_list=web_log_handler._msg_buffer)


@bottle.route('/test_email_delivery')
def test_email_delivery():
    """Send a test email
    """
    mailer.send_msg(body_txt='Email delivery test - please ignore this message.')
    log.info('Test email sent.')
    bottle.redirect('/')


def parse_args():
    """Parse CLI arguments
    :returns: args instance
    """
    parser = ArgumentParser(description='Firelet daemon')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    parser.add_argument('-c', '--cf',  nargs='?',
                        default = '/etc/firelet/firelet.ini', help='configuration file')
    parser.add_argument('-r', '--repodir',  nargs='?',
                        help='repository directory')
    parser.add_argument('-o', '--rootdir',  nargs='?',
                        help='root directory')
    parser.add_argument('-l', '--logfile',  nargs='?',
                        help='log file name')
    #parser.add_argument('-b', '--daemonize', action='store_true', default=False,
    #                    help='run as a daemon')
    #parser.add_argument('-p', '--pidfile',  nargs='?',
    #                    default='/var/run/firelet.pid', help='pid file name')
    args = parser.parse_args()
    return args

def main():
    global app
    global conf
    setproctitle('firelet')
    args = parse_args()

    try:
        conf = ConfReader(fn=args.cf)
    except Exception, e:
        logging.error("Exception %s while reading configuration file '%s'" % (e, args.cf))
        exit(1)

    if args.repodir:
        conf.data_dir = args.repodir
    logfile = args.logfile if args.logfile else conf.logfile

    # daemonization is handled externally by start-stop-daemon
    # daemoncontext = daemon.DaemonContext()
    #if args.daemonize:
    #    if args.rootdir:
    #        daemoncontext.working_directory = args.rootdir
    #    daemoncontext.umask = 66
    #    daemoncontext.stdout = open(logfile, 'a')
    #    daemoncontext.stderr = open(logfile, 'a')
    #    print args.pidfile
    #    #daemoncontext.pidfile = lockfile.FileLock(args.pidfile)
    #    daemoncontext.pidfile = lockfile.FileLock('/tmp/foo')
    #    daemoncontext.open()

    # setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(process)d] %(levelname)s %(name)s (%(funcName)s) %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S' # %z for timezone
    )
    log.addHandler(web_log_handler)
    if args.debug:
        log.debug("Debug mode")
        log.debug("Configuration file: '%s'" % args.cf)
        log.debug("Logfile (unused in debug mode): '%s'" % logfile)
        bottle_debug(True)
    else:
        logging.basicConfig(
            level=logging.DEBUG,
        )
        fh = logging.handlers.TimedRotatingFileHandler(
            logfile,
            when='midnight',
            utc=True,
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s [%(process)d] %(levelname)s %(name)s (%(funcName)s) %(message)s'))
        log.addHandler(fh)

    log.success("Firelet started.")

    globals()['users'] = Users(d=conf.data_dir)
    globals()['mailer'] = Mailer(
        sender = conf.email_sender,
        recipients = conf.email_recipients,
        smtp_server = conf.email_smtp_server,
    )

    session_opts = {
        'session.type': 'cookie',
        'session.validate_key': True,
    }

    if conf.demo_mode:
        globals()['fs'] = DemoGitFireSet(conf.data_dir)
        log.info("Configuration loaded. Demo mode.")
        session_opts['session.secure'] = True
        session_opts['session.type'] = 'memory'
    else:
        globals()['fs'] = GitFireSet(conf.data_dir)
        log.info("Configuration loaded.")
        # Instruct the browser to sever send the cookie over unencrypted
        # connections
        session_opts['session.secure'] = True
        session_opts['session.type'] = 'memory'

    log.info("%d users, %d hosts, %d rules, %d networks loaded." %
        tuple(map(len, (users, fs.hosts, fs.rules, fs.networks)))
    )

    log.info(repr(session_opts));
    #app = bottle.default_app()
    app = SessionMiddleware(app, session_opts)

    logging.getLogger('paste.httpserver.ThreadPool').setLevel(logging.WARN)
    try:
        run(
            app=app,
            host=conf.listen_address,
            port=conf.listen_port,
            quiet=not args.debug,
            reloader=args.debug,
            server='auto'
        )
    except:
        logging.error("Unhandled exception", exc_info=True)
        raise #TODO: wrap this around main() ?
              #is it a duplicate of HTTPError logging?

    # Run until terminated by SIGKILL or SIGTERM
    mailer.join()
    #daemoncontext.close()


if __name__ == "__main__":
    main()










