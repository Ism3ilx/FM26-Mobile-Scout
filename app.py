import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Triple Sync Decoder", layout="wide")
st.title("🏹 رادار الدراويش: مفكك شفرة الثلاثي الملكي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)

    # 1. استخراج الأسماء (المخزن الرئيسي)
    st.sidebar.info("🔍 جاري جرد مخزن الأسماء...")
    # بنركز على المنطقة اللي دايما فيها الأسماء (من 30MB لـ 45MB)
    names_area = data[30000000:45000000]
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
    # تنظيف الأسماء من الكلمات اللي مش لعيبة
    trash = ['Madrid', 'Paris', 'League', 'City', 'United', 'Club', 'Stadium', 'Division']
    names_pool = [n for n in names_pool if n not in trash]
    names_pool = list(dict.fromkeys(names_pool))

    # 2. إدخال بيانات "الثلاثي" للمعايرة
    st.sidebar.header("🎯 بيانات المعايرة (من اللعبة)")
    st.sidebar.write("ادخل طاقات اللاعبين كما تظهر في اللعبة:")
    
    # كورتوا (كحارس مرمى طاقاته بتختلف في الترتيب أحياناً)
    c_age = st.sidebar.number_input("عمر كورتوا", value=33)
    c_pace = st.sidebar.number_input("سرعة كورتوا", value=11)
    
    # فالفيردي
    v_age = st.sidebar.number_input("عمر فالفيردي", value=27)
    v_pace = st.sidebar.number_input("سرعة فالفيردي", value=17)

    # 3. البحث عن "البصمة الجماعية"
    st.info("📡 جاري البحث عن ترتيب (كورتوا -> فالفيردي -> كرفخال)...")
    
    player_data = []
    # المسافة التقريبية بين اللاعب والتاني في FM Mobile هي 48 أو 52 بايت
    # هنمشي بمسح شامل لأول 15 مليون بايت
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 130 <= pa <= 200: # أي لاعب بموهبة عالية
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                player_data.append({
                    "PA": pa,
                    "العمر": age,
                    "السرعة": pace,
                    "التحمل": stamina,
                    "العنوان (Hex)": hex(i),
                    "Offset": i
                })

    if player_data:
        df_players = pd.DataFrame(player_data).drop_duplicates(subset=['العنوان (Hex)'])
        
        # 4. المزامنة والتحكم
        st.sidebar.header("⚙️ المزامنة النهائية")
        shift = st.sidebar.number_input("تحريك الأسماء (Shift)", value=0)
        
        # محاولة ذكية لإيجاد كورتوا
        courtois_idx = df_players[(df_players['العمر'] == c_age) & (df_players['السرعة'] == c_pace)].index
        auto_shift = 0
        if not courtois_idx.empty and "Thibaut Courtois" in names_pool:
            auto_shift = names_pool.index("Thibaut Courtois") - courtois_idx[0]
            st.sidebar.success(f"💡 مقترح المزامنة: {auto_shift}")

        final_results = []
        applied_shift = shift + auto_shift
        
        for idx, row in enumerate(df_players.itertuples()):
            n_idx = idx + applied_shift
            if 0 <= n_idx < len(names_pool):
                final_results.append({
                    "الاسم المتوقع": names_pool[n_idx],
                    "PA (الموهبة)": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل,
                    "العنوان": row._5
                })

        final_df = pd.DataFrame(final_results)

        # 5. عرض النتائج والتحميل
        st.subheader("✅ معايرة الثلاثي الملكي")
        # فحص وجود الثلاثة
        targets = ["Courtois", "Valverde", "Carvajal"]
        check_df = final_df[final_df['الاسم المتوقع'].str.contains('|'.join(targets), case=False)]
        st.table(check_df)

        st.subheader("💎 كافة البيانات المفككة")
        st.dataframe(final_df, use_container_width=True)

        # زر التحميل الشامل
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل كافة البيانات المستخرجة (CSV)",
            data=csv,
            file_name="ismaily_madrid_decoded.csv",
            mime="text/csv",
        )
    else:
        st.error("لم نجد بيانات مطابقة. تأكد من رفع الملف الصحيح.")
        
