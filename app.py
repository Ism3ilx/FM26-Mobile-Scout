import streamlit as st
import pandas as pd

st.set_page_config(page_title="FM26 Hex Inspector", layout="wide")
st.title("🔬 أداة تشريح بايتات اللاعبين")

uploaded_file = st.file_uploader("ارفع ملف الحفظ", type=["dat", "fms"])
search_name = st.text_input("اكتب اسم لاعب تعرف عمره وقدراته بدقة (مثلاً: Thibaut Courtois)")

if uploaded_file and search_name:
    data = uploaded_file.read()
    
    # تحويل الاسم إلى بايتات للبحث الدقيق
    name_bytes = search_name.encode('utf-8')
    offset = data.find(name_bytes)
    
    if offset != -1:
        start_data = offset + len(name_bytes)
        # سحب 100 بايت خلف الاسم مباشرة
        chunk = list(data[start_data : start_data + 100])
        
        st.success(f"✅ تم العثور على {search_name} في الملف!")
        st.write("إليك الأرقام المخزنة خلف اسمه بالترتيب (Index):")
        
        # إنشاء جدول يعرض رقم الخانة (Index) والقيمة الموجودة فيها
        df_bytes = pd.DataFrame({
            "الموقع (Index)": range(100),
            "القيمة (Value)": chunk
        })
        
        # تلوين الأرقام المهمة لتسهيل رؤيتها
        def highlight_values(val):
            if 15 <= val <= 40:
                return 'background-color: lightyellow; color: black'
            elif 100 <= val <= 200:
                return 'background-color: lightgreen; color: black'
            return ''
            
        st.dataframe(df_bytes.style.map(highlight_values, subset=['القيمة (Value)']), height=600)
    else:
        st.error("لم يتم العثور على الاسم. تأكد من كتابة الحروف بشكل صحيح (كابيتال/سمول).")
