import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="محلل إزاحات FM26", layout="wide")
st.title("🧪 أداة تجربة الإزاحات لملفات FM26")
st.markdown("""
ارفع ملف حفظ `.fms` أو `.dat` واستخدم أشرطة التمرير لتجربة إزاحات مختلفة
حتى تحصل على بيانات لاعبين منطقية. القيم الافتراضية هي من الكود الأصلي.
""")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ", type=["dat", "fms", "sav"])

# ------------------- إعدادات الإزاحة -------------------
with st.sidebar:
    st.header("⚙️ إعدادات الإزاحة")
    st.markdown("عدّل القيم حتى تظهر بيانات صحيحة.")

    # نطاق البحث عن العمر داخل السجل
    age_search_start = st.number_input("بداية البحث عن العمر (بايت)", value=80, min_value=0, max_value=200)
    age_search_end   = st.number_input("نهاية البحث عن العمر (بايت)", value=140, min_value=0, max_value=200)

    # الإزاحة النسبية لـ CA و PA من موقع العمر
    ca_offset = st.slider("إزاحة CA (نسبة لموقع العمر)", min_value=-50, max_value=50, value=-12)
    pa_offset = st.slider("إزاحة PA (نسبة لموقع العمر)", min_value=-50, max_value=50, value=-10)

    # إزاحات السمات البدنية
    pace_offset    = st.slider("إزاحة السرعة (Pace)", min_value=-20, max_value=50, value=18)
    stamina_offset = st.slider("إزاحة التحمل (Stamina)", min_value=-20, max_value=50, value=19)
    strength_offset= st.slider("إزاحة القوة (Strength)", min_value=-20, max_value=50, value=20)

    # طول السجل حول الاسم
    record_length  = st.number_input("طول السجل حول الاسم (بايت)", value=220, min_value=100, max_value=500)

    # الحد الأدنى لقبول PA
    min_pa = st.slider("الحد الأدنى لـ PA", min_value=0, max_value=200, value=110)

# ------------------- معالجة الملف -------------------
if uploaded_file:
    data = uploaded_file.read()

    # نمط البحث عن الأسماء (معدّل ليشمل حالات أوسع)
    # يمكن تعديله يدويًا إذا كانت الأسماء بتنسيق مختلف
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")

    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except:
            continue

        if len(name) < 8 or start_offset in seen_offsets:
            continue

        if start_offset + record_length > len(data):
            continue

        record = list(data[start_offset : start_offset + record_length])

        # البحث عن العمر
        age = None
        age_idx = -1
        for i in range(age_search_start, min(age_search_end, len(record))):
            if 16 <= record[i] <= 42:
                # تحقق من وجود 0 في الخلية المجاورة (علامة شائعة على قيمة منفردة)
                if (i+1 < len(record) and record[i+1] == 0) or (i-1 >= 0 and record[i-1] == 0):
                    age = record[i]
                    age_idx = i
                    break

        if age is None or age_idx == -1:
            continue

        # استخراج القيم باستخدام الإزاحات الحالية
        ca_candidate = record[age_idx + ca_offset] if 0 <= age_idx + ca_offset < len(record) else 0
        pa_candidate = record[age_idx + pa_offset] if 0 <= age_idx + pa_offset < len(record) else 0
        pace     = record[age_idx + pace_offset]     if 0 <= age_idx + pace_offset     < len(record) else 0
        stamina  = record[age_idx + stamina_offset]  if 0 <= age_idx + stamina_offset  < len(record) else 0
        strength = record[age_idx + strength_offset] if 0 <= age_idx + strength_offset < len(record) else 0

        # تصحيح القيم
        pa = pa_candidate if min_pa <= pa_candidate <= 200 else 0
        ca = ca_candidate if 100 <= ca_candidate <= 200 else (pa - 10 if pa > 0 else 0)

        if pa > 0:  # قبلنا أي PA أعلى من الصفر لتجربة أوسع
            results.append({
                "الاسم": name,
                "العمر": age,
                "السرعة": pace if 1 <= pace <= 20 else None,
                "التحمل": stamina if 1 <= stamina <= 20 else None,
                "القوة": strength if 1 <= strength <= 20 else None,
                "CA": ca,
                "PA": pa,
            })
            seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])

        # فلترة حسب الاسم
        search = st.text_input("🔍 بحث بالاسم")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]

        st.success(f"تم اكتشاف {len(df)} لاعبًا باستخدام الإزاحات الحالية.")
        st.dataframe(df, use_container_width=True)

        # تنزيل CSV للتجربة
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 تحميل CSV", csv, "extracted_players.csv", "text/csv")
    else:
        st.warning("لم يتم العثور على أي لاعبين. جرّب تغيير الإزاحات أو رفع ملف آخر.")
