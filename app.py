import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Global Scout", layout="wide")
st.title("⚽ كشاف FM26: النسخة العالمية الشاملة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. نمط بحث "وحشي" يصطاد أي شيء يشبه الاسم (بما في ذلك الحروف المزخرفة)
    # هذا النمط يبحث عن حرف كبير يليه حروف صغيرة (بما في ذلك الحروف اللاتينية المزخرفة)
    player_pattern = re.compile(b"([A-Z][a-z\x80-\xff]{2,15}(?:\s|-)[A-Z][a-z\x80-\xff]{2,15})")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        raw_name = match.group(1)
        
        # محاولة فك التشفير بأكثر من طريقة لدعم "مبابي وجولير"
        name = ""
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                name = raw_name.decode(encoding).strip()
                break
            except:
                continue
        
        if not name or name in seen_names or len(name) < 5:
            continue
            
        start_offset = match.start()
        
        # قراءة بلوك البيانات (توسيع النطاق لضمان عدم ضياع أي لاعب)
        if start_offset + 160 <= len(data):
            record = list(data[start_offset : start_offset + 160])
            
            # 2. البحث عن العمر (الخانة 110 من البداية هي المفتاح الذي وجدناه لكورتوا)
            # سنبحث في نطاق (105-115) لاستخراج العمر بدقة
            age_zone = record[105:118]
            age_candidates = [x for x in age_zone if 16 <= x <= 43]
            
            # 3. البحث عن القدرات (نطاق أوسع لاصطياد فالفيردي ومبابي)
            ability_zone = record[50:110]
            potentials = [x for x in ability_zone if 110 <= x <= 200]
            
            if age_candidates and len(potentials) >= 2:
                potentials.sort(reverse=True)
                pa = potentials[0]
                ca = potentials[1]
                age = age_candidates[0]
                
                # 4. فلتر "اللاعب الحقيقي" (Data Density)
                # فحص عدد البايتات النشطة حول الاسم (اللاعب الحقيقي ملفه "مليء" بالبيانات)
                data_density = len([x for x in record[40:140] if x != 0])
                
                if data_density > 28: # تقليل الرقم قليلاً لضمان ظهور كل اللاعبين
                    results.append({
                        "الاسم": name,
                        "العمر": age,
                        "CA": ca,
                        "PA": pa,
                        "النمو": pa - ca,
                        "الحالة": "🌟 سوبر" if pa > 170 else "✅ محترف"
                    })
                    seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="PA", ascending=False)
        
        # واجهة الفلترة
        st.success(f"✅ تم العثور على {len(df)} لاعب (تم دعم الأسماء المزخرفة)")
        
        c1, c2 = st.columns(2)
        with c1:
            search = st.text_input("🔍 ابحث عن لاعب (Mbappe, Guler, Ismaily...):")
        with c2:
            min_pa = st.number_input("الحد الأدنى للـ PA:", 100, 200, 120)
            
        final_df = df[df['PA'] >= min_pa]
        if search:
            final_df = final_df[final_df['الاسم'].str.contains(search, case=False, na=False)]
            
        st.dataframe(final_df, use_container_width=True)
    else:
        st.error("لم يتم العثور على لاعبين. جرب رفع ملف آخر.")

# تم حذف البلالين نهائياً
