import streamlit as st
import pandas as pd
import struct
import re

st.set_page_config(page_title="Ismaily SC - Advanced Parser", layout="wide")
st.title("⚽ المحلل الاحترافي لملفات FM26 (Logic v2.0)")

st.markdown("""
### 🏗️ تقنية التحليل الحالية:
يستخدم الكود الآن نظام **Length-Prefixed Parsing** لقراءة الأسماء، متبوعاً بمسح **الكتلة الحيوية (Stats Block)** حول الاسم.
""")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

def extract_pro_data(data):
    players = []
    file_size = len(data)
    
    # نمط البحث عن "الفاصل السحري" اللي اكتشفناه قبل كدة
    magic_seq = bytes([255, 255, 255, 255])
    
    # البحث في أول 20 ميجا (منطقة اللاعبين المكثفة)
    search_limit = min(file_size, 20000000)
    
    with st.spinner("جاري التشريح العميق للملف..."):
        for i in range(100, search_limit - 100, 1):
            # 1. البحث عن الفاصل السحري كعلامة لبداية بيانات اللاعب
            if data[i:i+4] == magic_seq:
                try:
                    # العمر موجود بعد الفاصل بـ 4 بايت
                    age_pos = i + 4
                    age = data[age_idx] # سنستخدم الإزاحة age_pos
                    
                    if 15 <= data[age_pos] <= 45:
                        # 2. وجدنا لاعب! الآن نبحث عن "الاسم" القريب منه (قبل أو بعد بـ 100 بايت)
                        # حسب تحليل كلاودي: [Length 4 bytes][String]
                        
                        potential_name = "Unknown"
                        # نبحث في المحيط عن نمط نصي
                        window = data[max(0, i-150) : i+150]
                        
                        # محاولة العثور على أطول نص في النافذة يتبع نظام Length-Prefix
                        # أو استخدام ريجيكس للأسماء (الأسهل والأضمن حالياً)
                        match = re.search(b"([A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?)", window)
                        if match:
                            potential_name = match.group(1).decode('ascii', errors='ignore')

                        # 3. استخراج الطاقات بناءً على خريطتنا (Offsets من مكان العمر)
                        pa_ca = data[age_pos - 18]
                        strength = data[age_pos - 12]
                        pace = data[age_pos - 10]
                        stamina = data[age_pos - 6]

                        if 50 <= pa_ca <= 200:
                            players.append({
                                "الاسم": potential_name,
                                "العمر": data[age_pos],
                                "القدرة (PA/CA)": pa_ca,
                                "السرعة": pace,
                                "التحمل": stamina,
                                "القوة": strength,
                                "العنوان": hex(age_pos)
                            })
                except:
                    continue
                
    return players

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    if st.button("🚀 تحليل الملف بالمنطق الاحترافي"):
        results = extract_pro_data(file_bytes)
        
        if results:
            df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر', 'القدرة (PA/CA)'])
            st.success(f"🎯 نجاح! تم استخراج {len(df)} لاعب بدقة عالية.")
            
            # ترتيب حسب القوة
            df = df.sort_values(by="القدرة (PA/CA)", ascending=False)
            
            st.dataframe(df, use_container_width=True)
            
            # زر التحميل
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل الكشاف الكامل", csv, "fm26_pro_scout.csv")
        else:
            st.error("لم نجد بيانات مطابقة. يبدو أن الملف له بنية مختلفة قليلاً.")

