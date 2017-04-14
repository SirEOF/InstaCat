# coding=utf-8

import ConfigParser
import sys
import logging
import getpass
from clint.textui import puts, colored
import account

logging.basicConfig(level=logging.DEBUG, filename='log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
CFG = ConfigParser.ConfigParser()


def check_cfg():
    try:
        CFG_FILE = open('config.ini')
        CFG.read('config.ini')
        CFG.get('config', 'sessionid')
        TILES_FILE = open('Tiles.json')
    except Exception:
        err = None
        puts(colored.yellow('\n[W] looks like bot is not config yet'))
        puts(colored.white('[H] Please use --config option\n'))
        logger.warning(err)
        sys.exit()


def configuration():
    success = False

    try:
        puts(colored.green('\n[-] Welcome to InstaCat configuration section .\n'))
        puts(colored.red(
            '[!] Attention :  We do not save any sensentive data such as username and password anywhere ! '))
        username = raw_input('\n[+] Please Enter your Username : ')
        password = getpass.getpass('[+] Please Enter your password (not echoing) : ')
        puts(colored.yellow('\n[-] Start Login ... '))
        if not account.login(username, password):
            puts(colored.red('[!] Wrong username or password , please try again . '))
            while not success:
                username = raw_input('\n[+] Please Enter your Username again : ')
                password = getpass.getpass('[+] Please Enter your password again (not echoing) :')
                success = account.login(username, password)
        CFG.add_section('config')
        CFG.set('config', 'sessionid', account.SESSIONID)
        CFG.set('config', 'mid', account.MID)
        CFG.set('config', 'csrf', account.CSRF)
        CFG.set('config', 'username', account.USERNAME)
        configfile = open('config.ini', 'wb')
        CFG.write(configfile)
        configfile.close()
        tilefile = open('Tiles.json', 'w')
        tilefile.write('{"past": [],"present": []}')
        tilefile.close()
        logger.info('config success')
        puts(colored.green('\n[!] Bot configuration success ! \n    You can start bot now . \n'))
    except Exception:
        err = None
        puts(colored.red('[E] oh no , we have a problem in bot , please check log file !'))
        logger.error(err)


def read_config():
    global CONFIG, SESSIONID, MID, CSRF, USERNAME, TILES_PATH

    try:
        CFG_FILE = open('config.ini')

        try:
            CFG.read('config.ini')
        except Exception:
            err = None
            return err

    except Exception:
        e = None
        print e

    try:
        SESSIONID = CFG.get('config', 'sessionid')
        MID = CFG.get('config', 'mid')
        CSRF = CFG.get('config', 'csrf')
        USERNAME = CFG.get('config', 'username')
        TILES_PATH = 'Tiles.json'
    except Exception:
        err = None
        puts(colored.red('[E] oh no , we have a problem in bot , please check log file !'))
        logger.error(err)
