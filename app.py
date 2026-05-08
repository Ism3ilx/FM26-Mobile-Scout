import streamlit as st
import pandas as pd

st.set_page_config(page_title="FM26 Hex Profiler - Raw Mode", layout="wide")
st.title("🔬 مختبر تفكيك البيانات (النسخة الخام)")

st.info("استخدم هذا الكود لمطابقة القيم مع صور مهارات اللاعبين بدقة.")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])
player_names = st.text_input("اكتب أسماء اللاعبين (مثال: Courtois, Federico Valverde)", placeholder="اسم اللاعب كما في اللعبة")

if uploaded_file and player_names:
    data = uploaded_file.read()
    names_to_search = [n.strip() for n in player_names.split(',')]
    
    for search_name in names_to_search:
        st.subheader(f"📊 البيانات الخام للاعب: {search_name}")
        
        # البحث عن الاسم بترميز Latin-1 لضمان التقاط الحروف المزخرفة
        try:
            name_bytes = search_name.encode('latin-1')
            offset = data.find(name_bytes)
        except Exception as e:
            st.error(f"خطأ في تشفير الاسم: {e}")
            continue
        
        if offset != -1:
            # نسحب 160 بايت من بداية الاسم (Index 0 سيكون أول حرف في الاسم)
            chunk = list(data[offset : offset + 160])
            
            raw_data = []
            for i, val in enumerate(chunk):
                # قراءة الرمز (إذا كان حرفاً قابلاً للطباعة)
                char_val = chr(val) if 32 <= val <= 126 else " "
                
                raw_data.append({
                    "Index (الموقع)": i,
                    "Decimal (القيمة)": val,
                    "Hex (السداسي)": hex(val).upper().replace('0X', '').zfill(2),
                    "Char (الرمز)": char_val
                })
            
            # تحويل البيانات لجدول عرض
            df_raw = pd.DataFrame(raw_data)
            
            # عرض الجدول مع إمكانية التمرير (بدون تلوين)
            st.table(df_raw) # استخدمت st.table بدلاً من dataframe لعرض ثابت وواضح
            
            st.write(f"📍 تم العثور على اللاعب عند الموقع الأصلي في الملف: **{offset}**")
            st.write("---")
        else:
            st.error(f"❌ لم يتم العثور على '{search_name}' في هذا الملف.")

