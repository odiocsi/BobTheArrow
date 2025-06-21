import requests
from datetime import datetime
import pytz
import time

REGION_PLATFORM_MAP = {
    'na1': 'americas',
    'br1': 'americas',
    'lan1': 'americas',
    'las1': 'americas',
    'kr': 'asia',
    'jp1': 'asia',
    'eun1': 'europe',
    'euw1': 'europe',
    'tr1': 'europe',
    'ru': 'europe',
    'oc1': 'sea',
    'ph2': 'sea',
    'sg2': 'sea',
    'th2': 'sea',
    'tw2': 'sea',
    'vn2': 'sea',
}

class LolAPI:
    def __init__(self, TOKEN):
        self.__headers = {"X-Riot-Token": TOKEN}
        self.__ddragon_version = "14.11.1"

    def __get_platform_routing(self, region):
        return region.lower()

    def __get_regional_routing(self, region):
        return REGION_PLATFORM_MAP.get(region.lower(), 'americas')

    def __get_time(self, timestamp_ms):
        utc_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=pytz.utc)
        return utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    def __get_puuid(self, game_name, tag_line, region):
        regional_routing = self.__get_regional_routing(region)
        url = f"https://{regional_routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        try:
            response = requests.get(url, headers=self.__headers)
            if response.status_code == 200:
                return response.json()['puuid']
            else:
                print(f"Error fetching PUUID: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def __get_summoner_id(self, puuid, region):
        platform_routing = self.__get_platform_routing(region)
        url = f"https://{platform_routing}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        try:
            response = requests.get(url, headers=self.__headers)
            if response.status_code == 200:
                return response.json()['id']
            else:
                print(f"Error fetching Summoner ID: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def __get_aggregated_stats(self, puuid, region, match_count=20):
        regional_routing = self.__get_regional_routing(region)
        url_matches = f"https://{regional_routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={match_count}"
        try:
            response_matches = requests.get(url_matches, headers=self.__headers)
            if response_matches.status_code != 200:
                return None, f"Error fetching match list: {response_matches.status_code}"
            match_ids = response_matches.json()

            if not match_ids:
                return {}, None

            champion_stats = {}
            total_wins = 0
            last_match_time = 0

            for match_id in match_ids:
                url_match_detail = f"https://{regional_routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
                resp_detail = requests.get(url_match_detail, headers=self.__headers)

                if resp_detail.status_code == 200:
                    match_data = resp_detail.json()

                    player_data = next((p for p in match_data['info']['participants'] if p['puuid'] == puuid), None)
                    if not player_data:
                        continue

                    if last_match_time == 0:
                        last_match_time = match_data['info']['gameEndTimestamp']

                    champ_name = player_data['championName']
                    win = player_data['win']
                    kills = player_data['kills']
                    deaths = player_data['deaths']
                    assists = player_data['assists']
                    play_time = player_data['timePlayed']

                    if win:
                        total_wins += 1

                    if champ_name not in champion_stats:
                        champion_stats[champ_name] = {'matches': 0, 'wins': 0, 'kills': 0, 'deaths': 0, 'assists': 0, 'play_time': 0}

                    champion_stats[champ_name]['matches'] += 1
                    if win:
                        champion_stats[champ_name]['wins'] += 1
                    champion_stats[champ_name]['kills'] += kills
                    champion_stats[champ_name]['deaths'] += deaths
                    champion_stats[champ_name]['assists'] += assists
                    champion_stats[champ_name]['play_time'] += play_time
                else:
                    print(f"Could not fetch details for match {match_id}. Status: {resp_detail.status_code}")

                time.sleep(0.1)

            return {
                'total_matches': len(match_ids),
                'total_wins': total_wins,
                'champion_stats': champion_stats,
                'last_update_timestamp': last_match_time
            }, None

        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {e}"


    def get_player_data(self, game_name, tag_line, region):
        puuid = self.__get_puuid(game_name, tag_line, region)
        if not puuid:
            return "Player not found."

        summoner_id = self.__get_summoner_id(puuid, region)
        if not summoner_id:
            return "Could not retrieve summoner details."

        platform_routing = self.__get_platform_routing(region)
        url_rank = f"https://{platform_routing}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        rank_str = "Unranked"
        try:
            resp_rank = requests.get(url_rank, headers=self.__headers)
            if resp_rank.status_code == 200:
                rank_data = resp_rank.json()
                solo_rank = next((q for q in rank_data if q['queueType'] == 'RANKED_SOLO_5x5'), None)
                if solo_rank:
                    rank_str = f"{solo_rank['tier']} {solo_rank['rank']} ({solo_rank['leaguePoints']} LP)"
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch rank: {e}")

        aggregated_stats, error = self.__get_aggregated_stats(puuid, region)
        if error:
            return error
        if not aggregated_stats or not aggregated_stats.get('champion_stats'):
            return {'rank': rank_str, 'update': "N/A", 'winrate': "N/A - No recent matches found", 'heroes': []}

        try:
            winrate = f"{aggregated_stats['total_wins'] / aggregated_stats['total_matches'] * 100:.2f}%"
        except ZeroDivisionError:
            winrate = "N/A"

        processed_heroes = []
        for name, stats in aggregated_stats['champion_stats'].items():
            processed_heroes.append(self.__extract_hero_data(name, stats))

        sorted_heroes = sorted(processed_heroes, key=lambda x: x["matches"], reverse=True)

        returndata = {
            'update': self.__get_time(aggregated_stats['last_update_timestamp']) if aggregated_stats.get('last_update_timestamp') else "N/A",
            'rank': rank_str,
            'winrate': winrate,
            'heroes': sorted_heroes[:3]
        }
        return returndata

    def __extract_hero_data(self, name, hero_stats):
        try:
            winrate_val = hero_stats['wins'] / hero_stats['matches'] * 100
            winrate_str = f"{winrate_val:.2f}%"
        except ZeroDivisionError:
            winrate_str = "0.00%"

        try:
            deaths = hero_stats['deaths'] if hero_stats['deaths'] > 0 else 1
            kda = (hero_stats['kills'] + hero_stats['assists']) / deaths
            kda_str = f"{kda:.2f}"
        except ZeroDivisionError:
            kda_str = "Perfect"

        extracted = {
            'name': name,
            'matches': hero_stats['matches'],
            'winrate': winrate_str,
            'kda': kda_str,
            'playtime': f"{hero_stats['play_time'] / 3600:.1f}h",
            'img_url': f"https://ddragon.leagueoflegends.com/cdn/{self.__ddragon_version}/img/champion/{name}.png"
        }
        return extracted


