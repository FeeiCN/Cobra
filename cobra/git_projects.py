# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import json
import requests
import re
import threading
from .log import logger
from .config import code_path, Config

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue


def start():
    url = Config('git', 'gitlab_url').value
    private_token = Config('git', 'private_token').value
    cobra_ip = Config('git', 'cobra_ip').value
    key = Config('cobra', 'secret_key').value
    threads = []
    pages = get_pages(url, private_token)
    q_pages = queue.Queue(pages)
    result_path = code_path + '/result_sid'
    fi = open(result_path, 'w+')
    for i in range(int(pages)):
        q_pages.put(i + 1)

    for i in range(10):
        thread = threading.Thread(target=get_git_urls, args=(url, private_token, cobra_ip, key, q_pages, fi))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    fi.close()
    logger.info("All projects have been pushed")


def get_git_urls(url, private_token, cobra_ip, key, q_pages, fi):
    """
    :param url: The gitlab's projects api ,example:http://xxx.gitlab.com/api/v3/projects
    :param private_token: The user's private_token
    :param cobra_ip: The Cobra server's ip
    :param key: The Cobra api key
    :param q_pages: The Queue of pages
    :param fi: The result in this file
    :return:
    """
    while not q_pages.empty():
        git_urls = []
        page = q_pages.get()
        params = {'private_token': private_token, 'page': page}
        url = url
        r = request_target(url, params, method="get")

        if r.status_code == 200:
            data = r.json()  # 一个页面中的Json数据，默认20条
            for j in range(len(data)):
                git_url = data[j]['http_url_to_repo']
                git_branch = data[j]['default_branch']

                if git_branch is not None:
                    request_url = git_url + ':' + git_branch

                else:
                    request_url = git_url

                git_urls.append(request_url)
            res = push_to_api(git_urls, cobra_ip, key, fi)
            if res:
                logger.info("page %d git push success" % page)
            else:
                logger.info("page %d git push fail" % page)

        elif r.status_code == 404:
            logger.warning("page %d 404" % page)

        else:
            logger.warning("page %d is %d" % page, r.status_code)
        q_pages.task_done()


def request_target(target_url, params=None, header=None, method="get"):
    if method == "get":
        response = requests.get(url=target_url, params=params, headers=header)
        return response
    if method == "post":
        response = requests.post(url=target_url, data=json.dumps(params), headers=header)
        return response


def push_to_api(urls, cobra_ip, key, fi):
    headers = {"Content-Type": "application/json"}
    url = cobra_ip + "/api/add"
    payload = {"key": key, "target": urls}
    r = request_target(url, payload, headers, method="post")
    if r.status_code == 200:
        fi.write(str(r.json()) + '\n')
        logger.info(r.json())
        return True
    else:
        logger.info(r.json())
        return False


def get_pages(url, private_token):
    params = {"private_token": private_token}
    response = request_target(url, params)
    res = response.headers['link'].split(",")
    res = res[2]
    res = re.search(r"all\?page=(\d*)&per_page=0", res)
    pages = res.group(1)
    return pages
