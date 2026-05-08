import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Decoder", layout="wide")
st.title("🏹 مفكك شفرات FM26: نسخة استخراج البيانات الكاملة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    file_size = len(data)
    
    # 1. جلب مخزن الأسماء (String Pool)
    # بنجيب كل اللي شبه الأسامي من بعد 30 مليون بايت
    st.sidebar.info("🔍 جاري جرد مخزن الأسماء...")
    names_area = data[30000000:45000000]
    raw_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in raw_names]
    # تنظيف الأسماء من الكلمات العامة
    exclude = ['Madrid', 'Paris', 'League', 'City', 'United', 'Club', 'Stadium']
    names_pool = [n for n in names_pool if n not in exclude]
    names_pool = list(dict.fromkeys(names_pool))

    # 2. استخراج كتل بيانات اللاعبين (Attributes Blocks)
    st.info("📡 جاري مسح كتل البيانات...")
    player_blocks = []
    
    # مسح منطقة الطاقات (عادة من 1MB لـ 15MB)
    for i in range(1000, 15000000, 4):
        pa = data[i]
        if 130 <= pa <= 200: # بنركز على اللعيبة القوية بس
            age = data[i+2]
            if 15 <= age <= 40:
                # بنسحب بلوك 20 بايت عشان نضمن إننا جبنا كل الطاقات
                block_hex = data[i:i+20].hex()
                player_blocks.append({
                    "PA": pa,
                    "العمر": age,
                    "العنوان (Hex)": hex(i),
                    "البصمة (Raw)": block_hex,
                    "Index": len(player_blocks)
                })

    if player_blocks:
        df_blocks = pd.DataFrame(player_blocks)
        
        st.sidebar.header("⚙️ لوحة المعايرة")
        shift = st.sidebar.number_input("تحريك الأسماء (Shift)", value=0, step=1)
        
        # 3. عملية الربط (The Sync)
        final_data = []
        for idx, row in enumerate(df_blocks.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                # فك تشفير الطاقات (بناءً على ملفك الأخير)
                # السرعة غالباً هي البايت رقم 6 أو 10 في البلوك
                raw = bytes.fromhex(row._4) # البصمة الخام
                pace = raw[6] if len(raw) > 6 else 0
                stamina = raw[7] if len(raw) > 7 else 0
                
                final_data.append({
                    "الاسم": names_pool[name_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة المتوقعة": pace if pace <= 20 else "N/A",
                    "العنوان": row._3
                })

        final_df = pd.DataFrame(final_data)
        
        # عرض البيانات
        st.subheader("📋 البيانات المستخرجة (قبل التحميل)")
        st.write("استخدم خانة البحث تحت عشان تلاقي كورتوا وتعرف الـ Shift المظبوط كام.")
        
        search_name = st.text_input("🔍 ابحث عن اسم لاعب (مثل Courtois):")
        if search_name:
            match = final_df[final_df['الاسم'].str.contains(search_name, case=False)]
            st.table(match)
            if not match.empty:
                st.success("لو لقيت الاسم راكب على العمر الصح، يبقى التحميل جاهز!")

        st.dataframe(final_df, use_container_width=True)

        # 4. زر التحميل السحري
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل البيانات المفككة بالكامل (CSV)",
            data=csv,
            file_name="ismaily_decoded_data.csv",
            mime="text/csv",
        )
    else:
        st.error("لم يتم العثور على بيانات. تأكد من رفع ملف السيف الصحيح.")
                
