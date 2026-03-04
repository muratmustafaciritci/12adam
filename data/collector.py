# data/collector.py

"""
Veri toplama modülü - Hibrit API + Mock
API başarısız olursa otomatik Mock'a düşer
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import SETTINGS


@dataclass
class APICall:
    """API çağrı kaydı"""
    endpoint: str
    timestamp: datetime
    success: bool
    response_size: int


class DataCollector:
    """Hibrit veri toplama - API + Mock"""
    
    def __init__(self, mode: str = 'auto'):
        self.mode = mode  # 'api', 'mock', 'auto'
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.call_history: List[APICall] = []
        self.api_available = False
        self.fallback_to_mock = False
        
        # API URL'leri
        self.base_urls = {
            'api_football': 'https://v3.football.api-sports.io',
            'football_data': 'https://api.football-data.org/v4',
            'openweather': 'http://api.openweathermap.org/data/2.5'
        }
        
        # Mock veri hazırla
        self._init_mock_data()
    
    def _init_mock_data(self):
        """Mock veritabanını başlat"""
        self.mock_teams = {
            'TSL': [
                {'id': 1, 'name': 'Galatasaray', 'code': 'GAL', 'country': 'Turkey', 'founded': 1905, 'venue': 'Rams Park', 'city': 'Istanbul'},
                {'id': 2, 'name': 'Fenerbahçe', 'code': 'FEN', 'country': 'Turkey', 'founded': 1907, 'venue': 'Ülker Stadyum', 'city': 'Istanbul'},
                {'id': 3, 'name': 'Beşiktaş', 'code': 'BJK', 'country': 'Turkey', 'founded': 1903, 'venue': 'Tüpraş Stadyumu', 'city': 'Istanbul'},
                {'id': 4, 'name': 'Trabzonspor', 'code': 'TS', 'country': 'Turkey', 'founded': 1967, 'venue': 'Papara Park', 'city': 'Trabzon'},
                {'id': 5, 'name': 'Başakşehir', 'code': 'IBB', 'country': 'Turkey', 'founded': 1990, 'venue': 'Fatih Terim Stadyumu', 'city': 'Istanbul'},
                {'id': 6, 'name': 'Konyaspor', 'code': 'KON', 'country': 'Turkey', 'founded': 1922, 'venue': 'Medaş Konya Stadyumu', 'city': 'Konya'},
                {'id': 7, 'name': 'Sivasspor', 'code': 'SIV', 'country': 'Turkey', 'founded': 1967, 'venue': 'Yeni Sivas 4 Eylül Stadyumu', 'city': 'Sivas'},
                {'id': 8, 'name': 'Alanyaspor', 'code': 'ALY', 'country': 'Turkey', 'founded': 1948, 'venue': 'Alanya Oba Stadyumu', 'city': 'Alanya'},
                {'id': 9, 'name': 'Antalyaspor', 'code': 'ANT', 'country': 'Turkey', 'founded': 1966, 'venue': 'Corendon Airlines Park', 'city': 'Antalya'},
                {'id': 10, 'name': 'Gaziantep FK', 'code': 'GFK', 'country': 'Turkey', 'founded': 1988, 'venue': 'Kalyon Stadyumu', 'city': 'Gaziantep'},
                {'id': 11, 'name': 'Adana Demirspor', 'code': 'ADS', 'country': 'Turkey', 'founded': 1940, 'venue': 'Yeni Adana Stadyumu', 'city': 'Adana'},
                {'id': 12, 'name': 'Hatayspor', 'code': 'HTY', 'country': 'Turkey', 'founded': 1967, 'venue': 'Yeni Hatay Stadyumu', 'city': 'Hatay'},
                {'id': 13, 'name': 'Kayserispor', 'code': 'KYS', 'country': 'Turkey', 'founded': 1966, 'venue': 'RHG Enertürk Enerji Stadyumu', 'city': 'Kayseri'},
                {'id': 14, 'name': 'Çaykur Rizespor', 'code': 'RIZ', 'country': 'Turkey', 'founded': 1953, 'venue': 'Çaykur Didi Stadyumu', 'city': 'Rize'},
                {'id': 15, 'name': 'Kasımpaşa', 'code': 'KAS', 'country': 'Turkey', 'founded': 1921, 'venue': 'Recep Tayyip Erdoğan Stadyumu', 'city': 'Istanbul'},
                {'id': 16, 'name': 'Samsunspor', 'code': 'SAM', 'country': 'Turkey', 'founded': 1965, 'venue': 'Samsun 19 Mayıs Stadyumu', 'city': 'Samsun'},
                {'id': 17, 'name': 'Ankaragücü', 'code': 'ANK', 'country': 'Turkey', 'founded': 1910, 'venue': 'Eryaman Stadyumu', 'city': 'Ankara'},
                {'id': 18, 'name': 'Karagümrük', 'code': 'FKG', 'country': 'Turkey', 'founded': 1926, 'venue': 'Atatürk Olimpiyat Stadyumu', 'city': 'Istanbul'},
                {'id': 19, 'name': 'Pendikspor', 'code': 'PEN', 'country': 'Turkey', 'founded': 1950, 'venue': 'Pendik Stadyumu', 'city': 'Istanbul'},
            ],
            'T1': [
                {'id': 101, 'name': 'Eyüpspor', 'code': 'EYU', 'country': 'Turkey', 'founded': 1919, 'venue': 'Eyüp Stadyumu', 'city': 'Istanbul'},
                {'id': 102, 'name': 'Göztepe', 'code': 'GOZ', 'country': 'Turkey', 'founded': 1925, 'venue': 'Gürsel Aksel Stadyumu', 'city': 'Izmir'},
                {'id': 103, 'name': 'Kocaelispor', 'code': 'KOC', 'country': 'Turkey', 'founded': 1966, 'venue': 'Kocaeli Stadyumu', 'city': 'Izmit'},
                {'id': 104, 'name': 'Sakaryaspor', 'code': 'SAK', 'country': 'Turkey', 'founded': 1965, 'venue': 'Yeni Sakarya Atatürk Stadyumu', 'city': 'Adapazarı'},
                {'id': 105, 'name': 'Boluspor', 'code': 'BOL', 'country': 'Turkey', 'founded': 1965, 'venue': 'Bolu Atatürk Stadyumu', 'city': 'Bolu'},
                {'id': 106, 'name': 'Manisa FK', 'code': 'MAN', 'country': 'Turkey', 'founded': 1994, 'venue': 'Manisa 19 Mayıs Stadyumu', 'city': 'Manisa'},
                {'id': 107, 'name': 'Bandırmaspor', 'code': 'BAN', 'country': 'Turkey', 'founded': 1965, 'venue': 'Bandırma 17 Eylül Stadyumu', 'city': 'Bandırma'},
                {'id': 108, 'name': 'Erzurumspor', 'code': 'ERZ', 'country': 'Turkey', 'founded': 1968, 'venue': 'Kazım Karabekir Stadyumu', 'city': 'Erzurum'},
                {'id': 109, 'name': 'Altay', 'code': 'ALT', 'country': 'Turkey', 'founded': 1914, 'venue': 'Alsancak Mustafa Denizli Stadyumu', 'city': 'Izmir'},
                {'id': 110, 'name': 'Adanaspor', 'code': 'ADA', 'country': 'Turkey', 'founded': 1954, 'venue': 'Yeni Adana Stadyumu', 'city': 'Adana'},
            ],
            'T2': [
                {'id': 201, 'name': 'Ankara Demirspor', 'code': 'AND', 'country': 'Turkey', 'founded': 1930, 'venue': 'Ankara Demirspor Stadyumu', 'city': 'Ankara'},
                {'id': 202, 'name': 'Zonguldak Kömürspor', 'code': 'ZON', 'country': 'Turkey', 'founded': 1925, 'venue': 'Karaelmas Stadyumu', 'city': 'Zonguldak'},
                {'id': 203, 'name': 'Kastamonuspor', 'code': 'KAS', 'country': 'Turkey', 'founded': 1966, 'venue': 'Kastamonu Gazi Stadyumu', 'city': 'Kastamonu'},
                {'id': 204, 'name': 'Etimesgut Belediyespor', 'code': 'ETI', 'country': 'Turkey', 'founded': 1990, 'venue': 'Etimesgut Stadyumu', 'city': 'Ankara'},
                {'id': 205, 'name': 'Nazilli Belediyespor', 'code': 'NAZ', 'country': 'Turkey', 'founded': 1974, 'venue': 'Nazilli Stadyumu', 'city': 'Nazilli'},
            ]
        }
        
        # Mock istatistikler
        self.mock_stats = {}
        for league, teams in self.mock_teams.items():
            for team in teams:
                self.mock_stats[team['id']] = {
                    'matches_played': random.randint(15, 25),
                    'wins': random.randint(5, 15),
                    'draws': random.randint(3, 8),
                    'loses': random.randint(2, 10),
                    'goals_for': random.randint(20, 45),
                    'goals_against': random.randint(15, 40),
                    'avg_goals_scored': round(random.uniform(1.0, 2.0), 2),
                    'avg_goals_conceded': round(random.uniform(0.8, 1.8), 2),
                    'clean_sheets': random.randint(3, 12),
                    'failed_to_score': random.randint(2, 8),
                    'form': ''.join(random.choice(['W', 'W', 'D', 'L']) for _ in range(5))
                }
    
    async def initialize(self):
        """Başlangıç - API test et"""
        if self.mode in ['api', 'auto']:
            await self._test_api_connection()
        
        if self.mode == 'api' and not self.api_available:
            raise Exception("API bağlantısı kurulamadı! Mock modunu deneyin.")
        
        if self.fallback_to_mock:
            print("[BİLGİ] API başarısız, Mock moduna geçiliyor...")
    
    async def _test_api_connection(self):
        """API bağlantısını test et"""
        if not SETTINGS.API_FOOTBALL_KEY:
            return
        
        try:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=SETTINGS.API_TIMEOUT))
            headers = {'x-apisports-key': SETTINGS.API_FOOTBALL_KEY}
            
            async with self.session.get(
                f"{self.base_urls['api_football']}/status",
                headers=headers
            ) as response:
                if response.status == 200:
                    self.api_available = True
                    print("[✓] API bağlantısı başarılı")
                else:
                    self.fallback_to_mock = True
                    print(f"[✗] API hatası: {response.status}")
                    
        except Exception as e:
            self.fallback_to_mock = True
            print(f"[✗] API bağlantı hatası: {e}")
        
        finally:
            if not self.api_available and self.session:
                await self.session.close()
                self.session = None
    
    def _should_use_mock(self) -> bool:
        """Mock kullanılmalı mı?"""
        if self.mode == 'mock':
            return True
        if self.mode == 'auto' and self.fallback_to_mock:
            return True
        if not self.api_available:
            return True
        return False
    
    async def get_teams(self, league_code: str) -> List[Dict]:
        """Takımları getir - API veya Mock"""
        if self._should_use_mock():
            return await self._get_teams_mock(league_code)
        return await self._get_teams_api(league_code)
    
    async def _get_teams_api(self, league_code: str) -> List[Dict]:
        """API'den takımları getir"""
        league_id = SETTINGS.get_league_id(league_code)
        headers = {'x-apisports-key': SETTINGS.API_FOOTBALL_KEY}
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.base_urls['api_football']}/teams",
                params={'league': league_id, 'season': 2025},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and 'response' in data:
                        return [
                            {
                                'id': team['team']['id'],
                                'name': team['team']['name'],
                                'code': team['team'].get('code', ''),
                                'country': team['team']['country'],
                                'founded': team['team'].get('founded', 0),
                                'venue': team['venue']['name'] if 'venue' in team else '',
                                'city': team['venue']['city'] if 'venue' in team else 'Istanbul'
                            }
                            for team in data['response']
                        ]
        except Exception as e:
            print(f"[API HATA] {e}")
        
        # API başarısız, Mock'a düş
        self.fallback_to_mock = True
        return await self._get_teams_mock(league_code)
    
    async def _get_teams_mock(self, league_code: str) -> List[Dict]:
        """Mock takımları döndür"""
        return self.mock_teams.get(league_code, [])
    
    async def get_team_stats(self, team_id: int, league_code: str) -> Dict:
        """Takım istatistikleri - API veya Mock"""
        if self._should_use_mock():
            return self._get_team_stats_mock(team_id)
        return await self._get_team_stats_api(team_id, league_code)
    
    async def _get_team_stats_api(self, team_id: int, league_code: str) -> Dict:
        """API'den istatistikleri getir"""
        league_id = SETTINGS.get_league_id(league_code)
        headers = {'x-apisports-key': SETTINGS.API_FOOTBALL_KEY}
        
        try:
            async with self.session.get(
                f"{self.base_urls['api_football']}/teams/statistics",
                params={'team': team_id, 'league': league_id, 'season': 2025},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and 'response' in data:
                        stats = data['response']
                        return {
                            'matches_played': stats['fixtures']['played']['total'],
                            'wins': stats['fixtures']['wins']['total'],
                            'draws': stats['fixtures']['draws']['total'],
                            'loses': stats['fixtures']['loses']['total'],
                            'goals_for': stats['goals']['for']['total']['total'],
                            'goals_against': stats['goals']['against']['total']['total'],
                            'avg_goals_scored': stats['goals']['for']['average']['total'],
                            'avg_goals_conceded': stats['goals']['against']['average']['total'],
                            'clean_sheets': stats['clean_sheet']['total'],
                            'failed_to_score': stats['failed_to_score']['total'],
                            'form': stats.get('form', 'WWDLW')
                        }
        except Exception as e:
            print(f"[API HATA] {e}")
        
        self.fallback_to_mock = True
        return self._get_team_stats_mock(team_id)
    
    def _get_team_stats_mock(self, team_id: int) -> Dict:
        """Mock istatistikleri döndür"""
        return self.mock_stats.get(team_id, {
            'matches_played': 20,
            'wins': 10,
            'draws': 5,
            'loses': 5,
            'goals_for': 30,
            'goals_against': 25,
            'avg_goals_scored': 1.5,
            'avg_goals_conceded': 1.25,
            'clean_sheets': 5,
            'failed_to_score': 5,
            'form': 'WWDLW'
        })
    
    async def get_h2h(self, team1_id: int, team2_id: int) -> List[Dict]:
        """Karşılıklı maç geçmişi - Mock"""
        matches = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(random.randint(3, 6)):
            match_date = base_date + timedelta(days=i*60)
            home_goals = random.randint(0, 3)
            away_goals = random.randint(0, 3)
            
            matches.append({
                'date': match_date.isoformat(),
                'home_team': 'Takım A' if i % 2 == 0 else 'Takım B',
                'away_team': 'Takım B' if i % 2 == 0 else 'Takım A',
                'home_goals': home_goals,
                'away_goals': away_goals,
                'winner': 'home' if home_goals > away_goals else 'away' if away_goals > home_goals else 'draw'
            })
        
        return matches
    
    async def get_fixtures(self, league_code: str, days_ahead: int = 7) -> List[Dict]:
        """Gelecek maçlar - Mock"""
        teams = await self.get_teams(league_code)
        if len(teams) < 2:
            return []
        
        matches = []
        base_date = datetime.now()
        
        for i in range(5):
            match_date = base_date + timedelta(days=i+1)
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t['id'] != home_team['id']])
            
            matches.append({
                'id': 10000 + i,
                'date': match_date.isoformat(),
                'home_team': home_team['name'],
                'away_team': away_team['name'],
                'home_id': home_team['id'],
                'away_id': away_team['id'],
                'venue': home_team.get('venue', '')
            })
        
        return matches
    
    async def get_weather(self, city: str, date: str = None) -> Dict:
        """Hava durumu - Mock"""
        conditions = [
            {'temp': 22, 'feels_like': 22, 'humidity': 50, 'wind_speed': 8, 'rain': 0, 'description': 'açık hava', 'clouds': 10},
            {'temp': 18, 'feels_like': 18, 'humidity': 60, 'wind_speed': 12, 'rain': 0, 'description': 'parçalı bulutlu', 'clouds': 40},
            {'temp': 15, 'feels_like': 14, 'humidity': 80, 'wind_speed': 15, 'rain': 5, 'description': 'yağmurlu', 'clouds': 80},
            {'temp': 25, 'feels_like': 26, 'humidity': 40, 'wind_speed': 5, 'rain': 0, 'description': 'güneşli', 'clouds': 0},
        ]
        return random.choice(conditions)
    
    def get_api_usage(self) -> Dict:
        """API kullanımı"""
        if self._should_use_mock():
            return {
                'daily_limit': 50,
                'used_today': 0,
                'remaining': 50,
                'success_rate': 100.0,
                'mode': 'MOCK (Simülasyon)'
            }
        
        today = datetime.now().date()
        today_calls = [c for c in self.call_history if c.timestamp.date() == today]
        
        return {
            'daily_limit': SETTINGS.DAILY_API_LIMIT,
            'used_today': len(today_calls),
            'remaining': SETTINGS.DAILY_API_LIMIT - len(today_calls),
            'success_rate': sum(1 for c in today_calls if c.success) / len(today_calls) * 100 if today_calls else 0,
            'mode': 'API (Gerçek Veri)'
        }
    
    async def close(self):
        """Kapat"""
        if self.session:
            await self.session.close()