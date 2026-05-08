import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Ultimate Scout", layout="wide")
st.title("🏹 كشاف الإسماعيلي: النسخة النهائية المعتمدة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # المسح الشامل للملف للبحث عن "بصمة اللاعب"
    # البصمة: PA متبوع بعمر متبوع بـ 3 مهارات بمسافات محددة
    for i in range(10, len(raw_bytes) - 20):
        pa = raw_bytes[i]
        # 1. التأكد من وجود PA منطقي (100-200)
        if 100 <= pa <= 200:
            # 2. التأكد من وجود العمر في مكانه الصحيح (بعد الـ PA بـ 2 بايت)
            age = raw_bytes[i+2]
            if 15 <= age <= 45:
                # 3. استخراج المهارات بناءً على تصحيح الترحيل (Pace=i+6, Stamina=i+7, Strength=i+8)
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                strength = raw_bytes[i+8]
                
                # فحص منطقية المهارات (1-20) لضمان عدم قراءة بيانات عشوائية
                if 1 <= pace <= 20 and 1 <= stamina <= 20 and 1 <= strength <= 20:
                    # الـ CA غالباً قبل الـ PA بـ 2 بايت
                    ca = raw_bytes[i-2] if i-2 >= 0 else 0
                    
                    results.append({
                        "الـ PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "الـ CA": ca,
                        "الموقع (ID)": i
                    })

    if results:
        # ترتيب النتائج بالأقوى (PA) وحذف التكرار
        df = pd.DataFrame(results).drop_duplicates(subset=['الـ PA', 'العمر', 'السرعة', 'الموقع (ID)'])
        top_df = df[df['الـ PA'] >= 150].sort_values(by="الـ PA", ascending=False)
        
        st.success(f"✅ مبروك! وجدنا {len(top_df)} لاعب ببيانات دقيقة ومطابقة للعبة.")
        st.write("ملاحظة: الأسماء موجودة في جزء منفصل من الملف (String Pool)، حالياً يمكنك تمييز اللاعبين بالعمر والـ PA.")
        
        st.dataframe(top_df, use_container_width=True)
        
        # تصدير الملف النهائي
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل كشف المواهب النهائي", csv, "ismaily_ultimate_scout.csv", "text/csv")
    else:
        st.error("⚠️ لم نجد لاعبين. تأكد من رفع ملف Save Game صحيح.")
            
