import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Mega Scout", layout="wide")
st.title("🏹 كشاف الإسماعيلي: الرادار الشامل (أرقام + أسماء)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    results = []
    
    # 1. البحث عن الطاقات (النمط اللي نجحنا فيه)
    for i in range(1000, len(raw_bytes) - 50):
        pa = raw_bytes[i]
        if 150 <= pa <= 200: # بنبحث عن المواهب العالية فقط
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                strength = raw_bytes[i+8]
                
                # التأكد إنها بيانات لاعب (المهارات بين 1 و 20)
                if 5 <= pace <= 20 and 5 <= stamina <= 20:
                    
                    # 2. محاولة إيجاد اسم اللاعب (البحث عن نص قريب قبل الإزاحة)
                    player_name = "Unknown"
                    # نبحث في الـ 300 بايت اللي قبل الـ PA عن أي نص انجليزي
                    search_area = data[max(0, i-300):i]
                    names = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", search_area)
                    if names:
                        try:
                            player_name = names[-1].decode('latin-1')
                        except:
                            pass

                    results.append({
                        "الاسم المتوقع": player_name,
                        "الـ PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "الموقع (ID)": i
                    })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الموقع (ID)'])
        # ترتيب حسب القوة (PA)
        top_df = df.sort_values(by="الـ PA", ascending=False)
        
        st.success(f"🎯 رادار الدراويش رصد {len(top_df)} موهبة!")
        st.write("ملاحظة: إذا ظهر الاسم 'Unknown'، يمكنك البحث في اللعبة عن لاعب بنفس العمر والسرعة والـ PA.")
        
        st.dataframe(top_df, use_container_width=True)
        
        # تحميل الملف
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل قائمة المواهب", csv, "ismaily_scout_names.csv", "text/csv")
    else:
        st.error("⚠️ لم يتم العثور على بيانات. تأكد من أن الملف هو Save Game للنسخة الصحيحة.")
                    
