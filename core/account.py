# coding=utf-8

from clint.textui import puts, indent, colored
import logging
import requests
import random

logging.basicConfig(level=logging.DEBUG, filename='log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

useragents = [
    'Mozilla/4.0 (compatible; MSIE 5.0; SunOS 5.10 sun4u; X11)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.2pre) Gecko/20100207 Ubuntu/9.04 (jaunty) Namoroka/3.6.2pre',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser;',
    'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6)',
    'Microsoft Internet Explorer/4.0b1 (Windows 95)',
    'Opera/8.00 (Windows NT 5.1; U; en)',
    'amaya/9.51 libwww/5.4.0',
    'Mozilla/4.0 (compatible; MSIE 5.0; AOL 4.0; Windows 95; c_athome)',
    'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; ZoomSpider.net bot; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; QihooBot 1.0 qihoobot@qihoo.net)',
    'Mozilla/4.0 (compatible; MSIE 5.0; Windows ME) Opera 5.11 [en]']


def login(username, password):
    global SESSIONID, CSRF, MID, CSRF, USERNAME

    try:
        useragent = random.choice(useragents)
        puts(colored.yellow('[-] setting user agent ' + useragent))
        r = requests.get('https://instagram.com/', verify=False)
        csrf_token = r.cookies['csrftoken']
        puts(colored.yellow('[-] setting CSRF to ' + csrf_token))
        post_url = 'https://www.instagram.com/accounts/login/ajax/'

        post_data = {
            'username': username,
            'password': password
        }

        header = {
                "User-Agent": useragent,
                'X-Instagram-AJAX': '1',
                "X-CSRFToken": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                'Cookie': 'csrftoken=' + csrf_token
        }

        r = requests.post(post_url, headers=header, data=post_data, verify=False, allow_redirects=False)

        if r.text.find('"authenticated": true') != -1:
            puts(colored.green('[!] Login success .'))
            SESSIONID = r.cookies['sessionid']
            CSRF = r.cookies['csrftoken']
            MID = r.cookies['mid']
            USERNAME = username
            puts(colored.green('[-] session id grabbed success . '))
        else:
            return False

        return True
    except Exception:
        err = None
        puts(colored.red('[E] oh no , we have a problem in bot , please check log file !'))
        logger.error(err)
