import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Scanner", layout="wide")
st.title("⚽ كشاف الإسماعيلي: نسخة البصمة الرقمية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        # سحب سجل بيانات واسع (300 بايت) لضمان عدم ضياع أي مهارة
        if start_offset + 300 <= len(data):
            record = list(data[start_offset : start_offset + 300])
            
            # --- استراتيجية البحث بالبصمة (Fingerprint) ---
            # إحنا بندور على "تتابع" مهارات منطقي (3 أرقام ورا بعض بين 5 و 20)
            # ده بيضمن إننا لقينا بلوك المهارات مش رقم عشوائي
            
            skill_block_idx = -1
            for i in range(100, 180): # المهارات البدنية دايماً في الرينج ده بعد الاسم
                if i + 2 < len(record):
                    # فحص 3 خانات متتالية (السرعة، التحمل، القوة)
                    if 5 <= record[i] <= 20 and 5 <= record[i+1] <= 20 and 5 <= record[i+2] <= 20:
                        # تأكيد إضافي: لازم يكون قبلهم بشوية رقم العمر (16-43)
                        # العمر غالباً بيبعد عن السرعة بـ 29 خانة لورا
                        potential_age_idx = i - 29
                        if 0 <= potential_age_idx < len(record):
                            if 16 <= record[potential_age_idx] <= 43:
                                skill_block_idx = i
                                age_idx = potential_age_idx
                                break
            
            if skill_block_idx != -1:
                results.append({
                    "الاسم": name,
                    "العمر": record[age_idx],
                    "السرعة": record[skill_block_idx],
                    "التحمل": record[skill_block_idx + 1],
                    "القوة": record[skill_block_idx + 2],
                    "PA": record[age_idx - 11] if 100 <= record[age_idx - 11] <= 200 else None,
                    "CA": record[age_idx - 13] if 100 <= record[age_idx - 13] <= 200 else None
                })
                seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        
        st.success(f"✅ تم العثور على {len(df)} لاعب ببصمة صحيحة.")
        
        search = st.text_input("🔍 ابحث عن اسم اللاعب:")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df.sort_values(by="PA", ascending=False, na_position='last'), use_container_width=True)
    else:
        st.error("❌ الرادار لم يتعرف على بصمة المهارات. تأكد من جودة ملف الحفظ.")
                    
