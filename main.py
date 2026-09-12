import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("X_API_KEY", "mistik-secret-key-2026")

# Web Dashboard HTML Arayüzü
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mistik Ajan Holding - Komut Merkezi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
        .btn-primary { background-color: #6366f1; border: none; font-weight: 600; padding: 12px; }
        .btn-primary:hover { background-color: #4f46e5; }
        .form-control { background-color: #0f172a; border: 1px solid #334155; color: #f8fafc; }
        .form-control:focus { background-color: #0f172a; color: #f8fafc; border-color: #6366f1; box-shadow: none; }
        .result-box { background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 16px; white-space: pre-wrap; font-size: 0.95rem; line-height: 1.6; }
        .badge-agent { background-color: #312e81; color: #a5b4fc; border: 1px solid #4338ca; }
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="d-flex align-items-center justify-content-between mb-4 pb-3 border-bottom border-secondary">
                    <div>
                        <h2 class="fw-bold mb-1" style="color: #818cf8;">MİSTİK AJAN HOLDİNG</h2>
                        <p class="text-secondary mb-0">Otonom Yapay Zeka Ajansı Kontrol Merkezi | v28.0-Stable</p>
                    </div>
                    <span class="badge bg-success px-3 py-2">Sistem Canlıda</span>
                </div>

                <div class="card p-4 mb-4 shadow">
                    <h5 class="mb-3 text-light">Yeni Görev & Strateji İsteği</h5>
                    <form id="analyzeForm">
                        <div class="mb-3">
                            <textarea id="queryInput" class="form-control" rows="3" placeholder="Örn: Mistik Ajan Holding için 2026 sosyal medya ve büyüme stratejisi oluştur..." required>Mistik Ajan Holding için 2026 sosyal medya ve büyüme stratejisi oluştur.</textarea>
                        </div>
                        <button type="submit" id="submitBtn" class="btn btn-primary w-100">
                            <span id="btnText">Otonom Ajanları Çalıştır</span>
                            <span id="btnSpinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                        </button>
                    </form>
                </div>

                <div id="resultsContainer" class="d-none">
                    <div class="card p-4 mb-4 shadow">
                        <div class="d-flex align-items-center mb-3">
                            <span class="badge badge-agent me-2 px-3 py-2">İstihbarat & Strateji Direktörlüğü</span>
                        </div>
                        <div id="stratResult" class="result-box text-slate-200"></div>
                    </div>

                    <div class="card p-4 mb-4 shadow">
                        <div class="d-flex align-items-center mb-3">
                            <span class="badge badge-agent me-2 px-3 py-2">Kreatif & Video Kurgu Yönetmenliği</span>
                        </div>
                        <div id="creativeResult" class="result-box text-slate-200"></div>
                    </div>

                    <div class="card p-4 shadow">
                        <h5 class="mb-3 text-light">Üretilen Kapak / Konsept Görseli</h5>
                        <div class="text-center">
                            <img id="generatedImg" src="" class="img-fluid rounded border border-secondary mb-3 d-none" style="max-height: 400px;" alt="Üretilen Konsept">
                            <br>
                            <a id="imgLink" href="#" target="_blank" class="btn btn-outline-info btn-sm">Görseli Yüksek Çözünürlükte Aç</a>
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

            btnText.innerText = "Ajanlar Analiz Yapıyor (Lütfen Bekleyin)...";
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
                    alert("Hata Oluştu: " + response.statusText);
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

# Mevcut /analyze endpoint kodlarınızın devamı buradadır...