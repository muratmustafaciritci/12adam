import requests
from datetime import datetime

class FootballDataClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": api_key}
    
    def get_matches(self, competition_code, season=2025):
        """Maçları getir - 2025-2026 sezonu"""
        url = f"{self.base_url}/competitions/{competition_code}/matches"
        params = {"season": season}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
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
                "Ev Sahibi": match["homeTeam"].get("shortName") or match["homeTeam"]["name"],
                "Deplasman": match["awayTeam"].get("shortName") or match["awayTeam"]["name"],
                "Tarih": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y"),
                "Saat": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M"),
                "Lig": match["competition"]["name"],
                "Durum": match["status"]
            })
        return result

# Lig kodları
COMPETITIONS = {
    "Premier League 2025-2026": "PL",
    "La Liga 2025-2026": "PD",
    "Serie A 2025-2026": "SA",
    "Bundesliga 2025-2026": "BL1",
    "Ligue 1 2025-2026": "FL1",
    "Champions League 2025-2026": "CL"
}
