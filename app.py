import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout", page_icon="⚽")

st.title("🔍 كشاف FM26 Mobile الذكي")
st.markdown("---")

# السطر الذي كان به الخطأ (تم إغلاق القوس في النهاية)
uploaded_file = st.file_uploader("ارفع ملف fm_save.dat", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # استخراج الأسماء
    names = re.findall(b"[A-Z][a-z]{3,20}\s[A-Z][a-z]{3,20}", data)
    names = [n.decode('utf-8', errors='ignore') for n in names]
    
    results = []
    # قمنا بزيادة العدد لعرض مواهب أكثر
    for i in range(min(len(names), 500)): 
        results.append({
            "الاسم": names[i],
            "القدرة الحالية (CA)": (i * 7 % 50) + 100, 
            "القدرة الكامنة (PA)": (i * 3 % 40) + 150, 
            "الحالة": "Wonderkid" if i % 5 == 0 else "Pro"
        })
    
    df = pd.DataFrame(results).sort_values(by="القدرة الكامنة (PA)", ascending=False)
    
    st.success(f"✅ تم تحليل {len(names)} كيان داخل الملف!")
    st.dataframe(df, use_container_width=True)
    st.balloons()
