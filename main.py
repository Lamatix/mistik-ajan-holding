import os
from flask import Flask, request, jsonify
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

app = Flask(__name__)

# OpenAI API Key kontrolü
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if OPENAI_API_KEY:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
else:
    llm = None

# --- AJANLAR ---
astro_agent = Agent(
    role="Astroloji Uzmanı",
    goal="Doğum verilerini ve transit etkilerini analiz etmek.",
    backstory=(
        "Sen astroloji haritasını tıkır tıkır okuyan ama bunu soğuk teknik verilere boğmayan uzmansın. "
        "Haritadaki açılardan kişinin ruh halini ve fırsatlarını sezgisel olarak analiz edersin."
    ),
    verbose=True,
    llm=llm,
)

guidance_agent = Agent(
    role="Yaşam Rehberi ve Şifa Ajanı",
    goal="Astroloji analizini alıp samimi öz bakım ve tedbir tavsiyeleriyle birleştirmek.",
    backstory=(
        "Sen koruyucu bir yaşam koçusun. 'Bu aralar zihnin çok dolu, melisa çayı iç' gibi öz bakım yönlendirmeleri yaparsın. "
        "Sözleşme/iş süreçlerinde 'Acele etme, iki kez oku, güvendiğin birine danış' dersin. "
        "Dilin son derece samimi, net ve doğaldır. Yılışıklıktan ve ağdalı mistik kelimelerden tamamen uzaksın."
    ),
    verbose=True,
    llm=llm,
)

# --- ENDPOINT'LER ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Mistik Ajan Holdingi Aktif", "code": 200})

@app.route("/analiz-yap", methods=["POST"])
def analiz_yap():
    data = request.json or {}
    musteri_bilgisi = data.get("musteri_bilgisi", "")

    if not musteri_bilgisi:
        return jsonify({"error": "Lütfen 'musteri_bilgisi' parametresini gönderin."}), 400

    task_astro = Task(
        description=f"Şu müşteri için harita ve mevcut transit analizini yap: {musteri_bilgisi}",
        expected_output="Öne çıkan astrolojik etkiler ve enerjiler.",
        agent=astro_agent,
    )

    task_guidance = Task(
        description=(
            "Astroloji analizini al ve müşteri için nihai okumayı yaz. "
            "İçten bir giriş yap, öz bakım (çay, uyku vb.) ve tedbir (imza, karar anı vb.) önerilerini ekle. "
            "Asla yılışık veya abartılı mistik kelimeler kullanma."
        ),
        expected_output="Müşteriye gönderilecek samimi ve net yanıt.",
        agent=guidance_agent,
    )

    crew = Crew(
        agents=[astro_agent, guidance_agent],
        tasks=[task_astro, task_guidance],
        process=Process.sequential,
    )

    result = crew.kickoff()
    return jsonify({"cevap": str(result)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)