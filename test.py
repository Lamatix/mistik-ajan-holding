import requests

# Render üzerindeki canlı API endpoint adresi
url = "https://mistik-ajan-holding.onrender.com/analyze"

# Ajanlara gönderilecek test sorusu
payload = {
    "query": "Astrolojik haritamda Merkür retrosu var. Kariyerim için haftalık tavsiye ve buna uygun bir Instagram görseli üret."
}

headers = {
    "Content-Type": "application/json"
}

print("Mistik Ajan Holding'e istek gönderiliyor, lütfen bekleyin...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=180)
    
    if response.status_code == 200:
        print("\n=== HOLDİNG RAPORU VE DALL-E 3 GÖRSEL LINKI ===\n")
        print(response.json().get("holding_report"))
    else:
        print(f"Hata Oluştu! Durum Kodu: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Baglanti Hatasi: {str(e)}")