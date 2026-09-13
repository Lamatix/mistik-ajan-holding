import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim

app = FastAPI(title="MYSTIC THREAD STUDIO", version="3.0")

geolocator = Nominatim(user_agent="mystic_thread_studio")

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
    lang: Optional[str] = "tr"

@app.post("/analyze_astro")
async def analyze_astro(req: AstroRequest):
    try:
        lat = req.latitude
        lng = req.longitude

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

        date_parts = req.birth_date.replace("/", ".").replace("-", ".").split(".")
        day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

        time_parts = req.birth_time.split(":")
        hour, minute = int(time_parts[0]), int(time_parts[1])

        utc_hour = hour - 3 + (minute / 60.0)
        julian_day = swe.julday(year, month, day, utc_hour)

        planets = {
            "Güneş / Sun": round(swe.calc_ut(julian_day, swe.SUN)[0][0], 2),
            "Ay / Moon": round(swe.calc_ut(julian_day, swe.MOON)[0][0], 2),
            "Merkür / Mercury": round(swe.calc_ut(julian_day, swe.MERCURY)[0][0], 2),
            "Venüs / Venus": round(swe.calc_ut(julian_day, swe.VENUS)[0][0], 2),
            "Mars / Mars": round(swe.calc_ut(julian_day, swe.MARS)[0][0], 2),
            "Jüpiter / Jupiter": round(swe.calc_ut(julian_day, swe.JUPITER)[0][0], 2),
            "Satürn / Saturn": round(swe.calc_ut(julian_day, swe.SATURN)[0][0], 2),
            "Uranüs / Uranus": round(swe.calc_ut(julian_day, swe.URANUS)[0][0], 2),
            "Neptün / Neptune": round(swe.calc_ut(julian_day, swe.NEPTUNE)[0][0], 2),
            "Plüton / Pluto": round(swe.calc_ut(julian_day, swe.PLUTO)[0][0], 2),
        }

        houses, ascmc = swe.houses(julian_day, lat, lng, b'P')
        ascendant_degree = round(ascmc[0], 2)

        zodiac_signs = ["Koç / Aries", "Boğa / Taurus", "İkizler / Gemini", "Yengeç / Cancer", 
                        "Aslan / Leo", "Başak / Virgo", "Terazi / Libra", "Akrep / Scorpio", 
                        "Yay / Sagittarius", "Oğlak / Capricorn", "Kova / Aquarius", "Balık / Pisces"]
        asc_sign = zodiac_signs[int(ascendant_degree // 30)]

        analysis_text = f"""
        <h3>Harita Analizi ({req.name})</h3>
        <p><strong>Yükselen / Ascendant:</strong> {ascendant_degree}° {asc_sign}</p>
        <p><strong>Konum / Location:</strong> {req.district} / {req.city} ({req.country}) - Enlem: {lat}, Boylam: {lng}</p>
        <hr>
        <h4>Gezegen Konumları / Planetary Positions:</h4>
        <ul>
            {"".join([f"<li><strong>{planet}:</strong> {deg}°</li>" for planet, deg in planets.items()])}
        </ul>
        <hr>
        <p><strong>Analiz / Analysis:</strong> "{req.question}"</p>
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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
            .form-control, .form-select { background-color: #0f172a; border: 1px solid #334155; color: #f8fafc; }
            .form-control:focus, .form-select:focus { background-color: #0f172a; color: #fff; border-color: #6366f1; box-shadow: none; }
            .btn-primary { background-color: #6366f1; border: none; font-weight: 600; padding: 12px; }
            .btn-primary:hover { background-color: #4f46e5; }
        </style>
    </head>
    <body class="container py-4">

        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-indigo">✨ MYSTIC THREAD STUDIO</h2>
                <p class="text-muted mb-0" id="subTitle">Holding Otonom Ajan Konsolu</p>
            </div>
            <div class="d-flex align-items-center gap-2">
                <select id="langSelect" class="form-select form-select-sm" onchange="changeLanguage()">
                    <option value="tr" selected>Türkçe</option>
                    <option value="en">English</option>
                    <option value="zh">中文 (Chinese)</option>
                    <option value="hi">हिन्दी (Hindi)</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="ar">العربية (Arabic)</option>
                    <option value="bn">বাংলা (Bengali)</option>
                    <option value="pt">Português</option>
                    <option value="ru">Русский</option>
                    <option value="ur">اردو (Urdu)</option>
                    <option value="de">Deutsch</option>
                    <option value="it">Italiano</option>
                </select>
                <span class="badge bg-success px-3 py-2">ONLINE</span>
            </div>
        </div>

        <div class="card p-4">
            <h4 class="mb-4" id="formTitle">Doğum Haritası ve Mistik Analiz İsteği</h4>
            
            <form id="astroForm" onsubmit="handleAstroSubmit(event)">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblTitle">Ad Soyad / Danışan</label>
                        <input type="text" id="astroNameInput" class="form-control" value="Danışan" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblDate">Doğum Tarihi</label>
                        <input type="text" id="astroDateInput" class="form-control" value="15.05.1995" placeholder="GG.AA.YYYY" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblTime">Doğum Saati</label>
                        <input type="text" id="astroTimeInput" class="form-control" value="14:30" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblCountry">Doğum Ülkesi</label>
                        <input type="text" id="astroCountryInput" class="form-control" value="Türkiye" onblur="fetchCoordinates()" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblCity">Doğum İli (Şehir)</label>
                        <input type="text" id="astroCityInput" class="form-control" value="İstanbul" onblur="fetchCoordinates()" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label" id="lblDistrict">Doğum İlçesi</label>
                        <input type="text" id="astroDistrictInput" class="form-control" value="Kadıköy" onblur="fetchCoordinates()" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label" id="lblLat">Enlem (Otomatik)</label>
                        <input type="text" id="astroLatInput" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label" id="lblLng">Boylam (Otomatik)</label>
                        <input type="text" id="astroLngInput" class="form-control">
                    </div>
                </div>

                <div class="mb-4">
                    <label class="form-label" id="lblQuery">Odaklanılacak Soru / Konu</label>
                    <textarea id="astroQueryInput" class="form-control" rows="3">Kariyer ve potansiyel fırsatlarım yönünde potansiyelim nedir?</textarea>
                </div>

                <button type="submit" id="astroSubmitBtn" class="btn btn-primary w-100">
                    <span id="astroBtnText">Swiss Ephemeris Haritasını Çıkar ve Analiz Et</span>
                    <span id="astroBtnSpinner" class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true"></span>
                </button>
            </form>

            <div id="resultCard" class="mt-4 p-3 rounded d-none" style="background-color: #0f172a; border: 1px solid #334155;">
                <h5 class="text-indigo" id="resultTitle">Analiz Sonucu</h5>
                <div id="astroResultBox"></div>
            </div>
        </div>

        <script>
        const i18n = {
            tr: {
                subTitle: "Holding Otonom Ajan Konsolu",
                formTitle: "Doğum Haritası ve Mistik Analiz İsteği",
                lblTitle: "Ad Soyad / Danışan",
                lblDate: "Doğum Tarihi",
                lblTime: "Doğum Saati",
                lblCountry: "Doğum Ülkesi",
                lblCity: "Doğum İli (Şehir)",
                lblDistrict: "Doğum İlçesi",
                lblLat: "Enlem (Otomatik)",
                lblLng: "Boylam (Otomatik)",
                lblQuery: "Odaklanılacak Soru / Konu",
                btnText: "Swiss Ephemeris Haritasını Çıkar ve Analiz Et",
                resultTitle: "Analiz Sonucu"
            },
            en: {
                subTitle: "Holding Autonomous Agent Console",
                formTitle: "Birth Chart & Mystic Analysis Request",
                lblTitle: "Full Name / Client",
                lblDate: "Date of Birth",
                lblTime: "Time of Birth",
                lblCountry: "Country of Birth",
                lblCity: "City of Birth",
                lblDistrict: "District of Birth",
                lblLat: "Latitude (Auto)",
                lblLng: "Longitude (Auto)",
                lblQuery: "Question / Focus Area",
                btnText: "Generate Swiss Ephemeris Chart & Analyze",
                resultTitle: "Analysis Result"
            },
            de: {
                subTitle: "Konsole für Autonome Agenten",
                formTitle: "Geburtshoroskop & Mystische Analyse",
                lblTitle: "Vollständiger Name",
                lblDate: "Geburtsdatum",
                lblTime: "Geburtszeit",
                lblCountry: "Geburtsland",
                lblCity: "Geburtsstadt",
                lblDistrict: "Bezirk",
                lblLat: "Breitengrad (Auto)",
                lblLng: "Längengrad (Auto)",
                lblQuery: "Frage / Fokusbereich",
                btnText: "Horoskop berechnen & analysieren",
                resultTitle: "Analyseergebnis"
            },
            it: {
                subTitle: "Console per Agenti Autonomi",
                formTitle: "Carta Natale e Analisi Mistica",
                lblTitle: "Nome e Cognome",
                lblDate: "Data di Nascita",
                lblTime: "Ora di Nascita",
                lblCountry: "Paese di Nascita",
                lblCity: "Città di Nascita",
                lblDistrict: "Distretto",
                lblLat: "Latitudine (Auto)",
                lblLng: "Longitudine (Auto)",
                lblQuery: "Domanda / Focus",
                btnText: "Calcola Grafico ed Analizza",
                resultTitle: "Risultato dell'Analisi"
            },
            es: {
                subTitle: "Consola de Agentes Autónomos",
                formTitle: "Carta Natal y Análisis Místico",
                lblTitle: "Nombre Completo",
                lblDate: "Fecha de Nacimiento",
                lblTime: "Hora de Nacimiento",
                lblCountry: "País de Nacimiento",
                lblCity: "Ciudad de Nacimiento",
                lblDistrict: "Distrito",
                lblLat: "Latitud (Auto)",
                lblLng: "Longitud (Auto)",
                lblQuery: "Pregunta / Enfoque",
                btnText: "Generar Carta y Analizar",
                resultTitle: "Resultado del Análisis"
            },
            fr: {
                subTitle: "Console d'Agents Autonomes",
                formTitle: "Thème Astral et Analyse Mystique",
                lblTitle: "Nom Complet",
                lblDate: "Date de Naissance",
                lblTime: "Heure de Naissance",
                lblCountry: "Pays de Naissance",
                lblCity: "Ville de Naissance",
                lblDistrict: "District",
                lblLat: "Latitude (Auto)",
                lblLng: "Longitude (Auto)",
                lblQuery: "Question / Sujet",
                btnText: "Générer la Carte et Analyser",
                resultTitle: "Résultat de l'Analyse"
            }
        };

        function changeLanguage() {
            const lang = document.getElementById("langSelect").value;
            const dict = i18n[lang] || i18n["en"];
            
            for (const key in dict) {
                const el = document.getElementById(key);
                if (el) el.innerText = dict[key];
            }
        }

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
                    const fallbackRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + " " + country)}`);
                    const fallbackData = await fallbackRes.json();
                    if (fallbackData && fallbackData.length > 0) {
                        document.getElementById("astroLatInput").value = parseFloat(fallbackData[0].lat).toFixed(4);
                        document.getElementById("astroLngInput").value = parseFloat(fallbackData[0].lon).toFixed(4);
                    }
                }
            } catch (err) {
                console.warn("Geo Error:", err);
            }
        }

        window.addEventListener("DOMContentLoaded", () => {
            fetchCoordinates();
        });

        async function handleAstroSubmit(event) {
            if (event) event.preventDefault();

            const btnText = document.getElementById("astroBtnText");
            const btnSpinner = document.getElementById("astroBtnSpinner");
            const submitBtn = document.getElementById("astroSubmitBtn");
            const resultCard = document.getElementById("resultCard");
            const resultBox = document.getElementById("astroResultBox");

            if (submitBtn) submitBtn.disabled = true;
            if (btnSpinner) btnSpinner.classList.remove("d-none");

            try {
                const country = document.getElementById("astroCountryInput")?.value.trim() || "Türkiye";
                const city = document.getElementById("astroCityInput")?.value.trim() || "";
                const district = document.getElementById("astroDistrictInput")?.value.trim() || "";
                
                let latVal = document.getElementById("astroLatInput")?.value.trim();
                let lngVal = document.getElementById("astroLngInput")?.value.trim();

                let lat = latVal ? parseFloat(latVal.replace(",", ".")) : null;
                let lng = lngVal ? parseFloat(lngVal.replace(",", ".")) : null;

                const payload = {
                    name: document.getElementById("astroNameInput")?.value || "Danışan",
                    birth_date: document.getElementById("astroDateInput")?.value || "",
                    birth_time: document.getElementById("astroTimeInput")?.value || "",
                    country: country,
                    city: city,
                    district: district,
                    latitude: lat,
                    longitude: lng,
                    question: document.getElementById("astroQueryInput")?.value || "",
                    lang: document.getElementById("langSelect").value
                };

                const response = await fetch("/analyze_astro", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error(`Server Error: ${response.status}`);

                const data = await response.json();
                
                if (resultCard && resultBox) {
                    resultCard.classList.remove("d-none");
                    resultBox.innerHTML = data.analysis;
                }

            } catch (err) {
                console.error("Astro Error:", err);
                alert("Error: " + err.message);
            } finally {
                if (submitBtn) submitBtn.disabled = false;
                if (btnSpinner) btnSpinner.classList.add("d-none");
            }
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)