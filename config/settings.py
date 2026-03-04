# config/settings.py

"""
12 Adam - Türkiye Futbol Tahmin Sistemi (Hibrit API + Mock)
Geliştirici: Murat Mustafa Ciritçi
Web: https://www.muratciritci.com.tr
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path


@dataclass
class Settings:
    """Sistem ayarları - Hibrit API + Mock"""
    
    # Geliştirici Bilgileri
    DEVELOPER: str = "Murat Mustafa Ciritçi"
    WEBSITE: str = "https://www.muratciritci.com.tr"
    EMAIL: str = "murat@muratciritci.com.tr"
    VERSION: str = "1.1.0-hybrid"
    LICENSE: str = "Proprietary"
    
    # API Anahtarları
    API_FOOTBALL_KEY: str = field(default_factory=lambda: os.getenv('API_FOOTBALL_KEY', ''))
    FOOTBALL_DATA_KEY: str = field(default_factory=lambda: os.getenv('FOOTBALL_DATA_KEY', ''))
    OPENWEATHER_KEY: str = field(default_factory=lambda: os.getenv('OPENWEATHER_KEY', ''))
    
    # Çalışma Modu: 'auto' (önce API, hata olursa Mock), 'api', 'mock'
    DEFAULT_MODE: str = 'auto'
    
    # API Limitleri
    DAILY_API_LIMIT: int = 50
    API_CALL_DELAY: float = 1.2
    MAX_RETRIES: int = 3
    API_TIMEOUT: int = 10  # Saniye
    
    # Desteklenen Ligler (2025-2026 sezonu)
    LEAGUES: Dict[str, Dict] = field(default_factory=lambda: {
        'TSL': {
            'name': 'Süper Lig 2025-2026',
            'country': 'Turkey',
            'id': 203,
            'season': 2025
        },
        'T1': {
            'name': '1. Lig 2025-2026',
            'country': 'Turkey', 
            'id': 204,
            'season': 2025
        },
        'T2': {
            'name': '2. Lig 2025-2026',
            'country': 'Turkey',
            'id': 205,
            'season': 2025
        }
    })
    
    # Veritabanı (SQLite - ücretsiz)
    DB_PATH: str = field(default_factory=lambda: str(Path.home() / '.12adam' / 'data.db'))
    DB_ECHO: bool = False
    
    # Cache (Bellek içi - Redis yok)
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 saat (saniye)
    
    # ML Model Ayarları
    MODELS_ENABLED: List[str] = field(default_factory=lambda: ['random_forest', 'poisson'])
    ENSEMBLE_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'random_forest': 0.6,
        'poisson': 0.4
    })
    
    # Monte Carlo Simülasyonu
    DEFAULT_SIMULATIONS: int = 1000
    MAX_SIMULATIONS: int = 5000  # Ücretsiz limit
    
    # Tahmin Ayarları
    MIN_CONFIDENCE_THRESHOLD: float = 0.55
    VALUE_BET_THRESHOLD: float = 0.05  # %5
    
    # Kelly Kriteri
    KELLY_FRACTION: float = 0.5  # Yarım Kelly (güvenli)
    MAX_BET_PERCENTAGE: float = 0.05  # Bankroll'un max %5'i
    
    # Logging
    LOG_LEVEL: str = 'INFO'
    LOG_FILE: str = field(default_factory=lambda: str(Path.home() / '.12adam' / 'app.log'))
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Kullanıcı Arayüzü
    CONSOLE_COLORS: bool = True
    TABLE_MAX_ROWS: int = 20
    
    # Admin Girişi - BURAYA EKLENDİ
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_DURATION: int = 300  # 5 dakika (saniye)
    
    def __post_init__(self):
        """Başlangıç kontrolleri"""
        # Klasör oluştur
        db_dir = Path(self.DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        log_dir = Path(self.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_league_id(self, league_code: str) -> int:
        """Lig kodundan API ID'si al"""
        return self.LEAGUES.get(league_code, {}).get('id', 0)
    
    def get_league_name(self, league_code: str) -> str:
        """Lig kodundan isim al"""
        return self.LEAGUES.get(league_code, {}).get('name', 'Bilinmiyor')
    
    def is_api_configured(self) -> bool:
        """API anahtarları yapılandırılmış mı?"""
        return bool(self.API_FOOTBALL_KEY or self.FOOTBALL_DATA_KEY)
    
    def show_banner(self) -> str:
        """Başlangıç banner'ı"""
        return f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║           ██████╗  ██╗      █████╗ ██████╗  █████╗ ███╗   ███╗                       ║
║           ██╔══██╗ ██║     ██╔══██╗██╔══██╗██╔══██╗████╗ ████║                       ║
║           ██████╔╝ ██║     ███████║██║  ██║███████║██╔████╔██║                       ║
║           ██╔══██╗ ██║     ██╔══██║██║  ██║██╔══██║██║╚██╔╝██║                       ║
║           ██████╔╝ ███████╗██║  ██║██████╔╝██║  ██║██║ ╚═╝ ██║                       ║
║           ╚═════╝  ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝                       ║
║                                                                                      ║
║                    TÜRKİYE FUTBOL TAHMİN SİSTEMİ                                     ║
║                         HİBRİT MOD v{self.VERSION}                                   ║
║                                                                                      ║
║              Geliştirici: {self.DEVELOPER}                                           ║
║              Web: {self.WEBSITE}                                                     ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """


# Global settings instance - BU SATIR EN SONDA OLMALI
SETTINGS = Settings()