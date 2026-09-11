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

API_KEY = os.environ.get("HOLDING_API_KEY", "mistik-secret-key-2026")

_ddg_search = DuckDuckGoSearchRun()

@tool("Web Search Tool")
def execute_web_search(query: str) -> str:
    """İnternette güncel bilgi ve trend araması yapar."""
    try:
        return _ddg_search.run(query)
    except Exception as e:
        return f"Arama hatası: {str(e)}"

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
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"Luxury, esoteric high-end artwork: {prompt_text[:200]}",
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

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Mistik Ajan Holding Canlıda!", 
        "version": "27.0-FastAgencyEngine"
    })

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Mistik Ajan Holding için 2026 sosyal medya stratejisi oluştur.")
    
    openai_key = os.environ.get("OPENAI_API_KEY")

    try:
        llm = LLM(
            model="gpt-4o-mini",
            api_key=openai_key
        )

        # --- OPTİMİZE EDİLMİŞ 5 AJAN ---
        trend_hunter = Agent(
            role="Trend ve Akım Takipçisi",
            goal="Sektördeki en son viral akımları ve pazarlama trendlerini tespit etmek.",
            backstory="Sosyal medyanın nabzını tutan dijital trend avcısısınız.",
            tools=search_tools, # Sadece trend hunter arama yapar
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        competitor_analyst = Agent(
            role="Sektör ve Rakip Analisti",
            goal="Rakiplerin zayıf noktalarını ve farklılaşma fırsatlarını belirlemek.",
            backstory="Pazarı hızla analiz eden istihbarat uzmanısınız.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        strategy_lead = Agent(
            role="Holding Strateji Direktörü",
            goal="Trend ve rakip verilerini birleştirerek holding büyüme stratejisini çizmek.",
            backstory="Mistik Ajan Holding'in karar verici liderisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        creative_director = Agent(
            role="Kreatif ve İçerik Direktörü",
            goal="Stratejiye uygun kanca odaklı Reels senaryosu ve İngilizce görsel prompt üretmek.",
            backstory="Sıra dışı fikirlerle kitleleri etkileyen kreatif liderisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        video_editor = Agent(
            role="Video Montaj ve Kurgu Yönetmeni",
            goal="Senaryo için kurgu, geçiş (transition) ve ses efekti (SFX) rehberi hazırlamak.",
            backstory="Reels videolarının izlenme sürelerini artıran uzman kurgucusunuz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        # --- KISA VE NET GÖREVLER ---
        t1 = Task(
            description=f"Şu konu hakkındaki güncel trendleri kısaca araştır: {user_query}",
            expected_output="Önemli trendler özeti.",
            agent=trend_hunter
        )

        t2 = Task(
            description=f"Konuyla ilgili rakip fırsatlarını değerlendir: {user_query}",
            expected_output="Rakip analizi özeti.",
            agent=competitor_analyst
        )

        t3 = Task(
            description="Verileri sentezleyip Mistik Ajan Holding için 3 maddelik ana stratejiyi yaz.",
            expected_output="Holding Büyüme Stratejisi.",
            agent=strategy_lead
        )

        t4 = Task(
            description="Stratejiye uygun kanca odaklı Reels senaryosu yaz ve en sona lüks 1 cümlelik İNGİLİZCE görsel prompt'u ekle.",
            expected_output="Kreatif senaryo ve İngilizce görsel prompt.",
            agent=creative_director
        )

        t5 = Task(
            description="Senaryo için kurgu, geçiş ve ses efektleri rehberini yaz.",
            expected_output="Video kurgu rehberi.",
            agent=video_editor
        )

        holding_crew = Crew(
            agents=[trend_hunter, competitor_analyst, strategy_lead, creative_director, video_editor],
            tasks=[t1, t2, t3, t4, t5],
            process=Process.sequential,
            verbose=True
        )

        holding_crew.kickoff()

        image_prompt = str(t4.output) if hasattr(t4, 'output') and t4.output else user_query
        generated_image_url = create_dalle_image(image_prompt, openai_key)

        response_payload = {
            "status": "success",
            "trend_report": str(t1.output),
            "competitor_report": str(t2.output),
            "master_strategy": str(t3.output),
            "creative_package": str(t4.output),
            "video_editing_guide": str(t5.output),
            "generated_image_url": generated_image_url
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
            "message": f"İşlem Hatası: {str(e)}"
        }
        return Response(
            json.dumps(error_payload, ensure_ascii=False),
            status=500,
            mimetype="application/json"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))