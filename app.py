import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", layout="wide")
st.title("⚽ كشاف الإسماعيلي: نسخة المسح المحيطي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        if start_offset + 300 <= len(data):
            record = list(data[start_offset : start_offset + 300])
            
            # 1. إيجاد العمر (نقطة الارتكاز التي ضبطت معك)
            age_idx = -1
            for i in range(80, 150):
                if 16 <= record[i] <= 42:
                    # تأكيد إضافي أن هذا هو العمر (يكون محاطاً بأصفار في الغالب)
                    if record[i+1] == 0 or record[i-1] == 0:
                        age_idx = i
                        break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # 2. المسح المحيطي للطاقات البدنية
                # سنبحث عن أول "تجمع" لـ 3 أرقام (Pace, Stamina, Strength) 
                # في النطاق من (العمر + 20) إلى (العمر + 45)
                
                pace, stamina, strength = 0, 0, 0
                for j in range(age_idx + 20, age_idx + 45):
                    if j + 2 < len(record):
                        # مهارات النجوم مثل كارفخال وفالفيردي دايما فوق 10
                        if 8 <= record[j] <= 20 and 5 <= record[j+1] <= 20 and 8 <= record[j+2] <= 20:
                            pace = record[j]
                            stamina = record[j+1]
                            strength = record[j+2]
                            break
                
                # 3. استخراج PA (دائماً يسبق العمر بمسافة ثابتة تقريباً)
                pa = record[age_idx - 11] if 100 <= record[age_idx - 11] <= 200 else None

                if pace > 0: # لا تضف اللاعب إلا لو وجدت طاقاته
                    results.append({
                        "الاسم": name,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "PA": pa
                    })
                    seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        st.success(f"🎯 تم ضبط الإحداثيات! وجدنا {len(df)} لاعب بطاقات دقيقة.")
        
        search = st.text_input("🔍 ابحث عن لاعب (مثلاً: Valverde):")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
                
