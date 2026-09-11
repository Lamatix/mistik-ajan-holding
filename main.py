import json
import os
import urllib.parse
from functools import wraps
from flask import Flask, Response, request, jsonify
from crewai import Agent, Crew, Process, Task, LLM
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.environ.get("HOLDING_API_KEY", "mistik-secret-key-2026")

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
        "version": "28.0-StableAgencyEngine"
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

        # RAM dostu 2 ana uzman birim
        intelligence_lead = Agent(
            role="Trend, Rakip ve Strateji Direktörü",
            goal="Sektörel trendleri, rakip boşluklarını ve Mistik Ajan Holding için ana büyüme stratejisini çıkarmak.",
            backstory="Pazar istihbaratı ve stratejik kararlardan sorumlu lider ajan.",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

        production_lead = Agent(
            role="Kreatif ve Video Kurgu Yönetmeni",
            goal="Stratejiye uygun viral Reels senaryosu, kurgu rehberi ve İngilizce görsel prompt yazmak.",
            backstory="Içerik kurgusu ve görsel direktörlükten sorumlu kreatif lider.",
            verbose=False,
            allow_delegation=False,
            llm=llm
        )

        task1 = Task(
            description=f"Şu konuyu trendler, rakip fırsatları ve holding stratejisi açısından analiz et: {user_query}. Çıktıyı 3 ayrı başlıkta sun: 1- Trendler, 2- Rakip Analizi, 3- Ana Strateji.",
            expected_output="Trend, Rakip ve Strateji Raporu.",
            agent=intelligence_lead
        )

        task2 = Task(
            description="Stratejiye uygun viral kanca odaklı Reels senaryosu, saniye saniye kurgu/geçiş rehberi ve en sona 1 cümlelik İNGİLİZCE görsel prompt ekle.",
            expected_output="Reels Senaryosu, Kurgu Rehberi ve İngilizce Görsel Prompt.",
            agent=production_lead
        )

        holding_crew = Crew(
            agents=[intelligence_lead, production_lead],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=False
        )

        holding_crew.kickoff()

        image_prompt = str(task2.output) if hasattr(task2, 'output') and task2.output else user_query
        generated_image_url = create_dalle_image(image_prompt, openai_key)

        response_payload = {
            "status": "success",
            "intelligence_and_strategy": str(task1.output),
            "creative_and_video_guide": str(task2.output),
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