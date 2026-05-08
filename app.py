import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Scout", layout="wide")
st.title("🏹 كشاف الإسماعيلي: نسخة المعايرة الدقيقة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء بالكامل
    # بدأنا من 30 مليون لأنك لقيت يامال هناك
    search_area_names = data[30000000:] 
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", search_area_names)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    
    # 2. استخراج الطاقات
    player_data = []
    for i in range(1000, 10000000):
        pa = raw_bytes[i]
        if 150 <= pa <= 200:
            age = raw_bytes[i+2]
            if 15 <= age <= 21:
                # التحقق من منطقية المهارات
                if 5 <= raw_bytes[i+6] <= 20 and 5 <= raw_bytes[i+7] <= 20:
                    player_data.append({"pa": pa, "age": age, "offset": i})

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data).drop_duplicates(subset=['offset'])
        
        # 3. المعايرة: هنحاول نلاقي "يامال" في البيانات
        # يامال عمره 18 والـ PA بتاعه عالي
        yamal_candidates = df_players[(df_players['age'] == 18) & (df_players['pa'] >= 180)]
        
        # دمج الأسماء مع البيانات مع إتاحة "إزاحة" (Offset) للمستخدم لتصحيح الترتيب
        st.sidebar.header("⚙️ إعدادات الدقة")
        shift = st.sidebar.number_input("تعديل ترتيب الأسماء (Shift)", value=0, step=1)
        
        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA": row.pa,
                    "العمر": row.age,
                    "الموقع": row.offset
                })
        
        final_df = pd.DataFrame(final_results)
        
        st.success(f"✅ تم استخراج {len(final_df)} لاعب.")
        st.info("💡 نصيحة: لو لقيت 'يامال' مكتوب جنبه طاقات لاعب تاني، غير رقم الـ (Shift) من القائمة الجانبية لحد ما الاسم يظبط مع الطاقات.")
        
        st.dataframe(final_df.sort_values(by="PA", ascending=False), use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الكشف النهائي", csv, "ismaily_precision_final.csv", "text/csv")
        
