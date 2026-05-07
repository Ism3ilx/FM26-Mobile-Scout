import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Advanced Scout", page_icon="⚽", layout="wide")
st.title("🔍 كشاف FM26 Mobile (النسخة المصححة)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء مع مساحة للبيانات الرقمية بعدها
    # سنبحث عن الأسماء التي يتبعها تسلسل باينري معين يميز "اللاعبين" عن "قائمة الأسماء العامة"
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    
    results = []
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة بلوك البيانات الذي يلي الاسم (80 بايت)
        block = list(data[offset : offset + 80])
        
        # الفلترة: في FM، بيانات اللاعب الحقيقية تحتوي على كثافة عددية معينة
        # إذا كان البلوك يحتوي على أصفار كثيرة جداً، فهو غالباً مجرد اسم في القائمة وليس لاعباً
        zero_count = block.count(0)
        if zero_count > 40: continue 

        # البحث عن القدرات (CA/PA) - عادة تكون في النصف الثاني من البلوك
        abilities = [x for x in block[10:] if 100 <= x <= 200]
        
        # البحث عن العمر - في النسخة الموبايل، العمر غالباً يكون في أول 5-8 بايتات بعد الاسم مباشرة
        # وهو رقم ينحصر منطقياً بين 15 و 40
        potential_age = block[2:10]
        age_found = "غير معروف"
        for val in potential_age:
            if 15 <= val <= 40:
                age_found = val
                break
        
        if len(abilities) >= 2:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # شرط إضافي: استبعاد النتائج التي تعطي CA/PA متطابقين دائماً (بيانات وهمية)
            if pa != ca:
                results.append({
                    "الاسم": name,
                    "العمر": age_found,
                    "القدرة الحالية (CA)": ca,
                    "القدرة الكامنة (PA)": pa,
                    "إمكانية التطور": pa - ca
                })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم'])
        
        # تنظيف البيانات: استبعاد الأسماء التي لا تحتوي على أرقام منطقية
        df = df[df['القدرة الكامنة (PA)'] > 110] 
        
        st.success(f"✅ تم تنقية البيانات والعثور على {len(df)} لاعب حقيقي.")
        
        # خيارات العرض
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("ابحث عن لاعب (مثلاً لاعبي الإسماعيلي):")
        with col2:
            sort_opt = st.selectbox("ترتيب حسب:", ["PA (الأفضل مستقبلاً)", "CA (الأفضل حالياً)", "العمر"])

        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]

        sort_map = {"PA (الأفضل مستقبلاً)": "القدرة الكامنة (PA)", "CA (الأفضل حالياً)": "القدرة الحالية (CA)", "العمر": "العمر"}
        df = df.sort_values(by=sort_map[sort_opt], ascending=(True if sort_opt=="العمر" else False))
        
        st.dataframe(df, use_container_width=True)
    else:
        st.error("لم نتمكن من استخراج بيانات دقيقة. حاول رفع ملف حفظ مختلف.")

    st.balloons()
