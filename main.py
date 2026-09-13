import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim

app = FastAPI(title="MYSTIC THREAD STUDIO", version="2.0")

# Geocoding servisi
geolocator = Nominatim(user_agent="mystic_thread_studio")

# Request Modeli
class AstroRequest(BaseModel):
    name: Optional[str] = "Danışan"
    birth_date: str
    birth_time: str
    country: Optional[str] = "Türkiye"
    city: str
    district: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    question: Optional[str] = ""

@app.post("/analyze_astro")
async def analyze_astro(req: AstroRequest):
    try:
        lat = req.latitude
        lng = req.longitude

        # Enlem/Boylam boş geldiyse backend tarafında garantiye al
        if lat is None or lng is None:
            location_query = f"{req.district}, {req.city}, {req.country}".strip(", ")
            location = geolocator.geocode(location_query)
            if location:
                lat = location.latitude
                lng = location.longitude
            else:
                city_query = f"{req.city}, {req.country}".strip(", ")
                city_loc = geolocator.geocode(city_query)
                if city_loc:
                    lat = city_loc.latitude
                    lng = city_loc.longitude
                else:
                    lat, lng = 41.0082, 28.9784

        # Tarih & Saat Formatlama
        date_parts = req.birth_date.replace("/", ".").replace("-", ".").split(".")
        day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

        time_parts = req.birth_time.split(":")
        hour, minute = int(time_parts[0]), int(time_parts[1])

        # UTC Dönüşümü (Türkiye varsayılan UTC+3)
        utc_hour = hour - 3 + (minute / 60.0)

        # Swiss Ephemeris Hesaplaması
        julian_day = swe.julday(year, month, day, utc_hour)

        planets = {
            "Güneş": round(swe.calc_ut(julian_day, swe.SUN)[0][0], 2),
            "Ay": round(swe.calc_ut(julian_day, swe.MOON)[0][0], 2),
            "Merkür": round(swe.calc_ut(julian_day, swe.MERCURY)[0][0], 2),
            "Venüs": round(swe.calc_ut(julian_day, swe.VENUS)[0][0], 2),
            "Mars": round(swe.calc_ut(julian_day, swe.MARS)[0][0], 2),
            "Jüpiter": round(swe.calc_ut(julian_day, swe.JUPITER)[0][0], 2),
            "Satürn": round(swe.calc_ut(julian_day, swe.SATURN)[0][0], 2),
            "Uranüs": round(swe.calc_ut(julian_day, swe.URANUS)[0][0], 2),
            "Neptün": round(swe.calc_ut(julian_day, swe.NEPTUNE)[0][0], 2),
            "Plüton": round(swe.calc_ut(julian_day, swe.PLUTO)[0][0], 2),
        }

        # Ev Yükseklikleri & Yükselen Burç (Placidus)
        houses, ascmc = swe.houses(julian_day, lat, lng, b'P')
        ascendant_degree = round(ascmc[0], 2)

        zodiac_signs = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", 
                        "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
        asc_sign = zodiac_signs[int(ascendant_degree // 30)]

        analysis_text = f"""
        <h3>Harita Analizi ({req.name})</h3>
        <p><strong>Yükselen Burç:</strong> {ascendant_degree}° {asc_sign}</p>
        <p><strong>Hesaplanan Konum:</strong> {req.district} / {req.city} ({req.country}) - Enlem: {lat}, Boylam: {lng}</p>
        <hr>
        <h4>Gezegen Konumları:</h4>
        <ul>
            {"".join([f"<li><strong>{planet}:</strong> {deg}°</li>" for planet, deg in planets.items()])}
        </ul>
        <hr>
        <p><strong>Odaklanılan Konu Analizi:</strong> "{req.question}" sorunuz doğrultusunda haritanızdaki açısal etkiler potansiyelinizin yüksek olduğunu göstermektedir.</p>
        """

        return {
            "status": "success",
            "name": req.name,
            "ascendant": f"{ascendant_degree}° {asc_sign}",
            "coordinates": {"lat": lat, "lng": lng},
            "planets": planets,
            "analysis": analysis_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hesaplama hatası: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MYSTIC THREAD STUDIO</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; color: #f8fafc; }
            .form-control { background-color: #0f172a; border: 1px solid #334155; color: #f8fafc; }
            .form-control:focus { background-color: #0f172a; color: #fff; border-color: #6366f1; box-shadow: none; }
            .btn-primary { background-color: #6366f1; border: none; font-weight: 600; padding: 12px; }
            .btn-primary:hover { background-color: #4f46e5; }
            .nav-tabs .nav-link { color: #94a3b8; border: none; }
            .nav-tabs .nav-link.active { background-color: transparent; color: #818cf8; border-bottom: 2px solid #818cf8; font-weight: bold; }
        </style>
    </head>
    <body class="container py-4">

        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-indigo">✨ MYSTIC THREAD STUDIO</h2>
                <p class="text-muted mb-0">Holding Otonom Ajan Konsolu | Astroloji, Tarot & Kahve Falı</p>
            </div>
            <span class="badge bg-success px-3 py-2">Sistem Canlıda</span>
        </div>

        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <a class="nav-link active" href="#">Swiss Ephemeris Astroloji</a>
            </li>
        </ul>

        <div class="card p-4">
            <h4 class="mb-4">Doğum Haritası ve Mistik Analiz İsteği</h4>
            
            <form id="astroForm" onsubmit="handleAstroSubmit(event)">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Ad Soyad / Danışan</label>
                        <input type="text" id="astroNameInput" class="form-control" value="Danışan" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum Tarihi</label>
                        <input type="text" id="astroDateInput" class="form-control" value="15.05.1995" placeholder="GG.AA.YYYY" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum Saati</label>
                        <input type="text" id="astroTimeInput" class="form-control" value="14:30" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum Ülkesi</label>
                        <input type="text" id="astroCountryInput" class="form-control" value="Türkiye" onblur="fetchCoordinates()" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum İli (Şehir)</label>
                        <input type="text" id="astroCityInput" class="form-control" value="İstanbul" onblur="fetchCoordinates()" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Doğum İlçesi</label>
                        <input type="text" id="astroDistrictInput" class="form-control" value="Kadıköy" onblur="fetchCoordinates()" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Enlem (Otomatik Güncellenir)</label>
                        <input type="text" id="astroLatInput" class="form-control" placeholder="Şehir/İlçe girince otomatik dolar">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Boylam (Otomatik Güncellenir)</label>
                        <input type="text" id="astroLngInput" class="form-control" placeholder="Şehir/İlçe girince otomatik dolar">
                    </div>
                </div>

                <div class="mb-4">
                    <label class="form-label">Odaklanılacak Soru / Konu</label>
                    <textarea id="astroQueryInput" class="form-control" rows="3">Kariyer ve potansiyel fırsatlarım yönünde potansiyelim nedir?</textarea>
                </div>

                <button type="submit" id="astroSubmitBtn" class="btn btn-primary w-100">
                    <span id="astroBtnText">Swiss Ephemeris Haritasını Çıkar ve Analiz Et</span>
                    <span id="astroBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true"></span>
                </button>
            </form>

            <div id="resultCard" class="mt-4 p-3 rounded d-none" style="background-color: #0f172a; border: 1px solid #334155;">
                <h5 class="text-indigo">Analiz Sonucu</h5>
                <div id="astroResultBox"></div>
            </div>
        </div>

        <script>
        // Şehir veya İlçe değiştiğinde koordinatları anında kutulara dolduran fonksiyon
        async function fetchCoordinates() {
            const country = document.getElementById("astroCountryInput")?.value.trim() || "Türkiye";
            const city = document.getElementById("astroCityInput")?.value.trim() || "";
            const district = document.getElementById("astroDistrictInput")?.value.trim() || "";

            if (!city) return;

            const queryLocation = `${district} ${city} ${country}`.trim();
            try {
                const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryLocation)}`);
                const geoData = await geoRes.json();

                if (geoData && geoData.length > 0) {
                    document.getElementById("astroLatInput").value = parseFloat(geoData[0].lat).toFixed(4);
                    document.getElementById("astroLngInput").value = parseFloat(geoData[0].lon).toFixed(4);
                } else {
                    // Sadece Şehir dene
                    const fallbackRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + " " + country)}`);
                    const fallbackData = await fallbackRes.json();
                    if (fallbackData && fallbackData.length > 0) {
                        document.getElementById("astroLatInput").value = parseFloat(fallbackData[0].lat).toFixed(4);
                        document.getElementById("astroLngInput").value = parseFloat(fallbackData[0].lon).toFixed(4);
                    }
                }
            } catch (err) {
                console.warn("Otomatik koordinat alma hatası:", err);
            }
        }

        // Sayfa ilk yüklendiğinde varsayılan değerler için (İstanbul/Kadıköy) koordinat çek
        window.addEventListener("DOMContentLoaded", () => {
            fetchCoordinates();
        });

        async function handleAstroSubmit(event) {
            // Sayfanın yenilenip atmasını engeller
            if (event) event.preventDefault();

            const btnText = document.getElementById("astroBtnText");
            const btnSpinner = document.getElementById("astroBtnSpinner");
            const submitBtn = document.getElementById("astroSubmitBtn");
            const resultCard = document.getElementById("resultCard");
            const resultBox = document.getElementById("astroResultBox");

            if (submitBtn) submitBtn.disabled = true;
            if (btnText) btnText.innerText = "Konum ve Harita Hesaplanıyor...";
            if (btnSpinner) btnSpinner.classList.remove("d-none");

            try {
                const country = document.getElementById("astroCountryInput")?.value.trim() || "Türkiye";
                const city = document.getElementById("astroCityInput")?.value.trim() || "";
                const district = document.getElementById("astroDistrictInput")?.value.trim() || "";
                
                let latVal = document.getElementById("astroLatInput")?.value.trim();
                let lngVal = document.getElementById("astroLngInput")?.value.trim();

                let lat = latVal ? parseFloat(latVal.replace(",", ".")) : null;
                let lng = lngVal ? parseFloat(lngVal.replace(",", ".")) : null;

                // Kutu boş kalmışsa gönderim anında tekrar dene
                if (lat === null || lng === null) {
                    const queryLocation = `${district} ${city} ${country}`.trim();
                    const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryLocation)}`);
                    const geoData = await geoRes.json();

                    if (geoData && geoData.length > 0) {
                        lat = parseFloat(geoData[0].lat);
                        lng = parseFloat(geoData[0].lon);
                    }
                }

                const payload = {
                    name: document.getElementById("astroNameInput")?.value || "Danışan",
                    birth_date: document.getElementById("astroDateInput")?.value || "",
                    birth_time: document.getElementById("astroTimeInput")?.value || "",
                    country: country,
                    city: city,
                    district: district,
                    latitude: lat,
                    longitude: lng,
                    question: document.getElementById("astroQueryInput")?.value || ""
                };

                const response = await fetch("/analyze_astro", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`Sunucu Hatası: ${response.status}`);
                }

                const data = await response.json();
                
                if (resultCard && resultBox) {
                    resultCard.classList.remove("d-none");
                    resultBox.innerHTML = data.analysis;
                }

            } catch (err) {
                console.error("Astro Analiz Hatası:", err);
                alert("Analiz sırasında bir hata oluştu: " + err.message);
            } finally {
                resetAstroButton();
            }
        }

        function resetAstroButton() {
            const btnText = document.getElementById("astroBtnText");
            const btnSpinner = document.getElementById("astroBtnSpinner");
            const submitBtn = document.getElementById("astroSubmitBtn");
            
            if (submitBtn) submitBtn.disabled = false;
            if (btnText) btnText.innerText = "Swiss Ephemeris Haritasını Çıkar ve Analiz Et";
            if (btnSpinner) btnSpinner.classList.add("d-none");
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)