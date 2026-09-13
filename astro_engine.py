import swisseph as swe
from datetime import datetime

class AstroEngine:
    def __init__(self):
        # Swiss Ephemeris varsayılan hesaplama ayarları
        swe.set_ephe_path('') # Dahili ephemeris kullanımı

    def calculate_natal_chart(self, year, month, day, hour, minute, lat, lon):
        """
        Kullanıcı doğum verilerinden hassas gezegen ve ev konumlarını hesaplar.
        """
        # UTC Zamanına Dönüştürme (Örn: Türkiye için UTC+3 varsayımı)
        # Gelişmiş aşamada pytz ile dinamik zaman dilimi yapılır.
        utc_hour = hour - 3 + (minute / 60.0)
        julian_day = swe.julday(year, month, day, utc_hour)

        # Gezegen Tanımları
        planets = {
            "Güneş": swe.SUN,
            "Ay": swe.MOON,
            "Merkür": swe.MERCURY,
            "Venüs": swe.VENUS,
            "Mars": swe.MARS,
            "Jüpiter": swe.JUPITER,
            "Satürn": swe.SATURN,
            "Uranüs": swe.URANUS,
            "Neptün": swe.NEPTUNE,
            "Plüton": swe.PLUTO
        }

        zodiac_signs = [
            "Koç", "Boğa", "İkizler", "Yengeç", 
            "Aslan", "Başak", "Terazi", "Akrep", 
            "Yay", "Oğlak", "Kova", "Balık"
        ]

        chart_data = {"planets": {}, "houses": {}}

        # 1. Gezegen Konumlarını Hesapla
        for name, planet_id in planets.items():
            res, _ = swe.calc_ut(julian_day, planet_id)
            lon_deg = res[0]
            sign_idx = int(lon_deg // 30)
            degree_in_sign = lon_deg % 30
            
            chart_data["planets"][name] = {
                "sign": zodiac_signs[sign_idx],
                "degree": round(degree_in_sign, 2)
            }

        # 2. Ev Sistemlerini Hesapla (Placidus 'P')
        houses, ascmc = swe.houses(julian_day, lat, lon, b'P')
        ascendant_deg = ascmc[0]
        asc_sign_idx = int(ascendant_deg // 30)
        
        chart_data["ascendant"] = {
            "sign": zodiac_signs[asc_sign_idx],
            "degree": round(ascendant_deg % 30, 2)
        }

        return chart_data

# Test Kullanımı
if __name__ == "__main__":
    engine = AstroEngine()
    # Örnek: 15 Mayıs 1995, Saat 14:30, İstanbul (Enlem: 41.0082, Boylam: 28.9784)
    result = engine.calculate_natal_chart(1995, 5, 15, 14, 30, 41.0082, 28.9784)
    print("Hesaplanan Doğum Haritası Verisi:\n", result)