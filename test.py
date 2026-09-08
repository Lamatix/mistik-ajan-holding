import requests
import json

# Render Canlı URL'si veya Yerel URL
URL = "https://mistik-ajan-holding.onrender.com/analyze"

payload = {
    "query": "2026 yılı için Mistik Ajan Holding dijital büyüme ve içerik stratejisi analizi yap."
}

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "mistik-secret-key-2026"
}

print("Mistik Ajan Holding'e istek gönderiliyor, lütfen bekleyin...")

try:
    response = requests.post(URL, json=payload, headers=headers, timeout=120)
    print(f"Yanıt Kodu: {response.status_code}")
    
    try:
        res_json = response.json()
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
    except Exception:
        print("Yanıt Metni:")
        print(response.text)

except Exception as e:
    print(f"İstek Hatası: {e}")