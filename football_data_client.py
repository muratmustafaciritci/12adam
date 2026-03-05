import requests
from datetime import datetime

class FootballDataClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": api_key}
    
    def get_matches(self, competition_code):
        """Maçları getir"""
        url = f"{self.base_url}/competitions/{competition_code}/matches"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if "matches" in data:
                return self._format_matches(data["matches"])
            return []
            
        except Exception as e:
            print(f"API Hatası: {e}")
            return []
    
    def _format_matches(self, matches):
        """Formatla"""
        result = []
        for match in matches:
            result.append({
                "Ev Sahibi": match["homeTeam"]["shortName"] or match["homeTeam"]["name"],
                "Deplasman": match["awayTeam"]["shortName"] or match["awayTeam"]["name"],
                "Tarih": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y"),
                "Saat": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M"),
                "Lig": match["competition"]["name"],
                "Durum": match["status"]
            })
        return result

# Lig kodları
COMPETITIONS = {
    "Premier League 2024-2025": "PL",
    "La Liga 2024-2025": "PD",
    "Serie A 2024-2025": "SA",
    "Bundesliga 2024-2025": "BL1",
    "Ligue 1 2024-2025": "FL1",
    "Champions League 2024-2025": "CL"
}
