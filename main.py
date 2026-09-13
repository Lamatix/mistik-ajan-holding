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
app = FastAPI(title="MYSTIC THREAD STUDIO - Executive Enterprise Engine", version="8.0")
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

geolocator = Nominatim(user_agent="mystic_thread_studio_enterprise_v8")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

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
    if req.city and req.country:
        loc = geolocator.geocode(location_query)
        if loc:
            lat, lng = loc.latitude, loc.longitude
    if lat is None or lng is None:
        lat, lng = 41.0082, 28.9784

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
    Sen Mistik Holding Baş Astrolog Ajanısın. Premium kurumsal hizmet veriyorsun.
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
        <title>MYSTIC THREAD STUDIO - Enterprise Holding Engine</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary-color: #4f46e5;
                --primary-hover: #4338ca;
                --bg-main: #f8fafc;
                --card-border: #e2e8f0;
            }
            body { background-color: var(--bg-main); color: #0f172a; font-family: 'Inter', system-ui, -apple-system, sans-serif; }
            .main-header { background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); color: white; padding: 2rem 0; border-radius: 0 0 20px 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
            .card-custom { background: #ffffff; border: 1px solid var(--card-border); border-radius: 16px; box-shadow: 0 4px 20px -2px rgba(0,0,0,0.05); }
            
            .agent-card {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 1rem;
                cursor: pointer;
                transition: all 0.25s ease;
                background: #ffffff;
            }
            .agent-card:hover {
                border-color: var(--primary-color);
                transform: translateY(-3px);
                box-shadow: 0 8px 15px -3px rgba(79, 70, 229, 0.15);
            }
            .agent-card.active {
                border-color: var(--primary-color);
                background: linear-gradient(135deg, #eeefef 0%, #e0e7ff 100%);
                box-shadow: 0 0 0 2px var(--primary-color);
            }

            .form-label { font-weight: 600; color: #334155; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
            .form-control, .form-select { border-radius: 8px; border: 1.5px solid #cbd5e1; padding: 0.75rem 1rem; font-weight: 500; }
            .form-control:focus, .form-select:focus { border-color: var(--primary-color); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15); }
            
            .btn-action { background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); border: none; border-radius: 10px; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }
            .btn-action:hover { background: linear-gradient(135deg, #4338ca 0%, #312e81 100%); transform: translateY(-1px); }
            
            .quick-btn { border: 1px solid #cbd5e1; background: #ffffff; color: #475569; border-radius: 20px; padding: 0.35rem 0.9rem; font-size: 0.825rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
            .quick-btn:hover { background: var(--primary-color); color: white; border-color: var(--primary-color); }
            
            .result-container { background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(0,0,0,0.08); padding: 2rem; }
            .result-body h1, .result-body h2, .result-body h3 { color: #1e1b4b; margin-top: 1.5rem; font-weight: 700; }
            .result-body p { line-height: 1.8; color: #334155; font-size: 1.05rem; }
            .result-body ul { background: #f8fafc; padding: 1.25rem 2rem; border-radius: 10px; border-left: 4px solid var(--primary-color); }
        </style>
    </head>
    <body>

        <header class="main-header mb-4">
            <div class="container d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 fw-bold mb-1"><i class="fa-solid fa-crown text-warning me-2"></i>MYSTIC THREAD STUDIO</h1>
                    <p class="mb-0 text-white-50 font-monospace small">ENTERPRISE MULTI-AGENT ORCHESTRATION ENGINE • 180 STORE NETWORK READY</p>
                </div>
                <div class="text-end">
                    <span class="badge bg-success px-3 py-2 rounded-pill"><i class="fa-solid fa-circle-check me-1"></i> SYSTEM ACTIVE</span>
                </div>
            </div>
        </header>

        <div class="container pb-5">
            <div class="row g-3 mb-4">
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card active" onclick="selectAgent('ceo', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-chess-king fs-4 text-indigo me-2" style="color:#4f46e5;"></i>
                            <strong class="text-dark">CEO Ajanı</strong>
                        </div>
                        <small class="text-muted d-block">Bütüncül Sentez & Strateji</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('astro', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-planet-ringed fs-4 me-2" style="color:#0284c7;"></i>
                            <strong class="text-dark">Astroloji</strong>
                        </div>
                        <small class="text-muted d-block">Doğum Haritası & Transit</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('tarot', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-cards fs-4 me-2" style="color:#d97706;"></i>
                            <strong class="text-dark">Tarot & Kehanet</strong>
                        </div>
                        <small class="text-muted d-block">3 Kart Sembolik Açılım</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('numerology', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-calculator fs-4 me-2" style="color:#059669;"></i>
                            <strong class="text-dark">Numeroloji</strong>
                        </div>
                        <small class="text-muted d-block">Kader & Titreşim Sayısı</small>
                    </div>
                </div>
                <div class="col-md-4 col-lg-2.4">
                    <div class="agent-card" onclick="selectAgent('dream', this)">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fa-solid fa-moon fs-4 me-2" style="color:#7c3aed;"></i>
                            <strong class="text-dark">Rüya Analiz</strong>
                        </div>
                        <small class="text-muted d-block">Bilinçaltı Çözümleme</small>
                    </div>
                </div>
            </div>

            <div class="card-custom p-4 mb-4">
                <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
                    <h4 class="fw-bold mb-0 text-dark" id="formTitle"><i class="fa-solid fa-sliders text-indigo me-2"></i>CEO Ajanı - Bütüncül Holding Sentezi</h4>
                    <span class="text-muted small"><i class="fa-solid fa-shield-halved text-success me-1"></i> Safe & Encrypted Data</span>
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

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <label class="form-label mb-0">Soru / Niyet / Rüya Detayı</label>
                            <div class="d-flex gap-1">
                                <button type="button" class="quick-btn" onclick="setQuestion('Gelecek dönemdeki kariyer, yatırım ve finansal fırsatlarım nelerdir?')">💼 Kariyer & Finans</button>
                                <button type="button" class="quick-btn" onclick="setQuestion('İlişki ve evlilik potansiyelim, ruh eşi döngülerim neleri gösteriyor?')">❤️ İlişki & Uyum</button>
                                <button type="button" class="quick-btn" onclick="setQuestion('Bu gece gördüğüm rüyanın derin psikolojik ve mistik anlamı nedir?')">🌙 Rüya Analizi</button>
                            </div>
                        </div>
                        <textarea id="queryInput" class="form-control" rows="3" placeholder="Ajanlarımıza sormak istediğiniz konuyu detaylıca buraya yazabilirsiniz..." required>Gelecek dönemdeki kariyer ve finansal fırsatlarım nelerdir?</textarea>
                    </div>

                    <button type="submit" id="submitBtn" class="btn btn-action text-white w-100 py-3 fs-5">
                        <span id="btnText"><i class="fa-solid fa-wand-magic-sparkles me-2"></i>Holding Ajan Analizini Başlat</span>
                        <span id="btnSpinner" class="spinner-border spinner-border-sm d-none me-2" role="status"></span>
                    </button>
                </form>
            </div>

            <div id="resultCard" class="result-container d-none">
                <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
                    <div>
                        <span class="badge bg-indigo text-white mb-1" style="background:#4f46e5;">EXECUTIVE REPORT</span>
                        <h3 class="fw-bold mb-0 text-dark">Mistik Holding Analiz Çıktısı</h3>
                    </div>
                    <button class="btn btn-outline-secondary btn-sm" onclick="window.print()"><i class="fa-solid fa-print me-1"></i> Raporu Yazdır / PDF</button>
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
            if (type === 'ceo') title.innerHTML = '<i class="fa-solid fa-chess-king text-indigo me-2"></i>CEO Ajanı - Bütüncül Holding Sentezi';
            else if (type === 'astro') title.innerHTML = '<i class="fa-solid fa-planet-ringed text-indigo me-2"></i>Astroloji Ajanı - Doğum Haritası Raporu';
            else if (type === 'tarot') title.innerHTML = '<i class="fa-solid fa-cards text-indigo me-2"></i>Tarot Ajanı - Kart Kehaneti';
            else if (type === 'numerology') title.innerHTML = '<i class="fa-solid fa-calculator text-indigo me-2"></i>Numeroloji Ajanı - Sayısal Frekans Analizi';
            else if (type === 'dream') title.innerHTML = '<i class="fa-solid fa-moon text-indigo me-2"></i>Rüya Ajanı - Bilinçaltı Çözümlemesi';
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
                btnText.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Holding Ajan Analizini Başlat';
            }
        }
        </script>
    </body>
    </html>
    """