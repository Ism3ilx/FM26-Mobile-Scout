import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Final precision", layout="wide")
st.title("🏹 رادار الإسماعيلي: نسخة الدقة القصوى")

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
            
            # فحص المنطقة من i-10 إلى i-2 (منطقة المهارات المحتملة)
            # هنطلع كل الأرقام اللي بين 5 و 20 في المنطقة دي
            potential_skills = [raw_bytes[k] for k in range(i-10, i-1) if 5 <= raw_bytes[k] <= 20]
            
            # الـ PA ثابت مكانه في ملفك (i-8 أو i-9)
            pa = raw_bytes[i-8]
            if not (100 <= pa <= 200): pa = raw_bytes[i-9]

            if 15 <= age <= 43 and len(potential_skills) >= 3:
                # ترتيب المهارات بناءً على تحليل عينات ملفك السابقة
                # السرعة غالباً هي أبعد واحدة لورا، والقوة هي الأقرب للعمر
                results.append({
                    "الـ PA": pa,
                    "العمر": age,
                    "السرعة": raw_bytes[i-6], 
                    "التحمل": raw_bytes[i-4],
                    "القوة": raw_bytes[i-2],
                    "الـ CA": ca,
                    "الموقع": i
                })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الموقع'])
        # تصفية اللاعبين اللي مهاراتهم منطقية (مش أصفار)
        df = df[(df['السرعة'] > 0) & (df['التحمل'] > 0)]
        top_df = df[df['الـ PA'] >= 150].sort_values(by="الـ PA", ascending=False)
        
        st.success(f"✅ تم الضبط! وجدنا {len(top_df)} لاعب.")
        st.dataframe(top_df, use_container_width=True)
        
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير النهائي", csv, "ismaily_ultra_scout.csv", "text/csv")
    else:
        st.error("النمط محتاج ضبط بسيط كمان. جرب ترفع الملف.")
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
            
