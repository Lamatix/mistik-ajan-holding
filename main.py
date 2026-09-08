import json
import os
from flask import Flask, Response, request
from crewai import Agent, Crew, Process, Task

app = Flask(__name__)

# ---------------------------------------------------------
# AJANLARIN TANIMLANMASI (8 Ajanlı Holding Kadrosu)
# ---------------------------------------------------------

# 1. Stratejik Analist
analyst = Agent(
    role="Stratejik Analist",
    goal="Kullanıcının durumunu hızlıca incelemek.",
    backstory="Mistik Ajan Holding'in baş analistisin. Verileri özet bir şekilde analiz edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 2. Risk ve Kriz Danışmanı
risk_consultant = Agent(
    role="Risk ve Kriz Danışmanı",
    goal="Ana riskleri tespit etmek.",
    backstory="Holding'in koruyucu muhafızısın. Kritik riskleri doğrudan uyarırsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 3. Kaynak ve Bütçe Stratejisti
finance_strategist = Agent(
    role="Kaynak ve Bütçe Stratejisti",
    goal="Zaman ve bütçe verimliliği planlamak.",
    backstory="Mali uzmansın. Bütçe ve kaynak önerisini somut tutarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 4. Saha ve İcra Direktörü
operations_director = Agent(
    role="Saha ve İcra Direktörü",
    goal="Uygulanabilir 3 adımlık eylem planı sunmak.",
    backstory="Pragmatik uygulayıcısın. Adımları net ve eyleme dönüştürülebilir yazarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 5. Mistik Analist
mystic_analyst = Agent(
    role="Mistik ve Astrolojik Analist",
    goal="Konunun sezgisel ve astrolojik/döngüsel boyutunu incelemek.",
    backstory="Mistik Holding'in sezgisel danışmanısın. Zamanlama, kozmik döngüler ve içsel potansiyel üzerine rehberlik edersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 6. İçerik ve Senaryo Üreticisi
creative_director = Agent(
    role="İçerik ve Senaryo Üreticisi",
    goal="Stratejiyi yaratıcı sosyal medya/dijital içerik konseptlerine dönüştürmek.",
    backstory="Kreatif direktörsün. Fikirleri viral olacak içerik senaryolarına çevirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 7. PR ve Müşteri İlişkileri Direktörü
pr_director = Agent(
    role="PR ve Müşteri İlişkileri Direktörü",
    goal="Marka algısı ve müşteri iletişimi dilini belirlemek.",
    backstory="Holding'in dışa dönük yüzüsün. Müşteri memnuniyetini ve marka itibarını yönetirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# 8. Holding Genel Koordinatörü
coordinator = Agent(
    role="Holding Genel Koordinatörü",
    goal="Tüm 7 ajanın çıktısını sentezleyip nihai Holding Raporunu sunmak.",
    backstory="Holding Orkestra Şefisin. Farklı alanlardan gelen tüm analizleri kusursuz bir raporda birleştirirsin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

# ---------------------------------------------------------
# FLASK ENDPOINT'LERİ
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    response_data = json.dumps({"status": "Mistik Ajan Holding Canlıda!", "version": "3.0-8Agents"}, ensure_ascii=False)
    return Response(response_data, content_type="application/json; charset=utf-8")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası sun.")

    # 8 Ajanlı Görev Yapısı
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
        description="Bütçe verimliliği için 2 somut tavsiye ver.",
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
        description="Bu proje/durum için 1 adet yaratıcı içerik veya senaryo fikri öner.",
        expected_output="Kreatif içerik fikri.",
        agent=creative_director
    )

    task7 = Task(
        description="Müşteri/hedef kitle iletişimi için 1 kritik PR tavsiyesi ver.",
        expected_output="PR ve iletişim tavsiyesi.",
        agent=pr_director
    )

    task8 = Task(
        description="Tüm 7 ajandan gelen girdileri birleştirip kullanıcıya düzenli, ilham verici ve net bir nihai Holding Raporu sun.",
        expected_output="Eksiksiz 8-Ajanlı Mistik Holding Danışmanlık Raporu.",
        agent=coordinator
    )

    holding_crew = Crew(
        agents=[
            analyst, risk_consultant, finance_strategist, operations_director,
            mystic_analyst, creative_director, pr_director, coordinator
        ],
        tasks=[task1, task2, task3, task4, task5, task6, task7, task8],
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
    app.run(host="0.0.0.0", port=5000)