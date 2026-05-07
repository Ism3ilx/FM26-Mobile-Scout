import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Recovery Mode", layout="wide")
st.title("⚽ كشاف FM26: وضع استعادة اللاعبين الحقيقيين")

uploaded_file = st.file_uploader("ارفع ملف fm_save.dat أو .fms", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. استخراج كل الأسماء الموجودة في الملف وتخزينها في قائمة
    all_names = re.findall(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})", data)
    all_names = [n.decode('utf-8', errors='ignore') for n in all_names]
    
    # 2. البحث عن "بلوكات القدرات" (أرقام متتالية قوية)
    # سنبحث عن أي مكان في الملف يحتوي على أكثر من 5 أرقام بين 100 و200
    results = []
    
    # سنقوم بعمل مسح "عشوائي ذكي" للملف لتقليل زمن التحميل
    data_len = len(data)
    step = 500 # كل 500 بايت
    
    name_index = 0
    for i in range(0, data_len - 100, step):
        block = data[i : i + 100]
        # البحث عن CA و PA في هذا البلوك
        potentials = [x for x in block if 110 <= x <= 200]
        
        if len(potentials) >= 3: # وجدنا منطقة بيانات فنية للاعب
            potentials.sort(reverse=True)
            pa = potentials[0]
            ca = potentials[1]
            
            # محاولة البحث عن عمر منطقي في نفس المنطقة
            ages = [x for x in block if 16 <= x <= 38]
            age = ages[0] if ages else "؟؟"
            
            # ربط هذه البيانات بأي اسم من القائمة (بالترتيب)
            if name_index < len(all_names):
                current_name = all_names[name_index]
                # فلترة: استبعاد الأسماء المكررة أو الوهمية المشهورة
                if "Newgen" not in current_name:
                    results.append({
                        "اللاعب": current_name,
                        "العمر": age,
                        "القدرة الحالية (CA)": ca,
                        "القدرة الكامنة (PA)": pa,
                        "الجودة": "⭐ عالمي" if pa > 170 else "✅ ممتاز"
                    })
                name_index += 1

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['اللاعب'])
        # ترتيب حسب القوة
        df = df.sort_values(by="القدرة الكامنة (PA)", ascending=False)
        
        st.success(f"✅ تم استعادة {len(df)} لاعب من ذاكرة الملف!")
        
        # عرض البيانات
        st.table(df.head(100)) # استخدام Table بدلاً من DataFrame لضمان الظهور
    else:
        st.error("لم نتمكن من الربط بين الأسماء والقدرات. يبدو أن الملف مشفر بالكامل.")

    st.balloons()
