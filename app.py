import streamlit as st
import pandas as pd
import re

# إعدادات الصفحة
st.set_page_config(page_title="Ismaily SC - Ultimate Scout", layout="wide", page_icon="⚽")

st.title("🏹 رادار الإسماعيلي - النسخة المرنة")
st.subheader("إصدار استعادة اللاعبين المفقودين")

# رفع الملف
uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط بحث مطور صيد الأسماء (داني كارفخال أو DANI CARVAJAL)
    # يبحث عن كلمة تبدأ بحرف كبير تليها كلمة أخرى تبدأ بحرف كبير
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})|([A-Z]{3,15}\s[A-Z]{3,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            # محاولة فك التشفير بلغات مختلفة لضمان القراءة
            name = match.group(0).decode('latin-1').strip()
        except: continue

        if len(name) < 5 or start_offset in seen_offsets: continue

        # سحب بلوك البيانات
        if start_offset + 250 <= len(data):
            record = list(data[start_offset : start_offset + 250])
            
            # البحث عن العمر (نقطة الارتكاز)
            age_idx = -1
            for i in range(50, 150): # توسيع نطاق البحث بعد الاسم
                val = record[i]
                if 16 <= val <= 43:
                    # بمجرد إيجاد رقم يصلح عمر، نعتبره نقطة الارتكاز
                    age_idx = i
                    break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # فحص المركز (حارس أم لا) - تعتمد على مهارة رد الفعل
                is_gk = True if record[age_idx + 5] > 10 else False
                
                # تطبيق الأرقام الذهبية
                pace = record[age_idx + 29]
                
                if is_gk:
                    stamina = record[age_idx + 36]
                    strength = record[age_idx + 31]
                    pos = "GK 🧤"
                else:
                    stamina = record[age_idx + 30]
                    strength = record[age_idx + 31]
                    pos = "Field 🏃"
                
                # استخراج القدرات
                pa = record[age_idx - 11] if 100 <= record[age_idx - 11] <= 200 else None
                ca = record[age_idx - 13] if 100 <= record[age_idx - 13] <= 200 else None

                results.append({
                    "الاسم": name,
                    "المركز": pos,
                    "العمر": age,
                    "السرعة": pace,
                    "التحمل": stamina,
                    "القوة": strength,
                    "PA": pa,
                    "CA": ca
                })
                seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        
        # أدوات التحكم
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("🔍 ابحث عن اسم اللاعب:")
        with col2:
            # جعلنا القيمة الافتراضية 0 لكي لا يختفي أحد
            min_pa = st.slider("الحد الأدنى للـ PA:", 0, 200, 0)

        # التصفية
        final_df = df[df['PA'].fillna(0) >= min_pa]
        if search_query:
            final_df = final_df[final_df['الاسم'].str.contains(search_query, case=False)]

        st.dataframe(
            final_df.sort_values(by="PA", ascending=False, na_position='last'), 
            use_container_width=True
        )
    else:
        st.error("⚠️ لم يتم العثور على لاعبين. جرب التأكد من ملف الحفظ.")
            
