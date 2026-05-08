import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Index Finder", layout="wide")
st.title("🏹 كاشف الـ Index والقيم - FM26")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data) # تحويل الملف لقائمة أرقام (Values)
    
    st.sidebar.header("🔍 إعدادات البحث")
    search_type = st.sidebar.selectbox("نوع البحث", ["بحث عن تسلسل (بصمة)", "عرض نطاق محدد (Dump)"])

    if search_type == "بحث عن تسلسل (بصمة)":
        target_input = st.text_input("أدخل الأرقام المطلوبة (مثلاً: 33,11,8,14)", "33,11,8,14")
        if target_input:
            # تحويل المدخلات لقائمة أرقام
            target_sequence = [int(x.strip()) for x in target_input.split(",")]
            n = len(target_sequence)
            
            results = []
            st.info(f"جاري البحث عن التسلسل {target_sequence}...")
            
            # البحث في أول 15 مليون بايت
            for i in range(len(raw_bytes[:15000000]) - n):
                if raw_bytes[i:i+n] == target_sequence:
                    results.append({
                        "بداية الـ Index": i,
                        "العنوان (Hex)": hex(i),
                        "التسلسل الموجود": str(raw_bytes[i:i+n])
                    })
            
            if results:
                st.success(f"✅ تم العثور على {len(results)} مطابقة!")
                df_results = pd.DataFrame(results)
                st.table(df_results)
                
                # إظهار التفاصيل لكل نتيجة
                selected_index = st.selectbox("اختار Index عشان تشوف اللي حوله:", df_results["بداية الـ Index"])
                if selected_index:
                    st.write(f"### البيانات حول الـ Index: {selected_index}")
                    neighborhood = []
                    for j in range(selected_index - 5, selected_index + 20):
                        neighborhood.append({
                            "الـ Index": j,
                            "العنوان (Hex)": hex(j),
                            "القيمة (Value)": raw_bytes[j] if j < len(raw_bytes) else "N/A"
                        })
                    st.dataframe(pd.DataFrame(neighborhood), height=500)
            else:
                st.error("لم يتم العثور على هذا التسلسل.")

    elif search_type == "عرض نطاق محدد (Dump)":
        start_idx = st.number_input("ابدأ من Index رقم:", value=4578412) # مثال لعنوان كورتوا
        length = st.number_input("عدد البايتات للعرض:", value=100)
        
        dump_data = []
        for i in range(start_idx, start_idx + length):
            if i < len(raw_bytes):
                dump_data.append({
                    "الـ Index": i,
                    "العنوان (Hex)": hex(i),
                    "القيمة": raw_bytes[i]
                })
        
        st.subheader(f"📊 عرض البيانات من {start_idx} إلى {start_idx + length}")
        st.table(pd.DataFrame(dump_data))

    # زر تحميل البيانات المعروضة
    if 'dump_data' in locals() or 'results' in locals():
        csv_data = pd.DataFrame(results if search_type == "بحث عن تسلسل (بصمة)" else dump_data)
        st.download_button("📥 تحميل هذه القائمة (CSV)", csv_data.to_csv(index=False).encode('utf-8-sig'), "index_dump.csv")
    
