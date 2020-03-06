# -*- coding: utf-8 -*-
import json
import sys
import urllib
from contextlib import closing
from urllib import parse
import threading
import os
import requests
import time
import re
import urllib
import socket
import socks
from configparser import ConfigParser

import scrapy
import re, datetime

from YoutubeVideoDownloader.ProgressBar import ProgressBar
from YoutubeVideoDownloader.util.CommonUtils import *

class DownloadSpider(scrapy.Spider):
    name = 'download'
    allowed_domains = ['youtubemultidownloader.net']
    start_urls = ['http://youtubemultidownloader.net/playlists.html']
    domain = 'http://youtubemultidownloader.net/playlists.html'
    parse_playlist_url = 'https://api.youtubemultidownloader.com/playlist?url='
    parse_video_url = 'https://api.youtubemultidownloader.com/video?url='
    path_domain = 'videos'
    # 播放列表
    target = []
    play_url = ''
    date_latest = ''
    date_latest_to_update = ''

    def checkdate(self, title):
        s = self.date_latest
        match = re.search('\d{4}\d{2}\d{2}', s)
        date1 = datetime.datetime.strptime(match.group(), '%Y%m%d').date()

        match = re.search('\d{4}\d{2}\d{2}', title)
        date2 = datetime.datetime.strptime(match.group(), '%Y%m%d').date()
        if date1 < date2:
            self.date_latest_to_update = date2.strftime("%Y%m%d")
            return True
        else:
            return False


    def write_config(self):
        filename = './config.ini'
        self.config = ConfigParser()
        self.config.read(filename, encoding='UTF-8')
        print('date_latest:', self.config['item']['date_latest'])
        self.date_latest = self.config['item']['date_latest']
        print('Write the latest date:',self.date_latest_to_update)
        self.config.set('item', 'date_latest', self.date_latest_to_update)
        with open(filename, 'w', encoding='utf-8') as file:
            self.config.write(file) 
        return


    def __init__(self, target=None, **kwargs):
        #print('count=',count)
        self.filename = './config.ini'
        self.config = ConfigParser()
        self.config.read(self.filename, encoding='UTF-8')
        print('url:', self.config['item']['url'])
        print('date_latest:', self.config['item']['date_latest'])
        print('===========')
        if target == '':
            target = self.config['item']['url']
        self.date_latest = self.config['item']['date_latest']
        print('target=',target)

        if '&list=' not in target:
            # 单个视频
            self.play_url = target
        else:
            # 播放列表，多个以空格切分
            self.target = target.split(' ')


    def parse(self, response):

        if self.target == []:
            # 下载单个视频
            video_tmp = json.loads(requests.get(self.parse_video_url + parse.quote(self.play_url)).content)
            if len(video_tmp) == 2:
                print(self.play_url + ' -> 不再提供')
            formats = video_tmp['format']
            for format in formats:
                if format['height'] == 720:
                    video_real_url = format['url']
                    file_path = self.path_domain + '/' + 'single'
                    video_name = self.play_url.split('v=')[1] + '.mp4'
                    mkdir(file_path)
                    if os.path.exists(file_path + '/' + video_name) == False:
                        print('正在下载 -> ' + self.play_url)
                        downloadFile(video_real_url, file_path, video_name)
                        print(self.play_url + ' -> 下载完成')
                    else:
                        print(self.play_url + ' -> 已下载')
                    break
        else:
            # 下载多个视频
            target_item_index = 1
            total_target_item = len(self.target)
            total_video_count = 1
            for target_item in self.target:
                data = json.loads(requests.get(self.parse_playlist_url + parse.quote(target_item)).content)
                videos = data['items']
                video_count = 1
                total_video_count2 = len(videos)
                play_list_name = target_item.split('&list=')[1]
                file_path = self.path_domain + '/playlist/' + play_list_name
                mkdir(file_path)
                for video in videos:
                    video_title = video['title']
                    video_name = video_title + '.mp4'
                    if not self.checkdate(video_title):
                        continue

                    # 图片不存在时再下载
                    if os.path.exists(file_path + '/' + video_name) == False:
                        video_url = video['url']
                        video_tmp = json.loads(requests.get(self.parse_video_url + parse.quote(video_url)).content)
                        if len(video_tmp) == 2:
                            print((str)(target_item_index) + '/' + (str)(total_target_item) + '个列表，第' + (str)(
                                video_count) + '/' + (str)(
                                total_video_count2) + '个视频 -> ' + play_list_name + ' ' + video_title + ' -> 不再提供')
                            video_count += 1
                            total_video_count += 1
                            continue
                        formats = video_tmp['format']
                        for format in formats:
                            if format['height'] == 720:
                                video_real_url = format['url']
                                print('正在下载第' + (str)(target_item_index) + '/' + (str)(total_target_item) + '个列表，第' + (
                                    str)(video_count) + '/' + (str)(
                                    total_video_count2) + '个视频 ' + play_list_name + ' ' + video_title)
                                downloadFile(video_real_url, file_path, video_name)
                                print((str)(target_item_index) + '/' + (str)(total_target_item) + '个列表，第' + (str)(
                                    video_count) + '/' + (str)(
                                    total_video_count2) + '个视频 -> ' + play_list_name + ' ' + video_title + ' -> 下载完成')
                                video_count += 1
                                total_video_count += 1
                                break
                    else:
                        print((str)(target_item_index) + '/' + (str)(total_target_item) + '个列表，第' + (str)(
                            video_count) + '/' + (str)(
                            total_video_count2) + '个视频 -> ' + play_list_name + ' ' + video_title + ' -> 已下载')
                        video_count += 1
                        total_video_count += 1
                        #if total_video_count > 1: #for debug
                        #    continue
                target_item_index += 1
            print('本次共下载' + (str)(total_target_item) + '个列表，' + (str)(total_video_count) + '个视频')

            self.write_config()

