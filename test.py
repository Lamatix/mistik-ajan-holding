import requests

url = "https://mistik-ajan-holding.onrender.com/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "mistik-secret-key-2026"
}
data = {
    "query": "Mistik Ajan Holding için 2026 sosyal medya ve büyüme stratejisi oluştur."
}

print("Mistik Ajan Holding'e istek gönderiliyor, lütfen bekleyin...")
try:
    response = requests.post(url, json=data, headers=headers, timeout=300)
    print("Yanıt Kodu:", response.status_code)
    print("Yanıt Metni:")
    print(response.text)
except Exception as e:
    print("İstek Hatası:", e)