# myapp.py
import logging
import logtestmod

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')
    logtestmod.do_something()
    logging.debug('Finished')
    from logging_tree import printout
    print printout()

if __name__ == '__main__':
    main()
