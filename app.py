import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Attribute Hunter", layout="wide")
st.title("🏹 رادار الدراويش: الماسح العالمي للسمات")

st.markdown("""
### 💡 فكرة البحث:
أدخل أرقام السمات التي تراها في اللعبة (مثل عمر كورتوا وسرعته وقوته)، وسيقوم الكود بفحص الملف بالكامل للعثور على أي منطقة تحتوي على هذه الأرقام متقاربة.
""")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    # قراءة الملف ككتلة واحدة لسرعة البحث
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)
    
    st.sidebar.header("🎯 البصمة المستهدفة")
    target_age = st.sidebar.number_input("العمر المكتوب في اللعبة:", value=32)
    
    st.sidebar.subheader("📊 السمات المرئية")
    # يمكنك إضافة أي سمات أخرى هنا لزيادة دقة البحث
    s_pace = st.sidebar.number_input("السرعة (Pace):", value=11)
    s_stam = st.sidebar.number_input("التحمل (Stamina):", value=8)
    s_stre = st.sidebar.number_input("القوة (Strength):", value=14)
    s_accel = st.sidebar.number_input("التسارع (Acceleration):", value=11)

    if st.button("🚀 ابدأ مسح الملف بالكامل"):
        results = []
        # نحدد نطاق البحث (غالباً أول 20 ميجا من الملف)
        search_limit = min(file_size, 20000000)
        
        with st.spinner("جاري فحص الملايين من البايتات..."):
            # القفز بمقدار 4 بايتات لتسريع العملية (نمط اللعبة)
            for i in range(1000, search_limit, 4):
                # إذا وجدنا العمر في هذا البايت
                if raw_bytes[i] == target_age:
                    # نفحص المنطقة المحيطة (نطاق 25 بايت) هل تحتوي على باقي السمات؟
                    window = raw_bytes[max(0, i-15) : min(len(raw_bytes), i+20)]
                    
                    # شرط المطابقة: يجب أن توجد كل هذه السمات في نفس المنطقة
                    if s_pace in window and s_stam in window and s_stre in window and s_accel in window:
                        results.append({
                            "Index": i,
                            "العنوان (Hex)": hex(i),
                            "البصمة المكتشفة": str(window)
                        })
                
                # إيقاف البحث إذا وجدنا نتائج كثيرة جداً لحماية المتصفح
                if len(results) > 50: break

        if results:
            st.success(f"🎯 تم العثور على {len(results)} منطقة تطابق هذه السمات!")
            df_results = pd.DataFrame(results)
            st.table(df_results)
            
            # تحليل هيكل أول نتيجة وجدناها
            st.write("### 🔬 التشريح الرقمي للاعب المكتشف:")
            match_idx = results[0]["Index"]
            structure = []
            for offset in range(-15, 25):
                curr_idx = match_idx + offset
                structure.append({
                    "الإزاحة (Offset)": offset,
                    "القيمة": raw_bytes[curr_idx],
                    "Hex": hex(raw_bytes[curr_idx]),
                    "ملاحظة": "العمر المستهدف" if offset == 0 else ""
                })
            st.dataframe(pd.DataFrame(structure).T)
            
            st.info("💡 انظر للقيمة التي تسبق 'العمر' بمسافة ثابتة (غالباً خطوتين أو أربعة)، ستجد الـ PA الخاص باللاعب.")
        else:
            st.error("❌ لم نجد هذا التجمع من الأرقام في الملف. تأكد من إدخال الأرقام بدقة كما هي في اللعبة.")

st.markdown("""
### 📝 لماذا هذا الكود أفضل؟
1. **شامل:** يمسح الملف بالكامل دون الحاجة لمعرفة مكان الأسماء.
2. **مرن:** يمكنك البحث بسمتين أو عشر سمات لتقليل النتائج العشوائية.
3. **كاشف:** بمجرد أن تجد "البلوك" الخاص باللاعب، ستعرف أماكن السمات المخفية (مثل PA و CA) لأنها ستكون دائماً في نفس المسافة من العمر.
""")
                    
