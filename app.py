import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Fix", layout="wide")
st.title("⚽ كشاف الإسماعيلي: النسخة المصححة بالمللي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        if start_offset + 300 <= len(data):
            record = list(data[start_offset : start_offset + 300])
            
            # 1. إيجاد العمر (نقطة الارتكاز)
            age_idx = -1
            for i in range(80, 150):
                if 16 <= record[i] <= 42:
                    if record[i+1] == 0:
                        age_idx = i
                        break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # 2. المسح المحيطي مع تصحيح الترحيل للاتجاه الصحيح
                pace, stamina, strength = 0, 0, 0
                for j in range(age_idx + 20, age_idx + 45):
                    if j + 2 < len(record):
                        # فحص بلوك المهارات (البحث عن 3 أرقام منطقية متتالية)
                        if 5 <= record[j] <= 20 and 5 <= record[j+1] <= 20 and 5 <= record[j+2] <= 20:
                            # التعديل بناءً على ملاحظتك (التحرك للأمام):
                            # إذا كانت السرعة تظهر في خانة التحمل، نأخذ الرقم التالي
                            pace = record[j+1]     # كانت تظهر في التحمل، الآن هي السرعة
                            stamina = record[j+2]    # الرقم الذي يليها هو التحمل
                            strength = record[j+3] if j+3 < len(record) else record[j+2] # القوة
                            break
                
                # 3. استخراج PA
                pa = record[age_idx - 11] if 100 <= record[age_idx - 11] <= 200 else None

                if pace > 0: 
                    results.append({
                        "الاسم": name,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "PA": pa
                    })
                    seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        st.success(f"🎯 تم تعديل اتجاه الترحيل! وجدنا {len(df)} لاعب.")
        
        search = st.text_input("🔍 ابحث عن لاعب للتأكد:")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
                    
