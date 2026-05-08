import streamlit as st
import re

st.set_page_config(page_title="Scanner Mode", layout="wide")
st.title("🔍 كاشف الهيكس (Hex Scanner)")

uploaded_file = st.file_uploader("ارفع الملف لفحصه دقيقاً", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    player_pattern = re.compile(b"([A-Z][a-zA-Z\x80-\xff]{1,15}\s[A-Z][a-zA-Z\x80-\xff]{1,15})")
    
    match = next(player_pattern.finditer(data), None)
    
    if match:
        start = match.start()
        name = match.group(1).decode('latin-1')
        st.write(f"### اسم اللاعب المكتشف: {name}")
        
        # سحب 200 بايت بعد الاسم مباشرة
        bytes_to_show = list(data[start : start + 200])
        
        st.write("### خريطة البيانات (البايتات بعد الاسم):")
        st.write("هذه الأرقام هي مفتاح الحل، انسخها لي هنا:")
        
        # عرض البيانات في شكل جدول مرقم لسهولة القراءة
        hex_data = []
        for i in range(0, len(bytes_to_show), 10):
            hex_data.append(bytes_to_show[i:i+10])
        
        st.table(hex_data)
    else:
        st.error("لم يتم العثور على أي أسماء.")
        
