import streamlit as st
import pandas as pd
import re

# إعدادات الصفحة
st.set_page_config(page_title="Ismaily SC - Ultimate Scout", layout="wide", page_icon="⚽")

# تنسيق واجهة المستخدم
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stDataFrame { border: 1px solid #ffcc00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 رادار الإسماعيلي - النسخة الاحترافية النهائية")
st.subheader("كشاف FM26 Mobile | مفكك الشفرات والمجموعات")

# رفع الملف
uploaded_file = st.file_uploader("ارفع ملف الحفظ لدراسته (صيغة .dat)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء (الاسم الأول والثاني)
    # يدعم الحروف اللاتينية المزخرفة والمسافات
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    # مسح الملف بالكامل
    for match in player_pattern.finditer(data):
        start_offset = match.start()
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        # تخطي الأسماء المكررة والقصيرة
        if len(name) < 8 or start_offset in seen_offsets: continue

        # سحب سجل بيانات اللاعب (250 بايت)
        if start_offset + 250 <= len(data):
            record = list(data[start_offset : start_offset + 250])
            
            # 1. تحديد "نقطة الارتكاز" (موقع العمر)
            age_idx = -1
            for i in range(80, 145):
                val = record[i]
                if 16 <= val <= 43:
                    # فحص "بصمة السرعة" للتأكد من الموقع (+29 هي القاعدة الذهبية)
                    if i + 31 < len(record):
                        p_check = record[i + 29]
                        if 5 <= p_check <= 20: # المهارات البدنية غالباً لا تقل عن 5 للنجوم
                            age_idx = i
                            break
            
            if age_idx != -1:
                age = record[age_idx]
                
                # 2. تحديد المركز (حارس مرمى أم لاعب ميدان)
                # بناءً على كورتوا: رد الفعل (Reflexes) في العمر + 5
                is_gk = True if record[age_idx + 5] > 10 else False
                
                # 3. استخراج الطاقات بناءً على "الأرقام الذهبية"
                pace = record[age_idx + 29] # ثابتة للجميع
                
                if is_gk:
                    # إزاحة الحراس (كورتوا: التحمل في العمر + 36)
                    stamina = record[age_idx + 36]
                    strength = record[age_idx + 31]
                    pos = "GK 🧤"
                else:
                    # إزاحة اللاعبين (كارفخال وفالفيردي: التحمل في العمر + 30)
                    stamina = record[age_idx + 30]
                    strength = record[age_idx + 31]
                    pos = "Field 🏃"
                
                # 4. استخراج القدرات CA/PA
                # استخدام None بدلاً من النصوص لمنع أخطاء الترتيب (Sorting)
                pa_val = record[age_idx - 11]
                ca_val = record[age_idx - 13]
                
                pa = pa_val if 100 <= pa_val <= 200 else None
                ca = ca_val if 100 <= ca_val <= 200 else None

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
        
        # تحويل الأعمدة لأرقام لضمان عمل الترتيب (Sorting)
        df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
        df['CA'] = pd.to_numeric(df['CA'], errors='coerce')

        st.success(f"✅ تم تحليل الملف بنجاح! الرادار وجد {len(df)} لاعب حقيقي.")
        
        # أدوات التحكم (البحث والفلترة)
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("🔍 ابحث عن لاعب محدد:")
        with col2:
            min_pa = st.slider("الحد الأدنى للـ PA:", 100, 200, 130)

        # تطبيق الفلاتر
        final_df = df[df['PA'].fillna(0) >= min_pa]
        if search_query:
            final_df = final_df[final_df['الاسم'].str.contains(search_query, case=False)]

        # عرض الجدول النهائي
        # الترتيب حسب PA تنازلياً، والقيم الفارغة تظهر في الأسفل
        st.dataframe(
            final_df.sort_values(by="PA", ascending=False, na_position='last'), 
            use_container_width=True,
            height=600
        )
        
        # زر التحميل
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل النتائج (CSV)", csv, "ismaily_scout_results.csv", "text/csv")

    else:
        st.error("لم يتم العثور على أي لاعبين. تأكد من أن الملف هو Save Game بصيغة .dat")

