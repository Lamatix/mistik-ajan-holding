import os
import json
import re
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from geopy.geocoders import Nominatim
from langchain_openai import ChatOpenAI
import swisseph as swe

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="MYSTIC THREAD STUDIO - Executive Enterprise Engine", version="10.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Timeout süresi 5 saniyeye yükseltildi
geolocator = Nominatim(user_agent="mystic_thread_studio_enterprise_v10", timeout=5)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

# Dış API çökerse kullanılacak yerel şehir koordinatları
TURKEY_CITIES_COORDS = {
    "ADANA": (37.0000, 35.3213), "ADIYAMAN": (37.7648, 38.2786), "AFYONKARAHİSAR": (38.7507, 30.5567),
    "AĞRI": (39.7191, 43.0503), "AMASYA": (40.6499, 35.8353), "ANKARA": (39.9334, 32.8597),
    "ANTALYA": (36.8969, 30.7133), "ARTVİN": (41.1828, 41.8183), "AYDIN": (37.8560, 27.8416),
    "BALIKESİR": (39.6484, 27.8826), "BİLECİK": (40.1501, 29.9792), "BİNGÖL": (38.8855, 40.4980),
    "BİTLİS": (38.4006, 42.1095), "BOLU": (40.7392, 31.6089), "BURDUR": (37.7203, 30.2908),
    "BURSA": (40.1885, 29.0610), "ÇANAKKALE": (40.1553, 26.4142), "ÇANKIRI": (40.6013, 33.6134),
    "ÇORUM": (40.5506, 34.9556), "DENİZLİ": (37.7765, 29.0864), "DİYARBAKIR": (37.9144, 40.2306),
    "EDİRNE": (41.6768, 26.5603), "ELAZIĞ": (38.6810, 39.2264), "ERZİNCAN": (39.7500, 39.5000),
    "ERZURUM": (39.9043, 41.2679), "ESKİŞEHİR": (39.7667, 30.5256), "GAZİANTEP": (37.0662, 37.3833),
    "GİRESUN": (40.9128, 38.3895), "GÜMÜŞHANE": (40.4603, 39.4814), "HAKKARİ": (37.5833, 43.7333),
    "HATAY": (36.4018, 36.3498), "ISPARTA": (37.7648, 30.5566), "MERSİN": (36.8000, 34.6333),
    "İSTANBUL": (41.0082, 28.9784), "İZMİR": (38.4237, 27.1428), "KARS": (40.6013, 43.0975),
    "KASTAMONU": (41.3887, 33.7827), "KAYSERİ": (38.7312, 35.4787), "KIRKLARELİ": (41.7333, 27.2167),
    "KIRŞEHİR": (39.1425, 34.1709), "KOCAELİ": (40.8533, 29.8815), "KONYA": (37.8746, 32.4932),
    "KÜTAHYA": (39.4167, 29.9833), "MALATYA": (38.3552, 38.3095), "MANİSA": (38.6191, 27.4289),
    "KAHRAMANMARAŞ": (37.5858, 36.9371), "MARDİN": (37.3212, 40.7245), "MUĞLA": (37.2153, 28.3636),
    "MUŞ": (38.7432, 41.5064), "NEVŞEHİR": (38.6244, 34.7144), "NİĞDE": (37.9667, 34.6833),
    "ORDU": (40.9839, 37.8764), "RİZE": (41.0201, 40.5234), "SAKARYA": (40.7569, 30.3783),
    "SAMSUN": (41.2928, 36.3313), "SİİRT": (37.9333, 41.9500), "SİNOP": (42.0231, 35.1531),
    "SİVAS": (39.7477, 37.0179), "TEKİRDAĞ": (40.9833, 27.5167), "TOKAT": (40.3167, 36.5500),
    "TRABZON": (41.0027, 39.7168), "TUNCELİ": (39.1079, 39.5401), "ŞANLIURFA": (37.1674, 38.7939),
    "UŞAK": (38.6823, 29.4082), "VAN": (38.4891, 43.4089), "YOZGAT": (39.8181, 34.8147),
    "ZONGULDAK": (41.4564, 31.7987), "AKSARAY": (38.3687, 34.0370), "BAYBURT": (40.2552, 40.2249),
    "KARAMAN": (37.1759, 33.2287), "KIRIKKALE": (39.8453, 33.5139), "BATMAN": (37.8812, 41.1351),
    "ŞIRNAK": (37.5164, 42.4611), "BARTIN": (41.6344, 32.3375), "ARDAHAN": (41.1105, 42.7022),
    "IĞDIR": (39.9180, 44.0450), "YALOVA": (40.6500, 29.2667), "KARABÜK": (41.2061, 32.6204),
    "KİLİS": (36.7184, 37.1212), "OSMANİYE": (37.0742, 36.2477), "DÜZCE": (40.8438, 31.1565)
}

# --- HESAPLAMA MOTORLARI ---
def calculate_life_path_number(birth_date_str: str) -> int:
    digits = [int(d) for d in re.findall(r"\d", birth_date_str)]
    total = sum(digits)
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(d) for d in str(total))
    return total

def calculate_name_number(name_str: str) -> int:
    char_map = {
        'a':1, 'j':1, 's':1, 'ş':1, 'b':2, 'k':2, 't':2, 'c':3, 'ç':3, 'l':3, 'u':3, 'ü':3,
        'd':4, 'm':4, 'v':4, 'e':5, 'n':5, 'w':5, 'f':6, 'o':6, 'ö':6, 'x':6,
        'g':7, 'ğ':7, 'p':7, 'y':7, 'h':8, 'q':8, 'z':8, 'i':9, 'ı':9, 'r':9
    }
    total = sum(char_map.get(c.lower(), 0) for c in name_str if c.isalpha())
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(d) for d in str(total))
    return total if total > 0 else 1

def get_ai_response(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "<div class='alert alert-danger font-monospace'>⚠️ HATA: OPENAI_API_KEY bulunamadı. Lütfen ortam değişkenlerini kontrol edin.</div>"
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
        response = llm.invoke(prompt)
        return response.content if response and response.content else "<div class='alert alert-warning'>Yanıt oluşturulamadı.</div>"
    except Exception as e:
        return f"<div class='alert alert-danger'>Sistem Hatası: {str(e)}</div>"

class AgentRequest(BaseModel):
    agent_type: str = Field("ceo", max_length=20)
    name: Optional[str] = Field("Danışan", max_length=100)
    birth_date: str = Field(..., max_length=15)
    birth_time: Optional[str] = Field("12:00", max_length=10)
    country: Optional[str] = Field("Türkiye", max_length=60)
    city: Optional[str] = Field("İstanbul", max_length=60)
    district: Optional[str] = Field("", max_length=60)
    question: Optional[str] = Field("", max_length=1000)

# --- UZMAN AJAN MOTORLARI ---
def astro_agent(req: AgentRequest) -> str:
    lat, lng = None, None
    location_query = f"{req.district + ', ' if req.district else ''}{req.city}, {req.country}"
    
    # 1. Aşama: Nominatim API denemesi (Try/Except korumalı)
    try:
        if req.city and req.country:
            loc = geolocator.geocode(location_query)
            if loc:
                lat, lng = loc.latitude, loc.longitude
    except Exception:
        pass # Zaman aşımlarında uygulamayı düşürmez

    # 2. Aşama: Fallback (Sözlükten koordinat bulma)
    if lat is None or lng is None:
        city_key = (req.city or "").strip().upper().replace("I", "İ").replace("İZMİR", "İZMİR")
        if city_key in TURKEY_CITIES_COORDS:
            lat, lng = TURKEY_CITIES_COORDS[city_key]
        else:
            lat, lng = 41.0082, 28.9784  # Varsayılan İstanbul koordinatı

    parts = [int(p) for p in re.sub(r"[^\d]", " ", req.birth_date).split() if p.isdigit()]
    day, month, year = (parts[0], parts[1], parts[2]) if len(parts) == 3 else (15, 5, 1995)
    
    clean_time = req.birth_time.replace(".", ":")
    t_parts = [int(p) for p in clean_time.split(":") if p.isdigit()]
    hour, minute = (t_parts[0], t_parts[1]) if len(t_parts) >= 2 else (12, 0)

    julian_day = swe.julday(year, month, day, hour + (minute / 60.0))
    cusps, ascmc = swe.houses(julian_day, lat, lng, b'P')
    ascendant_degree = round(ascmc[0], 2)
    asc_sign = SIGNS[int(ascendant_degree // 30)]

    planets_data = []
    bodies = {"Güneş": swe.SUN, "Ay": swe.MOON, "Merkür": swe.MERCURY, "Venüs": swe.VENUS, "Mars": swe.MARS, "Jüpiter": swe.JUPITER, "Satürn": swe.SATURN}
    for name, body_id in bodies.items():
        res, _ = swe.calc_ut(julian_day, body_id)
        deg = round(res[0], 2)
        sign = SIGNS[int(deg // 30)]
        planets_data.append(f"{name}: {sign} ({deg % 30:.2f}°)")

    prompt = f"""
    Sen Mistik Holding Baş Astrolog Ajanısın. Premium kurumsal ve ezoterik hizmet veriyorsun.
    Danışan: {req.name} | Doğum: {req.birth_date} {req.birth_time} | Konum: {location_query} (Enlem: {lat:.2f}, Boylam: {lng:.2f})
    Yükselen Burç: {asc_sign} ({ascendant_degree}°)
    Gezegen Konumları: {', '.join(planets_data)}
    Danışan Sorusu/Odak: "{req.question}"

    Lütfen Danışana yüksek prestijli, derinlikli, ev yerleşimleri ve transit gezegen etkilerini kapsayan detaylı bir Astrolojik Harita Raporu sun. 
    Metni HTML başlıkları, vurgulu listeler ve şık paragraflar ile biçimlendir.
    """
    return get_ai_response(prompt)

def tarot_agent(req: AgentRequest) -> str:
    prompt = f"""
    Sen Mistik Holding Tarot ve Kehanet Uzmanı Ajanısın.
    Danışan: {req.name}
    Niyet/Soru: "{req.question}"

    Danışan için 3 kartlık (Geçmiş, Şu An, Gelecek) sembolik açılım yap. Kartların isimlerini, arketiplerini ve sunduğu stratejik mesajları derinlemesine, estetik HTML formatında detaylandır.
    """
    return get_ai_response(prompt)

def numerology_agent(req: AgentRequest) -> str:
    life_path = calculate_life_path_number(req.birth_date)
    name_number = calculate_name_number(req.name)
    prompt = f"""
    Sen Mistik Holding Numeroloji ve Frekans Uzmanı Ajanısın.
    Danışan: {req.name} (İsim Sayısı / Ruh İfadesi Titreşimi: {name_number})
    Doğum Tarihi: {req.birth_date} (Kader / Yaşam Yolu Sayısı: {life_path})
    Soru/Detay: "{req.question}"

    Kader sayısı ({life_path}) ve İsim Titreşimi ({name_number}) senteziyle Danışanın potansiyellerini, güçlü yönlerini ve hayat döngülerini matematiksel/sembolik açıdan HTML formatında raporla.
    """
    return get_ai_response(prompt)

def dream_agent(req: AgentRequest) -> str:
    prompt = f"""
    Sen Mistik Holding Bilinçaltı ve Rüya Analiz Uzmanı Ajanısın.
    Danışan: {req.name}
    Rüya Detayı: "{req.question}"

    Bu rüyadaki arketipleri, psikanalitik sembolleri ve zihnin arka planındaki mesajları detaylı HTML raporu olarak çözümle.
    """
    return get_ai_response(prompt)

def ceo_agent_orchestrator(req: AgentRequest) -> str:
    astro_res = astro_agent(req)
    tarot_res = tarot_agent(req)
    num_res = numerology_agent(req)
    dream_res = dream_agent(req) if req.question else "Bilinçaltı/Rüya verisi girilmedi."

    synthesis_prompt = f"""
    Sen Mistik Holding'in CEO Ajanısın (Baş Mistik Rehber & Orkestratör).
    180 Mağazalık kurumsal ağımızın en üst düzey danışmanlık raporunu hazırlıyorsun.

    Danışan {req.name} için 4 uzman ajanın ürettiği veriler aşağıdadır:

    --- ASTROLOJİ RAPORU ---
    {astro_res[:800]}

    --- TAROT RAPORU ---
    {tarot_res[:800]}

    --- NUMEROLOJİ RAPORU ---
    {num_res[:800]}

    --- RÜYA & BİLİNÇALTI RAPORU ---
    {dream_res[:800]}

    GÖREVİN:
    Danışanın talebini ("{req.question}") merkeze alarak tüm uzmanlık alanlarını kapsayan **"MİSTİK HOLDİNG BÜTÜNCÜL STRATEJİ VE YOL HARİTASI"** raporu kaleme al.
    Raporun içinde şu bölümler HTML olarak bulunsun:
    1. 👑 **Executive Summary (CEO Özeti & Ana Tema)**
    2. 🪐 **Astroloji & Gezegen Enerjileri Stratejisi**
    3. 🃏 **Tarot Kehaneti & Eylem Adımları**
    4. 🔢 **Numerolojik Frekans & Dönem Analizi**
    5. 🚀 **Müşteri İçin 3 Maddelik Somut Aksiyon Plânı**

    Dil son derece saygın, kurumsal, ikna edici ve yüksek değerli (high-end) hissettirmelidir.
    """
    return get_ai_response(synthesis_prompt)

@app.post("/analyze_astro")
@limiter.limit("20/minute")
async def process_agent_request(request: Request, req: AgentRequest):
    try:
        if req.agent_type == "ceo":
            analysis = ceo_agent_orchestrator(req)
        elif req.agent_type == "astro":
            analysis = astro_agent(req)
        elif req.agent_type == "tarot":
            analysis = tarot_agent(req)
        elif req.agent_type == "numerology":
            analysis = numerology_agent(req)
        elif req.agent_type == "dream":
            analysis = dream_agent(req)
        else:
            analysis = ceo_agent_orchestrator(req)

        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return r"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MYSTIC THREAD STUDIO - Executive Enterprise Engine</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
                --card-bg: rgba(30, 27, 75, 0.4);
                --card-border: rgba(139, 92, 246, 0.25);
                --accent-gold: #f59e0b;
                --accent-purple: #8b5cf6;
                --text-bright: #f8fafc;
                --text-muted: #94a3b8;
            }
            body { 
                background: var(--bg-gradient); 
                color: var(--text-bright); 
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                min-height: 100vh;
            }
            .main-header { 
                background: rgba(15, 23, 42, 0.75); 
                backdrop-filter: blur(12px);
                border-bottom: 1px solid var(--card-border); 
                padding: 1.75rem 0; 
            }
            .card-custom { 
                background: var(--card-bg); 
                backdrop-filter: blur(16px);
                border: 1px solid var(--card-border); 
                border-radius: 18px; 
                box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5); 
            }
            
            .agent-card {
                border: 1px solid var(--card-border);
                border-radius: 14px;
                padding: 1.1rem;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: rgba(15, 23, 42, 0.5);
            }
            .agent-card:hover {
                border-color: var(--accent-purple);
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(139, 92, 246, 0.25);
            }
            .agent-card.active {
                border-color: var(--accent-gold);
                background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(30, 27, 75, 0.6) 100%);
                box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
            }

            .form-label { font-weight: 600; color: #cbd5e1; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.6px; }
            .form-control, .form-select { 
                border-radius: 10px; 
                border: 1px solid rgba(139, 92, 246, 0.3); 
                background-color: rgba(15, 23, 42, 0.7) !important; 
                color: #ffffff !important;
                padding: 0.75rem 1rem; 
                font-weight: 500; 
            }
            .form-control::placeholder { color: #64748b; }
            .form-control:focus, .form-select:focus { 
                border-color: var(--accent-gold); 
                box-shadow: 0 0 12px rgba(245, 158, 11, 0.25); 
            }
            
            .btn-action { 
                background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); 
                border: 1px solid rgba(255,255,255,0.2); 
                border-radius: 12px; 
                font-weight: 700; 
                letter-spacing: 0.5px; 
                color: #ffffff;
                box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4); 
                transition: all 0.3s ease;
            }
            .btn-action:hover { 
                background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%); 
                transform: translateY(-2px); 
                box-shadow: 0 6px 25px rgba(124, 58, 237, 0.6);
            }
            
            .quick-btn { 
                border: 1px solid rgba(139, 92, 246, 0.4); 
                background: rgba(30, 27, 75, 0.6); 
                color: #cbd5e1; 
                border-radius: 20px; 
                padding: 0.35rem 0.9rem; 
                font-size: 0.825rem; 
                font-weight: 500; 
                cursor: pointer; 
                transition: all 0.2s; 
            }
            .quick-btn:hover { 
                background: var(--accent-purple); 
                color: white; 
                border-color: var(--accent-purple); 
            }
            
            .result-container { 
                background: rgba(15, 23, 42, 0.85); 
                backdrop-filter: blur(20px);
                border-radius: 18px; 
                border: 1px solid var(--accent-gold); 
                box-shadow: 0 10px 40px rgba(0,0,0,0.7); 
                padding: 2.5rem; 
            }
            .result-body h1, .result-body h2, .result-body h3 { color: #fbbf24; margin-top: 1.5rem; font-weight: 700; }
            .result-body p { line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; }
            .result-body ul { background: rgba(30, 27, 75, 0.5); padding: 1.25rem 2rem; border-radius: 12px; border-left: 4px solid var(--accent-gold); }
        </style>
    </head>
    <body>

        <header class="main-header mb-4">
            <div class="container d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 fw-bold mb-1 text-white"><i class="fa-solid fa-crown text-warning me-2"></i>MYSTIC THREAD STUDIO</h1>
                    <p class="mb-0 text-white-50 font-monospace small">ENTERPRISE MULTI-AGENT ORCHESTRATION ENGINE • 180 STORE NETWORK</p>
                </div>
                <div class="text-end">
                    <span class="badge bg-purple px-3 py-2 rounded-pill" style="background:#6d28d9; border: 1px solid #a78bfa;"><i class="fa-solid fa-sparkles me-1 text-warning"></i> SYSTEM ACTIVE</span>
                </div>
            </div>
        </header>

        <div class="container pb-5">
            <div class="row g-3 mb-4">
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card active" onclick="selectAgent('ceo', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-chess-king fs-4 me-2" style="color:#fbbf24;"></i>
                            <strong class="text-white">CEO Ajanı</strong>
                        </div>
                        <small class="text-white-50 d-block">Bütüncül Sentez & Strateji</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('astro', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-planet-ringed fs-4 me-2" style="color:#38bdf8;"></i>
                            <strong class="text-white">Astroloji</strong>
                        </div>
                        <small class="text-white-50 d-block">Doğum Haritası & Transit</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('tarot', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-cards fs-4 me-2" style="color:#f59e0b;"></i>
                            <strong class="text-white">Tarot & Kehanet</strong>
                        </div>
                        <small class="text-white-50 d-block">3 Kart Sembolik Açılım</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('numerology', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-calculator fs-4 me-2" style="color:#34d399;"></i>
                            <strong class="text-white">Numeroloji</strong>
                        </div>
                        <small class="text-white-50 d-block">Kader & Titreşim Sayısı</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('dream', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-moon fs-4 me-2" style="color:#c084fc;"></i>
                            <strong class="text-white">Rüya Analiz</strong>
                        </div>
                        <small class="text-white-50 d-block">Bilinçaltı Çözümleme</small>
                    </div>
                </div>
            </div>

            <div class="card-custom p-4 mb-4">
                <div class="d-flex justify-content-between align-items-center mb-4 border-bottom border-secondary pb-3">
                    <h4 class="fw-bold mb-0 text-white" id="formTitle"><i class="fa-solid fa-wand-magic-sparkles text-warning me-2"></i>CEO Ajanı - Bütüncül Holding Sentezi</h4>
                    <span class="text-white-50 small"><i class="fa-solid fa-shield-halved text-success me-1"></i> Safe & Encrypted Data</span>
                </div>

                <form onsubmit="handleFormSubmit(event)">
                    <input type="hidden" id="selectedAgent" value="ceo">
                    
                    <div class="row g-3 mb-3">
                        <div class="col-md-4">
                            <label class="form-label">Ad Soyad / Danışan</label>
                            <input type="text" id="nameInput" class="form-control" value="Danışan" placeholder="Ad Soyad giriniz" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Doğum Tarihi (GG.AA.YYYY)</label>
                            <input type="text" id="dateInput" class="form-control" placeholder="Örn: 14.07.1987" oninput="formatDate(this)" maxlength="10" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Doğum Saati (SS:DK)</label>
                            <input type="text" id="timeInput" class="form-control" placeholder="Örn: 14:30" oninput="formatTime(this)" maxlength="5" required>
                        </div>
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-md-4">
                            <label class="form-label">Doğum Ülkesi</label>
                            <select id="countryInput" class="form-select">
                                <option value="Türkiye" selected>Türkiye</option>
                                <option value="Almanya">Almanya</option>
                                <option value="İngiltere">İngiltere</option>
                                <option value="ABD">ABD</option>
                                <option value="Diğer">Diğer</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Doğum Şehri</label>
                            <input type="text" id="cityInput" class="form-control" list="citiesList" placeholder="Şehir seçin veya yazın..." required>
                            <datalist id="citiesList">
                                <option value="Adana"><option value="Adıyaman"><option value="Afyonkarahisar"><option value="Ağrı"><option value="Amasya"><option value="Ankara"><option value="Antalya"><option value="Artvin"><option value="Aydın"><option value="Balıkesir"><option value="Bilecik"><option value="Bingöl"><option value="Bitlis"><option value="Bolu"><option value="Burdur"><option value="Bursa"><option value="Çanakkale"><option value="Çankırı"><option value="Çorum"><option value="Denizli"><option value="Diyarbakır"><option value="Edirne"><option value="Elazığ"><option value="Erzincan"><option value="Erzurum"><option value="Eskişehir"><option value="Gaziantep"><option value="Giresun"><option value="Gümüşhane"><option value="Hakkari"><option value="Hatay"><option value="Isparta"><option value="Mersin"><option value="İstanbul"><option value="İzmir"><option value="Kars"><option value="Kastamonu"><option value="Kayseri"><option value="Kırklareli"><option value="Kırşehir"><option value="Kocaeli"><option value="Konya"><option value="Kütahya"><option value="Malatya"><option value="Manisa"><option value="Kahramanmaraş"><option value="Mardin"><option value="Muğla"><option value="Muş"><option value="Nevşehir"><option value="Niğde"><option value="Ordu"><option value="Rize"><option value="Sakarya"><option value="Samsun"><option value="Siirt"><option value="Sinop"><option value="Sivas"><option value="Tekirdağ"><option value="Tokat"><option value="Trabzon"><option value="Tunceli"><option value="Şanlıurfa"><option value="Uşak"><option value="Van"><option value="Yozgat"><option value="Zonguldak"><option value="Aksaray"><option value="Bayburt"><option value="Karaman"><option value="Kırıkkale"><option value="Batman"><option value="Şırnak"><option value="Bartın"><option value="Ardahan"><option value="Iğdır"><option value="Yalova"><option value="Karabük"><option value="Kilis"><option value="Osmaniye"><option value="Düzce">
                            </datalist>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Doğum İlçesi</label>
                            <input type="text" id="districtInput" class="form-control" placeholder="Örn: Kadıköy, Çankaya, Karşıyaka">
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <label class="form-label mb-0">Soru / Niyet / Rüya Detayı</label>
                            <div class="d-flex gap-2">
                                <button type="button" class="quick-btn" onclick="setQuestion('Gelecek dönemdeki kariyer, yatırım ve finansal fırsatlarım nelerdir?')">💼 Kariyer & Finans</button>
                                <button type="button" class="quick-btn" onclick="setQuestion('İlişki ve evlilik potansiyelim, ruh eşi döngülerim neleri gösteriyor?')">❤️ İlişki & Uyum</button>
                                <button type="button" class="quick-btn" onclick="setQuestion('Bu gece gördüğüm rüyanın derin psikolojik ve mistik anlamı nedir?')">🌙 Rüya Analizi</button>
                            </div>
                        </div>
                        <textarea id="queryInput" class="form-control" rows="3" placeholder="Ajanlarımıza sormak istediğiniz konuyu detaylıca buraya yazabilirsiniz..." required>Gelecek dönemdeki kariyer ve finansal fırsatlarım nelerdir?</textarea>
                    </div>

                    <button type="submit" id="submitBtn" class="btn btn-action text-white w-100 py-3 fs-5">
                        <span id="btnText"><i class="fa-solid fa-sparkles text-warning me-2"></i>Holding Ajan Analizini Başlat</span>
                        <span id="btnSpinner" class="spinner-border spinner-border-sm d-none me-2" role="status"></span>
                    </button>
                </form>
            </div>

            <div id="resultCard" class="result-container d-none">
                <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-3 mb-4">
                    <div>
                        <span class="badge bg-warning text-dark font-monospace mb-1 fw-bold">EXECUTIVE REPORT</span>
                        <h3 class="fw-bold mb-0 text-white">Mistik Holding Analiz Çıktısı</h3>
                    </div>
                    <button class="btn btn-outline-light btn-sm" onclick="window.print()"><i class="fa-solid fa-print me-1"></i> Raporu Yazdır / PDF</button>
                </div>
                <div id="resultBox" class="result-body"></div>
            </div>
        </div>

        <script>
        function formatDate(input) {
            let v = input.value.replace(/\D/g, '');
            if (v.length > 8) v = v.substring(0, 8);
            if (v.length >= 5) {
                input.value = v.substring(0,2) + '.' + v.substring(2,4) + '.' + v.substring(4);
            } else if (v.length >= 3) {
                input.value = v.substring(0,2) + '.' + v.substring(2);
            } else {
                input.value = v;
            }
        }

        function formatTime(input) {
            let v = input.value.replace(/\D/g, '');
            if (v.length > 4) v = v.substring(0, 4);
            if (v.length >= 3) {
                input.value = v.substring(0,2) + ':' + v.substring(2);
            } else {
                input.value = v;
            }
        }

        function setQuestion(q) {
            document.getElementById('queryInput').value = q;
        }

        function selectAgent(type, el) {
            document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('selectedAgent').value = type;

            const title = document.getElementById('formTitle');
            if (type === 'ceo') title.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles text-warning me-2"></i>CEO Ajanı - Bütüncül Holding Sentezi';
            else if (type === 'astro') title.innerHTML = '<i class="fa-solid fa-planet-ringed text-info me-2"></i>Astroloji Ajanı - Doğum Haritası Raporu';
            else if (type === 'tarot') title.innerHTML = '<i class="fa-solid fa-cards text-warning me-2"></i>Tarot Ajanı - Kart Kehaneti';
            else if (type === 'numerology') title.innerHTML = '<i class="fa-solid fa-calculator text-success me-2"></i>Numeroloji Ajanı - Sayısal Frekans Analizi';
            else if (type === 'dream') title.innerHTML = '<i class="fa-solid fa-moon text-purple me-2"></i>Rüya Ajanı - Bilinçaltı Çözümlemesi';
        }

        async function handleFormSubmit(e) {
            e.preventDefault();
            const submitBtn = document.getElementById('submitBtn');
            const btnSpinner = document.getElementById('btnSpinner');
            const btnText = document.getElementById('btnText');
            const resultCard = document.getElementById('resultCard');
            const resultBox = document.getElementById('resultBox');

            const agent = document.getElementById('selectedAgent').value;
            submitBtn.disabled = true;
            btnSpinner.classList.remove('d-none');
            btnText.innerText = agent === 'ceo' ? "CEO Ajanı Tüm Alt Ajanları Orkestre Ediyor..." : "Uzman Ajan Analizi Hazırlıyor...";

            try {
                const payload = {
                    agent_type: agent,
                    name: document.getElementById('nameInput').value,
                    birth_date: document.getElementById('dateInput').value,
                    birth_time: document.getElementById('timeInput').value,
                    country: document.getElementById('countryInput').value,
                    city: document.getElementById('cityInput').value,
                    district: document.getElementById('districtInput').value,
                    question: document.getElementById('queryInput').value
                };

                const res = await fetch('/analyze_astro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Sunucu yanıt vermedi.");

                resultCard.classList.remove('d-none');
                resultBox.innerHTML = data.analysis;
                resultCard.scrollIntoView({ behavior: 'smooth' });

            } catch (err) {
                alert("İşlem Hatası: " + err.message);
            } finally {
                submitBtn.disabled = false;
                btnSpinner.classList.add('d-none');
                btnText.innerHTML = '<i class="fa-solid fa-sparkles text-warning me-2"></i>Holding Ajan Analizini Başlat';
            }
        }
        </script>
    </body>
    </html>
    """