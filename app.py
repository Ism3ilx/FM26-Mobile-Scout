import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - International Edition", layout="wide")
st.title("⚽ كشاف FM26: نسخة النجوم العالميين (مبابي وجولير)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. تحديث نمط البحث ليشمل الحروف المزخرفة واللاتينية (\x80-\xff)
    # هذا النمط سيتمكن من قراءة Mbappé و Güler وأي اسم يحتوي على علامات
    player_pattern = re.compile(b"([A-Z][a-z\x80-\xff]{1,15}(?:\s|-)[A-Z][a-z\x80-\xff]{1,15}(?:\s[A-Z][a-z\x80-\xff]{1,15})?)")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        try:
            # محاولة فك التشفير باستخدام 'latin-1' لدعم الحروف المزخرفة بشكل صحيح
            name = match.group(1).decode('latin-1').strip()
        except:
            continue
            
        start_offset = match.start()
        
        if name in seen_names or len(name) < 5:
            continue
            
        if start_offset + 150 <= len(data):
            record = list(data[start_offset : start_offset + 150])
            
            # 2. البحث المرن عن العمر (بناءً على إزاحة كورتوا 94 من النهاية)
            # سنبحث في نطاق أوسع قليلاً لضمان عدم ضياع أي لاعب
            age_window = record[80:135]
            age_candidates = [x for x in age_window if 16 <= x <= 42]
            
            # 3. البحث عن القدرات (CA/PA)
            ability_window = record[40:115]
            potential_candidates = [x for x in ability_window if 110 <= x <= 200]
            
            if age_candidates and len(potential_candidates) >= 2:
                potential_candidates.sort(reverse=True)
                pa = potential_candidates[0]
                ca = potential_candidates[1]
                age = age_candidates[0]
                
                # 4. تخفيف شرط "كثافة البيانات" لاصطياد اللاعبين الشباب
                # اللاعب الصغير قد لا يملك مهارات كثيرة مكتملة، لذا سنخفض الرقم لـ 25
                non_zero_check = len([x for x in record[40:130] if x != 0])
                
                if non_zero_check > 25:
                    results.append({
                        "اللاعب": name,
                        "العمر": age,
                        "القدرة الحالية (CA)": ca,
                        "القدرة الكامنة (PA)": pa,
                        "التطور المتوقع": pa - ca,
                        "النوع": "🌟 نجم عالمي" if pa > 170 else "📈 موهبة"
                    })
                    seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ تم بنجاح! الرادار التقط {len(df)} لاعب، بما في ذلك الأسماء المزخرفة.")
        
        # خيارات البحث والفلترة
        search = st.text_input("🔍 ابحث عن اسم (مثلاً: Mbappé أو Güler أو Ismaily):")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False, na=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.error("لم يتم العثور على بيانات. تأكد من أن الملف هو ملف حفظ وليس ملفاً آخر.")
