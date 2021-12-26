#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs

from collections import deque

from os.path import isfile,isdir
from sys import stderr

import threading

import youtube_dl
#TODO auto-updater

import mpv
#not pip install mpv
#user pip install python-mpv


import mypage
#local html code

def debug(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

def handlerFactory(player):
    class MyHandler(BaseHTTPRequestHandler):
        def build_page(self, result=""):
            #TODO seperate pagebuilds for different pages
            string = mypage.html_start + mypage.base_page
            string = string + "<p class=\"result\">%s</p>\n" % result
            #TODO add mpv state

            string = string + mypage.song_list
            string = string + "<p class=\"loaded\">\n"
            for t in player.get_mpv_titles():
                string = string + "%s<br>\n" % t
            string = string + "</p>\n"
            #TODO add front_queue
            string = string + "<p class=\"queued\">\n"
            for t in player.get_queue_titles():
                string = string + "%s<br>\n" % t
            string = string + "</p>\n"

            #for p in player.get_playlists():
            #    string = string + "<p>" + p + "</p>\n"

            string = string + mypage.html_end
            return string.encode("utf-8")

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.build_page())
            #TODO return page depending on requested url
            #NICE add favicon

        def parse_POST(self):
            ctype, pdict = parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = parse_qs(
                        self.rfile.read(length).decode("utf-8"),
                        keep_blank_values=1, encoding="utf-8")
            else:
                postvars = {}
            return postvars

        def do_POST(self):
            page = bytes("", "utf-8")
            responsedict = self.parse_POST()
            if 'control' in responsedict:
                debug(responsedict['control'])
                cmd = responsedict['control']
                if(cmd == ['play']):
                    player.mpv.pause = False
                    page = self.build_page("play")
                elif(cmd == ['pause']):
                    player.mpv.pause = True
                    page = self.build_page("pause")
                elif(cmd == ['vor']):
                    if(player.mpv.playlist):
                        player.mpv.playlist_next()
                    page = self.build_page("vor")
                elif(cmd == ['zurück']):
                    if(player.mpv.playlist):
                        player.mpv.playlist_prev()
                    page = self.build_page("zurück")
                else:
                    page = self.build_page("unknown mpv command")

            elif ('link' in responsedict) and ('ytlnk' in responsedict):
                debug(responsedict['link'][0] + " submitted link '"\
                    + responsedict['ytlnk'][0] + "'")
                front = (responsedict['link'][0] == "jetzt abspielen")
                result = player.load_from_url(responsedict['ytlnk'][0], front)
                page = self.build_page(result)
            else:
                debug(responsedict)
                page = self.build_page("unknown POST")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(page)
    return MyHandler

class Player():
    listfile = ""
    cachedir = None
    playlists = None
    ydl = None
    mpv = None

    queuelock = None
    back_queue = None #[(title, url, filename)]
    back_item = None
    front_queue = None #[([(title, url, filename)], seq)]
    front_item = None
    front_seq = 0
    seq_to_id = None
    worker = False
    dictlock = None
    file_to_title = None

    def __init__(self, listfile, ydl, cachedir):
        self.listfile = listfile
        self.playlists = {}
        self.ydl = ydl
        self.cachedir = cachedir
        self.back_queue = deque()
        self.front_queue = deque()
        self.front_seq = 0
        self.seq_to_id = {}
        self.queuelock = threading.Lock()
        self.file_to_title = {}
        self.dictlock = threading.Lock()
        self.worker = False
        self.mpv = mpv.MPV(force_window=False, log_handler=print)
        with open(listfile, 'r') as f:
            for line in f:
                self.resolve_listname(line)

    def check_for_songfile(self, url):
        return False

    def resolve_listname(self, url):
        self.save_listname(url, self.ydl.extract_info(url, download=False)['title'])

    def save_listname(self, url, title):
        self.playlists[url] = title

    def append_to_listfile(self, url, title):
        with open(self.listfile, 'a') as f:
            f.write(url)
        self.save_listname(url, title)

    def get_mpv_titles(self):
        r = []
        self.dictlock.acquire()
        for i in self.mpv.playlist:
            if 'filename' in i:
                if i['filename'] in self.file_to_title:
                    r.append(self.file_to_title[i['filename']])
        self.dictlock.release()
        return r

    def get_playlists(self):
        return self.playlists.values()

    def get_index_by_id(self, id):
        for index, d in enumerate(self.mpv.playlist):
            if('id' in d):
                if(d['id'] == id):
                    return index
        return -1

    def get_top_id(self):
        return self.mpv.playlist[0]['id']

    def ytdl_or_file(self, item):
        debug("ytdl_or_file")
        if( not isfile(item[2])):
            self.ydl.download([item[1]])
        self.dictlock.acquire()
        self.file_to_title[item[2]] = item[0]
        self.dictlock.release()
        if(len(self.mpv.playlist) == 0):
            self.mpv.play(item[2])
        else:
            self.mpv.playlist_append(item[2])

    def work_queues(self):
        while(True):
            self.queuelock.acquire()
            if self.front_queue:
                cont = self.front_queue[-1]
                item = cont[0].pop()
                if(not cont[0]):
                    self.front_queue.pop()
                self.queuelock.release()
                self.ytdl_or_file(item)
                if(cont[1] in self.seq_to_id):
                    index = self.get_index_by_id(self.seq_to_id[cont[1]])
                    self.mpv.playlist_move(len(self.mpv.playlist)-1,index + 1)
                else:
                    self.mpv.playlist_move(len(self.mpv.playlist)-1,0)
                    self.seq_to_id[cont[1]] = self.get_top_id()
                    self.mpv.playlist_play_index(0)
                #debug(self.mpv.playlist)
            elif self.back_queue:
                item = self.back_queue.popleft()
                self.queuelock.release()
                self.ytdl_or_file(item)
                #debug(self.mpv.playlist)
            else:
                self.worker = False
                self.queuelock.release()
                return

    def add_to_queue(self, item, front=False):
        self.queuelock.acquire()
        if(front == True):
            self.front_seq = self.front_seq + 1
            self.front_queue.append((item,self.front_seq))
            #front queue contains lists to keep
            #order of playlists correct
        else:
            self.back_queue.extend(item)
        if(self.worker == False):
            debug("started worker thread")
            threading.Thread(target=self.work_queues).start()
        self.queuelock.release()

    def get_queue_titles(self, front=False):
        self.queuelock.acquire()
        try:
            if(front == True):
                l = list(zip(list(zip(*self.front_queue))[0]))[0]
            else:
                l = list(zip(*self.back_queue))[0]
        except IndexError:
            l = []
        self.queuelock.release()
        return l


    def load_from_url(self, url, front=False):
        try:
            yresult = self.ydl.extract_info(url, download=False)
            if 'entries' in yresult:
                if not url in self.playlists:
                    self.append_to_listfile(url, yresult['title'])

                titles = []

                for video in yresult['entries']:
                    titles.append((video['title'],\
                                   video['webpage_url'],\
                                   self.ydl.prepare_filename(video)))
                    debug("playlist: " + video['title'] + "\t" + \
                          video['webpage_url'] + "\t" + \
                          self.ydl.prepare_filename(video))
                self.add_to_queue(titles, front)
                return "playlist " + yresult['title'] + " hinzugefügt"

            else:
                video = yresult
                debug("video: " + video['title'] + "\t" + video['webpage_url'] + "\t" + \
                    self.ydl.prepare_filename(video))
                self.add_to_queue([(video['title'],\
                                    video['webpage_url'],\
                                    self.ydl.prepare_filename(video))], front)
                return "video " + video['title'] + " hinzugefügt"

        except youtube_dl.utils.DownloadError:
            return u"ungültiger link"

if __name__ == "__main__":
    #TODO args handling for cachedir, port, listfile etc.
    if(isdir("/home/pi")):
        hostName = "0.0.0.0"
        serverPort = 8080
        cachedir = "/mnt/pi/usbcache/cachedir/"
        listfile = "/mnt/pi/usbcache/listfile"
    else:
        hostName = "localhost"
        serverPort = 8080
        cachedir = "cachedir/"
        listfile = "listfile"

    if(not isfile(listfile)):
        listfile = "/dev/null"
        debug("using /dev/null for nonexisting listfile")
    ydl = youtube_dl.YoutubeDL({'outtmpl': (cachedir + '%(id)s.%(ext)s'),\
                                'format':'bestaudio', 'quiet':True})

    player = Player(listfile, ydl, cachedir)
    debug("player started with listfile " + player.listfile + " and cachedir " + cachedir)

    handler = handlerFactory(player)
    webServer = HTTPServer((hostName, serverPort), handler)
    debug("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    debug("Server stopped.")
