import os
import urllib.parse
from flask import Flask, request, jsonify, render_template_string
from crewai import Agent, Task, Crew, Process
from openai import OpenAI

app = Flask(__name__)

# Konfigürasyon ve Güvenlik
EXPECTED_API_KEY = os.environ.get("X_API_KEY", "mistik-secret-key-2026")

# Web Dashboard HTML Arayüzü (Mystic Thread Studio Markalı & Beyaz Metin Odaklı)
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mystic Thread Studio - Komut Merkezi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background-color: #0f172a; 
            color: #ffffff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .card { 
            background-color: #1e293b; 
            border: 1px solid #334155; 
            border-radius: 12px; 
            color: #ffffff;
        }
        .btn-primary { 
            background-color: #6366f1; 
            border: none; 
            font-weight: 600; 
            padding: 12px; 
        }
        .btn-primary:hover { 
            background-color: #4f46e5; 
        }
        .form-control { 
            background-color: #0f172a; 
            border: 1px solid #334155; 
            color: #ffffff !important; 
        }
        .form-control:focus { 
            background-color: #0f172a; 
            color: #ffffff !important; 
            border-color: #6366f1; 
            box-shadow: none; 
        }
        /* YAZI OKUNABİLİRLİĞİ İÇİN TAM BEYAZ (#ffffff) SEÇİLDİ */
        .result-box { 
            background-color: #0f172a; 
            border: 1px solid #334155; 
            border-radius: 8px; 
            padding: 20px; 
            white-space: pre-wrap; 
            font-size: 0.98rem; 
            line-height: 1.7; 
            color: #ffffff !important; 
            font-weight: 400;
        }
        .badge-agent { 
            background-color: #312e81; 
            color: #ffffff; 
            border: 1px solid #4338ca; 
            font-size: 0.9rem;
            padding: 8px 14px;
        }
        .logo-glow { 
            filter: drop-shadow(0px 0px 8px rgba(99, 102, 241, 0.6)); 
        }
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
                                <defs>
                                    <linearGradient id="threadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stop-color="#818cf8" />
                                        <stop offset="50%" stop-color="#c084fc" />
                                        <stop offset="100%" stop-color="#38bdf8" />
                                    </linearGradient>
                                </defs>
                                <circle cx="50" cy="50" r="44" stroke="url(#threadGrad)" stroke-width="2.5" stroke-dasharray="6 4" opacity="0.6" />
                                <path d="M 25 65 C 35 35, 65 35, 75 65 C 65 85, 35 85, 25 65 Z" stroke="url(#threadGrad)" stroke-width="4" fill="none" stroke-linecap="round" />
                                <path d="M 25 35 C 35 65, 65 65, 75 35 C 65 15, 35 15, 25 35 Z" stroke="url(#threadGrad)" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.8" />
                                <path d="M 50 28 L 53 45 L 70 48 L 53 51 L 50 68 L 47 51 L 30 48 L 47 45 Z" fill="#ffffff" />
                                <circle cx="50" cy="48" r="3" fill="#818cf8" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="fw-bold mb-0" style="color: #818cf8; letter-spacing: 0.5px;">MYSTIC THREAD STUDIO</h2>
                            <p class="text-secondary mb-0" style="font-size: 0.9rem;">Otonom Yapay Zeka Ajansı Kontrol Merkezi | v28.0-Stable</p>
                        </div>
                    </div>
                    <span class="badge bg-success px-3 py-2">Sistem Canlıda</span>
                </div>

                <!-- Input Form -->
                <div class="card p-4 mb-4 shadow">
                    <h5 class="mb-3 text-light">Yeni Görev & Strateji İsteği</h5>
                    <form id="analyzeForm">
                        <div class="mb-3">
                            <textarea id="queryInput" class="form-control" rows="3" placeholder="Örn: Mystic Thread Studio için 2026 sosyal medya ve büyüme stratejisi oluştur..." required>Mystic Thread Studio için 2026 sosyal medya ve büyüme stratejisi oluştur.</textarea>
                        </div>
                        <button type="submit" id="submitBtn" class="btn btn-primary w-100">
                            <span id="btnText">Otonom Ajanları Çalıştır</span>
                            <span id="btnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                        </button>
                    </form>
                </div>

                <!-- Results Section -->
                <div id="resultsContainer" class="d-none">
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

                    <div class="card p-4 shadow">
                        <h5 class="mb-3 text-light">Konsepte Özel Üretilen Görsel</h5>
                        <div class="text-center">
                            <img id="generatedImg" src="" class="img-fluid rounded border border-secondary mb-3 d-none" style="max-height: 450px; object-fit: cover;" alt="Konsept Görseli">
                            <br>
                            <a id="imgLink" href="#" target="_blank" class="btn btn-outline-info btn-sm px-4 py-2">Görseli Yüksek Çözünürlükte Aç</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('analyzeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('queryInput').value;
            const submitBtn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            const resultsContainer = document.getElementById('resultsContainer');

            btnText.innerText = "Ajanlar Analiz ve Görsel Üretiyor...";
            btnSpinner.classList.remove('d-none');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-KEY': 'mistik-secret-key-2026'
                    },
                    body: JSON.stringify({ query: query })
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    document.getElementById('stratResult').innerText = data.intelligence_and_strategy || "İçerik üretilemedi.";
                    document.getElementById('creativeResult').innerText = data.creative_and_video_guide || "İçerik üretilemedi.";
                    
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
                btnText.innerText = "Otonom Ajanları Çalıştır";
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
        return jsonify({"error": "Unauthorized Access - Invalid X-API-KEY"}), 401

    data = request.get_json() or {}
    user_query = data.get("query", "Mystic Thread Studio için 2026 büyüme stratejisi oluştur.")

    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return jsonify({"error": "OPENAI_API_KEY environment variable is missing on Render."}), 500

        llm_model = "gpt-4o-mini"

        # Ajan Tanımları
        strategy_agent = Agent(
            role="İstihbarat ve Strateji Direktörü",
            goal="Verilen konu veya ajans için 2026 odaklı stratejik büyüme planı ve pazar analizi hazırlamak.",
            backstory="Sen Mystic Thread Studio'nun en kıdemli stratejistisin. Verileri analiz eder, trendleri yakalar ve en etkili büyüme adımlarını belirlersin.",
            verbose=False,
            allow_delegation=False,
            llm=llm_model
        )

        creative_agent = Agent(
            role="Kreatif ve Video Kurgu Yönetmeni",
            goal="Strateji doğrultusunda yüksek etkileşimli sosyal medya senaryoları, Reels/Shorts konseptleri üretmek.",
            backstory="Sen Mystic Thread Studio'nun kreatif dahi direktörüsün. İzleyiciyi ilk 3 saniyede yakalayan viral video senaryoları ve görsel konseptler tasarlarsın.",
            verbose=False,
            allow_delegation=False,
            llm=llm_model
        )

        task_strategy = Task(
            description=f"Konu: '{user_query}'. Bu konu için 3 maddelik net ve uygulanabilir 2026 büyüme ve içerik stratejisi hazırla.",
            expected_output="3 maddelik detaylı ve profesyonel strateji analizi.",
            agent=strategy_agent
        )

        task_creative = Task(
            description=f"Stratejiye uygun olarak 1 adet viral Instagram Reels/YouTube Shorts senaryosu yaz (Görsel kurgu, ses ve metin dahil). Aynı zamanda üretilecek görsel için İngilizce 1 cümlelik detaylı 'Image Generation Prompt' hazırla.",
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

        # DİNAMİK VE ANLAMLI GÖRSEL ÜRETİMİ
        # Öncelik 1: OpenAI DALL-E 3, Eğer bütçe/yetki hatası verirse -> Öncelik 2: Pollinations AI
        generated_image_url = None
        
        try:
            client = OpenAI(api_key=openai_key)
            dalle_prompt = f"Professional modern visual concept for Mystic Thread Studio, theme: {user_query}, high resolution 8k, cinematic lighting, futuristic digital studio style"
            
            img_res = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt[:1000],  # Max karakter sınırı
                n=1,
                size="1024x1024"
            )
            generated_image_url = img_res.data[0].url
        except Exception as img_err:
            print(f"[UYARI] DALL-E 3 görseli üretilemedi ({img_err}), Pollinations AI servisine geçiliyor...")
            
            # Ücretsiz & Kesintisiz Alternatif (Pollinations Flux/AI Engine)
            fallback_prompt = f"professional visual concept for {user_query}, modern digital agency, dark background, vivid neon elements, 8k resolution"
            encoded_prompt = urllib.parse.quote(fallback_prompt)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&seed=2026"

        response_data = {
            "intelligence_and_strategy": str(task_strategy.output),
            "creative_and_video_guide": str(task_creative.output),
            "generated_image_url": generated_image_url
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)