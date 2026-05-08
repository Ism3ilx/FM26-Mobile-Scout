import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Multi-Match Scout", layout="wide")
st.title("🏹 رادار الدراويش: البحث بالبصمة الحقيقية")

st.markdown("""
### 💡 كيف يعمل هذا البحث؟
ادخل بيانات اللاعب كما تراها في اللعبة تماماً، والكود سيبحث عن "تجمع" هذه الأرقام بالقرب من اسم اللاعب في ملف الـ Hex.
""")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 بيانات تعريفية")
        p_name = st.text_input("اسم اللاعب (كما هو مكتوب بالإنجليزية):", value="Courtois")
        p_age = st.number_input("العمر:", value=33)

    with col2:
        st.subheader("⚡ الطاقات (Attributes)")
        p_pace = st.number_input("السرعة (Pace):", value=11)
        p_stamina = st.number_input("التحمل (Stamina):", value=8)
        p_strength = st.number_input("القوة (Strength):", value=14)

    if st.button("🔍 ابدأ عملية المطابقة"):
        # 1. البحث عن مكان الاسم
        name_bytes = p_name.encode('ascii')
        name_indices = [i for i, _ in enumerate(data) if data.startswith(name_bytes, i)]
        
        if not name_indices:
            st.error(f"❌ لم يتم العثور على الاسم '{p_name}' في الملف ككلمة واضحة.")
        else:
            st.success(f"✅ تم العثور على الاسم في {len(name_indices)} موقع.")
            
            results = []
            for n_idx in name_indices:
                # 2. البحث عن "تجمع" الطاقات في محيط 200 بايت قبل وبعد الاسم
                # FM Mobile غالباً تضع الطاقات قبل الاسم مباشرة أو بعده بمسافة بسيطة
                search_range = range(n_idx - 150, n_idx + 50)
                
                found_in_context = False
                for i in search_range:
                    if i < 0 or i + 10 >= len(raw_bytes): continue
                    
                    # نبحث عن نمط: (العمر) يليه أو يسبقه (السرعة، التحمل، القوة)
                    # ملاحظة: المسافات بين الطاقات في الملف قد تكون 1 أو 2 بايت
                    if raw_bytes[i] == p_age:
                        # فحص المنطقة المحيطة بالعمر عن باقي الطاقات
                        context_window = raw_bytes[i-15 : i+15]
                        if p_pace in context_window and p_stamina in context_window:
                            found_in_context = True
                            match_idx = i
                            break
                
                if found_in_context:
                    results.append({
                        "الاسم": p_name,
                        "العنوان (Hex)": hex(match_idx),
                        "العنوان (Index)": match_idx,
                        "المنطقة": "محيط الاسم المكتشف",
                        "قيم قريبة": str(raw_bytes[match_idx-5 : match_idx+10])
                    })

            if results:
                st.write("### 🎯 المواقع المطابقة للبصمة:")
                df_res = pd.DataFrame(results)
                st.table(df_res)
                
                # إظهار الـ PA المستخفي
                st.info("💡 الرقم الذي يسبق 'العمر' مباشرة أو بخطوتين غالباً ما يكون هو الـ PA الذي نبحث عنه.")
                target_idx = results[0]["العنوان (Index)"]
                st.write(f"بايتات حول العمر: `{raw_bytes[target_idx-4 : target_idx+6]}`")
            else:
                st.warning("⚠️ وجدنا الاسم، لكن لم نجد تجمع الطاقات (العمر والسرعة) بجانبه مباشرة. قد تكون الطاقات مشفرة أو بعيدة.")

st.info("💡 نصيحة: جرب لاعب طاقاته 'فريدة' (أرقام مش متكررة كتير) عشان النتيجة تطلع دقيقة جداً.")
                    
