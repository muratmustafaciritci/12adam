import hashlib

yeni_sifre = input("Yeni şifreyi girin: ")
hash_degeri = hashlib.sha256(yeni_sifre.encode()).hexdigest()
print(f"\nYeni hash: {hash_degeri}")