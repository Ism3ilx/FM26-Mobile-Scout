import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Scout", layout="wide")
st.title("⚽ كشاف الإسماعيلي: النسخة الاحترافية (كاشف الحراس واللاعبين)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ لدراسته", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط بحث مرن جداً عشان مفيش لاعب يهرب
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        if start_offset + 250 <= len(data):
            record = list(data[start_offset : start_offset + 250])
            
            # 1. تحديد موقع العمر (نقطة الارتكاز)
            age_idx = -1
            for i in range(80, 145):
                if 16 <= record[i] <= 42:
                    # فحص "بصمة السرعة" للتأكد إن ده الـ Index الصح (دايماً +29)
                    if i + 29 < len(record) and 1 <= record[i+29] <= 20:
                        age_idx = i
                        break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # 2. فحص نوع اللاعب (حارس مرمى أم لاعب ميدان)
                # الحراس عندهم مهارات عالية في Index +5 (Reflexes)
                is_gk = True if record[age_idx + 5] > 10 else False
                
                # 3. تطبيق "الأرقام الذهبية" بناءً على النوع
                pace = record[age_idx + 29] # ثابتة للكل كما اكتشفنا
                
                if is_gk:
                    # إزاحة الحراس (بناءً على كورتوا)
                    stamina = record[age_idx + 36] 
                    strength = record[age_idx + 31] # القوة غالباً ثابتة أو قريبة
                    pos = "GK 🧤"
                else:
                    # إزاحة لاعبي الميدان (بناءً على كارفخال وفالفيردي)
                    stamina = record[age_idx + 30]
                    strength = record[age_idx + 31]
                    pos = "Outfield 🏃"
                
                # 4. القدرات الكامنة (PA) - (تقريباً -11 من العمر)
                pa = record[age_idx - 11]
                ca = record[age_idx - 13]

                results.append({
                    "الاسم": name,
                    "المركز": pos,
                    "العمر": age,
                    "السرعة": pace,
                    "التحمل": stamina,
                    "القوة": strength,
                    "PA": pa if 100 <= pa <= 200 else "---",
                    "CA": ca if 100 <= ca <= 200 else "---"
                })
                seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        st.success(f"✅ تم العثور على {len(df)} لاعب حقيقي وتصنيفهم!")
        
        # فلتر البحث
        search = st.text_input("🔍 ابحث عن لاعبك المفضل (مثلاً: Courtois):")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False), use_container_width=True)
    else:
        st.error("❌ لم نجد لاعبين. تأكد إن ملف الـ .dat هو ملف الحفظ الفعلي.")
