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
    """İnternette güncel bilgi, trend ve rakip analizi verisi arar."""
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
        "version": "26.0-FullAgencyEngine"
    })

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Mistik Ajan Holding için 2026 sosyal medya ve büyüme stratejisi oluştur.")
    
    openai_key = os.environ.get("OPENAI_API_KEY")

    try:
        llm = LLM(
            model="gpt-4o-mini",
            api_key=openai_key
        )

        # --- AJAN KADROSU ---
        trend_hunter = Agent(
            role="Trend ve Akım Takipçisi",
            goal="Sektördeki en son viral akımları, popüler sesleri ve pazarlama trendlerini tespit etmek.",
            backstory="Sosyal medyanın nabzını tutan, dijital trend avcısısınız.",
            tools=search_tools,
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        competitor_analyst = Agent(
            role="Sektör ve Rakip Analisti",
            goal="Rakiplerin stratejilerini, zayıf noktalarını ve farklılaşma fırsatlarını belirlemek.",
            backstory="Pazardaki tüm oyuncuları inceleyen deneyimli bir pazar istihbarat uzmanısınız.",
            tools=search_tools,
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        strategy_lead = Agent(
            role="Holding Strateji Direktörü",
            goal="Trend ve rakip analizlerini birleştirerek holding için ana büyüme stratejisini çizmek.",
            backstory="Mistik Ajan Holding'in karar vericisi ve strateji liderisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        creative_director = Agent(
            role="Kreatif ve İçerik Direktörü",
            goal="Stratejiye uygun viral kanca (hook) odaklı senaryolar ve metin paketleri oluşturmak.",
            backstory="Sıra dışı fikirler ve hikaye anlatımıyla kitleleri etkileyen kreatif liderisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        video_editor = Agent(
            role="Video Montaj ve Kurgu Yönetmeni",
            goal="Senaryoyu saniye saniye görsel geçişler, ses efektleri ve kurgu notları içeren montaj planına dönüştürmek.",
            backstory="Reels/Shorts videolarının izlenme sürelerini (watch time) tavan yaptıran uzman kurgucusunuz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        # --- GÖREV ZİNCİRİ ---
        t1 = Task(
            description=f"Şu konu hakkındaki güncel trendleri ve viral akımları araştır: {user_query}",
            expected_output="Önemli trendler ve popüler akımlar raporu.",
            agent=trend_hunter
        )

        t2 = Task(
            description=f"Konuyla ilgili rakiplerin durumunu incele ve boşlukları (fırsatları) tespit et: {user_query}",
            expected_output="Rakip analizi ve pazar fırsatları raporu.",
            agent=competitor_analyst
        )

        t3 = Task(
            description="Trend ve rakip verilerini sentezleyerek Mistik Ajan Holding için ana strateji planını oluştur.",
            expected_output="Kapsamlı Holding Büyüme Stratejisi.",
            agent=strategy_lead
        )

        t4 = Task(
            description="Strateji doğrultusunda viral kanca (hook) odaklı Reels senaryosu yaz ve en sona lüks 1 cümlelik İNGİLİZCE görsel prompt'u ekle.",
            expected_output="Kreatif senaryo paketi ve İngilizce görsel prompt.",
            agent=creative_director
        )

        t5 = Task(
            description="Yazılan senaryo için saniye saniye montaj, kurgu geçişleri, text overlay ve ses efekti (SFX) rehberi hazırla.",
            expected_output="Saniye saniye video montaj ve kurgu rehberi.",
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