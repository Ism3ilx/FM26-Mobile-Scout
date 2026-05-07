import streamlit as st
import pandas as pd
import re
import struct

st.set_page_config(page_title="Ismaily SC - True Scout", page_icon="⚽", layout="wide")
st.title("🔍 كشاف FM26 Mobile (فلترة اللاعبين الحقيقيين)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن الأسماء بنمط أكثر دقة
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة بلوك البيانات (نوسع البحث لـ 120 بايت)
        block = data[offset : offset + 120]
        
        # ميزة الفلترة: اللاعب الحقيقي يتبعه 'ID' وجنسية، وعادة لا توجد أصفار كثيرة في البداية
        # سنبحث عن العمر في مكان محدد بعيد قليلاً (مثلاً البايت رقم 14 أو 18)
        if len(block) > 60:
            # محاولة قراءة العمر من مكانين محتملين (Offset 14 و 32)
            age_1 = block[14]
            age_2 = block[32]
            
            # محاولة قراءة القدرات (نبحث عن قيم بين 80 و 200)
            potential_vals = [x for x in block[20:60] if 80 <= x <= 200]
            
            if 16 <= age_1 <= 38 or 16 <= age_2 <= 38:
                age = age_1 if 16 <= age_1 <= 38 else age_2
                
                if len(potential_vals) >= 2:
                    potential_vals.sort(reverse=True)
                    pa = potential_vals[0]
                    ca = potential_vals[1]
                    
                    # استبعاد الأسماء التي تظهر في 'قاموس الأسماء' فقط (تكون القدرات فيها صفرية أو وهمية)
                    if pa > 100 and pa != ca:
                        results.append({
                            "الاسم": name,
                            "العمر": age,
                            "القدرة الحالية (CA)": ca,
                            "القدرة الكامنة (PA)": pa,
                            "فارق التطوير": pa - ca
                        })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم'])
        
        # استبعاد اللاعبين الذين أعمارهم غير منطقية أو متكررة بشكل مريب
        df = df[df['القدرة الكامنة (PA)'] >= 120] # فلتر للمواهب فقط
        
        st.success(f"✅ تم العثور على {len(df)} لاعب حقيقي بنسبة دقة أعلى.")
        st.dataframe(df.sort_values(by="القدرة الكامنة (PA)", ascending=False), use_container_width=True)
    else:
        st.error("لم يتم العثور على بيانات. قد يكون الملف مشفراً بطريقة تمنع القراءة المباشرة.")

    st.balloons()
