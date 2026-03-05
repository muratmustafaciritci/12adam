import requests
import os
from datetime import datetime

class APIFootballClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": api_key
        }
    
    def get_matches(self, league_id, season=2024, date_from=None, date_to=None):
        """Lig maçlarını getir"""
        endpoint = f"{self.base_url}/fixtures"
        
        params = {
            "league": league_id,
            "season": season
        }
        
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if data.get("response"):
                return self._format_matches(data["response"])
            else:
                return []
                
        except Exception as e:
            print(f"API Hatası: {e}")
            return []
    
    def _format_matches(self, fixtures):
        """API yanıtını formatla"""
        matches = []
        
        for fixture in fixtures:
            match = {
                "Ev Sahibi": fixture["teams"]["home"]["name"],
                "Deplasman": fixture["teams"]["away"]["name"],
                "Tarih": datetime.strptime(fixture["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y"),
                "Saat": datetime.strptime(fixture["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M"),
                "Lig": fixture["league"]["name"],
                "Durum": fixture["fixture"]["status"]["short"]
            }
            matches.append(match)
        
        return matches

# Lig ID'leri
LEAGUE_IDS = {
    "Süper Lig 2023-2024": 203,
    "1. Lig 2023-2024": 204,
    "2. Lig 2023-2024": 205
}
