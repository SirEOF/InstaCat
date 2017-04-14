# coding=utf-8
from util import req, ObjectParser
import json


def get_user_info(username):
    url = 'https://www.instagram.com/%s/?__a=1' % username
    try:
        r = req(url, 'GET', None)
        if r.status_code != 200:
            return False
        else:
            user_info = ObjectParser(**json.loads(r.text))
            return user_info.user
    except Exception as err:
        print err
        exit()
        return False


def get_user_media(user_id):
    url = 'https://www.instagram.com/query/'
    payload = {'q': 'ig_user(%s){media{count,nodes{code,id,likes{count}},page_info}}' % user_id}
    try:
        r = req(url, 'POST', payload)
        if r.status_code != 200:
            return False
        else:
            user_media = ObjectParser(**json.loads(r.text))
            if user_media.media.count == 0:
                return False
            return user_media.media.nodes
    except Exception as err:
        return False


def get_media_likers(media_id):
    url = 'https://i.instagram.com/api/v1/media/%s/likers/?' % media_id
    try:
        r = req(url, 'GET', None)
        if r.status_code != 200:
            return False
        else:
            media_likers = ObjectParser(**json.loads(r.text))
            return media_likers.users

    except Exception as err:
        return False
