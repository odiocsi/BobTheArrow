import requests
from datetime import datetime
import pytz

class RivalsAPI:
    def __init__(self, TOKEN):
        self.__baseurl = "https://marvelrivalsapi.com/api/v1/"
        self.__headers = {"x-api-key": TOKEN}
        self.__map_names = {

        }
        self.__update_map_names()

    def get_player_data(self, name, season):
        try:
            if season == "update":
                requests.get(f"{self.__baseurl}player/{name}/update", headers=self.__headers)
                return True
            else: 
                response = requests.get(f"{self.__baseurl}player/{name}", params={'season': season}, headers=self.__headers)

                if response.status_code == 200:
                    data = response.json()

                    if data['isPrivate']:
                        return False

                    sorted_heroes = sorted(data["heroes_ranked"], key=lambda x: x["matches"], reverse=True)

                    heroes = []
                    for h in sorted_heroes[:3]:
                        heroes.append(self.__extract_hero_data(h))

                    rank = data['player']['rank']['rank']
                    if rank == "Invalid level":
                        rank = "N/A"

                    winrate = ""
                    try:
                        winrate = f"{data['overall_stats']['ranked']['total_wins']/data['overall_stats']['ranked']['total_matches']*100:.2f}%"
                    except:
                        winrate = "N/A"
                    finally:
                        returndata = {
                            'update': self.__get_time(data['updates']['last_history_update']),
                            'rank': rank,
                            'winrate': winrate,
                            'heroes': heroes
                        }

                    return returndata
                else:
                    print(f"{response.status_code}, Error: {response.text}")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_map_data(self, name, season):
        try:
            response = requests.get(f"{self.__baseurl}player/{name}", params={'season': season}, headers=self.__headers)

            if response.status_code == 200:
                data = response.json()


                if data['isPrivate']:
                    return False

                sorted_maps = sorted(data["maps"], key=lambda x: x['wins']/x["matches"], reverse=True)
                sorted_maps = [m for m in sorted_maps if m["map_id"]]

                returndata = {
                    'update': self.__get_time(data['updates']['last_history_update']),
                    'maps': [
                        {
                            'name': f"{self.__map_names.get(m['map_id'])}",
                            'matches': m['matches'],
                            'winrate': f"{m['wins'] / m['matches'] * 100:.2f}" if m['matches'] > 0 else "0.00",
                        }
                        for m in sorted_maps
                    ]
                }

                return returndata
            else:
                print(f"{response.status_code}, Error: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_matchup_data(self, name, season):
        try:
            response = requests.get(f"{self.__baseurl}player/{name}", params={'season': season}, headers=self.__headers)

            if response.status_code == 200:
                data = response.json()

                if data['isPrivate']:
                    return False

                sorted_heroes = sorted(data["hero_matchups"], key=lambda x: x['wins']/x["matches"], reverse=True)

                returndata = {
                    'update': self.__get_time(data['updates']['last_history_update']),
                    'heroes': [
                        {
                            'name': h['hero_name'],
                            'matches': h['matches'],
                            'winrate': f"{h['wins'] / h['matches'] * 100:.2f}" if h['matches'] > 0 else "0.00"
                        }
                        for h in sorted_heroes
                    ]
                }

                return returndata
            else:
                print(f"{response.status_code}, Error: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def __update_map_names(self):
        try:
            response = requests.get(f"{self.__baseurl}maps?page=1&limit=100", headers=self.__headers)
            if response.status_code == 200:
                data = response.json()
                map_names = {}

                for entry in data["maps"]:
                    map_id = entry.get("id")
                    map_name = entry.get("name") or "Unknown"
                    if map_id is not None:
                        map_names[map_id] = map_name

                self.__map_names = map_names
            else:
                print(f"{response.status_code}, Error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


    def __extract_hero_data(self, hero):
        extracted = {
            'name': hero['hero_name'],
            'matches': hero['matches'],
            'winrate': f"{hero['wins']/hero['matches']*100:.2f}",
            'mvpsvp': hero['mvp']+hero['svp'],
            'playtime': f"{hero['play_time']/3600:.0f}",
            'img_url': f"https://marvelrivalsapi.com/rivals{hero['hero_thumbnail']}",
        }

        return extracted
    
    def __get_time(self, time_str):
        try: 
            time_format = "%m/%d/%Y, %I:%M:%S %p"

            utc_minus_5 = pytz.timezone("America/New_York")  
            cet = pytz.timezone("Europe/Berlin")  

            return utc_minus_5.localize(datetime.strptime(time_str, time_format)).astimezone(cet).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "N/A"
      