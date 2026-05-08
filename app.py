import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Scout", layout="wide")
st.title("⚽ كشاف الإسماعيلي: النسخة النهائية المصححة")

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
            
            # 1. البحث عن "بلوك المهارات" (السرعة، التحمل، القوة)
            skill_idx = -1
            for j in range(100, 180):
                if j + 3 < len(record):
                    # نطبق القاعدة التي ضبطت معك الطاقات (الترحيل للأمام)
                    if 5 <= record[j+1] <= 20 and 5 <= record[j+2] <= 20 and 5 <= record[j+3] <= 20:
                        skill_idx = j
                        break
            
            if skill_idx != -1:
                # 2. استخراج الطاقات الصحيحة
                pace = record[skill_idx + 1]
                stamina = record[skill_idx + 2]
                strength = record[skill_idx + 3]
                
                # 3. تحديد مكان العمر بناءً على مكانه من السرعة (الرجوع 29 خطوة)
                age_pos = (skill_idx + 1) - 29
                
                if 0 <= age_pos < len(record):
                    # محاولة جلب العمر الحقيقي
                    age = record[age_pos]
                    
                    # فحص منطقية العمر (بين 16 و 43) وتصحيحه لو تطلب الأمر
                    if not (16 <= age <= 43):
                        if 16 <= record[age_pos + 1] <= 43: age = record[age_pos + 1]
                        elif 16 <= record[age_pos - 1] <= 43: age = record[age_pos - 1]

                    # 4. استخراج PA (قبل مكان العمر بـ 11 خانة)
                    # تم تصحيح الخطأ هنا (استبدال age_idx بـ age_pos)
                    pa = record[age_pos - 11] if 100 <= record[age_pos - 11] <= 200 else None
                    ca = record[age_pos - 13] if 100 <= record[age_pos - 13] <= 200 else None

                    results.append({
                        "الاسم": name,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "PA": pa,
                        "CA": ca
                    })
                    seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        
        st.success(f"🎯 الرادار يعمل بكفاءة! تم العثور على {len(df)} لاعب.")
        
        search = st.text_input("🔍 ابحث عن لاعب (مثل: Carvajal):")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
    else:
        st.error("⚠️ لم يتم العثور على لاعبين. تأكد أن الملف هو Save Game فعلي.")

