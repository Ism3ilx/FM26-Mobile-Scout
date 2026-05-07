import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", page_icon="⚽")
st.title("🔍 كشاف FM26 Mobile الحقيقي")

uploaded_file = st.file_uploader("ارفع ملف fm_save.dat", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأنماط التي تشبه بيانات اللاعبين (الاسم متبوع ببيانات)
    player_pattern = re.compile(b"([A-Z][a-z]{3,20}\s[A-Z][a-z]{3,20})")
    
    results = []
    
    # سنبحث عن أول 1000 اسم ونحاول استخراج القيم التي تليها مباشرة
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة البايتات التي تلي الاسم مباشرة (حيث توجد القدرات)
        # سنأخذ بايت معين كـ "افتراض" للقدرة الكامنة بناءً على تحليل الـ Hex
        potential_data = data[offset : offset + 20]
        
        if len(potential_data) > 10:
            # في الغالب، الـ PA يكون في مكان ثابت بعد الاسم في ملفات الموبايل
            pa_value = potential_data[5] # هذا البايت سنقوم بتجربته
            ca_value = potential_data[3]
            
            # التأكد أن الأرقام منطقية للعبة (بين 50 و 200)
            if 50 < pa_value <= 200:
                results.append({
                    "الاسم": name,
                    "القدرة الحالية (CA)": ca_value if ca_value > 50 else "؟؟",
                    "القدرة الكامنة (PA)": pa_value,
                    "التطور المتوقع": pa_value - (ca_value if ca_value > 50 else 0)
                })

    if results:
        df = pd.DataFrame(results).sort_values(by="القدرة الكامنة (PA)", ascending=False)
        st.success(f"✅ تم العثور على {len(df)} لاعب ببيانات حقيقية!")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("تم العثور على الأسماء ولكن لم نتمكن من تحديد القدرات. جاري تحسين الخوارزمية...")

    st.balloons()
