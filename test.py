import os
import json
from datetime import datetime
import requests

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

# YENİ CANLI URL: mts.onrender.com
url = "https://mts.onrender.com/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "mistik-secret-key-2026"
}

# Google Sheets Webhook URL
GOOGLE_SHEETS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxcgc69O8M1UmPKpooW-9Qs481rb9FaX8MIWwNYhhq-nSsdhU_j31C4u3CoTVu7-QXegQ/exec"

query_text = "Mystic Thread Studio için 2026 sosyal medya ve büyüme stratejisi oluştur."
data = {"query": query_text}

print("Mystic Thread Studio'ya (https://mts.onrender.com) istek gönderiliyor...")

try:
    response = requests.post(url, json=data, headers=headers, timeout=300)
    
    if response.status_code == 200:
        result = response.json()
        
        output_dir = "holding_raporlari"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        filename_json = os.path.join(output_dir, f"rapor_{timestamp}.json")
        filename_txt = os.path.join(output_dir, f"rapor_{timestamp}.txt")
        filename_pdf = os.path.join(output_dir, f"rapor_{timestamp}.pdf")
        
        # 1. JSON Kaydı
        with open(filename_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
        # 2. TXT Kaydı
        with open(filename_txt, "w", encoding="utf-8") as f:
            f.write(f"=== MYSTIC THREAD STUDIO RAPORU ({timestamp}) ===\n")
            f.write(f"SORGU / KONU: {query_text}\n\n")
            f.write("--- İSTİHBARAT VE STRATEJİ DİREKTÖRLÜĞÜ ---\n")
            f.write(result.get("intelligence_and_strategy", "") + "\n\n")
            f.write("--- KREATİF VE VİDEO KURGU YÖNETMENLİĞİ ---\n")
            f.write(result.get("creative_and_video_guide", "") + "\n\n")
            f.write("--- ÜRETİLEN GÖRSEL URL ---\n")
            f.write(result.get("generated_image_url", "") + "\n")
            
        # 3. PDF Oluşturma (ReportLab)
        doc = SimpleDocTemplate(filename_pdf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor('#4338ca'), spaceAfter=4)
        meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=2)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#1e293b'), spaceBefore=14, spaceAfter=6)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=6)

        elements = [
            Paragraph("MYSTIC THREAD STUDIO", title_style),
            Paragraph(f"Otonom Strateji & Prodüksiyon Raporu | Tarih: {date_str}", meta_style),
            Paragraph(f"<b>Sorgu / Konu:</b> {query_text}", meta_style),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4338ca'), spaceAfter=15),
            Paragraph("1. İSTİHBARAT VE STRATEJİ DİREKTÖRLÜĞÜ", section_style),
            Paragraph(result.get("intelligence_and_strategy", "").replace("\n", "<br/>"), body_style),
            Spacer(1, 10),
            Paragraph("2. KREATİF VE VİDEO KURGU YÖNETMENLİĞİ", section_style),
            Paragraph(result.get("creative_and_video_guide", "").replace("\n", "<br/>"), body_style),
            Spacer(1, 10),
            Paragraph("3. ÜRETİLEN GÖRSEL KONSEPTİ", section_style),
            Paragraph(f"<b>Görsel Bağlantısı:</b> <a href='{result.get('generated_image_url', '')}' color='blue'>{result.get('generated_image_url', '')}</a>", body_style)
        ]
        doc.build(elements)

        # 4. Google Sheets Otomatik Kayıt
        sheet_payload = {
            "date": date_str,
            "query": query_text,
            "intelligence_and_strategy": result.get("intelligence_and_strategy", ""),
            "creative_and_video_guide": result.get("creative_and_video_guide", ""),
            "generated_image_url": result.get("generated_image_url", "")
        }
        try:
            sheet_res = requests.post(GOOGLE_SHEETS_WEBHOOK_URL, json=sheet_payload, timeout=15)
            if sheet_res.status_code == 200:
                print(" Google Sheets Tablosuna Otomatik Aktarıldı!")
        except Exception as se:
            print(" Google Sheets Aktarım Hatası:", se)

        print("\n İşlem Başarılı!")
        print(f" JSON Raporu Kaydedildi: {filename_json}")
        print(f" TXT Raporu Kaydedildi: {filename_txt}")
        print(f" PDF Raporu Oluşturuldu: {filename_pdf}")
        
    else:
        print(f" Yanıt Kodu: {response.status_code}")
        print("Yanıt Metni:", response.text)

except Exception as e:
    print(" İstek Hatası:", e)