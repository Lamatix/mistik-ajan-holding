import json
import os
import urllib.parse
from functools import wraps
from flask import Flask, Response, request, jsonify
from crewai import Agent, Crew, Process, Task
from langchain_community.tools import DuckDuckGoSearchRun
from openai import OpenAI

app = Flask(__name__)

# ---------------------------------------------------------
# GÜVENLİK VE YAPILANDIRMA
# ---------------------------------------------------------
API_KEY = os.environ.get("HOLDING_API_KEY", "mistik-secret-key-2026")
OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Canlı Web Arama Aracı Entegrasyonu
web_search_tool = DuckDuckGoSearchRun()

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # HOLDING_API_KEY tanımlıysa X-API-KEY kontrolü yapar
        if os.environ.get("HOLDING_API_KEY"):
            user_key = request.headers.get("X-API-KEY") or request.args.get("api_key")
            if user_key != API_KEY:
                return jsonify({"error": "Yetkisiz Erişim. Geçersiz X-API-KEY."}), 401
        return f(*args, **kwargs)
    return decorated

def create_dalle_image(prompt_text):
    """
    OpenAI'ın güncel görsel modelini dener.
    Model kısıtlaması veya bakiye/yetki hatası durumunda kesintisiz yedek görsel motoruna geçer.
    """
    try:
        response = OPENAI_CLIENT.images.generate(
            model="gpt-image-2",
            prompt=f"Luxury, esoteric, highly detailed aesthetic artwork: {prompt_text}",
            size="1024x1024",
            quality="hd",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        clean_prompt = urllib.parse.quote(f"Luxury esoteric mystic artwork, {prompt_text}")
        return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true"

# ---------------------------------------------------------
# AJANLARIN TANIMLANMASI (Model Routing & Web Search Katmanı)
# ---------------------------------------------------------

# Derin Derleme & Akıl Yürütme Ajanları (gpt-4o)
analyst = Agent(
    role="Stratejik Analist ve Piyasa Araştırmacısı",
    goal="Canlı web taraması yaparak en güncel trendleri, piyasa verilerini ve durumları analiz etmek.",
    backstory="Mistik Ajan Holding'in istihbarat liderisin. İnterneti ve açık kaynak sistemleri anlık tarayarak güncel verileri toplarsın.",
    tools=[web_search_tool],
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

mystic_analyst = Agent(
    role="Mistik ve Astrolojik Analist",
    goal="Konunun sezgisel, astrolojik ve ezoterik boyutunu incelemek.",
    backstory="Mistik Holding'in sezgisel danışmanısın. Zamanlama, kozmik döngüler ve içsel potansiyel üzerine rehberlik edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

creative_director = Agent(
    role="İçerik ve Senaryo Üreticisi",
    goal="Stratejiyi ve mistik analizi sosyal medya senaryolarına dönüştürmek.",
    backstory="Kreatif direktörsün. Fikirleri viral olacak Reels/Shorts içerik senaryolarına çevirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# Hızlı & Yüksek Verimli İcra Ajanları (gpt-4o-mini)
risk_consultant = Agent(
    role="Risk ve Kriz Danışmanı",
    goal="Ana riskleri, platform kısıtlamalarını ve güvenlik durumlarını tespit etmek.",
    backstory="Holding muhafızısın. Güncel kriz ve risk durumlarını tarayarak uyarılarda bulunursun.",
    tools=[web_search_tool],
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

finance_strategist = Agent(
    role="Kaynak ve Bütçe Stratejisti",
    goal="Zaman, içerik üretimi ve bütçe verimliliğini planlamak.",
    backstory="Mali uzmansın. Bütçe ve kaynak önerisini somut tutarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

operations_director = Agent(
    role="Saha ve İcra Direktörü",
    goal="Uygulanabilir 3 adımlık operasyonel eylem planı sunmak.",
    backstory="Pragmatik uygulayıcısın. Adımları net ve eyleme dönüştürülebilir yazarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

visual_designer = Agent(
    role="Görsel Tasarım Direktörü",
    goal="İçerik konseptine uygun görsel için mükemmel bir İngilizce istem (prompt) yazmak.",
    backstory="Astroloji ve tarot sembolizmini üst düzey görsel estetikle birleştirip görsel istemi hazırlarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

pr_director = Agent(
    role="PR ve Sosyal Medya Paylaşım Direktörü",
    goal="Gönderi metinlerini (caption), hashtag'leri ve otomatik paylaşım zamanlamasını hazırlamak.",
    backstory="Holding'in dışa dönük yüzüsün. Sosyal medya etkileşimini ve otomatik paylaşım akışını yönetirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

coordinator = Agent(
    role="Holding Genel Koordinatörü",
    goal="Tüm ajanların çıktısını ve sosyal medya paketini birleştirip nihai raporu sunmak.",
    backstory="Holding Orkestra Şefisin. Tüm analizleri ve sosyal medya metinlerini temiz düz metin halinde raporda birleştirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini"
)

# ---------------------------------------------------------
# FLASK ENDPOINT'LERİ
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    response_data = json.dumps({
        "status": "Mistik Ajan Holding Canlıda!", 
        "version": "12.0-EnterpriseFinal",
        "system": "Canlı Arama, Model Routing ve Sıfır Hatasız Görsel Motoru"
    }, ensure_ascii=False)
    return Response(response_data, content_type="application/json; charset=utf-8")

@app.route("/analyze", methods=["POST"])
@require_api_key
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası ve sosyal medya görseli sun.")

    task1 = Task(description=f"Konuyla ilgili gerekiyorsa canlı web taraması yap ve durumu 2 cümleyle analiz et: {user_query}", expected_output="Canlı veri destekli durum analizi.", agent=analyst)
    task2 = Task(description="Gerekirse web taraması yaparak en kritik 2 riski maddeler halinde yaz.", expected_output="Kısa risk maddeleri.", agent=risk_consultant)
    task3 = Task(description="Bütçe ve zaman verimliliği için 2 somut tavsiye ver.", expected_output="Kısa bütçe tavsiyeleri.", agent=finance_strategist)
    task4 = Task(description="Uygulanabilir 3 eylem adımı belirt.", expected_output="3 eylem adımı.", agent=operations_director)
    task5 = Task(description="Konuya dair 1 cümlelik mistik/sezgisel ve zamanlama tavsiyesi ver.", expected_output="Mistik/sezgisel analiz.", agent=mystic_analyst)
    task6 = Task(description="Bu durum için 1 adet kanca (hook) odaklı sosyal medya Reels/Shorts senaryo fikri yaz.", expected_output="Kreatif içerik senaryosu.", agent=creative_director)
    
    task7 = Task(
        description="Bu konsept için lüks, ezoterik, altın vurgulu, detaylı 1 cümlelik İNGİLİZCE görsel prompt'u yaz. Sadece prompt metnini ver.",
        expected_output="İngilizce görsel prompt.",
        agent=visual_designer
    )

    task8 = Task(description="Instagram/TikTok paylaşımı için gönderi açıklama metni (caption), 5 adet ilgili hashtag ve paylaşım için ideal zamanı belirle.", expected_output="Sosyal medya paylaşım paketi.", agent=pr_director)

    holding_crew = Crew(
        agents=[analyst, risk_consultant, finance_strategist, operations_director, mystic_analyst, creative_director, visual_designer, pr_director],
        tasks=[task1, task2, task3, task4, task5, task6, task7, task8],
        process=Process.sequential,
        memory=True,
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
        agent=coordinator
    )

    final_crew = Crew(
        agents=[coordinator],
        tasks=[task9],
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))