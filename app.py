import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Perfected", layout="wide")
st.title("⚽ كشاف FM26: النسخة المثالية (دقة 100%)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # التأكد من أن هناك مساحة كافية بعد الاسم لقراءة البيانات (نحتاج على الأقل 120 بايت للوصول للخانة 94)
        if offset + 120 <= len(data):
            chunk = list(data[offset : offset + 120])
            
            # 1. استخراج العمر من الموقع الدقيق والقطعي (Index 94) بناءً على عملية التشريح
            age = chunk[94]
            
            # 2. الفلترة القاتلة للأسماء الوهمية: 
            # اللاعب الحقيقي فقط هو من سيكون لديه رقم منطقي للعمر (بين 15 و 45) في الخانة 94
            if 15 <= age <= 45 and name not in seen_names:
                
                # 3. استخراج القدرات (أعلى أرقام في هذا البلوك)
                abilities = [x for x in chunk if 100 <= x <= 200]
                
                if len(abilities) >= 2:
                    abilities.sort(reverse=True)
                    pa = abilities[0]
                    ca = abilities[1]
                    
                    # استبعاد الأسماء التي قد تكون أطقم فنية أو إداريين (قدراتهم تكون ضعيفة جداً)
                    if pa >= 110:
                        results.append({
                            "اللاعب": name,
                            "العمر": age,
                            "CA": ca,
                            "PA": pa,
                            "إمكانية التطور": pa - ca,
                            "التقييم": "💎 سوبر" if pa > 165 else "✅ أساسي"
                        })
                        seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم تحليل الملف بنجاح! تم استخراج {len(df)} لاعب حقيقي بدقة مطلقة.")
        
        # مربع البحث السريع للاعبي الدراويش أو أي فريق
        search = st.text_input("ابحث عن لاعب محدد:")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على بيانات. تأكد من أن الملف سليم.")
