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
app = FastAPI(title="MYSTIC THREAD STUDIO - Multi-Agent System", version="7.1")
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

geolocator = Nominatim(user_agent="mystic_thread_studio_v7")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

# --- HESAPLAMA YARDIMCILARI ---
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
        return "<p class='text-danger fw-bold'>OPENAI_API_KEY tanımlı değil. Ortam değişkenlerinizi kontrol edin.</p>"
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
        response = llm.invoke(prompt)
        return response.content if response and response.content else "<p class='text-warning fw-bold'>Yanıt oluşturulamadı.</p>"
    except Exception as e:
        return f"<p class='text-danger fw-bold'>Yapay Zeka Hatası: {str(e)}</p>"

class AgentRequest(BaseModel):
    agent_type: str = Field("ceo", max_length=20)
    name: Optional[str] = Field("Danışan", max_length=100)
    birth_date: str = Field(..., max_length=15)
    birth_time: Optional[str] = Field("12:00", max_length=10)
    country: Optional[str] = Field("Türkiye", max_length=60)
    city: Optional[str] = Field("İstanbul", max_length=60)
    question: Optional[str] = Field("", max_length=500)

# --- 1. ASTROLOJİ AJANI ---
def astro_agent(req: AgentRequest) -> str:
    lat, lng = None, None
    if req.city and req.country:
        loc = geolocator.geocode(f"{req.city}, {req.country}")
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
    bodies = {"Güneş": swe.SUN, "Ay": swe.MOON, "Merkür": swe.MERCURY, "Venüs": swe.VENUS, "Mars": swe.MARS}
    for name, body_id in bodies.items():
        res, _ = swe.calc_ut(julian_day, body_id)
        deg = round(res[0], 2)
        sign = SIGNS[int(deg // 30)]
        planets_data.append(f"{name}: {sign} ({deg % 30:.2f}°)")

    prompt = f"""
    Sen Baş Astrolog Ajanısın.
    Danışan: {req.name} | Doğum Tarihi/Saati: {req.birth_date} {req.birth_time} | Konum: {req.city}, {req.country}
    Yükselen Burç: {asc_sign} ({ascendant_degree}°)
    Gezegen Konumları: {', '.join(planets_data)}
    Soru/Konu: "{req.question}"

    Lütfen gezegen konumları, ev yerleşimleri ve transit etkilerini dikkate alarak HTML formatında profesyonel astrolojik analiz sun.
    """
    return get_ai_response(prompt)

# --- 2. TAROT AJANI ---
def tarot_agent(req: AgentRequest) -> str:
    prompt = f"""
    Sen Tarot ve Kehanet Uzmanı Ajanısın.
    Danışan: {req.name}
    Niyet/Soru: "{req.question}"

    3 kartlık (Geçmiş, Şu An, Gelecek) sembolik bir kart açılımı gerçekleştir ve HTML formatında detaylıca yorumla.
    """
    return get_ai_response(prompt)

# --- 3. NUMEROLOJİ AJANI ---
def numerology_agent(req: AgentRequest) -> str:
    life_path = calculate_life_path_number(req.birth_date)
    name_number = calculate_name_number(req.name)
    prompt = f"""
    Sen Numeroloji Uzmanı Ajanısın.
    Danışan: {req.name} (İsim Sayısı / Ruh İfadesi: {name_number})
    Doğum Tarihi: {req.birth_date} (Yaşam Yolu / Kader Sayısı: {life_path})
    Soru/Detay: "{req.question}"

    Yaşam yolu sayısı ({life_path}) ve isim titreşimi ({name_number}) temelinde potansiyelleri HTML formatında açıklayarak rehberlik sun.
    """
    return get_ai_response(prompt)

# --- 4. RÜYA TABİRİ AJANI ---
def dream_agent(req: AgentRequest) -> str:
    prompt = f"""
    Sen Bilinçaltı ve Rüya Analiz Ajanısın.
    Danışan: {req.name}
    Anlatılan Rüya: "{req.question}"

    Bu rüyadaki ana sembolleri, psikolojik katmanları ve bilinçaltı mesajlarını HTML formatında çözümle.
    """
    return get_ai_response(prompt)

# --- 5. CEO / ORKESTRASYON AJANI (MULTI-AGENT SYNTHESIS) ---
def ceo_agent_orchestrator(req: AgentRequest) -> str:
    astro_res = astro_agent(req)
    tarot_res = tarot_agent(req)
    num_res = numerology_agent(req)
    dream_res = dream_agent(req) if req.question else "Rüya verisi girilmedi."

    synthesis_prompt = f"""
    Sen Mistik Holding'in CEO Ajanısın (Baş Mistik Rehber).
    Danışan {req.name} için alt uzmanların (Astroloji, Tarot, Numeroloji, Rüya Tabiri) sunduğu raporlar aşağıdadır.

    --- ASTROLOJİ RAPORU ---
    {astro_res[:600]}...

    --- TAROT RAPORU ---
    {tarot_res[:600]}...

    --- NUMEROLOJİ RAPORU ---
    {num_res[:600]}...

    --- RÜYA & BİLİNÇALTI RAPORU ---
    {dream_res[:600]}...

    GÖREVİN:
    Danışanın sorusunu ("{req.question}") odağa alarak bu 4 uzman alanının verilerini üst düzey bir CEO strateji raporunda birleştir.
    Çelişen durumları dengele, ortak temaları öne çıkar ve Danışan için net bir Mistik Yol Haritası (Executive Action Plan) sun.
    Yanıtı şık HTML formatında (<h3>, <div class='alert alert-info'>, <ul>, <li>, <strong>) hazırla.
    """
    return get_ai_response(synthesis_prompt)

@app.post("/analyze_astro")
@limiter.limit("10/minute")
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
        <title>MYSTIC THREAD STUDIO - Holding Konsolu</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                background-color: #ffffff; 
                color: #1e293b; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            }
            .card { 
                background-color: #ffffff; 
                border: 1px solid #cbd5e1; 
                border-radius: 12px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .agent-card { 
                cursor: pointer; 
                border: 2px solid #cbd5e1; 
                transition: all 0.3s ease; 
                background-color: #f8fafc;
            }
            .agent-card:hover { 
                border-color: #6366f1; 
                transform: translateY(-2px); 
                background-color: #ffffff;
            }
            .agent-card.active { 
                border-color: #6366f1; 
                background-color: #eeefff; 
                box-shadow: 0 0 12px rgba(99, 102, 241, 0.25); 
            }
            .form-label {
                font-weight: 600;
                color: #0f172a;
            }
            .form-control { 
                background-color: #ffffff; 
                border: 1px solid #cbd5e1; 
                color: #0f172a; 
                font-weight: 500;
            }
            .form-control:focus { 
                background-color: #ffffff; 
                color: #0f172a; 
                border-color: #6366f1; 
                box-shadow: 0 0 0 0.25rem rgba(99, 102, 241, 0.25); 
            }
            .btn-primary { 
                background-color: #6366f1; 
                border: none; 
                font-weight: 600; 
            }
            .btn-primary:hover { 
                background-color: #4f46e5; 
            }
            #resultCard {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                color: #0f172a;
            }
            .text-indigo {
                color: #4f46e5 !important;
            }
        </style>
    </head>
    <body class="container py-4">
        
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
            <div>
                <h2 class="fw-bold text-indigo mb-0">✨ MYSTIC THREAD STUDIO</h2>
                <small class="text-secondary fw-semibold">Holding Otonom Multi-Agent Konsolu v7.1</small>
            </div>
            <span class="badge bg-success px-3 py-2 fs-6">5/5 AGENTS ONLINE</span>
        </div>

        <!-- AJAN SEÇİM ALANI -->
        <h6 class="mb-3 text-secondary fw-bold">Aktif Çalıştırılacak Ajanı Seçin:</h6>
        <div class="row mb-4">
            <div class="col-md-2 mb-2">
                <div class="card p-3 agent-card active" onclick="selectAgent('ceo', this)">
                    <h6 class="fw-bold mb-1 text-dark">👑 CEO Ajanı</h6>
                    <small class="text-secondary">Multi-Agent Sentez</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('astro', this)">
                    <h6 class="fw-bold mb-1 text-dark">🪐 Astroloji</h6>
                    <small class="text-secondary">Ephemeris Haritası</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('tarot', this)">
                    <h6 class="fw-bold mb-1 text-dark">🃏 Tarot</h6>
                    <small class="text-secondary">Kart Kehaneti</small>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('numerology', this)">
                    <h6 class="fw-bold mb-1 text-dark">🔢 Numeroloji</h6>
                    <small class="text-secondary">Kader & İsim Sayısı</small>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('dream', this)">
                    <h6 class="fw-bold mb-1 text-dark">🌙 Rüya Tabiri</h6>
                    <small class="text-secondary">Bilinçaltı Analizi</small>
                </div>
            </div>
        </div>

        <!-- FORM ALANI -->
        <div class="card p-4">
            <h4 class="mb-4 text-indigo fw-bold" id="formTitle">👑 CEO Ajanı - Multi-Agent Bütüncül Sentez</h4>
            <form onsubmit="handleFormSubmit(event)">
                <input type="hidden" id="selectedAgent" value="ceo">
                
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Ad Soyad / Danışan</label>
                        <input type="text" id="nameInput" class="form-control" value="Danışan" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum Tarihi</label>
                        <input type="text" id="dateInput" class="form-control" value="15.05.1995" placeholder="GG.AA.YYYY" required>
                    </div>
                    <div class="col-md-4 mb-3" id="timeGroup">
                        <label class="form-label">Doğum Saati</label>
                        <input type="text" id="timeInput" class="form-control" value="14:30" placeholder="HH:MM">
                    </div>
                </div>

                <div class="row" id="locationGroup">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Doğum Ülkesi</label>
                        <input type="text" id="countryInput" class="form-control" value="Türkiye">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Doğum Şehri</label>
                        <input type="text" id="cityInput" class="form-control" value="İstanbul">
                    </div>
                </div>

                <div class="mb-4">
                    <label class="form-label" id="queryLabel">Soru / Niyet / Rüya Detayı</label>
                    <textarea id="queryInput" class="form-control" rows="3">Gelecek dönemdeki kariyer ve finansal fırsatlarım nelerdir?</textarea>
                </div>

                <button type="submit" id="submitBtn" class="btn btn-primary w-100 py-3 fw-bold fs-5">
                    <span id="btnText">Ajan Analizini Başlat</span>
                    <span id="btnSpinner" class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true"></span>
                </button>
            </form>

            <div id="resultCard" class="mt-4 p-4 rounded d-none">
                <h5 class="text-indigo fw-bold mb-3 border-bottom pb-2">Analiz Sonucu</h5>
                <div id="resultBox" class="lh-lg"></div>
            </div>
        </div>

        <script>
        function selectAgent(type, el) {
            document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('selectedAgent').value = type;

            const title = document.getElementById('formTitle');
            if (type === 'ceo') title.innerText = "👑 CEO Ajanı - Multi-Agent Bütüncül Sentez";
            else if (type === 'astro') title.innerText = "🪐 Astroloji Ajanı - Doğum Haritası Analizi";
            else if (type === 'tarot') title.innerText = "🃏 Tarot Ajanı - Kart Açılımı";
            else if (type === 'numerology') title.innerText = "🔢 Numeroloji Ajanı - Kader Sayısı";
            else if (type === 'dream') title.innerText = "🌙 Rüya Ajanı - Bilinçaltı Analizi";
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
            btnText.innerText = agent === 'ceo' ? "CEO Bütün Ajanları Çalıştırıyor..." : "Ajan Analiz Ediyor...";

            try {
                const payload = {
                    agent_type: agent,
                    name: document.getElementById('nameInput').value,
                    birth_date: document.getElementById('dateInput').value,
                    birth_time: document.getElementById('timeInput').value,
                    country: document.getElementById('countryInput').value,
                    city: document.getElementById('cityInput').value,
                    question: document.getElementById('queryInput').value
                };

                const res = await fetch('/analyze_astro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Sunucu hatası oluştu.");

                resultCard.classList.remove('d-none');
                resultBox.innerHTML = data.analysis;

            } catch (err) {
                alert("Hata: " + err.message);
            } finally {
                submitBtn.disabled = false;
                btnSpinner.classList.add('d-none');
                btnText.innerText = "Ajan Analizini Başlat";
            }
        }
        </script>
    </body>
    </html>
    """