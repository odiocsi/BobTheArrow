from yt_dlp import YoutubeDL
import random

## Config
download_folder = "music"

search_opts = {
    'format': 'bestaudio/best',  
    'noplaylist': True,  
    'quiet': True,               
    'extract_flat': True,      
    'default_search': 'ytsearch',  
}

download_opts = {
    'format': 'bestaudio/best',  
    'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 
    'noplaylist': True,  
}

## Downloader class
class MusicDownloader:
    def __init__(self):
        self.results = []

    def search(self, query, max_results=5):
        self.results = []
        with YoutubeDL(search_opts) as ydl:
            search_result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        return search_result
    
    def download(self, url):
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)  
            return file_path  


## Playlist class
class Playlist:
    def __init__(self):
        self.__playlist = []
        self.__index = 0
        self.__loop = "no"
        self.current = []

    def add(self, title, url):
        self.__playlist.append({'title': title, 'url': url})
    
    def clear(self):
        self.__playlist = []

    def remove(self, i):
        if i < len(self.__playlist):
            self.__playlist.pop(i)

    def loop(self):
        if self.__loop == "no" and not self.isEmpty():
            if not (self.current in self.__playlist):
                self.__playlist.insert(0, self.current)
            self.__loop = "whole"
            return "🔁"
        if self.__loop == "whole" or (self.isEmpty() and not self.__loop == "one"):
            if (self.current in self.__playlist):
                self.__playlist.remove(self.current)
            self.__loop = "one"
            return "🔄"
        if self.__loop == "one":
            self.__loop = "no"
            return ""

    def isEmpty(self):  
        return not self.__playlist

    def shuffle(self):
        random.shuffle(self.__playlist)

    def next(self):
        if self.__playlist:
            if self.__loop == "whole":
                if not (self.current in self.__playlist):
                    self.__playlist.insert(0, self.current)
                if self.__index >= len(self.__playlist) - 1:
                    self.__index = 0
                else:
                    self.__index += 1
                self.current = self.__playlist[self.__index]
            elif self.__loop == "one":
                if (self.current in self.__playlist):
                    self.__playlist.remove(self.current)
                self.__index = 0
            else: 
                self.__index = 0
                self.current = self.__playlist.pop(0)

            return self.current

    def tostring(self):
        if self.__playlist:
            string = ""
            if not self.__loop == "whole":
                for i, item in enumerate(self.__playlist):
                    string += f"{i}. {item['title']}\n"
            else:
                list2 = self.__playlist[self.__index+1:]
                for i, item in enumerate(list2):
                    string += f"{i}. {item['title']}\n"
                list1 = self.__playlist[:self.__index+1]
                for i, item in enumerate(list1):
                    string += f"{i}. {item['title']}\n"
            return string
        else:
            return  "A lejátszasi lista üres"

