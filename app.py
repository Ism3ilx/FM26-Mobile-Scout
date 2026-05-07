import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", page_icon="⚽", layout="wide")
st.title("🔍 كشاف FM26 Mobile (الإصدار الاحترافي)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن أسماء اللاعبين
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    
    results = []
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # سحب 50 بايت بعد الاسم للبحث عن (العمر، القدرة الحالية، القدرة الكامنة)
        block = list(data[offset : offset + 50])
        
        # 1. البحث عن القدرات (بين 50 و 200)
        abilities = [x for x in block if 50 <= x <= 200]
        
        # 2. البحث عن العمر المحتمل (بين 14 و 40)
        # غالباً ما يكون العمر في أول 10 بايتات بعد الاسم مباشرة
        age_candidates = [x for x in block[:15] if 14 <= x <= 40]
        
        if len(abilities) >= 2:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # تحديد العمر (نأخذ أول قيمة منطقية تظهر في البلوك)
            age = age_candidates[0] if age_candidates else "غير معروف"
            
            # فلتر إضافي لاستبعاد البيانات العشوائية
            if pa > 80:
                results.append({
                    "الاسم": name,
                    "العمر": age,
                    "القدرة الحالية (CA)": ca,
                    "القدرة الكامنة (PA)": pa,
                    "فارق التطور": pa - ca
                })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم'])
        
        # إضافة خيار لترتيب النتائج حسب العمر أو القدرة
        sort_by = st.selectbox("ترتيب حسب:", ["القدرة الكامنة (PA)", "العمر", "فارق التطور"])
        
        if sort_by == "القدرة الكامنة (PA)":
            df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        elif sort_by == "العمر":
            df = df.sort_values(by="العمر", ascending=True)
        else:
            df = df.sort_values(by="فارق التطور", ascending=False)
            
        st.success(f"✅ تم العثور على {len(df)} لاعب!")
        
        # عرض الجدول النهائي
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على بيانات. تأكد من رفع ملف الحفظ الصحيح.")

    st.balloons()
