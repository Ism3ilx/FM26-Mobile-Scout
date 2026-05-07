import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", page_icon="⚽", layout="wide")
st.title("🔍 كشاف FM26 Mobile (تحسين الرادار)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن أسماء اللاعبين
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة 100 بايت بعد الاسم لضمان الوصول لمكان العمر والقدرات
        block = list(data[offset : offset + 100])
        
        # 1. البحث عن القدرات (بين 50 و 200)
        abilities = [x for x in block if 50 <= x <= 200]
        
        # 2. البحث عن العمر (تحسين الرادار):
        # في FM Mobile، العمر غالباً يسبق القدرات بمسافة قصيرة أو يليها مباشرة
        # سنبحث عن أول رقم منطقي بين 15 و 38 في البلوك بالكامل
        age_candidates = [x for x in block if 15 <= x <= 38]
        
        if len(abilities) >= 2:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # محاولة التقاط العمر: سنأخذ الرقم الذي يظهر قبل القدرات مباشرة إذا وجد
            # أو أول رقم في قائمة المرشحين
            age = "غير معروف"
            if age_candidates:
                # لتجنب تداخل العمر مع أرقام القدرات، نختار الرقم الذي يتكرر كعمر منطقي
                age = age_candidates[0]
            
            if pa > 90: # تركيز على اللاعبين الجيدين فقط
                results.append({
                    "الاسم": name,
                    "العمر": age,
                    "القدرة الحالية (CA)": ca,
                    "القدرة الكامنة (PA)": pa,
                    "فارق التطور": pa - ca
                })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم'])
        
        # تحويل عمود العمر لأرقام لسهولة الترتيب، مع معالجة "غير معروف"
        df['العمر'] = pd.to_numeric(df['العمر'], errors='coerce')
        
        st.success(f"✅ تم تحليل الملف بنجاح!")
        
        col1, col2 = st.columns(2)
        with col1:
            min_pa = st.slider("الحد الأدنى للقدرة الكامنة (PA)", 100, 200, 140)
        with col2:
            max_age = st.slider("الحد الأقصى للعمر", 15, 40, 25)

        # تطبيق الفلاتر
        filtered_df = df[(df['القدرة الكامنة (PA)'] >= min_pa) & 
                         ((df['العمر'] <= max_age) | (df['العمر'].isna()))]
        
        st.dataframe(filtered_df.sort_values(by="القدرة الكامنة (PA)", ascending=False), use_container_width=True)
    else:
        st.warning("جرب رفع ملف حفظ مختلف، يبدو أن هيكل هذا الملف معقد قليلاً.")

    st.balloons()
