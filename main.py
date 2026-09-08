import json
import os
from flask import Flask, Response, request
from crewai import Agent, Crew, Process, Task
from langchain_community.tools import DallEQueryRun
from langchain_community.utilities import DallEAPIWrapper

app = Flask(__name__)

# OpenAI ve DALL-E 3 Kurulumu
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

dalle_wrapper = DallEAPIWrapper(
    model="dall-e-3",
    size="1024x1024",
    quality="hd",
    api_key=OPENAI_API_KEY
)
dalle_tool = DallEQueryRun(api_wrapper=dalle_wrapper)

# ---------------------------------------------------------
# AJANLARIN TANIMLANMASI (Görsel ve Sosyal Medya Odaklı)
# ---------------------------------------------------------

# 1. Stratejik Analist
analyst = Agent(
    role="Stratejik Analist",
    goal="Kullanıcının durumunu ve talebini hızlıca analiz etmek.",
    backstory="Mistik Ajan Holding'in baş analistisin. Verileri özet bir şekilde analiz edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 2. Risk ve Kriz Danışmanı
risk_consultant = Agent(
    role="Risk ve Kriz Danışmanı",
    goal="Ana riskleri ve içerik/platform kısıtlamalarını tespit etmek.",
    backstory="Holding'in koruyucu muhafızısın. Kritik riskleri doğrudan uyarırsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 3. Kaynak ve Bütçe Stratejisti
finance_strategist = Agent(
    role="Kaynak ve Bütçe Stratejisti",
    goal="Zaman, içerik üretimi ve bütçe verimliliğini planlamak.",
    backstory="Mali uzmansın. Bütçe ve kaynak önerisini somut tutarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 4. Saha ve İcra Direktörü
operations_director = Agent(
    role="Saha ve İcra Direktörü",
    goal="Uygulanabilir 3 adımlık operasyonel eylem planı sunmak.",
    backstory="Pragmatik uygulayıcısın. Adımları net ve eyleme dönüştürülebilir yazarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 5. Mistik Analist
mystic_analyst = Agent(
    role="Mistik ve Astrolojik Analist",
    goal="Konunun sezgisel, astrolojik ve ezoterik boyutunu incelemek.",
    backstory="Mistik Holding'in sezgisel danışmanısın. Zamanlama, kozmik döngüler ve içsel potansiyel üzerine rehberlik edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 6. İçerik ve Senaryo Üreticisi
creative_director = Agent(
    role="İçerik ve Senaryo Üreticisi",
    goal="Stratejiyi ve mistik analizi sosyal medya senaryolarına dönüştürmek.",
    backstory="Kreatif direktörsün. Fikirleri viral olacak Reels/Shorts içerik senaryolarına çevirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 7. Görsel Tasarım Direktörü (DALL-E 3 Destekli)
visual_designer = Agent(
    role="Görsel Tasarım Direktörü",
    goal="İçerik konseptine uygun lüks, altın yaldızlı ve ezoterik yapay zeka görselleri tasarlamak ve üretmek.",
    backstory="Astroloji ve tarot sembolizmini üst düzey görsel estetikle birleştirip DALL-E 3 ile görsele dönüştürürsün.",
    tools=[dalle_tool],
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 8. PR ve Sosyal Medya Paylaşım Direktörü
pr_director = Agent(
    role="PR ve Sosyal Medya Paylaşım Direktörü",
    goal="Gönderi metinlerini (caption), hashtag'leri ve otomatik paylaşım zamanlamasını hazırlamak.",
    backstory="Holding'in dışa dönük yüzüsün. Sosyal medya etkileşimini ve otomatik paylaşım akışını yönetirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 9. Holding Genel Koordinatörü
coordinator = Agent(
    role="Holding Genel Koordinatörü",
    goal="Tüm ajanların çıktısını, görsel bağlantısını ve sosyal medya paketini birleştirip nihai raporu sunmak.",
    backstory="Holding Orkestra Şefisin. Tüm analizleri, üretilen görselleri ve sosyal medya metinlerini temiz düz metin halinde raporda birleştirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# ---------------------------------------------------------
# FLASK ENDPOINT'LERİ
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    response_data = json.dumps({
        "status": "Mistik Ajan Holding Canlıda!", 
        "version": "4.0-VisualAndSocialAgents",
        "system": "Otonom Görsel Tasarım ve Sosyal Medya Üretim Motoru"
    }, ensure_ascii=False)
    return Response(response_data, content_type="application/json; charset=utf-8")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası ve sosyal medya görseli sun.")

    task1 = Task(
        description=f"Durumu 2 cümleyle analiz et: {user_query}",
        expected_output="Kısa durum analizi.",
        agent=analyst
    )

    task2 = Task(
        description="En kritik 2 riski maddeler halinde yaz.",
        expected_output="Kısa risk maddeleri.",
        agent=risk_consultant
    )

    task3 = Task(
        description="Bütçe ve zaman verimliliği için 2 somut tavsiye ver.",
        expected_output="Kısa bütçe tavsiyeleri.",
        agent=finance_strategist
    )

    task4 = Task(
        description="Uygulanabilir 3 eylem adımı belirt.",
        expected_output="3 eylem adımı.",
        agent=operations_director
    )

    task5 = Task(
        description="Konuya dair 1 cümlelik mistik/sezgisel ve zamanlama tavsiyesi ver.",
        expected_output="Mistik/sezgisel analiz.",
        agent=mystic_analyst
    )

    task6 = Task(
        description="Bu durum için 1 adet kanca (hook) odaklı sosyal medya Reels/Shorts senaryo fikri yaz.",
        expected_output="Kreatif içerik senaryosu.",
        agent=creative_director
    )

    task7 = Task(
        description="Kreatif konsepti ve mistik analizi görselleştirmek için DALL-E 3 aracını kullanarak lüks, ezoterik ve estetik bir görsel üret. Üretilen görsel URL'sini rapora ekle.",
        expected_output="DALL-E 3 tarafından üretilen görselin URL bağlantısı ve kısa görsel tanımı.",
        agent=visual_designer
    )

    task8 = Task(
        description="Instagram/TikTok paylaşımı için gönderi açıklama metni (caption), 5 adet ilgili hashtag ve paylaşım için ideal zamanı belirle.",
        expected_output="Sosyal medya paylaşım paketi.",
        agent=pr_director
    )

    task9 = Task(
        description=(
            "Tüm ajanlardan gelen analizleri, DALL-E 3 görsel bağlantısını ve sosyal medya paylaşım paketini tek bir raporda birleştir. "
            "ÖNEMLİ FORMAT KURALI: Çıktıda kesinlikle `#`, `*`, `-` gibi Markdown kodları KULLANMA. "
            "Raporu tamamen düz metin (plain text) düzeninde sun."
        ),
        expected_output="Görsel bağlantılı ve paylaşıma hazır düz metin Holding Raporu.",
        agent=coordinator
    )

    holding_crew = Crew(
        agents=[
            analyst, risk_consultant, finance_strategist, operations_director,
            mystic_analyst, creative_director, visual_designer, pr_director, coordinator
        ],
        tasks=[task1, task2, task3, task4, task5, task6, task7, task8, task9],
        process=Process.sequential,
        verbose=True
    )

    result = holding_crew.kickoff()

    response_payload = {
        "status": "success",
        "holding_report": str(result)
    }

    return Response(
        json.dumps(response_payload, ensure_ascii=False),
        status=200,
        mimetype="application/json",
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))