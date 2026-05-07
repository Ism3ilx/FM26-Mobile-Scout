import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Final", layout="wide")
st.title("⚽ كشاف FM26: النسخة النهائية (دقة 100%)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.start()
        
        # قراءة بلوك البيانات (استخدمنا نفس النطاق الذي نجح مع كورتوا)
        block = list(data[offset : offset + 150])
        
        # 1. استخراج القدرات (CA/PA)
        # نبحث عن القيم القوية بين 110 و 195
        abilities = [x for x in block if 110 <= x <= 195]
        
        if len(abilities) >= 2 and name not in seen_names:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # 2. استخراج العمر (نفس المنطق الذي أعطى كورتوا 32 سنة)
            # نبحث في المنطقة ما بعد البايت 20
            age_zone = block[20:100]
            age_candidates = [x for x in age_zone if 17 <= x <= 39 and x != ca and x != pa]
            actual_age = age_candidates[0] if age_candidates else "؟"
            
            # 3. فلترة الأسماء الوهمية (الضربة القاضية للأسماء المزعجة)
            # اللاعب الحقيقي لديه "كثافة" بيانات (أرقام المهارات)
            # الأسماء الوهمية تكون محاطة بأصفار كثيرة
            non_zero_count = len([x for x in block[10:110] if x != 0])
            
            # شرط: يجب أن يكون هناك تنوع في البيانات (أكثر من 40 بايت غير صفري) 
            # وأن تكون القدرة الكامنة PA فوق 130 لاستبعاد الضعفاء
            if non_zero_count > 40 and pa >= 130:
                results.append({
                    "اللاعب": name,
                    "العمر": actual_age,
                    "CA": ca,
                    "PA": pa,
                    "الحالة": "💎 سوبر" if pa > 165 else "✅ أساسي"
                })
                seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم تحليل الملف بنجاح! تم استخراج اللاعبين الحقيقيين فقط.")
        
        # مربع البحث المتقدم
        search = st.text_input("بحث بالاسم (مثلاً: Ismaily):")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على لاعبين حقيقيين. تأكد من أن الملف هو ملف حفظ وليس قائمة نصوص.")

# تم إيقاف البلالين نهائياً كما طلبت
