import requests
import json
from datetime import datetime, timezone
class WfAPI:
    def __init__(self):
        self.__baseurl = "https://api.warframestat.us/"

    def get_cycle(self, platform):
        cetus = json.loads(requests.get(f"{self.__baseurl}{platform}/cetusCycle").text)
        fortuna = json.loads(requests.get(f"{self.__baseurl}{platform}/vallisCycle").text)
        cambion = json.loads(requests.get(f"{self.__baseurl}{platform}/cambionCycle").text)

        retval = {
            "cetus": f"{(cetus["state"]).capitalize()} {self.__time_until(cetus["expiry"], "worldstate")}",
            "vallis": f"{"Warm" if fortuna["isWarm"] else "Cold"} {self.__time_until(fortuna["expiry"], "worldstate")}",
            "cambion": f"{(cambion["state"]).capitalize()} {self.__time_until(cambion["expiry"], "worldstate")}",
        }

        return retval

    def get_trader(self, platform):
        baro = json.loads(requests.get(f"{self.__baseurl}{platform}/voidTrader").text)

        active = self.__time_until(baro["activation"], "baro") == "0m 0s"
        arrives = self.__time_until(baro["activation"], "baro")
        departs = self.__time_until(baro["expiry"], "baro")

        retval = {
            "status": active,
            "arrives": arrives,
            "departs": departs
        }

        return retval

    def __time_until(self, timestamp, typ):
        target = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        delta = target - now

        if delta.total_seconds() < 0:
            return "0m 0s"

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if typ == "worldstate":
            return f"{minutes}m {seconds}s"
        elif typ == "baro":
            return f"{days}d {hours}h {minutes}m {seconds}s"