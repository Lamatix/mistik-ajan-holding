import os
import urllib.parse
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
    <title>Mystic Thread Studio - Astroloji & Mistik Kontrol Merkezi</title>
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
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-10">
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
                            <p class="text-secondary mb-0" style="font-size: 0.9rem;">Swiss Ephemeris Destekli Profesyonel Astroloji Ajanı</p>
                        </div>
                    </div>
                    <span class="badge bg-success px-3 py-2">Sistem Canlıda</span>
                </div>

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
                                <input type="text" id="queryInput" class="form-control" value="Kariyer ve potansiyel fırsatlarım yönünde potansiyelim nedir?" required>
                            </div>
                        </div>
                        <button type="submit" id="submitBtn" class="btn btn-primary w-100">
                            <span id="btnText">Swiss Ephemeris Haritasını Çıkar ve Analiz Et</span>
                            <span id="btnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                        </button>
                    </form>
                </div>

                <div id="resultsContainer" class="d-none">
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

                    <div class="card p-4 shadow">
                        <h5 class="mb-3 text-light">Haritaya Özel Mistik Sembol Görseli</h5>
                        <div class="text-center">
                            <img id="generatedImg" src="" class="img-fluid rounded border border-secondary mb-3 d-none" style="max-height: 450px;" alt="Astroloji Görseli">
                            <br>
                            <a id="imgLink" href="#" target="_blank" class="btn btn-outline-info btn-sm px-4 py-2">Görseli Yüksek Çözünürlükte Aç</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('astroForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('nameInput').value;
            const date = document.getElementById('dateInput').value;
            const time = document.getElementById('timeInput').value;
            const query = document.getElementById('queryInput').value;

            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            const resultsContainer = document.getElementById('resultsContainer');

            btnText.innerText = "Harita Hesaplanıyor & Ajan Yorumluyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-KEY': 'mistik-secret-key-2026'
                    },
                    body: JSON.stringify({ name, birth_date: date, birth_time: time, query })
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    document.getElementById('rawChartResult').innerText = JSON.stringify(data.natal_chart_data, null, 2);
                    document.getElementById('astroResult').innerText = data.astrology_interpretation || "İçerik üretilemedi.";
                    
                    if (data.generated_image_url) {
                        const imgElem = document.getElementById('generatedImg');
                        imgElem.src = data.generated_image_url;
                        imgElem.classList.remove('d-none');
                        document.getElementById('imgLink').href = data.generated_image_url;
                    }

                    resultsContainer.classList.remove('d-none');
                    resultsContainer.scrollIntoView({ behavior: 'smooth' });
                } else {
                    const errData = await response.json();
                    alert("Hata Oluştu (" + response.status + "): " + (errData.error || response.statusText));
                }
            } catch (err) {
                alert("İstek Hatası: " + err.message);
            } finally {
                btnText.innerText = "Swiss Ephemeris Haritasını Çıkar ve Analiz Et";
                btnSpinner.classList.add('d-none');
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_DASHBOARD)

@app.route("/analyze", methods=["POST"])
def analyze():
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

        # Tarih ve saat ayrıştırma
        y, m, d = map(int, birth_date.split("-"))
        h, mn = map(int, birth_time.split(":"))

        # 1. SWISS EPHEMERIS ILE MATEMATİKSEL HESAPLAMA
        natal_chart = astro_engine.calculate_natal_chart(y, m, d, h, mn)

        # 2. CREWAI AJANI İLE MİSTİK YORUMLAMA
        astrolog_agent = Agent(
            role="Kıdemli Mistik Astrolog ve Doğum Haritası Yorumcusu",
            goal="Swiss Ephemeris'ten gelen matematiksel gezegen ve yükselen burç verilerini derin mistik sembolizm ve astrolog psikolojisiyle kişiye özel yorumlamak.",
            backstory="Sen Mystic Thread Studio'nun en tecrübeli astrologusun. Gezegen konumlarını ve açılarını ezbere bilmekle kalmaz, danışanın ruhsal potansiyelini nokta atışı analiz edersin.",
            verbose=False,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )

        task_interpretation = Task(
            description=f"""
Danışan Adı: {name}
Doğum Bilgisi: {birth_date} {birth_time}
Doğum Haritası Verisi (Swiss Ephemeris): {natal_chart}
Danışanın Özel Sorusu: '{user_query}'

Görev:
1. Yükselen burç, Güneş ve Ay burcu kombinasyonunu değerlendir.
2. Öne çıkan gezegen yerleşimlerinin danışanın sorusuyla olan bağlantısını açıkla.
3. Derin, rahatlatıcı ve yapıcı mistik dille 3 ana başlık altında kişiselleştirilmiş analiz yaz.
""",
            expected_output="Detaylı, profesyonel ve ilham verici doğum haritası analizi.",
            agent=astrolog_agent
        )

        crew = Crew(
            agents=[astrolog_agent],
            tasks=[task_interpretation],
            process=Process.sequential,
            verbose=False
        )

        crew.kickoff()

        # Görsel Üretimi (DALL-E 3 / Fallback Pollinations)
        generated_image_url = None
        prompt_desc = f"astrological natal chart art, {natal_chart['ascendant']['sign']} ascendant, mystical esoteric aesthetic, glowing constellation background, 8k"
        
        try:
            client = OpenAI(api_key=openai_key)
            img_res = client.images.generate(
                model="dall-e-3",
                prompt=prompt_desc,
                n=1,
                size="1024x1024"
            )
            generated_image_url = img_res.data[0].url
        except Exception:
            encoded_prompt = urllib.parse.quote(prompt_desc)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"

        response_data = {
            "natal_chart_data": natal_chart,
            "astrology_interpretation": str(task_interpretation.output),
            "generated_image_url": generated_image_url
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)