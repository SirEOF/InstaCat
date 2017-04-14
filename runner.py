#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import time
import sys
import requests
import socks
import socket
import json
import logging
from clint.textui import puts, indent, colored, prompt, validators
from core import instacat

global VERSION
VERSION = 1.4

# something to fix log bugs
requests.packages.urllib3.disable_warnings()

# Logging stuff
logging.basicConfig(level=logging.DEBUG, filename="log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock


def proxy_set(PROXY):
    try:
        prox, sp, port = PROXY.rpartition(':')
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, prox, int(port))
        # patch the socket module
        socket.socket = socks.socksocket
        socket.create_connection = create_connection
        requests.get("https://api.ipify.org")
        return True
    except Exception as err:
        print err
        return False


# bot main function


def start_bot():
    try:
        answ = prompt.yn(colored.yellow('\n[?] Do you wanna continue ?', True, True))
        if not answ:
            puts(colored.red("Exiting ..."))
            sys.exit()

        SEED_USER = prompt.query('[+] target USERNAME for scraping : ')

        seed_info = instacat.api.get_user_info(SEED_USER)
        if not seed_info:
            puts(colored.red('[!] Cannot Found Such username on instagram ! '))
            puts(colored.red('\n[!] Exiting ...\n'))
            sys.exit()
        elif seed_info.is_private:
            puts(colored.red('[!] User is private ! '))
            puts(colored.red('\n[!] Exiting ...\n'))
            sys.exit()

        answ = prompt.yn(colored.yellow('\n[?] Starting with default values (dummy mode) ?', True, True))
        if not answ:
            NUM_TO_FOLLOW = prompt.query('[+] NUM to FOLLOW on each round : ',
                                         default='100', validators=[validators.IntegerValidator()])
            NUM_TO_UNFOLLOW = prompt.query(
                '[+] NUM to UNFOLLOW on each round : ', default='100', validators=[validators.IntegerValidator()])
            DAY_TO_UNFOLLOW = prompt.query('[+] Unfollowing after days : ',
                                           default='3', validators=[validators.IntegerValidator()])
            PROXY = prompt.query('[+] Socks5 Proxy Support [127.0.0.1:9050] : ', validators=[])
            if PROXY != '':
                puts(colored.green("[!] Testing proxy ..."))
                while True:
                    if proxy_set(PROXY):
                        puts(colored.green("[!] Proxy success set to bot"))
                        break
                    else:
                        puts(colored.red("[!] Unable to connect through proxy , try again ..."))
                        PROXY = prompt.query('[+] Socks5 Proxy Support [127.0.0.1:9050] : ')
            else:
                PROXY = False

        else:
            NUM_TO_FOLLOW = 100
            NUM_TO_UNFOLLOW = 100
            DAY_TO_UNFOLLOW = 3
            PROXY = False

        puts(colored.green('\n[!] Starting Bot ......    OK'))
    except KeyboardInterrupt:
        puts(colored.red('\n[!] Exiting ...\n'))
        sys.exit()

    try:
        while True:
            tiles = {}
            already_followed = []
            with open("Tiles.json", "r+") as f:
                if ('{}' in f.read()):
                    f.write('{"past": [],"present": []}')
                    f.flush()
                f.close()
            with open("Tiles.json", "r") as tilefile:
                tiles = json.load(tilefile)
            already_followed = []
            for tile in tiles['present']:
                already_followed.append(tile['user_id'])
            for tile in tiles['past']:
                already_followed.append(tile['user_id'])

            puts(colored.yellow('[!] Load Users database ...') + colored.green('   OK'))
            puts(colored.yellow('[!] Start collection users for follow ...'))

            instacat.bot.scrape_users(NUM_TO_FOLLOW, SEED_USER, already_followed)

            puts(colored.green('\n[!] Start Following ' +
                               str(len(instacat.bot.scraped_users)) + ' users ...'))

            # Loop through scraped_users and like their photos and follow them
            for user_id in instacat.bot.scraped_users:
                try:
                    follow = instacat.bot.following(user_id)
                    if follow:
                        tiles['present'].append(
                            {'user_id': user_id, 'time_followed': time.time()})
                        with indent(4, quote=' |'):
                            puts(colored.green('User [' + str(user_id) + '] Followed'))

                except Exception as err:
                    puts(colored.red(
                        '[E] oh no , we have a problem in bot , please check log file !'))
                    logger.error(err)

                    # Work out who (if anyone) is due for unfollowing
            puts(colored.yellow('\n[-] Check which users should be unfollowing'))
            to_unfollow = []
            for tile in tiles['present']:
                if (time.time() - tile['time_followed']) > (60 * 60 * 24 * DAY_TO_UNFOLLOW):
                    to_unfollow.append(tile)
                if len(to_unfollow) >= NUM_TO_UNFOLLOW:
                    break

            puts(colored.yellow('\n[!] Unfollowing ' + str(len(to_unfollow)) + ' users ...\n'))

            # Unfollow users due for unfollowing
            for tile in to_unfollow:
                try:
                    unfollow = instacat.bot.unfollowing(tile['user_id'])
                    if unfollow == True:
                        tiles['present'].remove(tile)
                        tiles['past'].append(tile)
                        with indent(4, quote=' |'):
                            puts(colored.red('user [' + str(tile['user_id']) + '] Unfollowed '))
                except Exception as e:
                    puts(colored.red(
                        '[E] oh no , we have a problem in bot , please check log file !'))
                    logger.error(e)

            with open('Tiles.json', 'w') as f:
                json.dump(tiles, f)
                puts(colored.green('[-] Current state save to database success'))
                puts(colored.red('\n[!] Restarting Bot ... \n'))

    except KeyboardInterrupt:
        # ^C exits the script: Save Tiles.json first
        with open('Tiles.json', 'w') as f:
            json.dump(tiles, f)
            puts(colored.red('[!] Saved and exited'))


def header():
    me = instacat.bot.me
    os.system('tput reset')
    puts(colored.green(""".---------------------------------------------------------."""))
    puts(colored.green("""| |\___/|     ___         _         ___      _            |"""))
    puts(colored.green("""| )     (    |_ _|_ _  __| |_ __ _ / __|__ _| |_          |"""))
    puts(colored.green("""|=\     /=    | || ' \(_-<  _/ _` | (__/ _` |  _|         |"""))
    puts(colored.green("""|  )===(     |___|_||_/__/\__\__,_|\___\__,_|\__| v""" + str(VERSION) + "    |"))
    puts(colored.green("""| /     \                                                 |"""))
    puts(colored.green("""| |     |    [INFO]                                       |"""))
    puts(colored.green("""|/       \ """ + "  Username " + (me.username).ljust(36) + "|"))
    puts(colored.green("""|\       /   """ + str(me.followed_by.count) + (' Followers').ljust(44) + "|"))
    puts(colored.green("""| \__  _/    """ + str(me.follows.count) + (' Following').ljust(43) + "|"))
    puts(colored.green("""|   ( (      """ + str(me.media.count) + (' Post').ljust(44) + "|"))
    puts(colored.green("""|    ) )                                                  |"""))
    puts(colored.green("""|   (_(                                                   |"""))
    puts(colored.green("""'---------------------------------------------------------'"""))


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            try:
                if sys.argv[1] == '--config':
                    instacat.config.configuration()
                elif sys.argv[1] == '--help':
                    puts(colored.yellow('\ninstacat [options] :\n'))
                    with indent(quote=' >'):
                        puts(colored.yellow(
                            '--start     turn on the bot \n--config    start bot configuration \n--about     about us'))
                    print("\n")
                elif sys.argv[1] == '--start':
                    # check config
                    instacat.config.check_cfg()
                    # init bot
                    instacat.bot.config_bot()
                    # starting bot
                    header()
                    start_bot()
                elif sys.argv[1] == '--about':
                    puts(colored.green(
                        '\n[-------------------------------------------]'))
                    puts(colored.green('\n[ Instacat BOT v' + str(VERSION) + ' ]'))
                    puts(colored.green('[ Coded by N3TC4T ]'))
                    puts(colored.green('[ netcat[dot]av[at]gmail[dot]com ]\n'))
                    puts(colored.green(
                        '\n[-------------------------------------------]\n'))
                else:
                    puts(colored.yellow('\n[!] incorrect option , use --help \n'))

            except Exception as err:
                print(err)
                puts(colored.red(
                    '[E] oh no , we have a problem in bot , please check log file !'))
                logger.error(err)
                sys.exit()
        else:
            puts(colored.green('\n[!] Welcome to Instacat [Instagram bot] .\n'))
            puts(colored.yellow(
                '[-] Please use --help option to see how you can work with bot.\n'))
    except Exception as err:
        puts(colored.green('\n[!] Welcome to Instacat [Instagram bot] .\n'))
        puts(colored.yellow(
            '[-] Please use --help option to see how you can work with bot.\n'))
        logger.error(err)
        pass
