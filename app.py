import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Scout", layout="wide")
st.title("🏹 رادار الدراويش: النسخة الاحترافية المعتمدة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # بناءً على ملف الـ CSV اللي بعته، النمط هو:
    # [PA] يليه [CA] يليه [العمر] يليه [المهارات البدنية]
    # والـ CA قيمته فوق الـ 200 دائماً في ملفك
    
    for i in range(200, len(raw_bytes) - 100):
        # البحث عن بصمة الـ CA العالية (بين 220 و 240)
        if 220 <= raw_bytes[i] <= 245: 
            # إذا وجدنا CA، الـ PA غالباً يكون قبلها بـ 1 بايت أو 2
            pa = raw_bytes[i-1]
            if 100 <= pa <= 200:
                # العمر غالباً يكون بعد الـ CA بـ 1 بايت
                age = raw_bytes[i+1]
                if 15 <= age <= 45:
                    # المهارات البدنية تبدأ بعد العمر
                    pace = raw_bytes[i+2]
                    stamina = raw_bytes[i+3]
                    strength = raw_bytes[i+4]
                    
                    # تصحيح قيم المهارات (تحويلها من نظام الـ Byte لنظام الـ 20)
                    # في ملفك، الرقم 15 يمثل طاقة عالية، والرقم 5 يمثل طاقة ضعيفة
                    if 1 <= pace <= 20 and 1 <= stamina <= 20:
                        results.append({
                            "الموقع في الملف": i,
                            "العمر": age,
                            "السرعة": pace,
                            "التحمل": stamina,
                            "القوة": strength,
                            "PA": pa,
                            "CA (Raw)": raw_bytes[i]
                        })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الموقع في الملف'])
        # تصفية اللاعبين السوبر فقط (PA > 150)
        top_players = df[df['PA'] >= 150].sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم اختراق التشفير! وجدنا {len(top_players)} لاعب بمؤهلات 'سوبر'.")
        
        st.write("### 📋 قائمة المواهب المكتشفة:")
        st.dataframe(top_players, use_container_width=True)
        
        # زر تحميل البيانات
        csv = top_players.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل القائمة المحدثة (CSV)", csv, "ismaily_pro_scout.csv", "text/csv")
    else:
        st.error("لم نجد النمط المطلوب. حاول رفع ملف حفظ مختلف أو تأكد من إصدار اللعبة.")
    
