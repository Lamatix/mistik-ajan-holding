import os
from flask import Flask, jsonify, request
from crewai import Agent, Crew, Process, Task

app = Flask(__name__)

analyst = Agent(
    role="Stratejik Analist",
    goal="Kullanıcının durumunu hızlıca ve öz bir şekilde incelemek.",
    backstory="Sen Mistik Ajan Holding'in baş analistisin. Özet ve net analizler yaparsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

risk_consultant = Agent(
    role="Risk ve Kriz Danışmanı",
    goal="Ana riskleri maddeler halinde tespit etmek.",
    backstory="Sen koruyucu bir muhafızsın. En kritik 3 riski uyarır, geçersin.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

finance_strategist = Agent(
    role="Kaynak ve Bütçe Stratejisti",
    goal="Zaman ve bütçe verimliliği planlamak.",
    backstory="Mali uzmansın. Bütçe ve kaynak önerisini kısa tutarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

operations_director = Agent(
    role="Saha ve İcra Direktörü",
    goal="Uygulanabilir 3 adımlık eylem planı sunmak.",
    backstory="Pragmatik uygulayıcısın. Adımları net ve kısa yazarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

coordinator = Agent(
    role="Holding Genel Koordinatörü",
    goal="Sentezleyip nihai kararı 2 paragrafta sunmak.",
    backstory="Holding Orkestra Şefisin. Öz, güçlendirici ve net bir rapor sunarsın.",
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o"
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Mistik Ajan Holding Canlıda!", "version": "2.0-5Agents"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    user_query = data.get("query", "Hayatımdaki mevcut durumu değerlendirip bana yol haritası sun.")

    task1 = Task(
        description=f"Konuyu en fazla 2-3 cümleyle analiz et: {user_query}",
        expected_output="Kısa durum analizi.",
        agent=analyst
    )

    task2 = Task(
        description="En kritik 3 riski maddeler halinde yaz.",
        expected_output="Kısa risk maddeleri.",
        agent=risk_consultant
    )

    task3 = Task(
        description="Bütçe ve kaynak verimliliği için 2 somut tavsiye ver.",
        expected_output="Kısa bütçe tavsiyeleri.",
        agent=finance_strategist
    )

    task4 = Task(
        description="Uygulanabilir 3 eylem adımı belirt.",
        expected_output="3 eylem adımı.",
        agent=operations_director
    )

    task5 = Task(
        description="Tüm çıktıları birleştirip kullanıcıya öz ve net bir nihai Holding raporu sun.",
        expected_output="Kısa Holding Danışmanlık Raporu.",
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