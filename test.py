import requests
import json
import base64
from PIL import Image, ImageDraw
import io

BASE_URL = "https://mistik-ajan-holding.onrender.com"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": "mistik-secret-key-2026"
}

def create_mock_coffee_image():
    """Kahve falı testi için bellek üzerinde geçici bir test görseli üretir."""
    img = Image.new('RGB', (300, 300), color=(60, 40, 20))
    d = ImageDraw.Draw(img)
    d.ellipse([(50, 50), (250, 250)], fill=(20, 10, 5))
    d.ellipse([(100, 100), (160, 180)], fill=(120, 90, 60)) # Telve şekli simülasyonu
    
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_default_analyze():
    print_separator("0. VARSAYILAN /analyze ENDPOINT TESTİ (GERİYE DÖNÜK UYUM)")
    url = f"{BASE_URL}/analyze"
    payload = {
        "query": "Geriye dönük uyumluluk testi: Eski test istekleri çalışıyor mu?"
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        print("HTTP Yanıt Kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("\n[BAŞARILI] Yanıt İçeriği:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("\n[HATA]:", response.text)
    except Exception as e:
        print("\n[İSTİSNA HATA]:", str(e))

def test_strategy():
    print_separator("1. SOSYAL MEDYA & STRATEJİ AJANI TESTİ (/analyze_strategy)")
    url = f"{BASE_URL}/analyze_strategy"
    payload = {
        "query": "Mystic Thread Studio için 2026 yılı cross-platform büyüme ve video kurgu stratejisi hazırlayın."
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        print("HTTP Yanıt Kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("\n--- İSTİHBARAT VE STRATEJİ ---")
            print(data.get("intelligence_and_strategy"))
            print("\n--- KREATİF VE VİDEO REHBERİ ---")
            print(data.get("creative_and_video_guide"))
            print("\n--- ÜRETİLEN GÖRSEL URL ---")
            print(data.get("generated_image_url"))
        else:
            print("\n[HATA]:", response.text)
    except Exception as e:
        print("\n[İSTİSNA HATA]:", str(e))

def test_astro():
    print_separator("2. SWISS EPHEMERIS ASTROLOJİ AJANI TESTİ (/analyze_astro)")
    url = f"{BASE_URL}/analyze_astro"
    payload = {
        "name": "Sercan Bilir",
        "birth_date": "1995-05-15",
        "birth_time": "14:30",
        "query": "Kariyer potansiyelim, dijital projelerim ve önümdeki fırsatlar hakkında haritam ne söylüyor?"
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        print("HTTP Yanıt Kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("\n--- DOĞUM HARİTASI HESAPLAMA VERİSİ ---")
            print(json.dumps(data.get("natal_chart_data"), indent=2, ensure_ascii=False))
            print("\n--- ASTROLOG YORUMU ---")
            print(data.get("astrology_interpretation"))
            print("\n--- ÜRETİLEN GÖRSEL URL ---")
            print(data.get("generated_image_url"))
        else:
            print("\n[HATA]:", response.text)
    except Exception as e:
        print("\n[İSTİSNA HATA]:", str(e))

def test_tarot():
    print_separator("3. TAROT ÜSTADI AJANI TESTİ (/analyze_tarot)")
    url = f"{BASE_URL}/analyze_tarot"
    payload = {
        "cards": ["The Fool (Deli)", "The Tower (Yıkılan Kule)", "The Star (Yıldız)"],
        "query": "Proje ve içerik üretim süreçlerimde yaşadığım dönüşüm beni nereye götürecek?"
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        print("HTTP Yanıt Kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("\n--- TAROT AÇILIM YORUMU ---")
            print(data.get("tarot_interpretation"))
            print("\n--- ÜRETİLEN GÖRSEL URL ---")
            print(data.get("generated_image_url"))
        else:
            print("\n[HATA]:", response.text)
    except Exception as e:
        print("\n[İSTİSNA HATA]:", str(e))

def test_coffee():
    print_separator("4. KAHVE FALI & VISION AI TESTİ (/analyze_coffee)")
    url = f"{BASE_URL}/analyze_coffee"
    mock_base64 = create_mock_coffee_image()
    
    payload = {
        "image_base64": mock_base64,
        "query": "Gelecekteki maddi başarılar ve yeni iş ortaklıkları fincanda görünüyor mu?"
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        print("HTTP Yanıt Kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("\n--- VISION AI İLE TESPİT EDİLEN SEMBOLLER ---")
            print(data.get("detected_symbols"))
            print("\n--- KAHVE FALI YORUMU ---")
            print(data.get("coffee_interpretation"))
            print("\n--- ÜRETİLEN GÖRSEL URL ---")
            print(data.get("generated_image_url"))
        else:
            print("\n[HATA]:", response.text)
    except Exception as e:
        print("\n[İSTİSNA HATA]:", str(e))

if __name__ == "__main__":
    print("MYSTIC THREAD STUDIO - TÜM SERVİSLERİ KAPSAMLI TEST BAŞLATILIYOR...")
    test_default_analyze()
    test_strategy()
    test_astro()
    test_tarot()
    test_coffee()
    print_separator("TÜM TESTLER TAMAMLANDI")