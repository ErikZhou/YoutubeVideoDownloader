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

import scrapy

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

    def __init__(self, target=None, **kwargs):
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
                target_item_index += 1
            print('本次共下载' + (str)(total_target_item) + '个列表，' + (str)(total_video_count) + '个视频')