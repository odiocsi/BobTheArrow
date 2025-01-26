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
        self.playlist = []
        self.results = []

    def search_youtube(self, query, max_results=5):
        self.results = []
        with YoutubeDL(search_opts) as ydl:
            search_result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        return search_result
    
    def download(self, url):
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)  
            return file_path  



#for id, entry in enumerate(search_result['entries'], start=1):
#    print(f"{id}. {entry['title']} ({entry['url']})")