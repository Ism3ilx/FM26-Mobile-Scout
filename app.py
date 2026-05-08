import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Search & Index Decoder", layout="wide")
st.title("🏹 رادار البحث والتحليل الرقمي (Index & Value)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج مخزن الأسماء
    st.sidebar.info("🔍 جاري جرد الأسماء...")
    names_area = data[30000000:45000000]
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
    names_pool = list(dict.fromkeys(names_pool))

    # 2. استخراج كتل البيانات الخام (PA, Age, etc.)
    st.sidebar.info("📡 جاري استخراج الطاقات...")
    player_data = []
    # المسح الشامل في منطقة الطاقات
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 130 <= pa <= 200: # فلتر اللاعبين المميزين
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                player_data.append({"address": i, "pa": pa, "age": age})

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data)
        
        st.subheader("🔎 ابحث عن اسم اللاعب")
        search_query = st.text_input("اكتب اسم اللاعب (مثل: Courtois أو Valverde):")
        
        # لوحة التحكم في الـ Shift للمزامنة
        st.sidebar.header("⚙️ معايرة المزامنة")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)

        if search_query:
            # البحث عن الاسم في المخزن
            matches = [n for n in names_pool if search_query.lower() in n.lower()]
            
            if matches:
                st.success(f"✅ تم العثور على {len(matches)} اسم.")
                
                for name in matches:
                    name_idx = names_pool.index(name)
                    # حساب الـ Index المقابل في البيانات بناءً على الـ Shift
                    data_idx = name_idx - shift
                    
                    if 0 <= data_idx < len(df_players):
                        p_info = df_players.iloc[data_idx]
                        base_address = int(p_info["address"])
                        
                        st.write(f"### 📊 البيانات الرقمية للاعب: {name}")
                        st.write(f"**العنوان الرئيسي (Hex):** `{hex(base_address)}` | **الـ Index:** `{base_address}`")
                        
                        # جدول الـ Index والقيمة (عرض 20 بايت من نقطة الصفر)
                        details = []
                        for offset in range(0, 20):
                            current_idx = base_address + offset
                            details.append({
                                "الـ Index": current_idx,
                                "العنوان (Hex)": hex(current_idx),
                                "القيمة (Value)": raw_bytes[current_idx],
                                "الوصف المتوقع": "PA" if offset == 0 else "العمر" if offset == 2 else "مهارة" if offset > 4 else "-"
                            })
                        
                        st.table(pd.DataFrame(details))
                        st.write("---")
                    else:
                        st.warning(f"الاسم '{name}' موجود لكن الـ Index بتاعه خارج نطاق البيانات المستخرجة. جرب تغيير الـ Shift.")
            else:
                st.error("الاسم غير موجود.")

        # عرض قائمة سريعة للمراجعة
        with st.expander("👁️ معاينة سريعة لكافة الـ Indices"):
            sample = []
            for i in range(min(50, len(df_players))):
                n_idx = i + shift
                if 0 <= n_idx < len(names_pool):
                    sample.append({
                        "الاسم": names_pool[n_idx],
                        "Index البداية": df_players.iloc[i]["address"],
                        "PA": df_players.iloc[i]["pa"],
                        "العمر": df_players.iloc[i]["age"]
                    })
            st.dataframe(pd.DataFrame(sample))
                
