from yt_dlp import YoutubeDL

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

class Playlist:
    def __init__(self):
        self.__playlist = []
        self.__index = 0
        self.__isloop = False
        self.__isloop1 = False
        self.current = []

    def add(self, title, url):
        self.__playlist.append({'title': title, 'url': url})
    
    def clear(self):
        self.__playlist = []

    def remove(self, i):
        if i < len(self.__playlist):
            self.__playlist.pop(i)

    def loop(self):
        if not self.__isloop and not self.__isloop1:
            self.__isloop = True
            return "🔁"
        if self.__isloop: 
            self.__isloop = False
            self.__isloop1 = True
            return "🔄"
        if self.__isloop1:
            self.__isloop1 = False
            return ""

    def isEmpty(self):  
        return not self.__playlist

    def shuffle(self):
        import random
        random.shuffle(self.__playlist)

    def next(self):
        if self.__playlist:
            if self.__isloop:
                if not (self.current in self.__playlist):
                    self.__playlist.insert(0, self.current)
                if self.__index == len(self.__playlist) - 1:
                    self.__index = 0
                else:
                    self.__index += 1
                self.current = self.__playlist[self.__index]
            elif self.__isloop1:
                if not (self.current in self.__playlist):
                    self.__playlist.insert(0, self.current)
                else:
                    self.__playlist.remove(self.current)
                    self.__playlist.insert(0, self.current)
                self.__index = 0
                self.current = self.__playlist[0]
            else: 
                self.__index = 0
                self.current = self.__playlist.pop(0)

            return self.current

    def tostring(self):
        if self.__playlist:
            string = ""
            if (self.__index == 0):
                i = 0
                counter = 1
                while i < len(self.__playlist):
                    string += f"{counter}. {self.__playlist[i]['title']}\n"
                    i += 1
                    counter += 1 
            else:
                i = self.__index +1
                counter = 1
                while i < len(self.__playlist):
                    string += f"{counter}. {self.__playlist[i]['title']}\n"
                    i += 1 
                    counter += 1
                i = 0
                while i <= self.__index:
                    string += f"{counter}. {self.__playlist[i]['title']}\n"
                    i += 1
                    counter += 1
            return string
        else:
            return  "A lejátszasi lista üres"
