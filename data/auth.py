# data/auth.py (Yeni dosya)

"""
Kimlik doğrulama modülü - Admin girişi
"""

import hashlib
import getpass
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

from config.settings import SETTINGS


class Authenticator:
    """Admin girişi yöneticisi"""
    
    def __init__(self):
        self.failed_attempts = 0
        self.lockout_until: Optional[datetime] = None
        self.authenticated = False
        self.current_user: Optional[str] = None
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi SHA256 ile hashle"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _mask_input(self, prompt: str = "Şifre: ") -> str:
        """Şifre girişini gizle (* olarak göster)"""
        print(prompt, end="", flush=True)
        password = ""
        
        while True:
            try:
                import msvcrt  # Windows
                char = msvcrt.getch()
                
                if char == b'\r' or char == b'\n':  # Enter
                    print()
                    break
                elif char == b'\x08':  # Backspace
                    if password:
                        password = password[:-1]
                        print('\b \b', end="", flush=True)
                else:
                    password += char.decode('utf-8', errors='ignore')
                    print('*', end="", flush=True)
                    
            except ImportError:
                # Linux/Mac - getpass kullan (gizli ama * göstermez)
                import getpass
                return getpass.getpass(prompt)
        
        return password
    
    def is_locked(self) -> Tuple[bool, int]:
        """Kilitli mi kontrol et"""
        if self.lockout_until and datetime.now() < self.lockout_until:
            remaining = int((self.lockout_until - datetime.now()).total_seconds())
            return True, remaining
        return False, 0
    
    def login(self) -> bool:
        """Giriş yap"""
        # Kilit kontrolü
        locked, remaining = self.is_locked()
        if locked:
            print(f"\n[🔒] Çok fazla hatalı giriş! {remaining} saniye bekleyin.")
            return False
        
        print("\n" + "="*60)
        print("🔐 ADMIN GİRİŞİ")
        print("="*60)
        
        # Kullanıcı adı
        username = input("Kullanıcı adı: ").strip().lower()
        
        # Şifre (gizli)
        password = self._mask_input("Şifre: ")
        
        # Doğrulama
        if username == SETTINGS.ADMIN_USERNAME:
            password_hash = self._hash_password(password)
            
            if password_hash == SETTINGS.ADMIN_PASSWORD_HASH:
                self.authenticated = True
                self.current_user = username
                self.failed_attempts = 0
                print(f"\n[✓] Hoş geldiniz, {username}!")
                return True
        
        # Başarısız giriş
        self.failed_attempts += 1
        remaining_attempts = SETTINGS.MAX_LOGIN_ATTEMPTS - self.failed_attempts
        
        print(f"\n[✗] Hatalı giriş! Kalan deneme: {remaining_attempts}")
        
        if self.failed_attempts >= SETTINGS.MAX_LOGIN_ATTEMPTS:
            self.lockout_until = datetime.now() + timedelta(seconds=SETTINGS.LOCKOUT_DURATION)
            print(f"[🔒] Hesap kilitlendi! {SETTINGS.LOCKOUT_DURATION // 60} dakika bekleyin.")
        
        return False
    
    def logout(self):
        """Çıkış yap"""
        self.authenticated = False
        self.current_user = None
        print("\n[←] Güvenli çıkış yapıldı.")
    
    def require_auth(self) -> bool:
        """Giriş gerekli mi kontrol et"""
        if not self.authenticated:
            return self.login()
        return True