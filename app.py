import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Match", layout="wide")
st.title("⚽ كشاف الإسماعيلي: نسخة الربط التكاملي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
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
            
            # 1. البحث عن "بلوك المهارات" أولاً (لأننا تأكدنا من مكانه)
            skill_idx = -1
            for j in range(100, 180):
                if j + 3 < len(record):
                    # إحنا بندور على 3 أرقام منطقية (السرعة، التحمل، القوة)
                    # بناءً على تعديلك الأخير (الترحيل للأمام)
                    if 5 <= record[j+1] <= 20 and 5 <= record[j+2] <= 20 and 5 <= record[j+3] <= 20:
                        skill_idx = j
                        break
            
            if skill_idx != -1:
                # 2. استخراج الطاقات (المظبوطة بناءً على كلامك)
                pace = record[skill_idx + 1]
                stamina = record[skill_idx + 2]
                strength = record[skill_idx + 3]
                
                # 3. استخراج العمر بناءً على مكانه من المهارات (الرجوع 29 خطوة من السرعة)
                # السرعة موجودة في skill_idx + 1، إذن العمر في (skill_idx + 1 - 29)
                age_pos = (skill_idx + 1) - 29
                
                if 0 <= age_pos < len(record):
                    age = record[age_pos]
                    
                    # فحص إضافي: لو العمر طلع مش منطقي، جرب الخانة اللي جنبه (أحياناً بيكون فيه ترحيل بسيط)
                    if not (16 <= age <= 43):
                        if 16 <= record[age_pos + 1] <= 43: age = record[age_pos + 1]
                        elif 16 <= record[age_pos - 1] <= 43: age = record[age_pos - 1]

                    # 4. استخراج PA (قبل العمر بـ 11 خانة)
                    pa = record[age_pos - 11] if 100 <= record[age_idx - 11] <= 200 else None

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
        st.success(f"🎯 تم الربط! وجدنا {len(df)} لاعب بطاقات وعمر مظبوطين.")
        
        search = st.text_input("🔍 ابحث عن لاعب للتأكد:")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
                
