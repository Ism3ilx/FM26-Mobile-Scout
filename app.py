import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Clean Scout", layout="wide")
st.title("⚽ كشاف FM26: نسخة اللاعبين الحقيقيين (بدون وهمي)")

uploaded_file = st.file_uploader("ارفع ملف fm_save.dat أو .fms", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. فلترة الأسماء الحقيقية فقط
    # سنبحث عن الأسماء التي يتبعها مباشرة بيانات رقمية (وليس بايتات فارغة)
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة قطعة البيانات خلف الاسم مباشرة
        chunk = data[offset : offset + 60]
        
        # ميزة الفلترة: اللاعب الحقيقي بياناته "مزدحمة"
        # إذا وجدنا أكثر من 15 بايت قيمتها صفر في أول 40 بايت، فهذا اسم وهمي من القاموس
        if chunk[:40].count(0) > 15:
            continue
            
        # البحث عن CA و PA (يجب أن يكونا أرقاماً قوية ومختلفة)
        stats = [x for x in chunk if 110 <= x <= 200]
        
        if len(stats) >= 2:
            stats.sort(reverse=True)
            pa = stats[0]
            ca = stats[1]
            
            # محاولة جلب العمر بدقة أكبر (غالباً يكون في أول 10 بايتات بعد الاسم)
            age_candidates = [x for x in chunk[:15] if 16 <= x <= 39]
            age = age_candidates[0] if age_candidates else "مجهول"
            
            # منع التكرار والأسماء الغريبة
            if name not in seen_names and pa > 125: # رفعنا الحد الأدنى لاستبعاد الضعفاء والوهميين
                results.append({
                    "اللاعب": name,
                    "العمر": age,
                    "القدرة الحالية (CA)": ca,
                    "القدرة الكامنة (PA)": pa,
                    "إمكانية التطور": pa - ca
                })
                seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        # ترتيب تلقائي للأفضل
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ تم العثور على {len(df)} لاعب حقيقي.")
        
        # إضافة مربع بحث للوصول للاعبي الإسماعيلي بسرعة
        search_name = st.text_input("ابحث عن لاعب محدد:")
        if search_name:
            df = df[df['اللاعب'].str.contains(search_name, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على لاعبين حقيقيين بمعايير قوية. تأكد من أن الملف هو Save Game.")

    # تم حذف سطر البلالين (st.balloons) بناءً على طلبك
