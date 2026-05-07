import streamlit as st
import pandas as pd

st.set_page_config(page_title="FM26 Hex Profiler", layout="wide")
st.title("🔬 مختبر تفكيك بيانات اللاعبين (نسخة التصحيح)")

st.info("ارفع ملف الحفظ واكتب الأسماء بدقة كما تظهر في اللعبة (بالحروف الكبيرة والصغيرة).")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])
player_names = st.text_input("اكتب أسماء اللاعبين (افصل بينهم بفصلة , )", placeholder="Courtois, Federico Valverde")

if uploaded_file and player_names:
    data = uploaded_file.read()
    names_to_search = [n.strip() for n in player_names.split(',')]
    
    for search_name in names_to_search:
        st.subheader(f"📊 تحليل بيانات اللاعب: {search_name}")
        
        # البحث عن الاسم بترميز Latin-1 لدعم الزخرفة والحروف العالمية
        try:
            name_bytes = search_name.encode('latin-1')
            offset = data.find(name_bytes)
        except:
            st.error(f"مشكلة في تشفير الاسم: {search_name}")
            continue
        
        if offset != -1:
            # المرجع الثابت هو أول حرف في الاسم
            # سحب 160 بايت شاملة الاسم وما بعده
            chunk = list(data[offset : offset + 160])
            
            # إنشاء جدول البيانات الخام
            hex_data = []
            for i, val in enumerate(chunk):
                # محاولة قراءة الحرف إذا كان قابلاً للطباعة
                char_val = chr(val) if 32 <= val <= 126 else "."
                
                hex_data.append({
                    "الموقع (Index)": i,
                    "القيمة (Decimal)": val,
                    "القيمة (Hex)": hex(val).upper().replace('0X', ''),
                    "الرمز": char_val
                })
            
            df_hex = pd.DataFrame(hex_data)
            
            # تلوين القيم لتسهيل الملاحظة
            def highlight_vals(row):
                val = row['القيمة (Decimal)']
                if 100 <= val <= 200:
                    return ['background-color: #d4edda'] * len(row) # أخضر للقدرات CA/PA
                elif 1 <= val <= 20:
                    return ['background-color: #fff3cd'] * len(row) # أصفر للمهارات الفنية
                return [''] * len(row)

            st.dataframe(df_hex.style.apply(highlight_vals, axis=1), height=600)
            st.write(f"📍 تم العثور على اللاعب عند الموقع (Offset): {offset}")
            st.write("---")
        else:
            st.error(f"❌ لم يتم العثور على '{search_name}' في الملف. تأكد من كتابة الاسم بدقة.")

