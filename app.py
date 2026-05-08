import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Real Madrid Sync", layout="wide")
st.title("🏹 رادار الدراويش: فك تشفير ريال مدريد")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. جرد مخزن الأسماء
    st.sidebar.info("جاري سحب الأسماء...")
    names_area = data[30000000:45000000]
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    names_pool = list(dict.fromkeys(names_pool))

    # 2. البحث عن بصمة كورتوا الدقيقة (33 سنة، 11 سرعة، 8 تحمل، 14 قوة)
    player_data = []
    found_courtois_idx = -1
    
    for i in range(1000, 15000000, 1):
        if i + 10 < len(raw_bytes):
            if raw_bytes[i+2] == 33 and raw_bytes[i+6] == 11 and raw_bytes[i+7] == 8 and raw_bytes[i+8] == 14:
                found_courtois_idx = i
                st.success(f"🎯 تم قنص كورتوا في العنوان: {hex(i)}")
                break
            
    search_start = found_courtois_idx if found_courtois_idx != -1 else 1000
    
    # استخراج اللاعبين (تم تصحيح استدعاء الأعمدة هنا)
    for i in range(search_start, 15000000, 48): 
        if i + 10 >= len(raw_bytes): break
        pa = raw_bytes[i]
        age = raw_bytes[i+2]
        if 15 <= age <= 40 and 130 <= pa <= 200:
            player_data.append({
                "PA": pa, "العمر": age, 
                "السرعة": raw_bytes[i+6], "التحمل": raw_bytes[i+7], 
                "القوة": raw_bytes[i+8], "Offset": i
            })

    if player_data:
        df_players = pd.DataFrame(player_data)
        
        st.sidebar.header("⚙️ ضبط يدوي")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)
        
        # محاولة التوفيق الآلي مع اسم كورتوا
        auto_shift = 0
        if "Thibaut Courtois" in names_pool:
            auto_shift = names_pool.index("Thibaut Courtois")

        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift + auto_shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة, # تم التصحيح من الالسرعة إلى السرعة
                    "التحمل": row.التحمل,
                    "القوة": row.القوة
                })
        
        final_df = pd.DataFrame(final_results)
        
        st.subheader("📊 فحص مطابقة ريال مدريد")
        st.table(final_df.head(5))
        
        st.subheader("💎 كشف مواهب العالم (Wonderkids)")
        # إظهار اللاعبين الواعدين (PA عالي وعمر صغير)
        wonderkids = final_df[(final_df['PA'] >= 175) & (final_df['العمر'] <= 21)]
        st.dataframe(wonderkids.sort_values(by="PA", ascending=False), use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير النهائي", csv, "ismaily_fixed_report.csv", "text/csv")
                    
