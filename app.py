import streamlit as st
import pandas as pd

st.set_page_config(page_title="رادار صيد السمات - Ismaily SC", layout="wide")
st.title("🏹 رادار الدراويش: الماسح الشامل بالبصمة الرقمية")

st.markdown("""
### 💡 فكرة الكود المعدل:
بدل البحث عن الأسماء (اللي ممكن تكون مشفرة أو بعيدة)، الكود ده بيمسح الملف بحثاً عن **"تجمع سمات"** لاعب إنت عارفه.
1. دخل عمر اللاعب وسرعته وتحمله وقوته (زي ما هم في اللعبة).
2. الكود هيطلع لك كل الأماكن اللي الأرقام دي ظهرت فيها "جنب بعض".
""")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms / .dat)", type=["dat", "fms", "sav"])

# ------------------- إعدادات البحث بالبصمة -------------------
with st.sidebar:
    st.header("🎯 البصمة المستهدفة")
    target_age = st.number_input("العمر (مثلاً 33):", value=33)
    
    st.subheader("📊 السمات المرئية (من اللعبة)")
    s_pace = st.number_input("السرعة (Pace):", value=11)
    s_stam = st.number_input("التحمل (Stamina):", value=8)
    s_stre = st.number_input("القوة (Strength):", value=14)
    
    st.divider()
    st.header("⚙️ إعدادات المسح")
    search_range = st.slider("نطاق البحث حول العمر (بايت)", 5, 50, 20)
    max_results = st.number_input("أقصى عدد نتائج", value=50)

# ------------------- معالجة الملف -------------------
if uploaded_file:
    file_data = uploaded_file.read()
    raw_bytes = list(file_data)
    
    if st.button("🚀 ابدأ المسح الشامل في الملف"):
        results = []
        
        # تحويل القيم لليست للبحث السريع
        target_cluster = [s_pace, s_stam, s_stre]
        
        # المسح الشامل (بنتخطى أول بايتات لأنها Header)
        with st.spinner("جاري فحص الملف بايت بايت..."):
            for i in range(100, len(raw_bytes) - 100):
                # البحث عن العمر كبوابة دخول
                if raw_bytes[i] == target_age:
                    # فحص المنطقة المحيطة (النافذة)
                    window = raw_bytes[i - search_range : i + search_range]
                    
                    # هل السمات التانية موجودة في النافذة دي؟
                    if all(attr in window for attr in target_cluster):
                        results.append({
                            "العنوان (Index)": i,
                            "العنوان (Hex)": hex(i),
                            "المحيط الرقمي": window
                        })
                
                if len(results) >= max_results:
                    break

        if results:
            st.success(f"🎯 تم العثور على {len(results)} مكان يطابق هذه البصمة!")
            
            # عرض النتائج في جدول
            display_data = []
            for r in results:
                display_data.append({
                    "Hex Address": r["العنوان (Hex)"],
                    "Raw Sequence": str(r["المحيط الرقمي"])
                })
            
            st.table(pd.DataFrame(display_data))
            
            # تحليل أعمق لأول نتيجة (التشريح الرقمي)
            st.divider()
            st.subheader("🔬 تشريح أول بصمة مكتشفة")
            target_idx = results[0]["العنوان (Index)"]
            
            analysis = []
            for offset in range(-20, 25):
                idx = target_idx + offset
                val = raw_bytes[idx]
                analysis.append({
                    "Offset": offset,
                    "Value": val,
                    "Hex": hex(val),
                    "Note": "🎯 العمر" if offset == 0 else "⭐ سمة" if val in target_cluster else ""
                })
            
            st.dataframe(pd.DataFrame(analysis).T)
            st.info("💡 بص على القيم اللي جنب 'العمر' بمسافات ثابتة.. لو لقيت رقم عالي (زي 170) قبل العمر بـ 2 أو 4 بايت، مبروك ده هو الـ PA.")
            
        else:
            st.error("❌ لم يتم العثور على أي تطابق. ده معناه إن القيم في الملف ممكن تكون (مجموعة + 1) أو (مجموعة - 1) أو المسافات بعيدة.")

