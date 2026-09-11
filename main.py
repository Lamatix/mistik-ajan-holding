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
    """İnternette güncel bilgi ve veri araması yapar."""
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
                prompt=f"Luxury, esoteric artwork: {prompt_text[:200]}",
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
        "version": "24.0-MemoryOptimized"
    })

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Mistik Ajan Holding için 2026 sosyal medya stratejisi ve görsel konsepti oluştur.")
    
    openai_key = os.environ.get("OPENAI_API_KEY")

    try:
        llm = LLM(
            model="gpt-4o-mini",
            api_key=openai_key
        )

        analyst = Agent(
            role="Holding Stratejik ve Mistik Analisti",
            goal="Konuyu hem pazar verileri hem de ezoterik/sezgisel açılardan analiz etmek.",
            backstory="Mistik Ajan Holding'in ana stratejistisiniz.",
            tools=search_tools,
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        creative_director = Agent(
            role="Kreatif Görsel Direktör",
            goal="Analizden yola çıkarak kanca odaklı sosyal medya senaryosu ve 1 cümlelik İNGİLİZCE görsel prompt'u üretmek.",
            backstory="Holding'in kreatif liderisiniz.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        task1 = Task(
            description=f"Konuyu stratejik ve sezgisel boyutta detaylıca analiz et: {user_query}", 
            expected_output="Kapsamlı analiz raporu.", 
            agent=analyst
        )
        
        task2 = Task(
            description="Bu analiz için viral kanca (hook) odaklı Reels senaryosu yaz ve en sona lüks/ezoterik 1 cümlelik İNGİLİZCE görsel prompt'u ekle.", 
            expected_output="Sosyal medya paketi ve İngilizce görsel prompt.", 
            agent=creative_director
        )

        holding_crew = Crew(
            agents=[analyst, creative_director],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=True
        )

        holding_crew.kickoff()

        image_prompt = str(task2.output) if hasattr(task2, 'output') and task2.output else user_query
        generated_image_url = create_dalle_image(image_prompt, openai_key)

        response_payload = {
            "status": "success",
            "holding_report": str(task1.output),
            "creative_package": str(task2.output),
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