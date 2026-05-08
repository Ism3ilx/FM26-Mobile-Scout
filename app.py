import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Pattern Hunter", layout="wide")
st.title("🏹 رادار الدراويش: صيد البصمة الرقمية")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    st.sidebar.header("🎯 أدخل بصمة لاعب تعرفه")
    target_age = st.sidebar.number_input("العمر (مثلاً كورتوا 33):", value=33)
    target_pace = st.sidebar.number_input("السرعة (Pace):", value=11)
    target_stamina = st.sidebar.number_input("التحمل (Stamina):", value=8)
    target_strength = st.sidebar.number_input("القوة (Strength):", value=14)

    if st.button("🚀 ابدأ مطابقة الأنماط في الملف"):
        results = []
        # هنمشي ببطء في أول 20 مليون بايت
        limit = min(len(raw_bytes), 20000000)
        
        st.info(f"⏳ جاري فحص {limit} بايت... انتظر ثواني.")
        
        for i in range(100, limit, 1):
            # بنبحث عن "تجمع" للقيم دي في نطاق 15 بايت
            # مش لازم يكونوا ورا بعض بالظبط، لأن اللعبة ممكن تحط بايت فاصل
            window = raw_bytes[i : i + 20]
            
            if target_age in window:
                # لو لقيت العمر، شوف هل بقية الطاقات موجودة معاه في نفس الـ 20 بايت؟
                if target_pace in window and target_stamina in window:
                    # مبروك! لقينا "تجمع" (Cluster) مريب
                    results.append({
                        "العنوان (Hex)": hex(i),
                        "العنوان (Index)": i,
                        "البصمة المكتشفة": str(window[:15]),
                        "المسافة": "تجمع قريب"
                    })

        if results:
            df = pd.DataFrame(results).drop_duplicates(subset=['العنوان (Hex)'])
            st.success(f"🎯 تم العثور على {len(df)} مكان محتمل لبصمة اللاعب!")
            st.table(df)
            
            st.write("---")
            st.subheader("🔬 تحليل أعمق لأول نتيجة:")
            first_match = results[0]["العنوان (Index)"]
            
            # عرض الجدول التفصيلي للقيم عشان نعرف مين الـ PA ومين الـ Age
            detailed_view = []
            for offset in range(-10, 20):
                idx = first_match + offset
                detailed_view.append({
                    "Offset": offset,
                    "Index": idx,
                    "Value": raw_bytes[idx],
                    "Hex": hex(raw_bytes[idx])
                })
            st.dataframe(pd.DataFrame(detailed_view).T)
            
            st.info("💡 بص على الجدول اللي فوق: الرقم اللي قيمته 33 هو العمر. شوف إيه الرقم اللي 'قبله' بمسافة ثابتة وقيمته (173 مثلاً لو ده كورتوا)، ده هيكون هو الـ PA.")
        else:
            st.error("❌ لم نجد هذا التجمع من الأرقام. حاول تغيير أرقام الطاقات أو التأكد منها من داخل اللعبة.")

st.markdown("""
### ✍️ ليه بنعمل كدة؟
اللعبة مستحيل تحط (33 و 11 و 8 و 14) جنب بعض بالصدفة إلا لو كانت دي بيانات لاعب. 
بمجرد ما نلاقي العنوان ده، هنعرف **"المسافة الثابتة"** (مثلاً السرعة دايماً بعد العمر بـ 4 بايتات). 
لما نعرف المسافة دي، هنطبقها على كل الأسماء اللي سحبناها قبل كدة.
""")
