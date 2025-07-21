import requests
import json
class WfAPI:
    def __init__(self):
        self.__baseurl = "https://api.warframestat.us/"

    def get_cycle(self, platform):
        cetus = json.loads(requests.get(f"{self.__baseurl}{platform}/cetusCycle").text)
        fortuna = json.loads(requests.get(f"{self.__baseurl}{platform}/vallisCycle").text)
        cambion = json.loads(requests.get(f"{self.__baseurl}{platform}/cambionCycle").text)

        retval = {
            "cetus": f"{(cetus["state"]).capitalize()} {cetus["timeLeft"]}",
            "vallis": f"{"Warm" if fortuna["isWarm"] else "Cold"} {fortuna["timeLeft"]}",
            "cambion": f"{(cambion["state"]).capitalize()} {cambion["timeLeft"]}",
        }

        return retval

    def get_trader(self, platform):
        baro = json.loads(requests.get(f"{self.__baseurl}{platform}/voidTrader").text)

        retval = {
            "status": baro["active"],
            "arrives": baro["startString"],
            "departs": baro["endString"]
        }

        return retval

