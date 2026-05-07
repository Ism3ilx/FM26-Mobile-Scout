import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", page_icon="⚽", layout="wide")
st.title("🔍 كشاف FM26 Mobile (الإصدار العميق)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء (نمط: اسم يبدأ بحرف كبير متبوع بمسافة واسم آخر)
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    
    results = []
    
    # فحص الملف
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # سحب الـ 40 بايت التي تلي الاسم مباشرة للبحث فيها
        potential_block = list(data[offset : offset + 40])
        
        # استخراج الأرقام التي تقع في نطاق قدرات اللاعبين (من 50 إلى 200)
        valid_scores = [x for x in potential_block if 50 <= x <= 200]
        
        if len(valid_scores) >= 2:
            # ترتيب الأرقام: الأكبر غالباً هو الـ PA والأصغر هو الـ CA
            valid_scores.sort(reverse=True)
            pa = valid_scores[0]
            ca = valid_scores[1]
            
            # فلتر لاستبعاد النتائج غير المنطقية (مثل أن يكون الـ CA مساوي للـ PA تماماً في كل اللاعبين)
            if pa > 60:
                results.append({
                    "الاسم": name,
                    "القدرة الحالية (CA)": ca,
                    "القدرة الكامنة (PA)": pa,
                    "فارق التطور": pa - ca
                })

    if results:
        # تحويل للجدول وحذف التكرار
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم'])
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ تم العثور على {len(df)} لاعب ببيانات دقيقة!")
        
        # إضافة شريط بحث وفلاتر
        search_query = st.text_input("بحث عن لاعب محدد (مثلاً من الإسماعيلي):")
        if search_query:
            df = df[df['الاسم'].str.contains(search_query, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على بيانات رقمية واضحة. تأكد أن الملف هو ملف حفظ (Save Game) وليس ملف إعدادات.")

    st.balloons()
