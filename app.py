import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Precision Scout", layout="wide")
st.title("⚽ كشاف FM26: النسخة التصحيحية (علاج الأعمار)")

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
        
        # قراءة بلوك البيانات المحيط بالاسم
        # زدنا المسافة لـ 160 بايت لأن العمر أحياناً يكون "بعيداً" في النسخ الجديدة
        block = list(data[offset : offset + 160])
        
        # 1. البحث عن القدرات (نبحث عن أعلى قيمتين في النطاق 100-200)
        abilities = [x for x in block if 100 <= x <= 200]
        
        if len(abilities) >= 2 and name not in seen_names:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # 2. البحث عن العمر الحقيقي (Logic Fix):
            # عادة العمر لا يكون أول رقم صغير نقابله. 
            # سنبحث عن رقم بين 17 و 39 في منطقة محددة (بين البايت 20 و 60) 
            # لتجنب أرقام الـ ID الصغيرة التي تلي الاسم مباشرة
            age_zone = block[20:80]
            age_candidates = [x for x in age_zone if 17 <= x <= 39 and x != ca and x != pa]
            
            # إذا لم نجد في المنطقة المحددة، نوسع البحث قليلاً
            actual_age = age_candidates[0] if age_candidates else "؟"
            
            # فلترة الأسماء الوهمية: الاسم الوهمي غالباً ما يفتقر لـ "التنوع" في البيانات
            # إذا كانت المنطقة تحتوي على الكثير من الأصفار، نتجاهله
            if block[10:100].count(0) < 30 and pa > 125:
                results.append({
                    "اللاعب": name,
                    "العمر": actual_age,
                    "CA": ca,
                    "PA": pa,
                    "النمو المحتمل": pa - ca
                })
                seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم العثور على {len(df)} لاعب حقيقي.")
        
        # تحسين واجهة العرض
        search = st.text_input("ابحث عن لاعب (مثل: Ismaily أو Courtois):")
        if search:
            df = df[df['اللاعب'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.error("لم يتم العثور على بيانات دقيقة. تأكد من أن الملف هو Save Game.")
