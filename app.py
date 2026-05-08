import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Calibration", layout="wide")
st.title("🏹 رادار الدراويش: ضبط المصنع النهائي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء (String Pool)
    st.sidebar.info("جاري فحص مخزن الأسماء...")
    search_area_names = data[30000000:] 
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", search_area_names)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    
    # 2. استخراج بيانات اللاعبين (الطاقات)
    player_data = []
    for i in range(1000, 15000000): # فحص أول 15 مليون بايت
        pa = raw_bytes[i]
        if 150 <= pa <= 200:
            age = raw_bytes[i+2]
            if 15 <= age <= 21:
                # التأكد من منطقية السرعة والتحمل (بين 5 و 20)
                if 5 <= raw_bytes[i+6] <= 20 and 5 <= raw_bytes[i+7] <= 20:
                    player_data.append({"pa": pa, "age": age, "offset": i, 
                                      "speed": raw_bytes[i+6], "stamina": raw_bytes[i+7]})

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data).drop_duplicates(subset=['offset'])
        
        st.sidebar.markdown("---")
        st.sidebar.header("🎯 معايرة الأسماء")
        # السلايدر السحري لضبط الترتيب
        shift = st.sidebar.slider("حرك لضبط الاسم مع العمر والطاقة (Shift)", -100, 100, 0)
        
        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم المتوقع": names_pool[name_idx],
                    "الـ PA (الموهبة)": row.pa,
                    "العمر": row.age,
                    "السرعة": row.speed,
                    "التحمل": row.stamina,
                    "ID": row.offset
                })
        
        final_df = pd.DataFrame(final_results)
        
        # عرض النتائج
        st.success(f"🔍 تم العثور على {len(final_df)} موهبة.")
        
        # البحث عن يامال لتسهيل المعايرة
        yamal_check = final_df[final_df['الاسم المتوقع'].str.contains("Yamal", case=False)]
        if not yamal_check.empty:
            st.warning("📍 رادار يامال: تم العثور على يامال في القائمة! تحقق من عمره (يجب أن يكون 18).")
            st.table(yamal_check)
        else:
            st.info("💡 حرك السلايدر حتى يظهر 'Lamine Yamal' في الجدول.")

        st.dataframe(final_df.sort_values(by="الـ PA (الموهبة)", ascending=False), use_container_width=True)
        
        # التحميل
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل كشف المواهب المظبوط", csv, "ismaily_perfect_scout.csv", "text/csv")
                    
