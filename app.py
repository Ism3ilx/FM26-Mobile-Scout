import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Precision", layout="wide")
st.title("🏹 رادار الإسماعيلي: نسخة الدقة والتحكم")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # البحث عن الـ CA (المرساة الثابتة في ملفك)
    for i in range(500, len(raw_bytes) - 50):
        if 220 <= raw_bytes[i] <= 245: 
            ca = raw_bytes[i]
            age = raw_bytes[i-1]
            
            # الـ PA غالباً ثابت قبل الـ CA بـ 8 خانات
            pa = raw_bytes[i-8]

            # فحص منطقية العمر والـ PA قبل الاستخراج
            if 15 <= age <= 43 and 100 <= pa <= 200:
                # استخراج المهارات بناءً على النمط الزوجي اللي اكتشفناه في ملفك
                p = raw_bytes[i-6] # السرعة
                s = raw_bytes[i-4] # التحمل
                strg = raw_bytes[i-2] # القوة
                
                # إضافة اللاعب فقط لو المهارات منطقية (أكبر من صفر)
                if p > 0 and s > 0:
                    player_data = {
                        "PA": pa,
                        "العمر": age,
                        "السرعة": p,
                        "التحمل": s,
                        "القوة": strg,
                        "CA": ca,
                        "الموقع": i
                    }
                    results.append(player_data)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الموقع'])
        top_df = df[df['PA'] >= 150].sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم الضبط! وجدنا {len(top_df)} لاعب.")
        st.dataframe(top_df, use_container_width=True)
        
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير", csv, "ismaily_precision_scout.csv", "text/csv")
    else:
        st.error("لم نجد بيانات مطابقة. تأكد من رفع الملف الصحيح.")
