import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Scout v3", layout="wide")
st.title("🏹 كشاف الإسماعيلي: الإصدار النهائي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء
    search_area_names = data[30000000:] 
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", search_area_names)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    
    # 2. استخراج الطاقات
    player_data = []
    for i in range(1000, 15000000):
        pa = raw_bytes[i]
        if 150 <= pa <= 200:
            age = raw_bytes[i+2]
            if 15 <= age <= 21:
                # التأكد من المهارات (Pace & Stamina)
                if 5 <= raw_bytes[i+6] <= 20 and 5 <= raw_bytes[i+7] <= 20:
                    player_data.append({
                        "PA": pa, "العمر": age, "الموقع": i,
                        "السرعة": raw_bytes[i+6], "التحمل": raw_bytes[i+7]
                    })

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data).drop_duplicates(subset=['الموقع'])
        
        # 3. التحكم في الـ Shift والبحث
        st.sidebar.header("🎯 ضبط الرادار")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0, step=1)
        search_name = st.text_input("🔍 ابحث عن لاعب لمعايرة الاسم (مثلاً: Yamal)")

        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل,
                    "ID": row.الموقع
                })
        
        final_df = pd.DataFrame(final_results)
        
        # تصفية النتائج بالبحث
        if search_name:
            filtered_df = final_df[final_df['الاسم'].str.contains(search_name, case=False)]
            st.subheader(f"📍 نتائج البحث عن: {search_name}")
            st.table(filtered_df)
        
        st.subheader("⭐ قائمة المواهب المكتشفة")
        st.dataframe(final_df.sort_values(by="PA", ascending=False), use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الكشف النهائي", csv, "ismaily_ultimate_scout_v3.csv", "text/csv")
            
