import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Scout", layout="wide")
st.title("⚽ كشاف FM26: النسخة الشاملة (البحث الذكي)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. نمط بحث شامل جداً (يصطاد فالفيردي والأسماء المركبة والقصيرة)
    player_pattern = re.compile(b"([A-Z][a-z]{1,15}(?:\s|-)[A-Z][a-z]{1,15}(?:\s[A-Z][a-z]{1,15})?)")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore').strip()
        start_offset = match.start()
        
        if name in seen_names:
            continue
            
        # 2. بدلاً من رقم ثابت، سنأخذ "بلوك" بيانات (150 بايت) من بداية الاسم
        if start_offset + 150 <= len(data):
            record = list(data[start_offset : start_offset + 150])
            
            # 3. البحث عن "بصمة اللاعب الحقيقي" داخل البلوك:
            # نبحث عن (عمر منطقي) و (PA قوي) و (CA قوي) في أي مكان داخل البلوك
            
            # البحث عن العمر (نبحث في النطاق من 80 إلى 125 بايت بعد البداية)
            age_candidates = [x for x in record[80:130] if 16 <= x <= 42]
            
            # البحث عن القدرات (نبحث في النطاق من 40 إلى 110 بايت بعد البداية)
            potential_candidates = [x for x in record[40:110] if 115 <= x <= 198]
            
            if age_candidates and len(potential_candidates) >= 2:
                # ترتيب القدرات لأخذ الأعلى (PA ثم CA)
                potential_candidates.sort(reverse=True)
                pa = potential_candidates[0]
                ca = potential_candidates[1]
                age = age_candidates[0]
                
                # فلترة إضافية: اللاعب الحقيقي بياناته "نشطة" (غير صفرية)
                non_zero_check = len([x for x in record[40:130] if x != 0])
                
                if non_zero_check > 30: # هذا الرقم يميز اللاعب الحقيقي عن "بقايا النصوص"
                    results.append({
                        "اللاعب": name,
                        "العمر": age,
                        "القدرة الحالية (CA)": ca,
                        "القدرة الكامنة (PA)": pa,
                        "إمكانية التطور": pa - ca,
                        "الجودة": "💎 عالمي" if pa > 165 else "✅ ممتاز"
                    })
                    seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ تم العثور على {len(df)} لاعب حقيقي بنجاح!")
        
        # مربع بحث احترافي
        search_query = st.text_input("🔍 ابحث عن فالفيردي أو أي لاعب آخر:")
        if search_query:
            df = df[df['اللاعب'].str.contains(search_query, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.error("لم يتم العثور على لاعبين. تأكد من أن الملف هو Save Game.")
