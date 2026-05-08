import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Flexible Scout", layout="wide")
st.title("🏹 رادار الدراويش: البحث المرن عن البصمة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    st.info("🔍 جاري جرد الأسماء من منطقة الـ 30 مليون...")
    names_area = data[30000000:45000000]
    # نمط محسن لجلب الأسماء الحقيقية فقط
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{2,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
    names_pool = list(dict.fromkeys(names_pool))

    # البحث المرن عن كورتوا
    st.info("🎯 جاري محاولة تحديد موقع كورتوا (عمر 33 - سرعة 11)...")
    courtois_offset = -1
    
    # هنبحث في أول 20 مليون بايت
    for i in range(1000, 20000000, 1):
        # بنبحث عن العمر 33 وبعده بمسافة بسيطة السرعة 11
        if raw_bytes[i+2] == 33: # العمر
            # بنشوف الـ 10 بايتات اللي بعده هل فيهم 11 (السرعة)؟
            if 11 in raw_bytes[i+3:i+15]: 
                courtois_offset = i
                break
    
    if courtois_offset != -1:
        st.success(f"📍 تم العثور على نقطة قريبة من كورتوا في العنوان: {hex(courtois_offset)}")
        
        player_list = []
        # سحب البيانات بنمط القفزات الثابتة (Offset)
        for i in range(1000, 15000000, 4):
            pa = raw_bytes[i]
            if 140 <= pa <= 200:
                age = raw_bytes[i+2]
                if 15 <= age <= 40:
                    # بنسحب القيم اللي حول الـ PA
                    player_list.append({
                        "PA": pa, "العمر": age, 
                        "السرعة": raw_bytes[i+6] if i+6 < len(raw_bytes) else 0,
                        "التحمل": raw_bytes[i+7] if i+7 < len(raw_bytes) else 0,
                        "Address": i
                    })
        
        df_players = pd.DataFrame(player_list).drop_duplicates(subset=['Address'])
        
        st.sidebar.header("⚙️ الضبط اليدوي")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)
        
        # محاولة مزامنة ذكية
        auto_shift = 0
        if "Thibaut Courtois" in names_pool:
            target_idx = names_pool.index("Thibaut Courtois")
            # بنحاول نخلي أول لاعب PA عالي يقابل أول اسم مهم
            auto_shift = target_idx
            
        final_results = []
        for idx, row in enumerate(df_players.itertuples()):
            n_idx = idx + shift + auto_shift
            if 0 <= n_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[n_idx],
                    "PA": row.PA,
                    "العمر": row.العمر,
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل
                })
        
        final_df = pd.DataFrame(final_results)
        
        st.subheader("📊 فحص جودة البيانات")
        # هنعرض أول 20 لاعب عشان تشوف كورتوا ظهر فين
        st.table(final_df.head(20))
        
        st.subheader("💎 قائمة الجواهر (Wonderkids)")
        wonderkids = final_df[(final_df['PA'] >= 180) & (final_df['العمر'] <= 21)]
        st.dataframe(wonderkids.sort_values(by="PA", ascending=False), use_container_width=True)

        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير", csv, "ismaily_flexible_scout.csv", "text/csv")
    else:
        st.error("❌ لسه مش لاقي البصمة. جرب تفتح اللعبة وتأكد من طاقة 'إندريك' (Endrick) واكتبها لي.")
        
