import requests

class LoLDataDragonAPI:
    """
    A simple wrapper for the League of Legends Data Dragon API.
    """
    def __init__(self):
        self.base_url = "https://ddragon.leagueoflegends.com"

    def get_latest_version(self) -> str:
        """Fetches the latest version of the Data Dragon API."""
        versions_url = f"{self.base_url}/api/versions.json"
        response = requests.get(versions_url)
        response.raise_for_status()
        return response.json()[0]

    def get_champions(self) -> dict:
        """Fetches the champion data from the Data Dragon API and returns a list of champions with name and icon_url."""
        latest_version = self.get_latest_version()
        champions_url = f"{self.base_url}/cdn/{latest_version}/data/en_US/champion.json"
        response = requests.get(champions_url)
        response.raise_for_status()
        data = response.json()
        champions = []
        for champ_key, champ in data["data"].items():
            champ_id = champ["id"]
            champions.append({
                "champion_id": champ_id,
                "name": champ["name"],
                "icon_url": f"{self.base_url}/cdn/{latest_version}/img/champion/{champ_id}.png"
            })
        return {"champions": champions, "count": len(champions)} 