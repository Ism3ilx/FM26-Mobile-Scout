import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Global Scanner", layout="wide")
st.title("🏹 رادار الدراويش: الماسح الشامل للملف")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    # قراءة الملف كبايتات
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)
    
    st.info(f"📁 تم تحميل الملف. الحجم: {file_size / (1024*1024):.2f} MB")

    # 1. المرحلة الأولى: جلب مخزن الأسماء (Name Pool)
    # بنسحب كل اللي شبه الأسامي من المنطقة المعتادة
    st.sidebar.info("🔍 جاري جرد الأسماء...")
    names_area = data[30000000:45000000] if file_size > 40000000 else data
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = list(dict.fromkeys([n.decode('ascii', errors='ignore') for n in found_names]))
    
    st.sidebar.success(f"✅ تم العثور على {len(names_pool)} اسم.")

    # 2. إعدادات البحث الشامل
    st.subheader("⚙️ إعدادات البحث الشامل")
    col1, col2, col3 = st.columns(3)
    with col1:
        search_limit = st.number_input("نطاق البحث (بالميجابايت):", value=20) * 1024 * 1024
    with col2:
        min_pa = st.number_input("أقل PA للبحث عنه:", value=130)
    with col3:
        shift_val = st.number_input("قيمة الـ Shift (للمزامنة):", value=0)

    if st.button("🚀 ابدأ المسح الشامل للملف"):
        progress_bar = st.progress(0)
        final_results = []
        
        # 3. المسح الرقمي (Attribute Scanning)
        # بنمشي في منطقة الطاقات ونطلع "البلوكات" اللي فيها بيانات حقيقية
        st.write("📡 جاري مطابقة البيانات الرقمية بالأسماء...")
        
        temp_stats = []
        for i in range(1000, int(search_limit), 4):
            pa = raw_bytes[i]
            if min_pa <= pa <= 200:
                age = raw_bytes[i+2]
                if 15 <= age <= 40:
                    temp_stats.append({
                        "index": i,
                        "pa": pa,
                        "age": age,
                        "pace": raw_bytes[i+6],
                        "stam": raw_bytes[i+7],
                        "stre": raw_bytes[i+8]
                    })
        
        # 4. المزامنة (The Matching Engine)
        for idx, stat in enumerate(temp_stats):
            # تحديث شريط التقدم
            if idx % 100 == 0:
                progress_bar.progress(min(idx / len(temp_stats), 1.0))
            
            # ربط كل بلوك بيانات بالاسم المقابل له بناءً على الترتيب والـ Shift
            name_idx = idx + shift_val
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "PA": stat["pa"],
                    "العمر": stat["age"],
                    "السرعة": stat["pace"],
                    "التحمل": stat["stam"],
                    "القوة": stat["stre"],
                    "العنوان (Hex)": hex(stat["index"])
                })

        if final_results:
            st.success(f"🎯 تم العثور على {len(final_results)} لاعب بنجاح!")
            df_final = pd.DataFrame(final_results)
            
            # عرض البيانات
            st.dataframe(df_final, use_container_width=True)
            
            # زر التحميل الشامل
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل قاعدة بيانات اللاعبين بالكامل (CSV)",
                data=csv,
                file_name="ismaily_global_scout.csv",
                mime="text/csv",
            )
        else:
            st.warning("لم يتم العثور على نتائج. حاول تغيير قيمة الـ Shift أو نطاق البحث.")

st.markdown("""
### 💡 إزاي تستخدم الكود ده صح؟
1. **ارفع الملف:** هيبدأ فوراً يلم الأسامي.
2. **المعايرة (الـ Shift):** دي أهم خطوة. بص على أول كام لاعب في الجدول. لو لقيت الاسم مش راكب على العمر (مثلاً طالع لك اسم حارس وعمره 17 سنة)، غير رقم الـ **Shift** لحد ما تلاقي أول 5 لعيبة بياناتهم صح.
3. **البحث الشامل:** بمجرد ما تظبط الـ Shift، اضغط على الزرار وسيب الكود يمسح الملف كله ويطلع لك ملف الإكسيل النهائي.
""")
                    
