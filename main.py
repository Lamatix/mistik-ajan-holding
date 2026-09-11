import json
import os
import urllib.parse
from functools import wraps
from flask import Flask, Response, request, jsonify
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from openai import OpenAI

app = Flask(__name__)

# ---------------------------------------------------------
# GÜVENLİK VE YAPILANDIRMA
# ---------------------------------------------------------
API_KEY = os.environ.get("HOLDING_API_KEY", "mistik-secret-key-2026")

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

def create_dalle_image(prompt_text, api_key):
    """
    Görsel Üretim Katmanı
    """
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.images.generate(
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

# ---------------------------------------------------------
# FLASK ENDPOINT'LERİ
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Mistik Ajan Holding Canlıda!", 
        "version": "22.0-DirectLLMFix",
        "system": "Otonom Görsel Tasarım ve Sosyal Medya Üretim Motoru"
    })

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası ve sosyal medya görseli sun.")
    
    openai_key = os.environ.get("OPENAI_API_KEY")

    # LLM Nesnesini Doğrudan Aktif Anahtarla Başlatma (Hatalı Proje Baglantisini Keser)
    try:
        custom_llm = LLM(
            model="gpt-4o-mini",
            api_key=openai_key
        )
    except Exception as e:
        custom_llm = "gpt-4o-mini"

    try:
        analyst = Agent(
            role="Stratejik Analist ve Piyasa Araştırmacısı",
            goal="Canlı web taraması yaparak en güncel trendleri ve durumları derinlemesine analiz etmek.",
            backstory="Mistik Ajan Holding'in üst düzey istihbarat liderisiniz.",
            tools=search_tools,
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        mystic_analyst = Agent(
            role="Mistik ve Astrolojik Analist",
            goal="Konunun sezgisel, astrolojik ve ezoterik boyutunu derinlemesine incelemek.",
            backstory="Mistik Holding'in ana sezgisel danışmanısınız.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        creative_director = Agent(
            role="İçerik ve Senaryo Üreticisi",
            goal="Stratejiyi ve mistik analizi yüksek etkileşimli sosyal medya senaryolarına dönüştürmek.",
            backstory="Kreatif direktörsünüz.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        visual_designer = Agent(
            role="Görsel Tasarım Direktörü",
            goal="Lüks ve ezoterik 1 cümlelik İngilizce görsel prompt'u yazmak.",
            backstory="Görsel estetik direktörüsünüz.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        coordinator = Agent(
            role="Holding Genel Koordinatörü",
            goal="Tüm analizleri ve sosyal medya paketini birleştirip nihai raporu sunmak.",
            backstory="Holding Orkestra Şefisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=custom_llm
        )

        task1 = Task(description=f"Durumu detaylı analiz et: {user_query}", expected_output="Durum analizi.", agent=analyst)
        task2 = Task(description="Konuya dair mistik/sezgisel tavsiye ver.", expected_output="Mistik analiz.", agent=mystic_analyst)
        task3 = Task(description="Bu durum için kanca (hook) odaklı sosyal medya Reels/Shorts senaryo fikri yaz.", expected_output="İçerik senaryosu.", agent=creative_director)
        task4 = Task(description="Bu konsept için lüks, ezoterik 1 cümlelik İNGİLİZCE görsel prompt'u yaz.", expected_output="İngilizce görsel prompt.", agent=visual_designer)

        holding_crew = Crew(
            agents=[analyst, mystic_analyst, creative_director, visual_designer],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential,
            verbose=True
        )

        holding_crew.kickoff()

        image_prompt = str(task4.output) if hasattr(task4, 'output') and task4.output else user_query
        generated_image_url = create_dalle_image(image_prompt, openai_key)

        task5 = Task(
            description=(
                f"Tüm analiz sonuçlarını ve sosyal medya paketini birleştir. "
                f"Raporun en sonuna üretilen görsel bağlantısını şu şekilde ekle: Görsel URL: {generated_image_url}\n"
                "ÖNEMLİ: Çıktıda Markdown (#, *, -) kullanma. Düz metin olarak sun."
            ),
            expected_output="Düz metin Holding Raporu.",
            agent=coordinator
        )

        final_crew = Crew(
            agents=[coordinator],
            tasks=[task5],
            process=Process.sequential,
            verbose=True
        )

        final_report = final_crew.kickoff()

        response_payload = {
            "status": "success",
            "holding_report": str(final_report)
        }

        return Response(
            json.dumps(response_payload, ensure_ascii=False),
            status=200,
            mimetype="application/json",
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

    except Exception as e:
        error_payload = {
            "status": "error",
            "message": f"Holding İşlem Hatası: {str(e)}"
        }
        return Response(
            json.dumps(error_payload, ensure_ascii=False),
            status=500,
            mimetype="application/json"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))