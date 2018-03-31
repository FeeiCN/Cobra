# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import json
import requests
import re
import threading
import argparse
from cobra.log import logger
from cobra.config import code_path, Config
from cobra.__version__ import __epilog_git__, __introduction_git__

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

git_urls = []


def start(target, format, output, rules, dels, all):
    """
    start push target to api
    :param target:
    :param format:
    :param output:
    :param rules:
    :param dels:
    :param all:
    :return:
    """
    url = Config('git', 'gitlab_url').value
    private_token = Config('git', 'private_token').value
    cobra_ip = Config('git', 'cobra_ip').value
    key = Config('cobra', 'secret_key').value
    threads = []
    result_path = code_path + '/result_sid'
    fi = open(result_path, 'a+')

    try:
        if all is False and target is not '':
            if isinstance(target, list):
                for tar in target:
                    fi.write(tar + '\n')
            else:
                fi.write(target + '\n')

            res = push_to_api(target, cobra_ip, key, fi, format, output, rules, dels)

        elif all is True and target is '':
            pages = get_pages(url, private_token)
            q_pages = queue.Queue(pages)

            for i in range(int(pages)):
                q_pages.put(i + 1)

            for i in range(10):
                thread = threading.Thread(target=get_git_urls, args=(url, private_token, q_pages, fi))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            res = push_to_api(git_urls, cobra_ip, key, fi, format, output, rules, dels)

        else:
            res = False

        if res:
            logger.info("[GIT-PRO] Git push success")
            logger.info("[GIT-PRO] All projects have been pushed")
        else:
            logger.warning("[GIT-PRO] Git push fail")

        fi.close()

    except requests.exceptions.MissingSchema:
        logger.warning('[GIT-PRO] Please write gitlab_url and private_token in config file')

    except requests.exceptions.ConnectionError:
        logger.warning('[GIT-PRO] Please check the cobra_ip or gitlab_url is right')

    except requests.exceptions.InvalidSchema:
        logger.warning('[GIT-PRO] Please add http:// before the cobra_ip or gitlab_url')

    except Exception as e:
        logger.warning('[GIT-PRO] {}'.format(e.message))


def get_git_urls(url, private_token, q_pages, fi):
    """
    :param url: The gitlab's projects api ,example:http://xxx.gitlab.com/api/v3/projects
    :param private_token: The user's private_token
    :param q_pages: The Queue of pages
    :param fi: The result in this file
    :return:
    """
    while not q_pages.empty():
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

                fi.write(request_url + '\n')
                git_urls.append(request_url)

        elif r.status_code == 404:
            logger.warning("[GIT-PRO] page %d 404" % page)

        else:
            logger.warning("[GIT-PRO] page %d is %d" % page, r.status_code)
        q_pages.task_done()


def request_target(target_url, params=None, header=None, method="get"):
    """
    start request
    :param target_url:
    :param params:
    :param header:
    :param method:
    :return:
    """
    if method == "get":
        response = requests.get(url=target_url, params=params, headers=header)
        return response

    if method == "post":
        response = requests.post(url=target_url, data=json.dumps(params), headers=header)
        return response


def push_to_api(urls, cobra_ip, key, fi, format, output, rules, dels):
    """
    :param urls:
    :param cobra_ip:
    :param key:
    :param fi:
    :param format:
    :param output:
    :param rules:
    :param dels:
    :return:
    """
    headers = {"Content-Type": "application/json"}
    url = cobra_ip + "/api/add"
    payload = {"key": key, "target": urls, "dels": dels, "formatter": format, "output": output,
               "rule": rules}
    r = request_target(url, payload, headers, method="post")

    if r.status_code == 200:
        fi.write(str(r.json()) + '\n')
        logger.info('[GIT-PRO] ' + str(r.json()))
        return True

    elif r.status_code == 404:
        logger.info("[GIT-PRO] The page is 404")

    else:
        logger.info('[GIT-PRO] ' + str(r.json()))
        return False


def get_pages(url, private_token):
    """
    get the pages num
    :param url:
    :param private_token:
    :return:
    """
    params = {"private_token": private_token}
    response = request_target(url, params)
    res = response.headers['link'].split(",")
    res = res[2]
    res = re.search(r"all\?page=(\d*)&per_page=0", res)
    pages = res.group(1)
    return pages


def _check_rule_name(name):
    return re.match(r'^(cvi|CVI)-\d{6}(\.xml)?', name.strip()) is not None


if __name__ == '__main__':
    special_rules = []

    parser = argparse.ArgumentParser(prog='git_projects', epilog=__epilog_git__, description=__introduction_git__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-t', '--target', dest='target', action='store', default='', metavar='<target>', help='The git address or git list, e.g: test/vul/v.php,test/vul/v.java')
    parser.add_argument('-f', '--format', dest='format', action='store', default='json', metavar='<format>', choices=['json', 'csv', 'xml'], help='report output format')
    parser.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='report output STREAM, FILE, HTTP API URL, MAIL')
    parser.add_argument('-r', '--rule', dest='rules', action='store', default=None, metavar='<rule_id>', help='specifies rules e.g: CVI-100001,cvi-190001')
    parser.add_argument('-d', '--dels', dest='dels', action='store_true', default=False, help='del target directory True or False')
    parser.add_argument('-a', '--all', dest='all', action='store_true', default=False, help='Git push all git-projects from gitlab')
    args = parser.parse_args()

    if args.target == '' and args.all is False:
        parser.print_help()
        exit()

    if ',' in args.target:
        targets = args.target.split(',')
    else:
        targets = args.target

    try:
        if ',' in args.rules:
            rules = args.rules.split(',')
            for rule in rules:
                if _check_rule_name(rule) is False:
                    logger.critical('[GIT-PRO] Exception special rule name(e.g: CVI-110001): {sr}'.format(sr=rule))
        else:
            if _check_rule_name(args.rules) is False:
                logger.critical('[GIT-PRO] Exception special rule name(e.g: CVI-110001): {sr}'.format(sr=args.rules))

    except TypeError:
        logger.info('[GIT-PRO] The rules is None, Cobra will use all rules to scan')

    start(targets, args.format, args.output, args.rules, args.dels, args.all)
