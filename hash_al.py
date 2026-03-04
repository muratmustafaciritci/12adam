import hashlib

sifre = input("Yeni sifre: ").strip()  # strip() boşlukları temizler
hash_degeri = hashlib.sha256(sifre.encode()).hexdigest()

print(f"\nSIFRE: {sifre}")
print(f"HASH:  {hash_degeri}")
print(f"\nUzunluk: {len(hash_degeri)} (64 olmalı)")