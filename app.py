import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="FM26 Ismaily SC - Elite Radar", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stDataFrame { border: 1px solid #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 رادار الإسماعيلي - كشاف FM26 Mobile")
st.subheader("نسخة التحليل الديناميكي (إصدار كارفخال-كورتوا-فالفيردي)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (DAT/FMS)", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء بنظام regex يدعم المسافات والحروف اللاتينية
    # يبحث عن نمط: حرف كبير يليه حروف صغيرة، مسافة، ثم حرف كبير يليه حروف صغيرة
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    results = []
    seen_offsets = set()

    for match in player_pattern.finditer(data):
        start_offset = match.start()
        
        try:
            name = match.group(1).decode('latin-1').strip()
        except: continue

        if len(name) < 8 or start_offset in seen_offsets: continue

        # سحب بلوك البيانات (200 بايت لضمان تغطية الإزاحة الناتجة عن طول الاسم)
        if start_offset + 200 <= len(data):
            record = list(data[start_offset : start_offset + 200])
            
            # --- المحرك الديناميكي (Dynamic Engine) ---
            # البحث عن العمر (رقم بين 16 و 42) في المنطقة المتوقعة (بعد الاسم بمسافة)
            found_age = None
            age_idx = -1
            
            # نبحث من Index 80 لـ 130 بناءً على ملاحظتك (104 كرفخال، 110 كورتوا، 112 فالفيردي)
            for i in range(80, 135):
                val = record[i]
                if 16 <= val <= 42:
                    # تأكيد البصمة: المهارات البدنية بتيجي بعد العمر بـ 20 لـ 22 خانة
                    # بنختبر لو فيه مهارات منطقية في المواقع دي
                    pace_check = record[i + 20]
                    stamina_check = record[i + 21]
                    if 5 <= pace_check <= 20 and 5 <= stamina_check <= 20:
                        found_age = val
                        age_idx = i
                        break
            
            if found_age and age_idx != -1:
                # استخراج البيانات بناءً على موقع العمر المكتشف
                pace = record[age_idx + 20]
                stamina = record[age_idx + 21]
                strength = record[age_idx + 22]
                
                # استخراج القدرات (CA/PA) - تسبق العمر بـ 10 لـ 15 خانة تقريباً
                potential_zone = record[age_idx-20 : age_idx]
                pots = [x for x in potential_zone if 110 <= x <= 200]
                pots.sort(reverse=True)
                
                pa = pots[0] if pots else 0
                ca = pots[1] if len(pots) > 1 else (pa - 10 if pa > 10 else 0)

                if pa > 120: # استبعاد اللاعبين الضعفاء والوهميين
                    results.append({
                        "الاسم الكامل": name,
                        "العمر": found_age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "CA": ca,
                        "PA": pa,
                        "الإزاحة (Offset)": age_idx
                    })
                    seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم الكامل', 'العمر'])
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"🎯 تم بنجاح! الرادار اصطاد {len(df)} لاعب حقيقي.")
        
        # أدوات التحكم
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("🔍 ابحث عن نجم محدد:")
        with col2:
            min_pa_filter = st.slider("الحد الأدنى للقدرة (PA):", 120, 200, 140)

        # التصفية
        final_df = df[df['PA'] >= min_pa_filter]
        if search_query:
            final_df = final_df[final_df['الاسم الكامل'].str.contains(search_query, case=False)]

        st.dataframe(final_df, use_container_width=True, height=600)
        
        # تصدير البيانات
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل قائمة الكشاف (CSV)", csv, "ismaily_scout_list.csv", "text/csv")
    else:
        st.warning("⚠️ لم يتم العثور على لاعبين حقيقيين. تأكد من أنك في صفحة Squad داخل اللعبة عند الحفظ.")

