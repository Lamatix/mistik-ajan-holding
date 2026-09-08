import os
from flask import Flask, jsonify, request
from crewai import Agent, Crew, Process, Task

app = Flask(__name__)

# ---------------------------------------------------------
# AJANLARIN TANIMLANMASI (Mistik Ajan Holding Kadrosu)
# ---------------------------------------------------------

# 1. Stratejik Analist
analyst = Agent(
    role="Stratejik Analist",
    goal="Kullanıcının durumunu bütünsel olarak incelemek, fırsatları ve ana dinamikleri belirlemek.",
    backstory="Sen Mistik Ajan Holding'in baş analistisin. Gelen her durumu yüzeysel değil, derinlemesine ve arketipler üzerinden analiz edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 2. Risk ve Kriz Danışmanı
risk_consultant = Agent(
    role="Risk ve Kriz Danışmanı",
    goal="Olası engelleri, kayıpları, duygusal/finansal tuzakları ve kriz senaryolarını önceden tespit etmek.",
    backstory="Sen koruyucu bir muhafızsın. Yanlış kararların getireceği maliyetleri hesaplar ve kullanıcıyı olası tuzaklara karşı uyarır, korursun.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 3. Kaynak ve Bütçe Stratejisti
finance_strategist = Agent(
    role="Kaynak ve Bütçe Stratejisti",
    goal="Zaman, maliyet, bütçe ve enerji verimliliğini optimum seviyeye getirecek planlama yapmak.",
    backstory="Sen mali ve kaynak yönetim uzmanısın. Her adımın enerji ve bütçe karşılığını hesaplar, maksimum verimlilik sağlarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 4. Saha ve İcra Direktörü
operations_director = Agent(
    role="Saha ve İcra Direktörü",
    goal="Analiz ve risk değerlendirmelerini net, adımları belli ve doğrudan uygulanabilir eylem planına çevirmek.",
    backstory="Sen pragmatik bir uygulayıcısın. Teorik bilgiyi gün gün, adım adım somut aksiyon maddelerine dönüştürürsün.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 5. Holding Genel Koordinatörü
coordinator = Agent(
    role="Holding Genel Koordinatörü",
    goal="Tüm birimlerden gelen verileri sentezleyip koruyucu, net, empatik ve profesyonel bir dille son raporu sunmak.",
    backstory="Sen Mistik Ajan Holding'in Orkestra Şefisin. Kurumsal jargona veya mistik klişelere kaçmadan, doğrudan ve güçlendirici bir üslupla nihai kararı iletirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# ---------------------------------------------------------
# FLASK ENDPOINT
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Mistik Ajan Holding Canlıda!", "version": "2.0-5Agents"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası sun.")

    task1 = Task(
        description=f"Şu konuyu derinlemesine incele ve ana dinamikleri çıkar: {user_query}",
        expected_output="Stratejik durum analizi ve temel fırsatlar.",
        agent=analyst
    )

    task2 = Task(
        description="Analiz edilen durumdaki riskleri, tuzakları ve dikkat edilmesi gereken noktaları belirle.",
        expected_output="Risk değerlendirmesi ve koruyucu uyarılar.",
        agent=risk_consultant
    )

    task3 = Task(
        description="Bu sürecin zaman, maliyet ve enerji verimliliği planını yap.",
        expected_output="Bütçe ve kaynak optimize önerileri.",
        agent=finance_strategist
    )

    task4 = Task(
        description="Analiz ve risk girdilerine göre somut, uygulanabilir adım adım aksiyon planı hazırla.",
        expected_output="Gün gün / adım adım icra planı.",
        agent=operations_director
    )

    task5 = Task(
        description="Tüm birimlerin çıktılarını birleştir. Mistik Ajan Holding adına kullanıcıya doğrudan, koruyucu ve net nihai kararı sun.",
        expected_output="Nihai Holding Danışmanlık Raporu.",
        agent=coordinator
    )

    holding_crew = Crew(
        agents=[analyst, risk_consultant, finance_strategist, operations_director, coordinator],
        tasks=[task1, task2, task3, task4, task5],
        process=Process.sequential,
        verbose=True
    )

    result = holding_crew.kickoff()

    return jsonify({
        "status": "success",
        "holding_report": str(result)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)