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
from pytube import YouTube


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
    key = ''
    value = 0
    def download(self, url, file_name):
        YouTube(url).streams.first().download(file_name)
        return


    def getindex(self, title):
        try:
            match = re.search('\d{4}\d{2}\d{2}', title)
            date = datetime.datetime.strptime(match.group(), '%Y%m%d').date()
            datestr = date.strftime("%Y%m%d")
            index = title[title.find(datestr)+9:-2]
            print('index======================')
            print(index)
            if self.value < int(index) :
                self.value = int(index)  # save index

            return index + '-'
        except:
            print("An exception occurred")
            return ''


    def checkdate(self, title):
        try:
            s = self.date_latest
            if len(s) < 4:
                return True # disable date check

            match = re.search('\d{4}\d{2}\d{2}', s)
            date1 = datetime.datetime.strptime(match.group(), '%Y%m%d').date()
            match = re.search('\d{4}\d{2}\d{2}', title)
            date2 = datetime.datetime.strptime(match.group(), '%Y%m%d').date()
            if date1 < date2:
                self.date_latest_to_update = date2.strftime("%Y%m%d")
                return True
            else:
                return False
        except:
            print("An exception occurred")
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


    def write_index(self, key, value):
        print('key=',key)
        print('value=',value)
        filename = './config.ini'
        config = ConfigParser()
        config.read(filename, encoding='UTF-8')
        #print('key from config:', self.config['item'][key])
        #config.add_section('keys')
        config['keys'][key] = str(value)
        with open(filename, 'w', encoding='utf-8') as file:
            config.write(file) 
        return


    def __init__(self, target=None, **kwargs):
        #print('count=',count)
        self.filename = './config.ini'
        self.config = ConfigParser()
        self.config.read(self.filename, encoding='UTF-8')
        print('url:', self.config['item']['url'])
        print('date_latest:', self.config['item']['date_latest'])
        if target == '':
            target = self.config['item']['url']
        self.date_latest = self.config['item']['date_latest']
        print('target=',target)
        self.value = 0

        if '&list=' not in target:
            # 单个视频
            self.play_url = target
        else:
            # 播放列表，多个以空格切分
            self.target = target.split(' ')


    def safe_download(self, video_real_url, video_url, file_path, new_name):
        downloadFile(video_real_url, file_path, new_name)
        newfile = file_path + '/' + new_name
        if os.path.getsize(newfile) < 10 :
            os.remove(newfile)
            self.download(video_url, newfile)
        print('===========newfile')
        print(newfile)


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

                #print('======================')
                #print(data)
                #debug only
                text_file = open("data.txt", "w")
                n = text_file.write(str(data))
                text_file.close()

                videos = data['items']
                #print('======================')
                #print(videos)
                video_count = 1
                total_video_count2 = len(videos)
                play_list_name = target_item.split('&list=')[1]
                file_path = self.path_domain + '/playlist/' + play_list_name

                self.key = play_list_name # save key

                mkdir(file_path)
                for video in videos:
                    video_title = video['title']
                    video_title = video_title.replace("/", "-")
                    video_name = video_title + '.mp4'
                    print('video_name:\n'+ video_name)
                    if not self.checkdate(video_title):
                        continue

                    #if total_video_count > 2: #for debug
                    #    continue

                    # 图片不存在时再下载
                    new_name = self.getindex(video_title) + video_name
                    new_file_path = file_path + '/' + new_name
                    if (os.path.exists(new_file_path) == False) or (os.path.getsize(new_file_path) < 10) :
                        video_url = video['url']
                        print('url=======',video_url)
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
                                #new_name = self.getindex(video_title) + video_name
                                #downloadFile(video_real_url, file_path, new_name)
                                #self.download(video_url, file_path)
                                self.safe_download(video_real_url, video_url, file_path, new_name)

                                print(video_real_url)
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

            #self.write_config()
            self.write_index(self.key, self.value)

