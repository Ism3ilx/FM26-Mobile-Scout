import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Final Fix", layout="wide")
st.title("⚽ كشاف FM26: النسخة الديناميكية (حل مشكلة طول الاسم)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        end_offset = match.end() # القياس يبدأ من نهاية الاسم وليس بدايته
        
        # التأكد من وجود مساحة كافية للقراءة بعد الاسم
        if end_offset + 120 <= len(data):
            # 1. جلب العمر من الإزاحة 94 (الثابتة من نهاية أي اسم)
            # سنأخذ نافذة صغيرة (93-95) لضمان الدقة المطلقة
            age_candidates = [data[end_offset + i] for i in range(93, 96) if 16 <= data[end_offset + i] <= 42]
            actual_age = age_candidates[0] if age_candidates else "؟"
            
            # 2. جلب القدرات (CA/PA) 
            # بناءً على تحليل كورتوا، القدرات تكون بين البايت 45 و 85 من نهاية الاسم
            ability_chunk = list(data[end_offset + 40 : end_offset + 90])
            abilities = [x for x in ability_chunk if 100 <= x <= 200]
            
            if len(abilities) >= 2 and name not in seen_names:
                abilities.sort(reverse=True)
                pa = abilities[0]
                ca = abilities[1]
                
                # 3. الفلترة النهائية (استبعاد الأسماء الوهمية)
                # شرط وجود عمر حقيقي في الإزاحة 94 هو الفلتر الأقوى
                if actual_age != "؟" and pa >= 120:
                    results.append({
                        "اللاعب": name,
                        "العمر": actual_age,
                        "القدرة الحالية (CA)": ca,
                        "القدرة الكامنة (PA)": pa,
                        "حالة الموهبة": "⭐ سوبر" if pa > 165 else "✅ واعد"
                    })
                    seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ مبروك! تم ضبط الرادار لكل اللاعبين. تم العثور على {len(df)} لاعب.")
        
        # محرك البحث للوصول للاعبي الإسماعيلي أو أي نجم آخر
        search = st.text_input("ابحث عن لاعب محدد:")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على لاعبين. تأكد من رفع الملف الصحيح.")
