import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Data Matcher", layout="wide")
st.title("🏹 محرك مطابقة الأسماء والبيانات الرقمية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء (Name Pool)
    # بنجرد كل الأسماء من المنطقة المعروفة (من 30 مليون لـ 45 مليون)
    st.sidebar.info("🔍 جاري جرد الأسماء...")
    names_area = data[30000000:45000000]
    # البحث عن نمط الأسماء (تبدأ بحرف كبير وبعدها حروف صغيرة)
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
    names_pool = list(dict.fromkeys(names_pool)) # حذف التكرار

    # 2. استخراج كتل البيانات (Attributes Blocks)
    # بنعمل مسح للمنطقة اللي فيها الطاقات (من 1 مليون لـ 15 مليون)
    st.sidebar.info("📡 جاري استخراج الطاقات الرقمية...")
    player_attributes = []
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 130 <= pa <= 200: # بنفلتر الموهوبين فقط
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                player_attributes.append({
                    "address": i,
                    "pa": pa,
                    "age": age,
                    "pace": raw_bytes[i+6],
                    "stamina": raw_bytes[i+7]
                })

    if player_attributes and names_pool:
        df_attr = pd.DataFrame(player_attributes)
        
        # 3. لوحة التحكم في البحث والمزامنة
        st.subheader("🔎 البحث والمطابقة")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("اكتب اسم اللاعب (مثلاً: Courtois):")
        with col2:
            shift = st.number_input("تعديل المزامنة (Shift)", value=0)

        if search_query:
            # البحث عن الاسم في المخزن المستخرج
            matches = [n for n in names_pool if search_query.lower() in n.lower()]
            
            if matches:
                st.success(f"✅ تم العثور على {len(matches)} اسم مطابق.")
                
                final_results = []
                for name in matches:
                    name_index = names_pool.index(name)
                    # المعادلة السحرية: ربط الـ Index بتاع الاسم بـ Index البيانات مع إضافة الـ Shift
                    data_index = name_index - shift
                    
                    if 0 <= data_index < len(df_attr):
                        p_data = df_attr.iloc[data_index]
                        final_results.append({
                            "الاسم المستهدف": name,
                            "الـ Index (العنوان)": p_data["address"],
                            "العنوان (Hex)": hex(int(p_data["address"])),
                            "PA": p_data["pa"],
                            "العمر": p_data["age"],
                            "السرعة": p_data["pace"],
                            "التحمل": p_data["stamina"]
                        })
                
                if final_results:
                    st.table(pd.DataFrame(final_results))
                    st.info("💡 لو العمر مش مطابق للاعب، غير قيمة الـ Shift لحد ما يظبط.")
                else:
                    st.warning("الاسم موجود لكن بياناته بعيدة جداً عن النطاق الحالي.")
            else:
                st.error("الاسم مش موجود في مخزن الأسماء.")

        # 4. عرض الجدول الكامل للمراجعة
        with st.expander("👁️ عرض قائمة المطابقة الكاملة (أول 100 لاعب)"):
            all_match = []
            for i in range(min(100, len(df_attr))):
                n_idx = i + shift
                if 0 <= n_idx < len(names_pool):
                    all_match.append({
                        "الاسم": names_pool[n_idx],
                        "العمر": df_attr.iloc[i]["age"],
                        "PA": df_attr.iloc[i]["pa"],
                        "العنوان": hex(int(df_attr.iloc[i]["address"]))
                    })
            st.dataframe(pd.DataFrame(all_match), use_container_width=True)
            
            # زر تحميل البيانات
            csv = pd.DataFrame(all_match).to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير الحالي", csv, "ismaily_matched_data.csv", "text/csv")
            
