import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Full Filter Radar", layout="wide")
st.title("🏹 رادار الدراويش الشامل (البحث بالهوية الكاملة)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    # قراءة الملف بالكامل
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    st.sidebar.header("🎯 معايير البحث عن اللاعب")
    target_name = st.sidebar.text_input("اسم اللاعب (بالإنجليزية):", value="Courtois")
    target_age = st.sidebar.number_input("العمر:", value=33)
    
    st.sidebar.subheader("📊 السمات الكاملة (Attributes)")
    p_pace = st.sidebar.number_input("السرعة (Pace):", value=11)
    p_stam = st.sidebar.number_input("التحمل (Stamina):", value=8)
    p_stre = st.sidebar.number_input("القوة (Strength):", value=14)

    if st.button("🚀 ابدأ مطابقة البيانات"):
        # 1. المرحلة الأولى: البحث عن الاسم في الملف
        name_bytes = target_name.encode('ascii')
        name_hits = [i for i, _ in enumerate(data) if data.startswith(name_bytes, i)]
        
        if not name_hits:
            st.error(f"❌ لم يتم العثور على اسم '{target_name}' في الملف.")
        else:
            st.success(f"✅ تم العثور على الاسم في {len(name_hits)} موقع. جاري فحص السمات...")
            
            final_matches = []
            
            for n_idx in name_hits:
                # 2. المرحلة الثانية: فحص منطقة "الجيران" (150 بايت قبل و50 بعد الاسم)
                # هندور في المحيط ده على تجمع (العمر + السمات)
                found_cluster = False
                cluster_address = 0
                
                search_start = max(0, n_idx - 150)
                search_end = min(len(raw_bytes), n_idx + 50)
                
                for i in range(search_start, search_end):
                    # بنبحث عن العمر كبوابة دخول
                    if raw_bytes[i] == target_age:
                        # لو لقينا العمر، بنشوف هل السمات التانية موجودة في نطاق 20 بايت حوله؟
                        window = raw_bytes[i-10 : i+20]
                        if p_pace in window and p_stam in window and p_stre in window:
                            found_cluster = True
                            cluster_address = i
                            break
                
                if found_cluster:
                    # 3. المرحلة الثالثة: جمع البيانات المستخلصة من العنوان المكتشف
                    final_matches.append({
                        "الاسم": target_name,
                        "العنوان (Hex)": hex(cluster_address),
                        "العنوان (Index)": cluster_address,
                        "PA المحتمل": raw_bytes[cluster_address - 2], # غالباً الـ PA قبل العمر بـ 2 بايت
                        "العمر": raw_bytes[cluster_address],
                        "السرعة": p_pace,
                        "التحمل": p_stam,
                        "القوة": p_stre,
                        "البصمة الكاملة": str(raw_bytes[cluster_address-5 : cluster_address+15])
                    })

            if final_matches:
                st.subheader("🎯 النتائج المطابقة")
                df_results = pd.DataFrame(final_matches)
                st.table(df_results)
                
                # تحليل أعمق للعنوان المكتشف
                st.info("💡 تحليل الهيكل الرقمي (Offset Analysis):")
                best_match = final_matches[0]["العنوان (Index)"]
                analysis_data = []
                for offset in range(-10, 20):
                    idx = best_match + offset
                    analysis_data.append({
                        "الازاحة (Offset)": offset,
                        "القيمة": raw_bytes[idx],
                        "الوصف المتوقع": "عمر اللاعب" if offset == 0 else "PA محتمل" if offset == -2 else "-"
                    })
                st.dataframe(pd.DataFrame(analysis_data).T)
            else:
                st.warning("⚠️ وجدنا الاسم، لكن السمات (السرعة والقوة) غير موجودة بالقرب منه. قد تكون البيانات في كتل منفصلة.")

st.markdown("""
### 📝 كيفية استخدام النتائج:
1. **التطابق:** لو لقيت الجدول طلع بيانات، بص على الـ **PA المحتمل**. ده هو الرقم اللي كنا بندور عليه!
2. **الاستخراج:** العنوان (Hex) اللي طلع لك هو "المفتاح". أي لاعب تاني في اللعبة هيكون له نفس "التصميم" (مثلاً الـ PA دايماً قبل العمر بـ 2 بايت).
3. **التجميع:** بمجرد ما نأكد المسافات دي، هعملك الكود اللي يسحب الـ 1000 لاعب كلهم في ثواني.
""")
                
