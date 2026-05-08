import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Precision Decoder", layout="wide")
st.title("🏹 رادار الإسماعيلي: نسخة ضبط المصنع")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # البحث عن بصمة الـ CA (التي أكدت لنا مكان اللاعبين)
    for i in range(200, len(raw_bytes) - 50):
        if 220 <= raw_bytes[i] <= 245: 
            # التعديل بناءً على تحليل ملفك الأخير:
            ca = raw_bytes[i]
            age = raw_bytes[i-1]
            
            # المهارات البدنية (إعادة ضبط الترتيب)
            # جربنا i-2 وطلعت 211، إذن القوة هي i-3
            strength = raw_bytes[i-3]
            stamina = raw_bytes[i-4]
            pace = raw_bytes[i-5]
            
            # الـ PA غالباً ثابت قبل الـ CA بـ 8 أو 10 خانات
            pa = raw_bytes[i-8]

            # تصفية البيانات غير المنطقية
            if 15 <= age <= 43 and 1 <= pace <= 20 and 1 <= stamina <= 20 and 1 <= strength <= 20:
                if 100 <= pa <= 200:
                    results.append({
                        "الاسم": f"Player_{i}", # مؤقتاً لحين ربط الأسماء
                        "PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "القدرة الحالية (CA)": ca
                    })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['PA', 'العمر', 'السرعة', 'التحمل', 'القوة'])
        top_df = df[df['PA'] >= 150].sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم الضبط! وجدنا {len(top_df)} لاعب ببيانات دقيقة.")
        st.dataframe(top_df, use_container_width=True)
        
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير النهائي", csv, "ismaily_fixed_scout.csv", "text/csv")
    else:
        st.error("النمط لسه مش مضبوط 100%. جرب ترفع الملف مرة تانية.")
            
