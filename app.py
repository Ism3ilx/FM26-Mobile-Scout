import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Decoder", layout="wide")
st.title("🏹 رادار الإسماعيلي: نسخة فك التشفير النهائية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # البحث عن نمط الـ CA المميز في ملفك (بين 220 و 240)
    for i in range(200, len(raw_bytes) - 50):
        if 220 <= raw_bytes[i] <= 245: 
            # بناءً على تحليلي للـ CSV:
            # الـ CA هو المركز (i)
            # العمر قبل الـ CA بـ خانة واحدة (i-1)
            # المهارات البدنية قبل العمر مباشرة (i-2, i-3, i-4)
            # الـ PA بعيد شوية لورا (قبل الـ CA بـ 8 خانات تقريباً)
            
            ca = raw_bytes[i]
            age = raw_bytes[i-1]
            strength = raw_bytes[i-2]
            stamina = raw_bytes[i-3]
            pace = raw_bytes[i-4]
            pa = raw_bytes[i-8]

            # شروط التحقق المنطقي (عشان مطلعش داتا وهمية)
            if 15 <= age <= 43 and 1 <= pace <= 20 and 1 <= stamina <= 20:
                if 100 <= pa <= 200:
                    results.append({
                        "الـ PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "الـ CA": ca,
                        "الموقع": i
                    })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الموقع'])
        # تصفية المواهب السوبر
        top_df = df[df['الـ PA'] >= 150].sort_values(by="الـ PA", ascending=False)
        
        st.success(f"✅ تم فك التشفير! وجدنا {len(top_df)} موهبة.")
        st.dataframe(top_df, use_container_width=True)
        
        # تصدير الملف
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل الكشاف المحدث", csv, "ismaily_final_scout.csv", "text/csv")
    else:
        st.error("لم نجد النمط المطلوب. تأكد أن الملف هو Save Game للنسخة الصحيحة.")
        
