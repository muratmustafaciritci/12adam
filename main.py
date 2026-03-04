#!/usr/bin/env python3
# main.py

"""
12 Adam - Türkiye Futbol Tahmin Sistemi (Hibrit API + Mock)
Geliştirici: Murat Mustafa Ciritçi
Web: https://www.muratciritci.com.tr
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, IntPrompt
    from rich.text import Text
    from rich.style import Style
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, IntPrompt
    from rich.text import Text
    from rich.style import Style

from config.settings import SETTINGS
from data.collector import DataCollector
from data.auth import Authenticator


class TurkishFootballPredictor:
    """Ana uygulama sınıfı - Hibrit mod + Admin girişi"""
    
    def __init__(self):
        self.console = Console(
            width=200,
            height=50,
            color_system="truecolor",
            force_terminal=True,
            legacy_windows=False
        )
        self.collector = None
        self.running = True
        self.auth = Authenticator()
    
    def print_banner(self):
        """Büyük başlangıç banner'ı"""
        banner = """
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
║                         HİBRİT MOD v{version}                                         ║
║                                                                                      ║
║              Geliştirici: {developer}                                                ║
║              Web: {website}                                                          ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """.format(
            version=SETTINGS.VERSION,
            developer=SETTINGS.DEVELOPER,
            website=SETTINGS.WEBSITE
        )
        
        self.console.print(banner, style="bold bright_cyan")
        
        # API durumu
        api_status = "✅ Yapılandırılmış" if SETTINGS.is_api_configured() else "❌ Eksik"
        self.console.print(f"\n[bold bright_green]API Durumu:[/bold bright_green] {api_status}")
        
        if not SETTINGS.is_api_configured():
            self.console.print("[bold bright_yellow]UYARI: API anahtarı bulunamadı! Mock modu kullanılacak.[/bold bright_yellow]")
            self.console.print("[bright_cyan]Ayarlamak için:[/bright_cyan]")
            self.console.print("[bright_white]$env:API_FOOTBALL_KEY='anahtarınız'[/bright_white]\n")
    
    def select_mode(self) -> str:
        """Çalışma modu seçimi"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]ÇALIŞMA MODU SEÇİN[/bold bright_cyan]")
        self.console.print("="*80 + "\n")
        
        table = Table(
            show_header=True,
            header_style="bold bright_white",
            border_style="bright_cyan",
            width=76
        )
        table.add_column("Kod", style="bold bright_cyan", width=6, justify="center")
        table.add_column("Mod", style="bold bright_green", width=15)
        table.add_column("Açıklama", style="bright_white", width=35)
        table.add_column("Durum", style="bold bright_yellow", width=15)
        
        api_status = "✅ Aktif" if SETTINGS.is_api_configured() else "❌ Anahtar Yok"
        
        table.add_row("1", "API Modu", "Gerçek veri (50 istek/gün)", api_status)
        table.add_row("2", "Mock Modu", "Simülasyon (limitsiz)", "✅ Her zaman")
        table.add_row("3", "Otomatik", "Önce API, hata olursa Mock", "⭐ Önerilen")
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "\n[bold bright_white]Seçiminiz[/bold bright_white]",
            choices=["1", "2", "3"],
            default="3"
        )
        
        modes = {"1": "api", "2": "mock", "3": "auto"}
        return modes[choice]
    
    def show_main_menu(self) -> str:
        """Ana menü"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]ANA MENÜ[/bold bright_cyan]")
        
        # Mod göster
        if self.collector:
            mode_str = "🔴 API (Gerçek Veri)" if not self.collector._should_use_mock() else "🟡 MOCK (Simülasyon)"
            user_str = f"👤 {self.auth.current_user}" if self.auth.current_user else ""
            self.console.print(f"[bold bright_green]{mode_str}[/bold bright_green]    [bold bright_yellow]{user_str}[/bold bright_yellow]")
        
        self.console.print("="*80)
        
        menu_items = [
            ("1", "⚽ Maç Tahmini Yap", "İki takım seç ve tahmin al"),
            ("2", "📅 Günün Maçları", "Bugün ve yarınki maçları gör"),
            ("3", "🔍 Takım Analizi", "Detaylı takım istatistikleri"),
            ("4", "📊 Lig Puan Durumu", "Güncel sıralama"),
            ("5", "📈 API Kullanımı", "Günlük limit durumu"),
            ("6", "🔄 Mod Değiştir", "API/Mock seçimi"),
            ("7", "🔒 Çıkış Yap", "Oturumu kapat"),
            ("0", "❌ Programdan Çık", "Tamamen kapat")
        ]
        
        table = Table(show_header=False, box=None, width=76)
        table.add_column("Kod", style="bold bright_cyan", width=6)
        table.add_column("İşlem", style="bold bright_green", width=25)
        table.add_column("Açıklama", style="bright_white")
        
        for code, name, desc in menu_items:
            table.add_row(f"[{code}]", name, desc)
        
        self.console.print(table)
        self.console.print("="*80)
        
        choice = Prompt.ask(
            "[bold bright_white]Seçiminiz[/bold bright_white]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="0"
        )
        return choice
    
    async def initialize(self):
        """Başlangıç"""
        mode = self.select_mode()
        
        try:
            self.collector = DataCollector(mode=mode)
            await self.collector.initialize()
            
            if self.collector.fallback_to_mock and mode == 'api':
                self.console.print("[bold bright_yellow]⚠️ API başarısız, Mock moduna geçildi.[/bold bright_yellow]")
                
        except Exception as e:
            self.console.print(f"[bold bright_red]✗ HATA: {e}[/bold bright_red]")
            if mode == 'api':
                self.console.print("[bold bright_yellow]Mock modunu deneyin.[/bold bright_yellow]")
                sys.exit(1)
            raise
    
    async def run(self):
        """Ana döngü"""
        self.print_banner()
        
        # GİRİŞ KONTROLÜ
        if not self.auth.require_auth():
            self.console.print("[bold bright_red]✗ Giriş başarısız! Program kapatılıyor...[/bold bright_red]")
            return
        
        await self.initialize()
        
        while self.running:
            try:
                choice = self.show_main_menu()
                
                if choice == "1":
                    await self.match_prediction()
                elif choice == "2":
                    await self.todays_matches()
                elif choice == "3":
                    await self.team_analysis()
                elif choice == "4":
                    await self.league_standings()
                elif choice == "5":
                    self.show_api_usage()
                elif choice == "6":
                    await self.change_mode()
                elif choice == "7":
                    self.auth.logout()
                    if self.auth.require_auth():
                        continue
                    else:
                        self.running = False
                elif choice == "0":
                    self.running = False
                    self.console.print("[bold bright_yellow]👋 Program kapatılıyor...[/bold bright_yellow]")
                    
            except KeyboardInterrupt:
                self.console.print("\n[bold bright_yellow]⚠️ İşlem iptal edildi.[/bold bright_yellow]")
            except Exception as e:
                self.console.print(f"\n[bold bright_red]✗ HATA: {e}[/bold bright_red]")
        
        if self.collector:
            await self.collector.close()
    
    async def match_prediction(self):
        """Maç tahmini menüsü"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]⚽ MAÇ TAHMİNİ[/bold bright_cyan]")
        self.console.print("="*80 + "\n")
        
        # Lig seçimi
        self.console.print("[bold bright_white]Lig Seçin:[/bold bright_white]")
        for code, info in SETTINGS.LEAGUES.items():
            self.console.print(f"  [bright_cyan]{code}:[/bright_cyan] [bright_white]{info['name']}[/bright_white]")
        
        league = Prompt.ask(
            "\n[bold bright_green]Lig kodu[/bold bright_green]",
            choices=list(SETTINGS.LEAGUES.keys()),
            default="TSL"
        )
        
        # Takımları getir
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[bright_cyan]Takımlar yükleniyor...[/bright_cyan]", total=None)
            teams = await self.collector.get_teams(league)
            progress.update(task, completed=True)
        
        if not teams:
            self.console.print("[bold bright_red]✗ Takım bilgisi alınamadı![/bold bright_red]")
            return
        
        # Takım listesi
        self.console.print(f"\n[bold bright_green]{len(teams)} takım bulundu:[/bold bright_green]")
        for i, team in enumerate(teams, 1):
            self.console.print(f"  [bright_cyan]{i:2d}.[/bright_cyan] [bright_white]{team['name']}[/bright_white]")
        
        # Ev sahibi seçimi
        self.console.print()
        home_idx = IntPrompt.ask(f"[bold bright_green]Ev sahibi takım numarası (1-{len(teams)})[/bold bright_green]")
        while home_idx < 1 or home_idx > len(teams):
            self.console.print(f"[bold bright_red]✗ Geçersiz! 1-{len(teams)} arası girin.[/bold bright_red]")
            home_idx = IntPrompt.ask(f"[bold bright_green]Ev sahibi takım numarası (1-{len(teams)})[/bold bright_green]")
        
        home_team = teams[home_idx - 1]
        
        # Deplasman seçimi
        away_idx = IntPrompt.ask(f"[bold bright_green]Deplasman takım numarası (1-{len(teams)})[/bold bright_green]")
        while away_idx < 1 or away_idx > len(teams) or away_idx == home_idx:
            if away_idx == home_idx:
                self.console.print("[bold bright_red]✗ Aynı takım olamaz![/bold bright_red]")
            else:
                self.console.print(f"[bold bright_red]✗ Geçersiz! 1-{len(teams)} arası girin.[/bold bright_red]")
            away_idx = IntPrompt.ask(f"[bold bright_green]Deplasman takım numarası (1-{len(teams)})[/bold bright_green]")
        
        away_team = teams[away_idx - 1]
        
        # Tahmin yap
        await self.make_prediction(home_team, away_team, league)
    
    async def make_prediction(self, home: Dict, away: Dict, league: str):
        """Tahmin hesaplama"""
        self.console.print(f"\n[bold bright_white]{home['name']} vs {away['name']}[/bold bright_white]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task1 = progress.add_task("[bright_cyan]İstatistikler alınıyor...[/bright_cyan]", total=None)
            home_stats = await self.collector.get_team_stats(home['id'], league)
            away_stats = await self.collector.get_team_stats(away['id'], league)
            progress.update(task1, completed=True)
            
            task2 = progress.add_task("[bright_cyan]Karşılıklı maçlar alınıyor...[/bright_cyan]", total=None)
            h2h = await self.collector.get_h2h(home['id'], away['id'])
            progress.update(task2, completed=True)
            
            task3 = progress.add_task("[bright_cyan]Hava durumu alınıyor...[/bright_cyan]", total=None)
            weather = await self.collector.get_weather(home.get('city', 'Istanbul'))
            progress.update(task3, completed=True)
        
        # Tahmin hesapla
        prediction = self.simple_predict(home_stats, away_stats, h2h, weather)
        self.show_prediction_result(home, away, prediction, weather)
    
    def simple_predict(
        self, 
        home_stats: Dict, 
        away_stats: Dict, 
        h2h: List[Dict],
        weather: Dict
    ) -> Dict:
        """Basit tahmin mantığı"""
        home_xg = float(home_stats.get('avg_goals_scored', 1.2))
        home_defense = float(home_stats.get('avg_goals_conceded', 1.2))
        away_xg = float(away_stats.get('avg_goals_scored', 1.0))
        away_defense = float(away_stats.get('avg_goals_conceded', 1.3))
        
        home_advantage = 1.3
        weather_factor = 0.8 if weather['rain'] > 5 else 1.0
        
        exp_home = home_xg * (1 / away_defense) * home_advantage * weather_factor
        exp_away = away_xg * (1 / home_defense) * weather_factor
        
        pred_home_goals = round(exp_home)
        pred_away_goals = round(exp_away)
        
        if pred_home_goals > pred_away_goals:
            prob_1, prob_x, prob_2 = 0.50, 0.25, 0.25
        elif pred_home_goals < pred_away_goals:
            prob_1, prob_x, prob_2 = 0.25, 0.25, 0.50
        else:
            prob_1, prob_x, prob_2 = 0.30, 0.40, 0.30
        
        confidence = abs(prob_1 - 0.33) + abs(prob_x - 0.33) + abs(prob_2 - 0.33)
        confidence = min(confidence * 1.5, 1.0)
        
        return {
            'predicted_score': {'home': pred_home_goals, 'away': pred_away_goals},
            'expected_goals': {'home': exp_home, 'away': exp_away},
            'probabilities': {'1': prob_1, 'X': prob_x, '2': prob_2},
            'confidence': confidence,
            'total_goals': pred_home_goals + pred_away_goals,
            'over_2_5': 1.0 if (pred_home_goals + pred_away_goals) > 2.5 else 0.0,
            'btts': 1.0 if (pred_home_goals > 0 and pred_away_goals > 0) else 0.0
        }
    
    def show_prediction_result(
        self, 
        home: Dict, 
        away: Dict, 
        pred: Dict,
        weather: Dict
    ):
        """Tahmin sonuçlarını göster"""
        panel = Panel(
            f"[bold bright_cyan]{home['name']}[/bold bright_cyan] vs [bold bright_red]{away['name']}[/bold bright_red]\n\n"
            f"[bold bright_white]Tahmini Skor:[/bold bright_white] [bold bright_green]{pred['predicted_score']['home']} - {pred['predicted_score']['away']}[/bold bright_green]\n"
            f"[bold bright_white]Beklenen Goller:[/bold bright_white] [bright_cyan]{pred['expected_goals']['home']:.2f}[/bright_cyan] - [bright_cyan]{pred['expected_goals']['away']:.2f}[/bright_cyan]",
            title="[bold bright_yellow]🏆 MAÇ TAHMİNİ[/bold bright_yellow]",
            border_style="bright_green",
            width=76
        )
        self.console.print(panel)
        
        # Olasılıklar tablosu
        table = Table(
            title="[bold bright_white]Maç Sonucu Olasılıkları[/bold bright_white]",
            border_style="bright_cyan",
            width=76
        )
        table.add_column("[bold bright_green]Ev Sahibi (1)[/bold bright_green]", justify="center", style="bright_green")
        table.add_column("[bold bright_yellow]Beraberlik (X)[/bold bright_yellow]", justify="center", style="bright_yellow")
        table.add_column("[bold bright_red]Deplasman (2)[/bold bright_red]", justify="center", style="bright_red")
        
        table.add_row(
            f"%{pred['probabilities']['1']*100:.1f}",
            f"%{pred['probabilities']['X']*100:.1f}",
            f"%{pred['probabilities']['2']*100:.1f}"
        )
        self.console.print(table)
        
        # Ek tahminler
        extras = Table(
            title="[bold bright_white]Ek Tahminler[/bold bright_white]",
            border_style="bright_magenta",
            width=76
        )
        extras.add_column("[bold bright_cyan]Alt/Üst 2.5[/bold bright_cyan]", justify="center", style="bright_cyan")
        extras.add_column("[bold bright_magenta]KG Var/Yok[/bold bright_magenta]", justify="center", style="bright_magenta")
        
        over_under = "Üst" if pred['over_2_5'] > 0.5 else "Alt"
        btts = "Var" if pred['btts'] > 0.5 else "Yok"
        
        extras.add_row(over_under, btts)
        self.console.print(extras)
        
        # Hava durumu ve güven
        self.console.print(f"\n[bold bright_white]🌤️ Hava Durumu:[/bold bright_white] [bright_cyan]{weather['description']}[/bright_cyan], [bright_yellow]{weather['temp']}°C[/bright_yellow]")
        
        conf_color = "bright_green" if pred['confidence'] > 0.7 else "bright_yellow" if pred['confidence'] > 0.5 else "bright_red"
        self.console.print(f"[bold bright_white]💪 Güven Skoru:[/bold bright_white] [{conf_color}]{pred['confidence']:.2f}/1.0[/{conf_color}]")
        
        if self.collector._should_use_mock():
            self.console.print("\n[bold bright_yellow]⚠️ Not: Mock veri kullanılıyor (simülasyon).[/bold bright_yellow]")
    
    async def todays_matches(self):
        """Günün maçları"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]📅 GÜNÜN MAÇLARI[/bold bright_cyan]")
        self.console.print("="*80 + "\n")
        
        league = Prompt.ask(
            "[bold bright_green]Lig[/bold bright_green]",
            choices=list(SETTINGS.LEAGUES.keys()),
            default="TSL"
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[bright_cyan]Yükleniyor...[/bright_cyan]", total=None)
            matches = await self.collector.get_fixtures(league, days_ahead=2)
            progress.update(task, completed=True)
        
        if not matches:
            self.console.print("[bold bright_yellow]⚠️ Yaklaşan maç bulunamadı.[/bold bright_yellow]")
            return
        
        table = Table(
            title=f"[bold bright_white]{SETTINGS.get_league_name(league)} - Gelecek Maçlar[/bold bright_white]",
            border_style="bright_green",
            width=76
        )
        table.add_column("[bold bright_cyan]Tarih[/bold bright_cyan]", width=16)
        table.add_column("[bold bright_cyan]Saat[/bold bright_cyan]", width=8)
        table.add_column("[bold bright_green]Ev Sahibi[/bold bright_green]")
        table.add_column("[bold bright_red]Deplasman[/bold bright_red]")
        
        for match in matches[:10]:
            date_obj = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
            table.add_row(
                date_obj.strftime("%d.%m.%Y"),
                date_obj.strftime("%H:%M"),
                match['home_team'],
                match['away_team']
            )
        
        self.console.print(table)
    
    async def team_analysis(self):
        """Takım analizi"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]🔍 TAKIM ANALİZİ[/bold bright_cyan]")
        self.console.print("="*80)
        self.console.print("[bold bright_yellow]⚠️ Bu özellik yakında eklenecek...[/bold bright_yellow]")
    
    async def league_standings(self):
        """Puan durumu"""
        self.console.print("\n" + "="*80)
        self.console.print("[bold bright_cyan]📊 PUAN DURUMU[/bold bright_cyan]")
        self.console.print("="*80)
        self.console.print("[bold bright_yellow]⚠️ Bu özellik yakında eklenecek...[/bold bright_yellow]")
    
    def show_api_usage(self):
        """API kullanım durumu"""
        usage = self.collector.get_api_usage()
        
        panel = Panel(
            f"[bold bright_white]Günlük Limit:[/bold bright_white] [bright_cyan]{usage['daily_limit']}[/bright_cyan]\n"
            f"[bold bright_white]Kullanılan:[/bold bright_white] [bright_yellow]{usage['used_today']}[/bright_yellow]\n"
            f"[bold bright_white]Kalan:[/bold bright_white] [bright_green]{usage['remaining']}[/bright_green]\n"
            f"[bold bright_white]Başarı Oranı:[/bold bright_white] [bright_magenta]%{usage['success_rate']:.1f}[/bright_magenta]\n"
            f"[bold bright_white]Aktif Mod:[/bold bright_white] [bright_cyan]{usage['mode']}[/bright_cyan]",
            title="[bold bright_yellow]📈 API KULLANIMI[/bold bright_yellow]",
            border_style="bright_blue",
            width=76
        )
        self.console.print(panel)
        
        if usage.get('remaining', 50) < 10:
            self.console.print("[bold bright_red]⚠️ UYARI: API limiti düşük![/bold bright_red]")
    
    async def change_mode(self):
        """Mod değiştir"""
        self.console.print("\n[bold bright_yellow]🔄 Mod değiştiriliyor...[/bold bright_yellow]")
        await self.collector.close()
        await self.initialize()


async def main():
    """Giriş noktası"""
    app = TurkishFootballPredictor()
    
    try:
        await app.run()
    except Exception as e:
        print(f"[bold bright_red]✗ Kritik hata: {e}[/bold bright_red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())