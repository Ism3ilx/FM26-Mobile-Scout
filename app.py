import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Player Search Engine", layout="wide")
st.title("🏹 رادار الدراويش: محرك البحث عن اللاعبين")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج كل الأسماء من منطقة الـ 30 مليون
    st.sidebar.info("🔍 جاري جرد الأسماء...")
    names_area = data[30000000:45000000]
    # نمط للبحث عن الأسماء الكاملة (كلمتين بتبدأ بحرف كبير)
    found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
    names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
    names_pool = list(dict.fromkeys(names_pool)) # حذف التكرار

    # 2. استخراج كتل بيانات اللاعبين (PA, Age, Stats)
    st.sidebar.info("📡 جاري استخراج الطاقات...")
    player_data = []
    # المسح في المنطقة المتوقع فيها الطاقات (من 1MB لـ 15MB)
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 130 <= pa <= 200: # بنجيب اللعيبة المهمة بس
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                player_data.append({
                    "PA": pa,
                    "العمر": age,
                    "السرعة": raw_bytes[i+6],
                    "التحمل": raw_bytes[i+7],
                    "القوة": raw_bytes[i+8],
                    "العنوان (Hex)": hex(i),
                    "Index": len(player_data)
                })

    if player_data and names_pool:
        df_players = pd.DataFrame(player_data)
        
        # 3. محرك البحث بالاسم
        st.subheader("🔎 ابحث عن بيانات اللاعب")
        search_query = st.text_input("اكتب اسم اللاعب هنا (مثلاً: Courtois أو Valverde):")
        
        # لوحة التحكم في الـ Shift (المزامنة)
        st.sidebar.header("⚙️ ضبط المزامنة")
        shift = st.sidebar.number_input("تعديل الترتيب (Shift)", value=0)

        if search_query:
            # البحث عن الـ Index بتاع الاسم في المخزن
            matching_names = [n for n in names_pool if search_query.lower() in n.lower()]
            
            if matching_names:
                st.write(f"✅ تم العثور على {len(matching_names)} اسم مطابق.")
                
                results = []
                for name in matching_names:
                    name_idx = names_pool.index(name)
                    # بنحاول نلاقي بيانات اللاعب بناءً على الترتيب والـ Shift
                    data_idx = name_idx - shift
                    
                    if 0 <= data_idx < len(df_players):
                        row = df_players.iloc[data_idx]
                        results.append({
                            "الاسم": name,
                            "PA (الموهبة)": row["PA"],
                            "العمر": row["العمر"],
                            "السرعة": row["السرعة"],
                            "التحمل": row["التحمل"],
                            "القوة": row["القوة"],
                            "مكانه في الـ Hex": row["العنوان (Hex)"]
                        })
                
                if results:
                    st.table(results)
                    st.success("💡 نصيحة: لو العمر مش مظبوط، غير رقم الـ Shift في الجنب لحد ما يظبط.")
                else:
                    st.warning("الاسم موجود لكن لم نجد بيانات مقابلة له في هذا النطاق.")
            else:
                st.error("الاسم ده مش موجود في مخزن الأسماء الحالي.")

        # عرض عينة شاملة تحت للتدقيق
        st.write("---")
        st.subheader("📊 معاينة سريعة لكافة اللاعبين")
        
        sample_results = []
        for i in range(min(100, len(df_players))):
            n_idx = i + shift
            if 0 <= n_idx < len(names_pool):
                sample_results.append({
                    "الاسم": names_pool[n_idx],
                    "PA": df_players.iloc[i]["PA"],
                    "العمر": df_players.iloc[i]["العمر"],
                    "العنوان": df_players.iloc[i]["العنوان (Hex)"]
                })
        st.dataframe(pd.DataFrame(sample_results), use_container_width=True)

        # زر التحميل
        full_csv = pd.DataFrame(sample_results).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل النتائج الحالية", full_csv, "search_results.csv", "text/csv")
                
