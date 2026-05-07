import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Elite Edition", layout="wide")
st.title("⚽ كشاف FM26: النسخة الاحترافية الشاملة")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # 1. تحسين نمط البحث عن الأسماء ليشمل الأسماء المركبة (مثل Alexander-Arnold) والأسماء القصيرة
    # النمط الجديد أكثر مرونة لالتقاط كل اللاعبين الحقيقيين
    player_pattern = re.compile(b"([A-Z][a-z]{1,15}(?:\s|-)[A-Z][a-z]{1,15}(?:\s[A-Z][a-z]{1,15})?)")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore').strip()
        end_offset = match.end()
        
        # التأكد من وجود مساحة كافية للبيانات (نحتاج 120 بايت بعد الاسم)
        if end_offset + 120 <= len(data):
            # 2. جلب العمر من الإزاحة الذهبية 94 (التي ضبطت أعمار كورتوا وغيره)
            age = data[end_offset + 94]
            
            # 3. الفلترة الصارمة لحذف اللاعبين الوهميين:
            # - الشرط الأول: العمر يجب أن يكون منطقياً (بين 15 و 45).
            # - الشرط الثاني: فحص "كثافة البيانات" (اللاعب الحقيقي لديه مهارات كثيرة غير صفرية).
            # - الشرط الثالث: القدرة الكامنة PA يجب أن تكون معقولة.
            
            # فحص كثافة البيانات في الـ 100 بايت التالية للاسم
            chunk = list(data[end_offset : end_offset + 110])
            non_zero_stats = len([x for x in chunk if x != 0])
            
            if 15 <= age <= 45 and non_zero_stats > 35:
                # استخراج القدرات (CA/PA) من النطاق المكتشف سابقاً
                ability_chunk = chunk[40:100]
                abilities = [x for x in ability_chunk if 100 <= x <= 200]
                
                if len(abilities) >= 2 and name not in seen_names:
                    abilities.sort(reverse=True)
                    pa = abilities[0]
                    ca = abilities[1]
                    
                    if pa >= 120:
                        # تصنيف إضافي لاكتشاف المواهب (Wonderkids)
                        category = "⭐ موهبة خارقة" if pa > 165 and age < 21 else "✅ لاعب محترف"
                        if age > 32: category = "👴 خبرة"

                        results.append({
                            "اللاعب": name,
                            "العمر": age,
                            "القدرة الحالية (CA)": ca,
                            "القدرة الكامنة (PA)": pa,
                            "إمكانية التطور": pa - ca,
                            "التصنيف": category
                        })
                        seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        
        # واجهة عرض متطورة
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 ابحث عن اسم (لاعب/نادي):")
        with col2:
            min_pa = st.slider("الحد الأدنى للقدرة الكامنة (PA):", 120, 200, 130)
        with col3:
            sort_by = st.selectbox("ترتيب حسب:", ["PA", "إمكانية التطور", "العمر"])

        # تطبيق الفلاتر
        filtered_df = df[df['القدرة الكامنة (PA)'] >= min_pa]
        if search:
            filtered_df = filtered_df[filtered_df['اللاعب'].str.contains(search, case=False)]
            
        sort_map = {"PA": "القدرة الكامنة (PA)", "إمكانية التطور": "إمكانية التطور", "العمر": "العمر"}
        filtered_df = filtered_df.sort_values(by=sort_map[sort_by], ascending=(sort_by == "العمر"))

        st.success(f"✅ تم العثور على {len(filtered_df)} لاعب حقيقي بنجاح.")
        st.dataframe(filtered_df, use_container_width=True)
        
        # ميزة إضافية: ملخص لأفضل المواهب المتاحة
        if not filtered_df.empty:
            st.subheader("💡 كشاف الدراويش ينصح بـ:")
            top_wonderkid = filtered_df.sort_values(by="القدرة الكامنة (PA)", ascending=False).iloc[0]
            st.info(f"أفضل لاعب متاح حالياً هو **{top_wonderkid['اللاعب']}** (PA: {top_wonderkid['القدرة الكامنة (PA)']})")
            
    else:
        st.warning("لم يتم العثور على لاعبين. تأكد من أن الملف هو Save Game نشط.")
