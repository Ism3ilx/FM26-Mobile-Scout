import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Decoder", layout="wide")
st.title("🏹 رادار الدراويش: فك التشفير بالبصمة المدريدية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء (String Pool)
    # البحث عن الأسماء في المنطقة الكثيفة (30MB - 45MB)
    names_area = data[30000000:45000000]
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    names_pool = list(dict.fromkeys(names_pool)) # تنظيف وتجهيز القائمة

    # 2. استخراج الطاقات بنظام الـ Blocks
    # البحث عن بصمة كورتوا (عمر 33، سرعة 11، تحمل 8، قوة 14)
    st.info("🔍 جاري البحث عن بصمة 'Thibaut Courtois' لمعايرة الرادار...")
    
    player_data = []
    # فحص شامل لأول 15 مليون بايت (منطقة بيانات اللاعبين)
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 130 <= pa <= 200:
            age = raw_bytes[i+2]
            pace = raw_bytes[i+6]
            stamina = raw_bytes[i+7]
            strength = raw_bytes[i+8]
            
            # التحقق من المنطقية
            if 15 <= age <= 40 and 5 <= pace <= 20:
                player_data.append({
                    "PA": pa, "Age": age, "Pace": pace, 
                    "Stamina": stamina, "Strength": strength, "Offset": i
                })

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data).drop_duplicates(subset=['Offset'])
        
        # 3. المزامنة الآلية (Auto-Sync)
        # البحث عن موقع كورتوا في البيانات المستخرجة
        # بصمة كورتوا: العمر 33، السرعة 11
        courtois_matches = df_players[(df_players['Age'] == 33) & (df_players['Pace'] == 11)]
        
        st.sidebar.header("⚙️ لوحة التحكم")
        if not courtois_matches.empty:
            # حساب الـ Shift التلقائي لجعل كورتوا يظهر في مكانه
            auto_shift = -(courtois_matches.index[0]) 
            st.sidebar.success(f"✅ تم اكتشاف البصمة! المزامنة الآلية: {auto_shift}")
        else:
            auto_shift = 0
            st.sidebar.warning("⚠️ لم يتم رصد البصمة آلياً، استخدم التعديل اليدوي.")

        shift = st.sidebar.number_input("تعديل يدوي للترتيب (Shift)", value=int(auto_shift))

        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA (الموهبة)": row.PA,
                    "العمر": row.Age,
                    "السرعة": row.Pace,
                    "التحمل": row.Stamina,
                    "القوة": row.Strength,
                    "العنوان (Hex)": hex(row.Offset)
                })

        final_df = pd.DataFrame(final_results)
        
        # عرض "الثلاثي المدريدي" للتأكد
        st.subheader("🏁 فحص الجودة (Target: Real Madrid)")
        targets = ["Courtois", "Diaz", "Endrick"]
        check_df = final_df[final_df['الاسم'].str.contains('|'.join(targets), case=False)]
        st.table(check_df)

        # عرض قائمة الجواهر (المواهب)
        st.subheader("💎 كشف مواهب العالم")
        # تصفية لعرض اللعيبة تحت 21 سنة بـ PA عالي
        wonderkids = final_df[(final_df['العمر'] <= 21) & (final_df['PA (الموهبة)'] >= 170)]
        st.dataframe(wonderkids.sort_values(by="PA (الموهبة)", ascending=False), use_container_width=True)

        # زر التحميل
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير الذهبي", csv, "ismaily_golden_scout.csv", "text/csv")
        
