import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Ultimate", layout="wide")
st.title("⚽ كشاف FM26: النسخة المعتمدة (تحليل كورتوا)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # البحث عن اللاعبين بنمط احترافي
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.start() # سنبدأ البحث من بداية الاسم
        
        # قراءة بلوك بيانات كبير حول الاسم (150 بايت)
        # في النسخ الجديدة، البيانات قد تسبق الاسم أو تلحقه بمسافة ثابتة
        block = list(data[max(0, offset-20) : offset+130])
        
        # استخراج القدرات (نركز على النطاق الذي ظهر فيه كورتوا)
        abilities = [x for x in block if 100 <= x <= 195]
        
        # استخراج العمر: سنبحث عن أول رقم بين 16 و 40 يظهر في "البايتات الذهبية"
        # جربنا تغيير الـ Range بناءً على تحليل ملفك
        age_search = [x for x in block if 16 <= x <= 39]
        
        if len(abilities) >= 2 and name not in seen_names:
            abilities.sort(reverse=True)
            pa = abilities[0]
            ca = abilities[1]
            
            # محاولة ذكية لجلب العمر (نتجنب أرقام القدرات)
            actual_age = "؟"
            for val in age_search:
                if val != pa and val != ca:
                    actual_age = val
                    break
            
            # فلترة الأسماء الوهمية: اللاعب الحقيقي بياناته "متغيرة"
            # الأسماء الوهمية غالباً ما تعطي نفس الـ PA لكل الأسماء في قطاع معين
            if pa > 120:
                results.append({
                    "الموقع": offset,
                    "اللاعب": name,
                    "العمر": actual_age,
                    "CA": ca,
                    "PA": pa,
                    "مستوى الموهبة": "💎 سوبر" if pa > 165 else "📈 واعد"
                })
                seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        
        # ترتيب حسب الموقع أو القوة
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم تحليل الملف. تم العثور على {len(df)} لاعب.")
        
        # فلتر العمر والقدرة
        col1, col2 = st.columns(2)
        with col1:
            min_pa_filter = st.number_input("الحد الأدنى لـ PA:", 100, 200, 130)
        with col2:
            search_query = st.text_input("بحث بالاسم (مثل لاعبي الإسماعيلي):")
            
        final_df = df[df['PA'] >= min_pa_filter]
        if search_query:
            final_df = final_df[final_df['اللاعب'].str.contains(search_query, case=False)]
            
        st.dataframe(final_df, use_container_width=True)
    else:
        st.error("لم يتم العثور على بيانات. حاول رفع الملف مرة أخرى.")

# تم إيقاف البلالين نهائياً
