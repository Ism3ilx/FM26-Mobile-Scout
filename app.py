import streamlit as st
import pandas as pd

st.set_page_config(page_title="FM26 Hex Profiler", layout="wide")
st.title("🔬 مختبر تفكيك بيانات اللاعبين")

st.info("استخدم هذه الأداة لتحديد مواقع (العمر، الجنسية، المركز، والمهارات) بدقة.")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])
player_names = st.text_input("اكتب أسماء اللاعبين (افصل بينهم بفصلة , )", placeholder="Courtois, Valverde")

if uploaded_file and player_names:
    data = uploaded_file.read()
    names_to_search = [n.strip() for n in player_names.split(',')]
    
    for search_name in names_to_search:
        st.subheader(f"📊 تحليل بيانات اللاعب: {search_name}")
        
        # البحث عن الاسم بترميز Latin-1 لدعم الزخرفة
        name_bytes = search_name.encode('latin-1')
        offset = data.find(name_bytes)
        
        if offset != -1:
            start_data = offset  # سنبدأ من أول حرف في الاسم ليكون المرجع ثابت (0)
            # سحب 160 بايت شاملة الاسم وما بعده
            chunk = list(data[start_offset : start_offset + 160])
            
            # إنشاء جدول البيانات الخام
            hex_data = []
            for i, val in enumerate(chunk):
                hex_data.append({
                    "الموقع (Index)": i,
                    "القيمة (Decimal)": val,
                    "القيمة (Hex)": hex(val).upper().replace('0X', ''),
                    "الوصف المحتمل": "بداية الاسم" if i == 0 else ""
                })
            
            df_hex = pd.DataFrame(hex_data)
            
            # عرض الجدول مع تلوين القيم التي تشبه المهارات (1-20) أو القدرات (100-200)
            def highlight_vals(row):
                val = row['القيمة (Decimal)']
                if 100 <= val <= 200:
                    return ['background-color: #d4edda'] * len(row) # أخضر للقدرات
                elif 1 <= val <= 20:
                    return ['background-color: #fff3cd'] * len(row) # أصفر للمهارات
                return [''] * len(row)

            st.dataframe(df_hex.style.apply(highlight_vals, axis=1), height=500)
            st.write("---")
        else:
            st.error(f"❌ لم يتم العثور على {search_name} في الملف. تأكد من كتابة الاسم كما يظهر في اللعبة.")

