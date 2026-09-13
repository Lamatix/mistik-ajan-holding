import os
import urllib.parse
import base64
from flask import Flask, request, jsonify, render_template_string
from crewai import Agent, Task, Crew, Process
from openai import OpenAI
from astro_engine import AstroEngine

app = Flask(__name__)

EXPECTED_API_KEY = os.environ.get("X_API_KEY", "mistik-secret-key-2026")
astro_engine = AstroEngine()

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mystic Thread Studio - Çoklu Otonom Ajan Kontrol Merkezi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; color: #ffffff; }
        .btn-primary { background-color: #6366f1; border: none; font-weight: 600; padding: 12px; }
        .btn-primary:hover { background-color: #4f46e5; }
        .form-control, .form-select { background-color: #0f172a; border: 1px solid #334155; color: #ffffff !important; }
        .form-control:focus, .form-select:focus { background-color: #0f172a; color: #ffffff !important; border-color: #6366f1; box-shadow: none; }
        .result-box { background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 20px; white-space: pre-wrap; font-size: 0.98rem; line-height: 1.7; color: #ffffff !important; }
        .badge-agent { background-color: #312e81; color: #ffffff; border: 1px solid #4338ca; font-size: 0.9rem; padding: 8px 14px; }
        .logo-glow { filter: drop-shadow(0px 0px 8px rgba(99, 102, 241, 0.6)); }
        .nav-tabs .nav-link { color: #94a3b8; border: none; font-weight: 600; }
        .nav-tabs .nav-link.active { color: #818cf8; background-color: transparent; border-bottom: 3px solid #6366f1; }
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <!-- Header -->
                <div class="d-flex align-items-center justify-content-between mb-4 pb-3 border-bottom border-secondary">
                    <div class="d-flex align-items-center gap-3">
                        <div class="logo-glow">
                            <svg width="52" height="52" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="50" cy="50" r="44" stroke="#818cf8" stroke-width="2.5" stroke-dasharray="6 4" opacity="0.6" />
                                <path d="M 50 28 L 53 45 L 70 48 L 53 51 L 50 68 L 47 51 L 30 48 L 47 45 Z" fill="#ffffff" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="fw-bold mb-0" style="color: #818cf8;">MYSTIC THREAD STUDIO</h2>
                            <p class="text-secondary mb-0" style="font-size: 0.9rem;">Holding Otonom Ajan Konsolu | Strateji, Astroloji, Tarot & Kahve Falı</p>
                        </div>
                    </div>
                    <span class="badge bg-success px-3 py-2">Sistem Canlıda</span>
                </div>

                <!-- Tab Seçimleri -->
                <ul class="nav nav-tabs mb-4" id="agentTabs" role="tablist">
                    <li class="nav-item">
                        <button class="nav-link active" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy-panel" type="button">Sosyal Medya & Büyüme</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" id="astro-tab" data-bs-toggle="tab" data-bs-target="#astro-panel" type="button">Swiss Ephemeris Astroloji</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" id="tarot-tab" data-bs-toggle="tab" data-bs-target="#tarot-panel" type="button">Tarot Okuması</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" id="coffee-tab" data-bs-toggle="tab" data-bs-target="#coffee-panel" type="button">Kahve Falı (Görsel Analiz)</button>
                    </li>
                </ul>

                <div class="tab-content" id="agentTabsContent">
                    <!-- MODÜL 1: STRATEJİ VE KREATİF AJANLAR -->
                    <div class="tab-pane fade show active" id="strategy-panel" role="tabpanel">
                        <div class="card p-4 mb-4 shadow">
                            <h5 class="mb-3 text-light">Strateji & Viral Video Senaryo İsteği</h5>
                            <form id="strategyForm">
                                <div class="mb-3">
                                    <textarea id="stratQueryInput" class="form-control" rows="3" placeholder="Örn: Mystic Thread Studio için 2026 sosyal medya ve büyüme stratejisi oluştur..." required>Mystic Thread Studio için 2026 sosyal medya ve büyüme stratejisi oluştur.</textarea>
                                </div>
                                <button type="submit" id="stratSubmitBtn" class="btn btn-primary w-100">
                                    <span id="stratBtnText">Strateji ve Kreatif Ajanları Çalıştır</span>
                                    <span id="stratBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- MODÜL 2: MİSTİK ASTROLOJİ AJANI -->
                    <div class="tab-pane fade" id="astro-panel" role="tabpanel">
                        <div class="card p-4 mb-4 shadow">
                            <h5 class="mb-3 text-light">Doğum Haritası ve Mistik Analiz İsteği</h5>
                            <form id="astroForm">
                                <div class="row g-3 mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label text-secondary">Ad Soyad / Danışan</label>
                                        <input type="text" id="nameInput" class="form-control" value="Danışan" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label text-secondary">Doğum Tarihi</label>
                                        <input type="date" id="dateInput" class="form-control" value="1995-05-15" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label text-secondary">Doğum Saati</label>
                                        <input type="time" id="timeInput" class="form-control" value="14:30" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label text-secondary">Odaklanılacak Soru / Konu</label>
                                        <input type="text" id="astroQueryInput" class="form-control" value="Kariyer ve potansiyel fırsatlarım yönünde potansiyelim nedir?" required>
                                    </div>
                                </div>
                                <button type="submit" id="astroSubmitBtn" class="btn btn-primary w-100">
                                    <span id="astroBtnText">Swiss Ephemeris Haritasını Çıkar ve Analiz Et</span>
                                    <span id="astroBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- MODÜL 3: TAROT OKUMASI -->
                    <div class="tab-pane fade" id="tarot-panel" role="tabpanel">
                        <div class="card p-4 mb-4 shadow">
                            <h5 class="mb-3 text-light">Tarot Kartı Açılımı & Yorumu</h5>
                            <form id="tarotForm">
                                <div class="row g-3 mb-3">
                                    <div class="col-md-4">
                                        <label class="form-label text-secondary">Geçmiş Kartı</label>
                                        <input type="text" id="tarotCard1" class="form-control" value="The Fool (Deli)" required>
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label text-secondary">Şimdi Kartı</label>
                                        <input type="text" id="tarotCard2" class="form-control" value="The Tower (Yıkılan Kule)" required>
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label text-secondary">Gelecek Kartı</label>
                                        <input type="text" id="tarotCard3" class="form-control" value="The Star (Yıldız)" required>
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label text-secondary">Niyet / Soru</label>
                                        <input type="text" id="tarotQuery" class="form-control" value="Aşk hayatımda ve ilişkilerimde beni ne bekliyor?" required>
                                    </div>
                                </div>
                                <button type="submit" id="tarotSubmitBtn" class="btn btn-primary w-100">
                                    <span id="tarotBtnText">Tarot Ajanına Okuma Yaptır</span>
                                    <span id="tarotBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- MODÜL 4: KAHVE FALI (GÖRSEL ANALİZ) -->
                    <div class="tab-pane fade" id="coffee-panel" role="tabpanel">
                        <div class="card p-4 mb-4 shadow">
                            <h5 class="mb-3 text-light">Kahve Fincanı Fotoğrafı ile Fal Yorumu</h5>
                            <form id="coffeeForm">
                                <div class="mb-3">
                                    <label class="form-label text-secondary">Fincan / Telve Fotoğrafı Yükleyin</label>
                                    <input type="file" id="coffeeImgInput" class="form-control" accept="image/*" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label text-secondary">Niyet / Soru</label>
                                    <input type="text" id="coffeeQuery" class="form-control" value="Maddi durumum ve geleceğim hakkında ne görünüyorsunuz?" required>
                                </div>
                                <button type="submit" id="coffeeSubmitBtn" class="btn btn-primary w-100">
                                    <span id="coffeeBtnText">Görsel İşleme Ajanı ile Fincanı Analiz Et</span>
                                    <span id="coffeeBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Sonuç Alanı -->
                <div id="resultsContainer" class="d-none">
                    <!-- Strateji Çıktıları -->
                    <div id="stratResultsBlock" class="d-none">
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">İstihbarat & Strateji Direktörlüğü</span>
                            </div>
                            <div id="stratResult" class="result-box"></div>
                        </div>
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Kreatif & Video Kurgu Yönetmenliği</span>
                            </div>
                            <div id="creativeResult" class="result-box"></div>
                        </div>
                    </div>

                    <!-- Astroloji Çıktıları -->
                    <div id="astroResultsBlock" class="d-none">
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Swiss Ephemeris Hesaplama Çıktısı</span>
                            </div>
                            <div id="rawChartResult" class="result-box font-monospace" style="font-size: 0.85rem;"></div>
                        </div>
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Kıdemli Mistik Astrolog Yorumu</span>
                            </div>
                            <div id="astroResult" class="result-box"></div>
                        </div>
                    </div>

                    <!-- Tarot Çıktısı -->
                    <div id="tarotResultsBlock" class="d-none">
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Kıdemli Tarot Üstadı Yorumu</span>
                            </div>
                            <div id="tarotResult" class="result-box"></div>
                        </div>
                    </div>

                    <!-- Kahve Falı Çıktısı -->
                    <div id="coffeeResultsBlock" class="d-none">
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Vision AI Telve Sembol Analizi</span>
                            </div>
                            <div id="coffeeVisionResult" class="result-box font-monospace" style="font-size: 0.85rem;"></div>
                        </div>
                        <div class="card p-4 mb-4 shadow">
                            <div class="d-flex align-items-center mb-3">
                                <span class="badge badge-agent me-2 rounded-pill">Mistik Kahve Falı Yorumu</span>
                            </div>
                            <div id="coffeeResult" class="result-box"></div>
                        </div>
                    </div>

                    <!-- Ortak Dinamik Görsel Çıktısı -->
                    <div class="card p-4 shadow mb-5">
                        <h5 class="mb-3 text-light">Konsepte Özel Üretilen Görsel</h5>
                        <div class="text-center">
                            <img id="generatedImg" src="" class="img-fluid rounded border border-secondary mb-3 d-none" style="max-height: 450px;" alt="Üretilen Görsel">
                            <br>
                            <a id="imgLink" href="#" target="_blank" class="btn btn-outline-info btn-sm px-4 py-2">Görseli Yüksek Çözünürlükte Aç</a>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function hideAllBlocks() {
            document.getElementById('stratResultsBlock').classList.add('d-none');
            document.getElementById('astroResultsBlock').classList.add('d-none');
            document.getElementById('tarotResultsBlock').classList.add('d-none');
            document.getElementById('coffeeResultsBlock').classList.add('d-none');
        }

        // STRATEJİ
        document.getElementById('strategyForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const query = document.getElementById('stratQueryInput').value;
            const submitBtn = document.getElementById('stratSubmitBtn');
            const btnText = document.getElementById('stratBtnText');
            const btnSpinner = document.getElementById('stratBtnSpinner');

            btnText.innerText = "Stratejist ve Kreatif Ajan Çalışıyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/analyze_strategy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-API-KEY': 'mistik-secret-key-2026' },
                    body: JSON.stringify({ query: query })
                });

                if (response.ok) {
                    const data = await response.json();
                    hideAllBlocks();
                    document.getElementById('stratResult').innerText = data.intelligence_and_strategy || "";
                    document.getElementById('creativeResult').innerText = data.creative_and_video_guide || "";
                    document.getElementById('stratResultsBlock').classList.remove('d-none');
                    
                    if (data.generated_image_url) {
                        const imgElem = document.getElementById('generatedImg');
                        imgElem.src = data.generated_image_url;
                        imgElem.classList.remove('d-none');
                        document.getElementById('imgLink').href = data.generated_image_url;
                    }
                    document.getElementById('resultsContainer').classList.remove('d-none');
                    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
                }
            } catch (err) { alert("Hata: " + err.message); } 
            finally {
                btnText.innerText = "Strateji ve Kreatif Ajanları Çalıştır";
                btnSpinner.classList.add('d-none');
                submitBtn.disabled = false;
            }
        });

        // ASTROLOJİ
        document.getElementById('astroForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const name = document.getElementById('nameInput').value;
            const date = document.getElementById('dateInput').value;
            const time = document.getElementById('timeInput').value;
            const query = document.getElementById('astroQueryInput').value;

            const submitBtn = document.getElementById('astroSubmitBtn');
            const btnText = document.getElementById('astroBtnText');
            const btnSpinner = document.getElementById('astroBtnSpinner');

            btnText.innerText = "Harita Hesaplanıyor & Astrolog Yorumluyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/analyze_astro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-API-KEY': 'mistik-secret-key-2026' },
                    body: JSON.stringify({ name, birth_date: date, birth_time: time, query })
                });

                if (response.ok) {
                    const data = await response.json();
                    hideAllBlocks();
                    document.getElementById('rawChartResult').innerText = JSON.stringify(data.natal_chart_data, null, 2);
                    document.getElementById('astroResult').innerText = data.astrology_interpretation || "";
                    document.getElementById('astroResultsBlock').classList.remove('d-none');
                    
                    if (data.generated_image_url) {
                        const imgElem = document.getElementById('generatedImg');
                        imgElem.src = data.generated_image_url;
                        imgElem.classList.remove('d-none');
                        document.getElementById('imgLink').href = data.generated_image_url;
                    }
                    document.getElementById('resultsContainer').classList.remove('d-none');
                    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
                }
            } catch (err) { alert("Hata: " + err.message); } 
            finally {
                btnText.innerText = "Swiss Ephemeris Haritasını Çıkar ve Analiz Et";
                btnSpinner.classList.add('d-none');
                submitBtn.disabled = false;
            }
        });

        // TAROT
        document.getElementById('tarotForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const c1 = document.getElementById('tarotCard1').value;
            const c2 = document.getElementById('tarotCard2').value;
            const c3 = document.getElementById('tarotCard3').value;
            const query = document.getElementById('tarotQuery').value;

            const submitBtn = document.getElementById('tarotSubmitBtn');
            const btnText = document.getElementById('tarotBtnText');
            const btnSpinner = document.getElementById('tarotBtnSpinner');

            btnText.innerText = "Tarot Kartları Yorumlanıyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/analyze_tarot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-API-KEY': 'mistik-secret-key-2026' },
                    body: JSON.stringify({ cards: [c1, c2, c3], query })
                });

                if (response.ok) {
                    const data = await response.json();
                    hideAllBlocks();
                    document.getElementById('tarotResult').innerText = data.tarot_interpretation || "";
                    document.getElementById('tarotResultsBlock').classList.remove('d-none');
                    
                    if (data.generated_image_url) {
                        const imgElem = document.getElementById('generatedImg');
                        imgElem.src = data.generated_image_url;
                        imgElem.classList.remove('d-none');
                        document.getElementById('imgLink').href = data.generated_image_url;
                    }
                    document.getElementById('resultsContainer').classList.remove('d-none');
                    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
                }
            } catch (err) { alert("Hata: " + err.message); } 
            finally {
                btnText.innerText = "Tarot Ajanına Okuma Yaptır";
                btnSpinner.classList.add('d-none');
                submitBtn.disabled = false;
            }
        });

        // KAHVE FALI (VISION)
        document.getElementById('coffeeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('coffeeImgInput');
            const query = document.getElementById('coffeeQuery').value;

            if (!fileInput.files[0]) {
                alert("Lütfen bir resim seçin.");
                return;
            }

            const submitBtn = document.getElementById('coffeeSubmitBtn');
            const btnText = document.getElementById('coffeeBtnText');
            const btnSpinner = document.getElementById('coffeeBtnSpinner');

            btnText.innerText = "Vision AI Fincanı İnceleyip Yorumluyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            const reader = new FileReader();
            reader.onload = async function() {
                const base64Img = reader.result.split(',')[1];
                try {
                    const response = await fetch('/analyze_coffee', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-API-KEY': 'mistik-secret-key-2026' },
                        body: JSON.stringify({ image_base64: base64Img, query: query })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        hideAllBlocks();
                        document.getElementById('coffeeVisionResult').innerText = "Tespit Edilen Semboller:\n" + data.detected_symbols;
                        document.getElementById('coffeeResult').innerText = data.coffee_interpretation || "";
                        document.getElementById('coffeeResultsBlock').classList.remove('d-none');
                        
                        if (data.generated_image_url) {
                            const imgElem = document.getElementById('generatedImg');
                            imgElem.src = data.generated_image_url;
                            imgElem.classList.remove('d-none');
                            document.getElementById('imgLink').href = data.generated_image_url;
                        }
                        document.getElementById('resultsContainer').classList.remove('d-none');
                        document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
                    }
                } catch (err) { alert("Hata: " + err.message); } 
                finally {
                    btnText.innerText = "Görsel İşleme Ajanı ile Fincanı Analiz Et";
                    btnSpinner.classList.add('d-none');
                    submitBtn.disabled = false;
                }
            };
            reader.readAsDataURL(fileInput.files[0]);
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_DASHBOARD)

# GERİYE DÖNÜK UYUMLULUK: GELEN VARSAYILAN /analyze İSTEKLERİNİ MISTIK STRATEJİYE YÖNLENDİR
@app.route("/analyze", methods=["POST"])
def analyze_default():
    return analyze_strategy()

# ENDPOINT 1: SOSYAL MEDYA & BÜYÜME STRATEJİSİ
@app.route("/analyze_strategy", methods=["POST"])
def analyze_strategy():
    client_key = request.headers.get("X-API-KEY")
    referer = request.headers.get("Referer")
    
    if not referer and client_key != EXPECTED_API_KEY:
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json() or {}
    user_query = data.get("query", "Mystic Thread Studio için 2026 büyüme stratejisi oluştur.")

    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return jsonify({"error": "OPENAI_API_KEY eksik."}), 500

        strategy_agent = Agent(
            role="İstihbarat ve Strateji Direktörü",
            goal="Verilen konu veya ajans için 2026 odaklı stratejik büyüme planı ve pazar analizi hazırlamak.",
            backstory="Sen Mystic Thread Studio'nun en kıdemli stratejistisin. Verileri analiz eder ve en etkili büyüme adımlarını belirlersin.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        creative_agent = Agent(
            role="Kreatif ve Video Kurgu Yönetmeni",
            goal="Strateji doğrultusunda yüksek etkileşimli sosyal medya senaryoları ve Reels/Shorts konseptleri üretmek.",
            backstory="Sen Mystic Thread Studio'nun kreatif dahi direktörüsün. İzleyiciyi ilk 3 saniyede yakalayan viral video senaryoları yazarsın.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        task_strategy = Task(
            description=f"Konu: '{user_query}'. Bu konu için 3 maddelik net ve uygulanabilir 2026 büyüme ve içerik stratejisi hazırla.",
            expected_output="3 maddelik detaylı ve profesyonel strateji analizi.",
            agent=strategy_agent
        )

        task_creative = Task(
            description=f"Stratejiye uygun olarak 1 adet viral Instagram Reels/YouTube Shorts senaryosu yaz.",
            expected_output="Tam video kurgu senaryosu ve içerik planı.",
            agent=creative_agent
        )

        crew = Crew(
            agents=[strategy_agent, creative_agent],
            tasks=[task_strategy, task_creative],
            process=Process.sequential,
            verbose=False
        )

        crew.kickoff()

        generated_image_url = None
        dalle_prompt = f"Professional modern visual concept for Mystic Thread Studio, theme: {user_query}, 8k, futuristic digital studio"
        try:
            client = OpenAI(api_key=openai_key)
            img_res = client.images.generate(model="dall-e-3", prompt=dalle_prompt[:1000], n=1, size="1024x1024")
            generated_image_url = img_res.data[0].url
        except Exception:
            encoded_prompt = urllib.parse.quote(dalle_prompt)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        return jsonify({
            "intelligence_and_strategy": str(task_strategy.output),
            "creative_and_video_guide": str(task_creative.output),
            "generated_image_url": generated_image_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ENDPOINT 2: SWISS EPHEMERIS ASTROLOJİ
@app.route("/analyze_astro", methods=["POST"])
def analyze_astro():
    client_key = request.headers.get("X-API-KEY")
    referer = request.headers.get("Referer")
    
    if not referer and client_key != EXPECTED_API_KEY:
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json() or {}
    name = data.get("name", "Danışan")
    birth_date = data.get("birth_date", "1995-05-15")
    birth_time = data.get("birth_time", "14:30")
    user_query = data.get("query", "Genel harita analizi ve potansiyeller.")

    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return jsonify({"error": "OPENAI_API_KEY eksik."}), 500

        y, m, d = map(int, birth_date.split("-"))
        h, mn = map(int, birth_time.split(":"))

        natal_chart = astro_engine.calculate_natal_chart(y, m, d, h, mn)

        astrolog_agent = Agent(
            role="Kıdemli Mistik Astrolog ve Doğum Haritası Yorumcusu",
            goal="Swiss Ephemeris verilerini derin mistik sembolizmle kişiye özel yorumlamak.",
            backstory="Sen Mystic Thread Studio'nun en tecrübeli astrologusun. Gezegen konumlarını analiz eder, danışanın ruhsal potansiyelini açıklarsın.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        task_interpretation = Task(
            description=f"Danışan: {name}\nHarita Verisi: {natal_chart}\nSoru: '{user_query}'\n\nDetaylı doğum haritası ve gelecek potansiyelleri analizi yaz.",
            expected_output="Derin mistik doğum haritası analizi.",
            agent=astrolog_agent
        )

        crew = Crew(agents=[astrolog_agent], tasks=[task_interpretation], process=Process.sequential, verbose=False)
        crew.kickoff()

        prompt_desc = f"astrological natal chart art, {natal_chart['ascendant']['sign']} ascendant, glowing constellation background, 8k"
        try:
            client = OpenAI(api_key=openai_key)
            img_res = client.images.generate(model="dall-e-3", prompt=prompt_desc, n=1, size="1024x1024")
            generated_image_url = img_res.data[0].url
        except Exception:
            encoded_prompt = urllib.parse.quote(prompt_desc)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        return jsonify({
            "natal_chart_data": natal_chart,
            "astrology_interpretation": str(task_interpretation.output),
            "generated_image_url": generated_image_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ENDPOINT 3: TAROT OKUMASI
@app.route("/analyze_tarot", methods=["POST"])
def analyze_tarot():
    client_key = request.headers.get("X-API-KEY")
    referer = request.headers.get("Referer")
    
    if not referer and client_key != EXPECTED_API_KEY:
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json() or {}
    cards = data.get("cards", ["The Fool", "The Tower", "The Star"])
    user_query = data.get("query", "Genel yaşam tavsiyesi")

    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return jsonify({"error": "OPENAI_API_KEY eksik."}), 500

        tarot_agent = Agent(
            role="Kıdemli Tarot Üstadı ve Mistik Yorumcu",
            goal="Çekilen tarot kartlarının sembolik ve psikolojik anlamlarını harmanlayarak kişiye özel derin okuma yapmak.",
            backstory="Sen yüzyıllık tarot geleneğini modern psikoloji ve sezgiyle harmanlayan bilge bir tarot üstadısın.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        task_tarot = Task(
            description=f"Çekilen Kartlar: Geçmiş: {cards[0]}, Şimdi: {cards[1]}, Gelecek: {cards[2]}\nSoru: '{user_query}'\n\nBu 3 kartın kombinasyonunu ve danışanın sorusuna yanıtını derinlemesine yorumla.",
            expected_output="3 açılımlı detaylı tarot analizi.",
            agent=tarot_agent
        )

        crew = Crew(agents=[tarot_agent], tasks=[task_tarot], process=Process.sequential, verbose=False)
        crew.kickoff()

        prompt_desc = f"mystical tarot card art featuring {cards[1]} and {cards[2]}, esoteric glowing aesthetic, 8k"
        try:
            client = OpenAI(api_key=openai_key)
            img_res = client.images.generate(model="dall-e-3", prompt=prompt_desc, n=1, size="1024x1024")
            generated_image_url = img_res.data[0].url
        except Exception:
            encoded_prompt = urllib.parse.quote(prompt_desc)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        return jsonify({
            "tarot_interpretation": str(task_tarot.output),
            "generated_image_url": generated_image_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ENDPOINT 4: KAHVE FALI (VISION AI)
@app.route("/analyze_coffee", methods=["POST"])
def analyze_coffee():
    client_key = request.headers.get("X-API-KEY")
    referer = request.headers.get("Referer")
    
    if not referer and client_key != EXPECTED_API_KEY:
        return jsonify({"error": "Unauthorized Access"}), 401

    data = request.get_json() or {}
    image_base64 = data.get("image_base64")
    user_query = data.get("query", "Genel kahve falı okuması")

    if not image_base64:
        return jsonify({"error": "Görsel yüklenmedi."}), 400

    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return jsonify({"error": "OPENAI_API_KEY eksik."}), 500

        client = OpenAI(api_key=openai_key)

        # 1. GPT-4o Vision ile Sembol Analizi
        vision_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Bu bir kahve fincanı fotoğrafı. Telveden oluşan belirgin şekilleri, hayvan, nesne, yol veya sayı sembollerini tespit et ve kısa bir liste olarak yaz."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        detected_symbols = vision_response.choices[0].message.content

        # 2. CrewAI Kahve Falı Yorumlama Ajanı
        coffee_agent = Agent(
            role="Mistik Kahve Falı Yorumcusu",
            goal="Vision modelinin tespit ettiği telve sembollerini geleneksel kahve falı literatürüyle yorumlamak.",
            backstory="Sen geleneksel Türk kahvesi falı geleneğini en ince detayına kadar bilen sezgisel bir falcısın.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        task_coffee = Task(
            description=f"Fincanda Tespit Edilen Semboller: {detected_symbols}\nDanışanın Sorusu: '{user_query}'\n\nBu sembolleri danışanın sorusuna odaklanarak geleneksel mistik dille yorumla.",
            expected_output="Bütünsel ve akıcı kahve falı yorumu.",
            agent=coffee_agent
        )

        crew = Crew(agents=[coffee_agent], tasks=[task_coffee], process=Process.sequential, verbose=False)
        crew.kickoff()

        prompt_desc = "mystical Turkish coffee cup reading art, glowing symbols in coffee grounds, dark aesthetic, 8k"
        try:
            img_res = client.images.generate(model="dall-e-3", prompt=prompt_desc, n=1, size="1024x1024")
            generated_image_url = img_res.data[0].url
        except Exception:
            encoded_prompt = urllib.parse.quote(prompt_desc)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        return jsonify({
            "detected_symbols": detected_symbols,
            "coffee_interpretation": str(task_coffee.output),
            "generated_image_url": generated_image_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)