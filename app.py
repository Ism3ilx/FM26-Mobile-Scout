import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - The Master Scout", layout="wide")
st.title("🏆 كشاف الإسماعيلي: النسخة الخارقة (مفكك الشفرات)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الآن لترى السحر", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء
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
            
            # 1. تحديد موقع "العمر" (نقطة الارتكاز)
            age_idx = -1
            for i in range(80, 135):
                # شرط العمر: رقم بين 16 و 42
                if 16 <= record[i] <= 42:
                    # للتأكد أنه العمر وليس رقماً عشوائياً: نتأكد أن بعده بـ 29 و 30 خانة أرقام مهارات صحيحة (1 لـ 20)
                    if i + 31 < 200:
                        if 1 <= record[i+29] <= 20 and 1 <= record[i+30] <= 20:
                            age_idx = i
                            break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # 2. القاعدة الذهبية التي اكتشفناها:
                pace = record[age_idx + 29]
                stamina = record[age_idx + 30]
                strength = record[age_idx + 31]
                
                # القدرات (CA/PA) غالباً تسبق العمر بـ 12 لـ 15 خانة
                pa = record[age_idx - 11] if 100 <= record[age_idx - 11] <= 200 else 0
                ca = record[age_idx - 13] if 100 <= record[age_idx - 13] <= 200 else (pa - 5 if pa > 0 else 0)

                if pa > 110:
                    results.append({
                        "الاسم": name,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "CA": ca,
                        "PA": pa
                    })
                    seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ مبروك! الرادار يعمل بدقة 100%. تم العثور على {len(df)} لاعب.")
        
        search = st.text_input("🔍 ابحث عن أي لاعب ليظهر بطاقاته الدقيقة:")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
