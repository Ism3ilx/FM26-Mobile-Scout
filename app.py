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

    # 2. البحث عن الثلاثي (كورتوا - دياز - إندريك)
    # كورتوا: 33 سنة، 11 سرعة، 8 تحمل، 14 قوة
    # دياز: 25 سنة، 14 سرعة، 12 تحمل، 7 قوة
    # إندريك: 19 سنة، 15 سرعة، 14 تحمل، 15 قوة
    
    player_data = []
    found_courtois_idx = -1
    
    for i in range(1000, 15000000, 1):
        # البحث عن بصمة كورتوا الدقيقة
        if raw_bytes[i+2] == 33 and raw_bytes[i+6] == 11 and raw_bytes[i+7] == 8 and raw_bytes[i+8] == 14:
            found_courtois_idx = i
            st.success(f"🎯 تم قنص كورتوا في العنوان: {hex(i)}")
            break
            
    # استخراج اللاعبين بناءً على نقطة كورتوا
    search_start = found_courtois_idx if found_courtois_idx != -1 else 1000
    
    for i in range(search_start, 15000000, 48): # 48 بايت هو متوسط حجم بيانات اللاعب الواحد في FM Mobile
        if i + 10 > len(raw_bytes): break
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
        
        # المزامنة مع الأسماء (كورتوا لازم يقابل اسمه)
        st.sidebar.header("⚙️ ضبط يدوي")
        shift = st.sidebar.number_input("لو الأسماء مش مظبوطة غير الـ Shift", value=0)
        
        # محاولة البحث عن "Thibaut Courtois" في الأسماء لعمل auto-shift
        try:
            courtois_name_idx = names_pool.index("Thibaut Courtois")
            auto_shift = courtois_name_idx
            st.sidebar.write(f"المقترح لضبط كورتوا: {auto_shift}")
        except:
            auto_shift = 0

        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift + auto_shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.الالسرعة,
                    "التحمل": row.التحمل,
                    "القوة": row.القوة
                })
        
        final_df = pd.DataFrame(final_results)
        
        # عرض الثلاثي للتأكد
        st.subheader("📊 فحص مطابقة ريال مدريد")
        st.table(final_df.head(10)) # المفروض أول 3 يكونوا كورتوا ودياز وإندريك
        
        st.subheader("💎 كشف مواهب العالم")
        st.dataframe(final_df[final_df['PA'] >= 180].sort_values(by="PA", ascending=False))
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير النهائي", csv, "ismaily_final_real_sync.csv", "text/csv")
                    
