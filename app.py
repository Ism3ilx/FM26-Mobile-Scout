import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Auto Sync Scout", layout="wide")
st.title("🏹 كشاف الإسماعيلي: نظام المزامنة التلقائية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)

    st.info("🔄 جاري تحليل البصمة الوراثية لملف الحفظ...")

    # 1. استخراج مخزن الأسماء (String Pool)
    # بنجيب كل الأسماء اللي في منطقة يامال اللي حددناها قبل كده
    names_area = data[30000000:45000000]
    names_pool = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in names_pool]
    names_pool = list(dict.fromkeys(names_pool)) # تنظيف الأسماء

    # 2. البحث عن "الثلاثي المدريدي" في منطقة الطاقات
    # كورتوا: 11 (سرعة), 8 (تحمل), 14 (قوة)
    # دياز: 14, 12, 7
    # إندريك: 15, 14, 15
    
    player_results = []
    # فحص منطقة الطاقات (أول 15 مليون بايت)
    for i in range(1000, 15000000, 1):
        # بنبحث عن كورتوا كدليل (العمر 33 والسرعة 11)
        if raw_bytes[i+2] == 33 and raw_bytes[i+6] == 11 and raw_bytes[i+7] == 8:
            st.success(f"📍 تم العثور على 'كورتوا' في العنوان: {hex(i)}")
            # بمجرد ما لقينا نقطة البداية، هنبدأ نسحب اللي بعده بالترتيب
            start_index = i
            break
    else:
        start_index = 1000 # لو ملحقش يلاقيه يبدأ من الأول
        st.warning("⚠️ لم يتم العثور على البصمة المدريدية بدقة، جاري المسح الشامل...")

    # 3. استخراج كل اللاعبين بناءً على النمط السليم
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 140 <= pa <= 200: # بنجيب اللعيبة الممتازة
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                if 5 <= pace <= 20 and 5 <= stamina <= 20:
                    player_results.append({
                        "PA": pa, "العمر": age, "السرعة": pace, 
                        "التحمل": stamina, "الموقع": i
                    })

    if player_results and names_pool:
        df_players = pd.DataFrame(player_results).drop_duplicates(subset=['الموقع'])
        
        # ميزة المزامنة: البحث عن ترتيب كورتوا في القائمة
        # غالباً كورتوا هيكون رقمه في القائمة هو نفس ترتيبه في الأسماء
        st.sidebar.header("🎯 معايرة نهائية")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)

        final_data = []
        for idx, row in enumerate(df_players.itertuples()):
            name_idx = idx + shift
            if 0 <= name_idx < len(names_pool):
                final_data.append({
                    "الاسم": names_pool[name_idx],
                    "PA (الموهبة)": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل,
                    "العنوان": hex(row.الموقع)
                })
        
        final_df = pd.DataFrame(final_data)
        
        # التأكيد على الثلاثي المدريدي
        st.subheader("✅ فحص المزامنة (ريال مدريد)")
        check_list = ["Courtois", "Diaz", "Endrick"]
        sync_check = final_df[final_df['الاسم'].str.contains('|'.join(check_list), case=False)]
        st.table(sync_check)

        st.subheader("💎 مواهب العالم المكتشفة")
        st.dataframe(final_df.sort_values(by="PA (الموهبة)", ascending=False), use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل قاعدة بيانات المواهب", csv, "ismaily_synced_scout.csv", "text/csv")
        
