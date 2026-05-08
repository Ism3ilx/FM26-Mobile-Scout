import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Gold Scout", layout="wide")
st.title("🏹 كشاف الإسماعيلي: النسخة الذهبية المستقرة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء (بيدور على أي اسمين بيبدأوا بحروف كبيرة)
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        if start_offset + 200 <= len(data):
            record = list(data[start_offset : start_offset + 200])
            
            # تحديد موقع العمر (نقطة الارتكاز)
            age_idx = -1
            for i in range(70, 140):
                val = record[i]
                # شرط العمر + التأكد من وجود مهارة منطقية في +29 (السرعة)
                if 16 <= val <= 43:
                    if i + 31 < len(record):
                        if 1 <= record[i+29] <= 20: 
                            age_idx = i
                            break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # تطبيق "المسطرة الذهبية" الموحدة (بدون تفرقة حراس)
                pace = record[age_idx + 29]
                stamina = record[age_idx + 30]
                strength = record[age_idx + 31]
                
                # القدرات (CA/PA) - بنظام الأرقام فقط لمنع أخطاء الترتيب
                pa_val = record[age_idx - 11]
                ca_val = record[age_idx - 13]
                
                pa = pa_val if 100 <= pa_val <= 200 else None
                ca = ca_val if 100 <= ca_val <= 200 else None

                results.append({
                    "الاسم": name,
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
        
        st.success(f"✅ الرادار شغال! تم العثور على {len(df)} لاعب.")

        # أدوات البحث والفلترة
        search = st.text_input("🔍 ابحث عن اسم اللاعب:")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        # الترتيب حسب PA (القيم الفارغة تنزل تحت)
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
    else:
        st.error("⚠️ لم يتم العثور على لاعبين. تأكد من ملف الحفظ.")
                
