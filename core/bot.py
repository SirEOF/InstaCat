# coding=utf-8
import sys
from clint.textui import puts, indent, colored

import logging

import config
from util import sleeper
from api import *

logging.basicConfig(level=logging.DEBUG, filename='log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def config_bot():
    global scraped_users
    global me

    config.read_config()

    scraped_users = []

    me = get_user_info(config.USERNAME)

    if not me:
        puts(colored.red('\n[!] We have problem connect to Instagram , please change your ip or use proxy! '))
        puts(colored.red('\n[!] Exiting ...\n'))
        sys.exit()


def following(user_id):
    try:
        # instagram will ban your account if you follow to much account so we follow only 30 user per hour ?
        sleeper()
        url = 'https://www.instagram.com/web/friendships/' + str(user_id) + '/follow/'
        while True:
            r = req(url, 'POST', None)
            if r.text.find('ok') != -1:
                return True
            if r.status_code != 200:
                sleeper()

    except Exception as err:
        puts(colored.red('[E] oh no , we have a problem in bot , please check log file !'))
        logger.error(err)


def unfollowing(user_id):
    try:
        sleeper()
        url = 'https://www.instagram.com/web/friendships/' + str(user_id) + '/unfollow/'
        while True:
            r = req(url, 'POST', None)
            if r.text.find('ok') != -1:
                return True
            if r.status_code != 200:
                sleeper()

    except Exception as err:
        puts(colored.red('[E] oh no , we have a problem in bot , please check log file !'))
        logger.error(err)


def check_user(user, ids_to_avoid=[]):
    try:

        if user.get('pk') in ids_to_avoid:
            return 'Already Checked'

        if not user.get('is_private'):
            user = get_user_info(user.get('username'))
            if not user.followed_by_viewer:
                if user.followed_by.count < 1000:
                    if user.profile_pic_url != 'https://ig-s-a-a.akamaihd.net/hphotos-ak-xfa1/t51.2885-19/11906329_960233084022564_1448528159_a.jpg' and user.full_name:
                        return 'Ready To Follow'
                    else:
                        return 'Seams Fake'
                else:
                    return 'Super Popular'
            else:
                return 'Followed Before'
        else:
            return 'Private'
    except Exception as e:
        print e


def scrape_users(num_to_follow, seed_user, already_followed):
    global scraped_users
    global ignored_users
    global last_media_idx

    scraped_users = []
    ignored_users = []

    while len(scraped_users) < num_to_follow:

        all_medias = get_user_media(user_id=get_user_info(seed_user).id)

        if 'last_media_idx' in globals():
            if last_media_idx:
                all_medias = all_medias[last_media_idx + 1:]

        if all_medias:
            for idx, media in enumerate(all_medias):
                last_media_idx = idx
                puts(colored.green('\n[-] Current scraping status :'))
                with indent(quote=' |'):
                    puts(colored.yellow('Remaining Users :' + str(num_to_follow - len(scraped_users))))
                    puts(colored.yellow('Remaining Media :' + str(len(all_medias) - idx)))

                puts(colored.yellow('\n[-] grabbing users liked [' + str(media.get('id')) + '] '))
                likers = get_media_likers(media_id=media.get('id'))

                puts(colored.green('[-] Checking [' + str(len(likers)) + '] user'))
                for user in likers:
                    check_result = check_user(user=user, ids_to_avoid=already_followed + scraped_users + ignored_users)
                    if check_result == 'Ready To Follow':
                        scraped_users.append(user.get('pk'))
                        with indent(quote=' |'):
                            puts(colored.green(('User [' + str(user.get('pk')) + ']').ljust(19) + 'Snached'))
                        if len(scraped_users) >= num_to_follow:
                            return
                    else:
                        ignored_users.append(int(user.get('pk')))
                        with indent(quote=' |'):
                            if check_result != 'Already Checked':
                                puts(colored.yellow(
                                    ('User [' + str(user.get('pk')) + ']').ljust(19) + 'Ignored [' + colored.red(
                                        check_result) + colored.yellow(']')))
                            else:
                                puts(colored.yellow(
                                    ('User [' + str(user.get('pk')) + ']').ljust(19) + 'Ignored'))
        else:
            puts(colored.red('[!] Cannot get user media or User has no media ! '))
            puts(colored.red('\n[!] Exiting ...\n'))
            sys.exit()
