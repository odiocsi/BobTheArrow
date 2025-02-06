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
        self.__isloop1 = False
        self.__isloop = not self.__isloop

    def loop1(self):
        self.__isloop = False
        self.__isloop1 = not self.__isloop1

    def getLoop(self):
        if (self.__isloop):
            return 1
        if (self.__isloop1):
            return 2
        return 0

    def shuffle(self):
        import random
        random.shuffle(self.__playlist)

    def next(self):
        if self.__playlist:
            self.current = self.__playlist.pop(0)
            if self.__isloop:
                self.__playlist.append(self.current)
            if self.__isloop1:
                self.__playlist.insert(0, self.current)
                
            return self.current
        return None

    def tostring(self):
        for i, song in enumerate(self.__playlist, start=1):
            print(f"{i}. {song['title']}")

