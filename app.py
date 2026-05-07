import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Final Boss", layout="wide")
st.title("⚽ كشاف FM26: النسخة المعتمدة نهائياً")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء (بداية السجل)
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        start_offset = match.start() # نعتمد على بداية الاسم كمرجع ثابت
        
        # قراءة بلوك بيانات كبير من بداية الاسم (200 بايت) لضمان شمول كل البيانات
        if start_offset + 200 <= len(data):
            record = list(data[start_offset : start_offset + 200])
            
            # 1. استخراج العمر (بناءً على عملية تشريح كورتوا: البداية + 110 بايت تقريباً)
            # سنبحث في نطاق صغير حول 110 لضمان الدقة لكل اللاعبين
            age_window = record[105:115]
            age_candidates = [x for x in age_window if 16 <= x <= 42]
            actual_age = age_candidates[0] if age_candidates else "؟"
            
            # 2. استخراج القدرات (CA/PA)
            # في ملفك، القدرات تقع عادة بين البايت 60 و 100 من بداية الاسم
            ability_window = record[60:105]
            abilities = [x for x in ability_window if 100 <= x <= 200]
            
            if len(abilities) >= 2 and name not in seen_names:
                abilities.sort(reverse=True)
                pa = abilities[0]
                ca = abilities[1]
                
                # 3. الفلترة القوية (استبعاد الوهميين)
                # اللاعب الحقيقي لديه "عمر" منطقي في الخانة المحددة
                if actual_age != "؟" and pa >= 120:
                    results.append({
                        "اللاعب": name,
                        "العمر": actual_age,
                        "CA": ca,
                        "PA": pa,
                        "الفرق": pa - ca,
                        "الوضع": "💎 واعد" if pa > 160 and int(actual_age) < 22 else "✅ متاح"
                    })
                    seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم بنجاح! العثور على {len(df)} لاعب حقيقي.")
        
        # فلتر البحث (للبحث عن لاعبي الإسماعيلي مثلاً)
        search = st.text_input("ابحث عن لاعب أو فريق:")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على لاعبين. جرب رفع الملف مرة أخرى.")
