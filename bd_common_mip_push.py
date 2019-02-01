from datetime import datetime
import os
import time
from configparser import ConfigParser
import _thread
import subprocess
from random import sample
import sys


def parse_config(config_path):
    config = ConfigParser()
    config.read(config_path, 'utf-8')
    timer_controller_1 = config.get('article', 'timer_controller_1')
    timer_controller_2 = config.get('article', 'timer_controller_2')
    timer_controller_3 = config.get('article', 'timer_controller_3')
    timer_controller_4 = config.get('article', 'timer_controller_4')
    timer_controller_5 = config.get('article', 'timer_controller_5')
    site = config.get('article', 'site')
    token = config.get('article', 'token')
    rand_all = int(config.get('article', 'rand_all'))
    if rand_all == 1:
        if os.path.exists('url/cache/') is not True:
            os.mkdir('url/cache')
        time_now = datetime.now().strftime('%H:%M:%S')
        if time_now == timer_controller_1:
            _thread.start_new_thread(push_url, (1, site, token, config))
        if time_now == timer_controller_2:
            _thread.start_new_thread(push_url, (2, site, token, config))
        if time_now == timer_controller_3:
            _thread.start_new_thread(push_url, (3, site, token, config))
        if time_now == timer_controller_4:
            _thread.start_new_thread(push_url, (4, site, token, config))
        if time_now == timer_controller_5:
            _thread.start_new_thread(push_url, (5, site, token, config))


def push_url(thread_num, site, token, config):
    sys.stdout.write('\n定时任务%s %s %s \n' % (thread_num, site, token))
    array_path = []
    array_number = []
    # 读取配置文件
    https = int(config.get('article', 'https'))
    for num in range(1, 15):
        try:
            list_path = config.get('article', 'path%s' % num)
            number = config.get('article', 'num%s' % num)
        except Exception as e:
            continue
        array_number.append(number)
        array_path.append(list_path)
    for num in range(0, len(array_path)):
        _thread.start_new_thread(create_all_urls, (thread_num, site, array_path[num], array_number[num], token, https))
        time.sleep(1)


def rand_char():
    char = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    return ''.join(sample(char, 5))


# 推送url到百度
def post_all_url(thread_num, domain, token, target_path, post_list):
    post = 'curl -H "Content-Type:text/plain" --data-binary @%s ' \
             '"http://data.zz.baidu.com/urls?site=%s&token=%s"' % (target_path, domain, token)
    output = subprocess.Popen(post, shell=True, stdout=subprocess.PIPE)
    out, err = output.communicate()
    try:
        http = eval(out)
        if b'success' in out:
            sys.stdout.write('\n%s 任务 %s 推送成功条 %s 条 剩余额度 %s 目标网址 %s 栏目 %s\n'
                             % (print_time(), thread_num, http['success'], http['remain'],
                                domain, post_list))

            return int(http['remain'])
        else:
            sys.stdout.write('\n推送失败! error: %s \n' % http['message'])
            return 0
    except IndexError as index:
        sys.stdout.write("\n%s %s \n" % (index, '服务器未返回数据'))
        time.sleep(3)


# 生成推送链接
def create_all_urls(thread_num, site, post_list, post_num, token, https):
    this_num = int(str(post_num).split(',')[thread_num - 1])
    target_path = 'url/cache/%s_%s_%s.txt' % (thread_num, post_list, str(site).replace('.', '_'))
    post_url = open(target_path, 'w+', encoding='utf-8')
    now_time = datetime.now().strftime('%Y%m%d')  # 现在
    if https == 1:
        for num in range(0, this_num):
            value = rand_char()
            target_url = 'https://' + site + '/' + post_list + '/' + now_time + value + '.html\n'
            post_url.write(target_url)
    else:
        for num in range(0, this_num):
            value = rand_char()
            target_url = 'http://' + site + '/' + post_list + '/' + now_time + value + '.html\n'
            post_url.write(target_url)
    post_url.close()
    post_all_url(thread_num, site, token, target_path, post_list)


def print_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def main():
    while True:
        for parent, dir_names, filename in os.walk('config'):
            for name in filename:
                config_path = os.path.join(parent, name)
                parse_config(config_path)
        time.sleep(1)


if __name__ == '__main__':
    main()
