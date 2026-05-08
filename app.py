import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Fix", layout="wide")
st.title("⚽ كشاف الإسماعيلي: النسخة النهائية المستقرة")

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
        except: 
            continue

        if len(name) < 8 or start_offset in seen_offsets: 
            continue

        if start_offset + 300 <= len(data):
            record = list(data[start_offset : start_offset + 300])
            
            # 1. البحث عن العمر (مستقل)
            age = 0
            found_age_idx = -1
            for i in range(80, 160):
                if 16 <= record[i] <= 43:
                    if i + 1 < len(record) and record[i+1] == 0:
                        age = record[i]
                        found_age_idx = i
                        break

            # 2. البحث عن المهارات (مستقل - مع تصحيح الترحيل للأمام j+1)
            pace, stamina, strength = 0, 0, 0
            for j in range(100, 200):
                if j + 3 < len(record):
                    # فحص بلوك المهارات
                    if 5 <= record[j+1] <= 20 and 5 <= record[j+2] <= 20 and 5 <= record[j+3] <= 20:
                        pace = record[j+1]
                        stamina = record[j+2]
                        strength = record[j+3]
                        break

            # 3. استخراج PA بناءً على مكان العمر
            pa = None
            if found_age_idx != -1:
                pa_pos = found_age_idx - 11
                if pa_pos >= 0:
                    pa_val = record[pa_pos]
                    pa = pa_val if 100 <= pa_val <= 200 else None

            # إضافة اللاعب إذا اكتملت البيانات الأساسية
            if age > 0 and pace > 0:
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
        st.success(f"✅ تم إصلاح الكود! الرادار وجد {len(df)} لاعب.")
        
        search = st.text_input("🔍 ابحث عن اسم اللاعب (مثل Valverde):")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
    else:
        st.error("⚠️ لم نجد بيانات منطقية. تأكد من رفع ملف الحفظ الصحيح.")
                                                   
