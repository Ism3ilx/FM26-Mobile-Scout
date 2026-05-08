import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Master Key", layout="wide")
st.title("🏹 رادار الدراويش: فك التشفير النهائي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. تنظيف مخزن الأسماء (فلتر الأندية والدوريات)
    st.sidebar.info("🔍 جاري جرد وتصفية الأسماء...")
    names_area = data[30000000:45000000]
    # نمط يجلب الاسم الكامل (اسمين وبينهم مسافة) ويستبعد الكلمات القصيرة جداً
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = []
    # فلتر لاستبعاد الكلمات المشهورة للأندية
    trash_words = ['Madrid', 'Paris', 'City', 'United', 'League', 'Club', 'Team', 'Stadium', 'Division']
    for n in found_names:
        name_str = n.decode('ascii', errors='ignore')
        if name_str not in names_pool and not any(w in name_str for w in trash_words):
            names_pool.append(name_str)

    # 2. البحث عن "كورتوا" (البوصلة)
    # كورتوا: 33 سنة، 11 سرعة، 8 تحمل، 14 قوة
    st.info("🎯 جاري قنص 'Thibaut Courtois' لتحديد نقطة الصفر...")
    courtois_offset = -1
    for i in range(1000, 20000000):
        # بصمة كورتوا: العمر (i+2)، السرعة (i+6)، التحمل (i+7)، القوة (i+8)
        if raw_bytes[i+2] == 33 and raw_bytes[i+6] == 11 and raw_bytes[i+7] == 8 and raw_bytes[i+8] == 14:
            courtois_offset = i
            break
    
    if courtois_offset != -1:
        st.success(f"📍 تم العثور على كورتوا في العنوان: {hex(courtois_offset)}")
        
        # 3. استخراج اللاعبين بناءً على المسافة الحقيقية
        # في FM Mobile المسافة غالباً بتكون ثابتة (مثلاً 100 أو 120 بايت)
        # هنجرب نمسح المنطقة اللي بعد كورتوا بذكاء
        final_list = []
        # البحث عن أي بايت PA في المنطقة المحيطة بكورتوا
        for i in range(1000, 15000000, 4): # فحص كل 4 بايتات للسرعة
            pa = raw_bytes[i]
            if 140 <= pa <= 200:
                age = raw_bytes[i+2]
                if 15 <= age <= 40:
                    pace = raw_bytes[i+6]
                    if 5 <= pace <= 20: # شرط منطقية السرعة
                        final_list.append({
                            "PA": pa, "العمر": age, "السرعة": pace,
                            "التحمل": raw_bytes[i+7], "القوة": raw_bytes[i+8],
                            "Address": i
                        })
        
        df_players = pd.DataFrame(final_list).drop_duplicates(subset=['Address'])
        
        # 4. المزامنة (Shift)
        st.sidebar.header("⚙️ ضبط يدوي")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)
        
        # محاولة وضع كورتوا في مكانه
        auto_shift = 0
        if "Thibaut Courtois" in names_pool:
            # بنحسب كورتوا ترتيبه كام في قائمة الـ PA ونخليه يقابل اسمه
            courtois_data_idx = df_players[df_players['Address'] == courtois_offset].index
            if not courtois_data_idx.empty:
                name_idx = names_pool.index("Thibaut Courtois")
                auto_shift = name_idx - courtois_data_idx[0]
        
        applied_shift = shift + auto_shift
        
        results = []
        for idx, row in enumerate(df_players.itertuples()):
            n_idx = idx + applied_shift
            if 0 <= n_idx < len(names_pool):
                results.append({
                    "الاسم": names_pool[n_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل,
                    "القوة": row.القوة
                })
        
        final_df = pd.DataFrame(results)
        
        # عرض التأكيد
        st.subheader("✅ فحص مطابقة ريال مدريد")
        targets = ["Courtois", "Brahim", "Endrick"]
        st.table(final_df[final_df['الاسم'].str.contains('|'.join(targets), case=False)])

        st.subheader("💎 قائمة المواهب (PA 180+)")
        st.dataframe(final_df[final_df['PA'] >= 180].sort_values(by="PA", ascending=False), use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الكشف النهائي", csv, "ismaily_final_sync.csv", "text/csv")
    else:
        st.error("❌ لم نجد بصمة كورتوا (33-11-8-14). تأكد أنك لم تقم بتغيير طاقاته في اللعبة.")
                
