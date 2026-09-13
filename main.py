import os
import json
import re
from typing import Optional
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
app = FastAPI(title="MYSTIC THREAD STUDIO", version="5.1")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Yapılandırması
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

geolocator = Nominatim(user_agent="mystic_thread_studio_v5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]

def calculate_life_path_number(birth_date_str: str) -> int:
    """Doğum tarihinden Numerolojik Yaşam Yolu Sayısını hesaplar."""
    digits = [int(d) for d in re.findall(r"\d", birth_date_str)]
    total = sum(digits)
    while total > 9 and total not in [11, 22, 33]:  # Üstat sayıları korur
        total = sum(int(d) for d in str(total))
    return total

def get_ai_response(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "<p class='text-danger'>OPENAI_API_KEY tanımlı değil. Lütfen ortam değişkenlerinizi kontrol edin.</p>"
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
        response = llm.invoke(prompt)
        return response.content if response and response.content else "<p class='text-warning'>Yanıt oluşturulamadı.</p>"
    except Exception as e:
        return f"<p class='text-danger'>Yapay Zeka Hatası: {str(e)}</p>"

class AgentRequest(BaseModel):
    agent_type: str = Field("astro", max_length=20)
    name: Optional[str] = Field("Danışan", max_length=100)
    birth_date: str = Field(..., max_length=15)
    birth_time: Optional[str] = Field("12:00", max_length=10)
    country: Optional[str] = Field("Türkiye", max_length=60)
    city: Optional[str] = Field("İstanbul", max_length=60)
    district: Optional[str] = Field("", max_length=60)
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    question: Optional[str] = Field("", max_length=500)
    lang: Optional[str] = Field("tr", max_length=5)

@app.post("/analyze_astro")
@limiter.limit("10/minute")
async def analyze_astro(request: Request, req: AgentRequest):
    try:
        if req.agent_type == "astro":
            lat, lng = req.latitude, req.longitude
            if lat is None or lng is None:
                loc = geolocator.geocode(f"{req.city}, {req.country}")
                lat, lng = (loc.latitude, loc.longitude) if loc else (41.0082, 28.9784)

            parts = [int(p) for p in re.sub(r"[^\d]", " ", req.birth_date).split() if p.isdigit()]
            day, month, year = (parts[0], parts[1], parts[2]) if len(parts) == 3 else (15, 5, 1995)
            
            clean_time = req.birth_time.replace(".", ":")
            t_parts = [int(p) for p in clean_time.split(":") if p.isdigit()]
            hour, minute = (t_parts[0], t_parts[1]) if len(t_parts) >= 2 else (12, 0)

            julian_day = swe.julday(year, month, day, hour + (minute / 60.0))
            cusps, ascmc = swe.houses(julian_day, lat, lng, b'P')
            ascendant_degree = round(ascmc[0], 2)
            asc_sign = SIGNS[int(ascendant_degree // 30)]

            # Gezegen Konumları Hesaplaması (Swiss Ephemeris)
            planets_data = []
            bodies = {
                "Güneş": swe.SUN,
                "Ay": swe.MOON,
                "Merkür": swe.MERCURY,
                "Venüs": swe.VENUS,
                "Mars": swe.MARS
            }

            for name, body_id in bodies.items():
                res, _ = swe.calc_ut(julian_day, body_id)
                deg = round(res[0], 2)
                sign = SIGNS[int(deg // 30)]
                planets_data.append(f"{name}: {sign} ({deg % 30:.2f}°)")

            planets_summary = ", ".join(planets_data)

            prompt = f"""
            Sen profesyonel ve bilge bir astrologsun.
            Danışan Adı: {req.name}
            Doğum Tarihi/Saati: {req.birth_date} {req.birth_time}
            Konum: {req.city}, {req.country} (Enlem: {lat}, Boylam: {lng})
            Yükselen Burç: {asc_sign} ({ascendant_degree}°)
            Gezegen Konumları: {planets_summary}
            Soru/Odak Noktası: "{req.question}"

            Lütfen bu astrolojik harita verilerini temel alarak derinlemesine bir analiz yap.
            Yanıtı temiz HTML formatında (<h3>, <p>, <ul>, <li>, <strong> etiketleriyle) sun.
            """
        
        elif req.agent_type == "tarot":
            prompt = f"""
            Sen sezgisel ve bilge bir Tarot Uzmanısın.
            Danışan: {req.name}
            Niyet/Soru: "{req.question}"
            
            Danışan için 3 kartlık (Geçmiş, Şu An, Gelecek) sembolik bir açılım yap ve detaylıca yorumla. Yanıtı temiz HTML formatında sun.
            """

        elif req.agent_type == "numerology":
            life_path = calculate_life_path_number(req.birth_date)
            prompt = f"""
            Sen uzman bir Numeroloji Danışmanısın.
            Danışan: {req.name}
            Doğum Tarihi: {req.birth_date}
            Hesaplanan Yaşam Yolu / Kader Sayısı: {life_path}
            Özel İstek/Soru: "{req.question}"

            Danışanın Yaşam Yolu Sayısı ({life_path}) üzerinden karakter potansiyelini, güçlü yönlerini ve yaşam döngülerini detaylıca HTML formatında açıkla.
            """

        elif req.agent_type == "dream":
            prompt = f"""
            Sen bilinçaltı ve rüya sembolleri uzmanısın.
            Danışan: {req.name}
            Anlatılan Rüya: "{req.question}"

            Bu rüyadaki ana sembolleri, psikolojik ve mistik katmanları analiz et. Yanıtı HTML formatında düzenli paragraflar halinde ver.
            """
        else:
            prompt = f"Danışan {req.name} için genel mistik rehberlik sun: {req.question}"

        ai_commentary = get_ai_response(prompt)
        return {"status": "success", "analysis": ai_commentary}

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
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
            .agent-card { cursor: pointer; border: 2px solid #334155; transition: all 0.3s ease; }
            .agent-card:hover { border-color: #6366f1; transform: translateY(-2px); }
            .agent-card.active { border-color: #6366f1; background-color: #334155; box-shadow: 0 0 15px rgba(99, 102, 241, 0.3); }
            .form-control, .form-select { background-color: #0f172a; border: 1px solid #334155; color: #fff; }
            .form-control:focus { background-color: #0f172a; color: #fff; border-color: #6366f1; box-shadow: none; }
            .btn-primary { background-color: #6366f1; border: none; font-weight: 600; }
            .btn-primary:hover { background-color: #4f46e5; }
        </style>
    </head>
    <body class="container py-4">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-indigo mb-0">✨ MYSTIC THREAD STUDIO</h2>
                <small class="text-muted">Holding Otonom Mistik Ajan Konsolu</small>
            </div>
            <span class="badge bg-success px-3 py-2">SYSTEM ONLINE</span>
        </div>

        <!-- AJAN SEÇİM ALANI -->
        <h6 class="mb-3 text-muted">Aktif Çalıştırılacak Ajanı Seçin:</h6>
        <div class="row mb-4">
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card active" onclick="selectAgent('astro', this)">
                    <h6 class="fw-bold mb-1">🪐 Astroloji Ajanı</h6>
                    <small class="text-muted">Doğum Haritası & Transitler</small>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('tarot', this)">
                    <h6 class="fw-bold mb-1">🃏 Tarot Ajanı</h6>
                    <small class="text-muted">Kart Okuma & Kehanet</small>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('numerology', this)">
                    <h6 class="fw-bold mb-1">🔢 Numeroloji Ajanı</h6>
                    <small class="text-muted">Kader Sayısı & Analiz</small>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="card p-3 agent-card" onclick="selectAgent('dream', this)">
                    <h6 class="fw-bold mb-1">🌙 Rüya Ajanı</h6>
                    <small class="text-muted">Bilinçaltı & Semboller</small>
                </div>
            </div>
        </div>

        <!-- FORM ALANI -->
        <div class="card p-4">
            <h4 class="mb-4" id="formTitle">Doğum Haritası ve Mistik Analiz İsteği</h4>
            <form onsubmit="handleFormSubmit(event)">
                <input type="hidden" id="selectedAgent" value="astro">
                
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
                    <label class="form-label" id="queryLabel">Odaklanılacak Soru / Konu</label>
                    <textarea id="queryInput" class="form-control" rows="3">Kariyer ve potansiyel fırsatlarım yönünde potansiyelim nedir?</textarea>
                </div>

                <button type="submit" id="submitBtn" class="btn btn-primary w-100 py-3 fw-bold">
                    <span id="btnText">Ajan Analizini Başlat</span>
                    <span id="btnSpinner" class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true"></span>
                </button>
            </form>

            <div id="resultCard" class="mt-4 p-3 rounded d-none" style="background-color: #0f172a; border: 1px solid #334155;">
                <h5 class="text-indigo mb-3">Analiz Sonucu</h5>
                <div id="resultBox"></div>
            </div>
        </div>

        <script>
        function selectAgent(type, el) {
            document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('selectedAgent').value = type;

            const title = document.getElementById('formTitle');
            const timeGrp = document.getElementById('timeGroup');
            const locGrp = document.getElementById('locationGroup');
            const qLbl = document.getElementById('queryLabel');

            if (type === 'astro') {
                title.innerText = "Doğum Haritası ve Mistik Analiz İsteği";
                timeGrp.style.display = "block";
                locGrp.style.display = "flex";
                qLbl.innerText = "Odaklanılacak Soru / Konu";
            } else if (type === 'tarot') {
                title.innerText = "Tarot Kart Açılımı ve Gelecek Analizi";
                timeGrp.style.display = "none";
                locGrp.style.display = "none";
                qLbl.innerText = "Niyetiniz veya Öğrenmek İstediğiniz Konu";
            } else if (type === 'numerology') {
                title.innerText = "Numeroloji & Kader Sayısı Analizi";
                timeGrp.style.display = "none";
                locGrp.style.display = "none";
                qLbl.innerText = "Özel İsteğiniz Varsa Belirtin (Opsiyonel)";
            } else if (type === 'dream') {
                title.innerText = "Rüya Tabiri ve Sembol Okumaları";
                timeGrp.style.display = "none";
                locGrp.style.display = "none";
                qLbl.innerText = "Gördüğünüz Rüyayı Detaylıca Yazın";
            }
        }

        async function handleFormSubmit(e) {
            e.preventDefault();
            const submitBtn = document.getElementById('submitBtn');
            const btnSpinner = document.getElementById('btnSpinner');
            const btnText = document.getElementById('btnText');
            const resultCard = document.getElementById('resultCard');
            const resultBox = document.getElementById('resultBox');

            submitBtn.disabled = true;
            btnSpinner.classList.remove('d-none');
            btnText.innerText = "Ajan Hesaplanıyor...";

            try {
                const payload = {
                    agent_type: document.getElementById('selectedAgent').value,
                    name: document.getElementById('nameInput').value,
                    birth_date: document.getElementById('dateInput').value,
                    birth_time: document.getElementById('timeInput').value,
                    country: document.getElementById('countryInput').value,
                    city: document.getElementById('cityInput').value,
                    question: document.getElementById('queryInput').value,
                    lang: 'tr'
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