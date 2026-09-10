import json
import os
import urllib.parse
from functools import wraps
from flask import Flask, Response, request, jsonify
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from openai import OpenAI

app = Flask(__name__)

# ---------------------------------------------------------
# GÜVENLİK VE YAPILANDIRMA
# ---------------------------------------------------------
API_KEY = os.environ.get("HOLDING_API_KEY", "mistik-secret-key-2026")
OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# DuckDuckGo Arama Aracı (CrewAI Uyumlu Sarıcı)
_ddg_search = DuckDuckGoSearchRun()

@tool("Web Search Tool")
def execute_web_search(query: str) -> str:
    """İnternette güncel bilgi, trend veya veri araması yapar."""
    try:
        return _ddg_search.run(query)
    except Exception as e:
        return f"Arama esnasında hata oluştu: {str(e)}"

search_tools = [execute_web_search]

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if os.environ.get("HOLDING_API_KEY"):
            user_key = request.headers.get("X-API-KEY") or request.args.get("api_key")
            if user_key != API_KEY:
                return jsonify({"error": "Yetkisiz Erişim. Geçersiz X-API-KEY."}), 401
        return f(*args, **kwargs)
    return decorated

def create_dalle_image(prompt_text):
    """
    Görsel Üretim Katmanı: DALL-E 3 dener, hata alırsa kesintisiz Pollinations AI kullanır.
    """
    try:
        response = OPENAI_CLIENT.images.generate(
            model="dall-e-3",
            prompt=f"Luxury, esoteric, highly detailed aesthetic artwork: {prompt_text[:200]}",
            size="1024x1024",
            quality="hd",
            n=1,
        )
        if response and hasattr(response, 'data') and len(response.data) > 0:
            return response.data[0].url
    except Exception:
        pass

    clean_prompt = urllib.parse.quote(f"Luxury esoteric mystic artwork, {prompt_text[:200]}")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true"

def run_holding_pipeline(primary_model, secondary_model):
    """
    Ajanları ve görevleri verilen model yetkileriyle çalıştıran ana motor.
    """
    analyst = Agent(
        role="Stratejik Analist ve Piyasa Araştırmacısı",
        goal="Canlı web taraması yaparak en güncel trendleri ve durumları derinlemesine analiz etmek.",
        backstory="Mistik Ajan Holding'in üst düzey istihbarat liderisiniz.",
        tools=search_tools,
        verbose=True,
        allow_delegation=False,
        llm=primary_model
    )

    mystic_analyst = Agent(
        role="Mistik ve Astrolojik Analist",
        goal="Konunun sezgisel, astrolojik ve ezoterik boyutunu derinlemesine incelemek.",
        backstory="Mistik Holding'in ana sezgisel danışmanısınız.",
        verbose=True,
        allow_delegation=False,
        llm=primary_model
    )

    creative_director = Agent(
        role="İçerik ve Senaryo Üreticisi",
        goal="Stratejiyi ve mistik analizi yüksek etkileşimli sosyal medya senaryolarına dönüştürmek.",
        backstory="Kreatif direktörsünüz.",
        verbose=True,
        allow_delegation=False,
        llm=primary_model
    )

    risk_consultant = Agent(
        role="Risk ve Kriz Danışmanı",
        goal="Ana riskleri ve kısıtlamaları tespit etmek.",
        backstory="Holding muhafızısınız.",
        tools=search_tools,
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    finance_strategist = Agent(
        role="Kaynak ve Bütçe Stratejisti",
        goal="Zaman, içerik üretimi ve bütçe verimliliğini planlamak.",
        backstory="Mali uzmansınız.",
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    operations_director = Agent(
        role="Saha ve İcra Direktörü",
        goal="Uygulanabilir 3 adımlık operasyonel eylem planı sunmak.",
        backstory="Pragmatik uygulayıcısınız.",
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    visual_designer = Agent(
        role="Görsel Tasarım Direktörü",
        goal="Lüks ve ezoterik 1 cümlelik İngilizce görsel prompt'u yazmak.",
        backstory="Görsel estetik direktörüsünüz.",
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    pr_director = Agent(
        role="PR ve Sosyal Medya Paylaşım Direktörü",
        goal="Gönderi metni (caption), hashtag'ler ve paylaşım zamanı belirlemek.",
        backstory="Sosyal medya etkileşim yöneticisisiniz.",
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    coordinator = Agent(
        role="Holding Genel Koordinatörü",
        goal="Tüm analizleri ve sosyal medya paketini birleştirip nihai raporu sunmak.",
        backstory="Holding Orkestra Şefisiniz.",
        verbose=True,
        allow_delegation=False,
        llm=secondary_model
    )

    return {
        "analyst": analyst,
        "mystic_analyst": mystic_analyst,
        "creative_director": creative_director,
        "risk_consultant": risk_consultant,
        "finance_strategist": finance_strategist,
        "operations_director": operations_director,
        "visual_designer": visual_designer,
        "pr_director": pr_director,
        "coordinator": coordinator
    }

# ---------------------------------------------------------
# FLASK ENDPOINT'LERİ
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Mistik Ajan Holding Canlıda!", 
        "version": "20.0-ResilientProduction",
        "system": "Otonom Görsel Tasarım ve Sosyal Medya Üretim Motoru"
    })

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası ve sosyal medya görseli sun.")

    # Otomatik Geçiş Silsilesi (Erişim Yetkisine Göre En Güçlüden En Stabile)
    model_pairs = [
        ("gpt-4o", "gpt-4o-mini"),
        ("gpt-4o-mini", "gpt-4o-mini"),
        ("gpt-3.5-turbo", "gpt-3.5-turbo")
    ]

    last_exception = None

    for primary_model, secondary_model in model_pairs:
        try:
            agents = run_holding_pipeline(primary_model, secondary_model)

            task1 = Task(description=f"Durumu detaylı analiz et: {user_query}", expected_output="Canlı veri destekli durum analizi.", agent=agents["analyst"])
            task2 = Task(description="En kritik riskleri ve kısıtlamaları yaz.", expected_output="Risk maddeleri.", agent=agents["risk_consultant"])
            task3 = Task(description="Bütçe ve zaman verimliliği için somut tavsiyeler ver.", expected_output="Bütçe tavsiyeleri.", agent=agents["finance_strategist"])
            task4 = Task(description="Uygulanabilir 3 adımlık eylem planı belirt.", expected_output="3 eylem adımı.", agent=agents["operations_director"])
            task5 = Task(description="Konuya dair mistik/sezgisel ve zamanlama tavsiyesi ver.", expected_output="Mistik/sezgisel analiz.", agent=agents["mystic_analyst"])
            task6 = Task(description="Bu durum için kanca (hook) odaklı sosyal medya Reels/Shorts senaryo fikri yaz.", expected_output="Kreatif içerik senaryosu.", agent=agents["creative_director"])
            task7 = Task(description="Bu konsept için lüks, ezoterik, detaylı 1 cümlelik İNGİLİZCE görsel prompt'u yaz. Sadece prompt metnini ver.", expected_output="İngilizce görsel prompt.", agent=agents["visual_designer"])
            task8 = Task(description="Instagram/TikTok paylaşımı için gönderi açıklama metni (caption), 5 adet ilgili hashtag ve paylaşım için ideal zamanı belirle.", expected_output="Sosyal medya paylaşım paketi.", agent=agents["pr_director"])

            holding_crew = Crew(
                agents=[agents["analyst"], agents["risk_consultant"], agents["finance_strategist"], agents["operations_director"], agents["mystic_analyst"], agents["creative_director"], agents["visual_designer"], agents["pr_director"]],
                tasks=[task1, task2, task3, task4, task5, task6, task7, task8],
                process=Process.sequential,
                verbose=True
            )

            holding_crew.kickoff()

            image_prompt = str(task7.output) if hasattr(task7, 'output') and task7.output else user_query
            generated_image_url = create_dalle_image(image_prompt)

            task9 = Task(
                description=(
                    f"Tüm analiz sonuçlarını ve sosyal medya paketini birleştir. "
                    f"Raporun en sonuna üretilen görsel bağlantısını doğrudan şu şekilde ekle: Görsel URL: {generated_image_url}\n"
                    "ÖNEMLİ FORMAT KURALI: Çıktıda kesinlikle `#`, `*`, `-` gibi Markdown kodları KULLANMA. "
                    "Raporu tamamen düz metin (plain text) düzeninde sun."
                ),
                expected_output="Görsel bağlantılı düz metin Holding Raporu.",
                agent=agents["coordinator"]
            )

            final_crew = Crew(
                agents=[agents["coordinator"]],
                tasks=[task9],
                process=Process.sequential,
                verbose=True
            )

            final_report = final_crew.kickoff()

            response_payload = {
                "status": "success",
                "active_model": primary_model,
                "holding_report": str(final_report)
            }

            return Response(
                json.dumps(response_payload, ensure_ascii=False),
                status=200,
                mimetype="application/json",
                headers={"Content-Type": "application/json; charset=utf-8"}
            )

        except Exception as e:
            last_exception = e
            # Eğer hata 403 / model erişimi veya bakiye hatası ise bir sonraki alt modele geçip tekrar dener
            continue

    # Tüm modeller başarısız olursa döndürülecek güvenlik yanıtı
    error_payload = {
        "status": "error",
        "message": f"Holding İşlem Hatası: {str(last_exception)}"
    }
    return Response(
        json.dumps(error_payload, ensure_ascii=False),
        status=500,
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))