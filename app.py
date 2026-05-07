import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC Scout - Pro", layout="wide")
st.title("⚽ كشاف FM26: النسخة الشاملة (بحث ذكي)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ الخاص بك", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # نمط البحث عن الأسماء (اللاعبين)
    player_pattern = re.compile(b"([A-Z][a-z]{2,15}\s[A-Z][a-z]{2,15})")
    
    results = []
    seen_names = set()
    
    for match in player_pattern.finditer(data):
        name = match.group(1).decode('utf-8', errors='ignore')
        offset = match.end()
        
        # قراءة 100 بايت (نطاق أوسع للبحث)
        chunk = list(data[offset : offset + 100])
        
        # استخراج كل الأرقام المنطقية في هذا النطاق
        # 1. البحث عن القدرات (أرقام بين 100 و 200)
        abilities = [x for x in chunk if 100 <= x <= 200]
        
        # 2. البحث عن العمر (أرقام بين 16 و 40)
        # سنركز على أول 20 بايت بعد الاسم للعمر
        age_options = [x for x in chunk[:20] if 16 <= x <= 40]
        
        if name not in seen_names:
            if len(abilities) >= 2:
                abilities.sort(reverse=True)
                pa = abilities[0]
                ca = abilities[1]
                age = age_options[0] if age_options else "؟"
                
                # تصنيف اللاعب
                status = "⭐ موهبة" if pa > 160 else "✅ لاعب أساسي"
                
                results.append({
                    "اللاعب": name,
                    "العمر": age,
                    "CA": ca,
                    "PA": pa,
                    "التقييم": status
                })
                seen_names.add(name)
            elif len(abilities) == 1: # إذا وجدنا PA فقط ولم نجد CA
                results.append({
                    "اللاعب": name,
                    "العمر": age_options[0] if age_options else "؟",
                    "CA": "غير محدد",
                    "PA": abilities[0],
                    "التقييم": "بيانات جزئية"
                })
                seen_names.add(name)

    if results:
        df = pd.DataFrame(results)
        
        # فلتر لاستبعاد الأسماء التي تظهر بدون أي بيانات PA (الوهميين)
        df = df[df['PA'] != "؟"]
        
        # ترتيب حسب القوة
        df = df.sort_values(by="PA", ascending=False)
        
        st.success(f"✅ تم العثور على {len(df)} كيان. استخدم البحث للعثور على لاعبيك.")
        
        # مربع البحث مهم جداً هنا
        search_box = st.text_input("ابحث عن لاعب (مثلاً: اكتب اسم لاعب من الإسماعيلي):")
        if search_box:
            df = df[df['اللاعب'].str.contains(search_box, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.error("لم نتمكن من الربط. الملف قد يكون بنظام تشفير مختلف.")

# ملاحظة: تم حذف st.balloons بناءً على طلبك السابق
