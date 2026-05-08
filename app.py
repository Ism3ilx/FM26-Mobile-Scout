import streamlit as st

st.set_page_config(page_title="Ismaily SC - Player Creator", layout="wide")
st.title("🏹 رادار الدراويش: محرك إنشاء اللاعبين بالبصمة")

st.markdown("""
### 💡 فكرة الكود:
1. اكتب طاقات لاعب "موجود فعلياً" في فريقك (عشان نلاقي مكانه).
2. اكتب الطاقات "الجديدة" اللي عايز تحول اللاعب ده ليها.
3. الكود هيعدل الملف ويطلع لك نسخة جديدة تحمل اللاعب الخارق بتاعك.
""")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = bytearray(uploaded_file.read()) # استخدام bytearray عشان نقدر نعدل
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 بصمة اللاعب الحالي (للبحث)")
        old_age = st.number_input("العمر الحالي", value=33)
        old_pa = st.number_input("الـ PA الحالي", value=173)
        old_pace = st.number_input("السرعة الحالية", value=11)
        old_stamina = st.number_input("التحمل الحالي", value=8)

    with col2:
        st.subheader("✨ طاقات اللاعب الجديد")
        new_age = st.number_input("العمر الجديد", value=17)
        new_pa = st.number_input("الـ PA الجديد (ماكس 200)", value=200)
        new_pace = st.number_input("السرعة الجديدة", value=20)
        new_stamina = st.number_input("التحمل الجديد", value=20)

    if st.button("🚀 إنشاء اللاعب وحفظ الملف"):
        # تحويل القيم لتسلسل بايتات (حسب هيكل FM المعتاد)
        # PA يكون في الأول، ثم بايت غير معروف، ثم العمر، ثم السرعة في بايت 6
        
        # هنبحث بـ (العمر والـ PA) كبداية لأنهم أضمن
        found_count = 0
        for i in range(len(data) - 10):
            # محاولة مطابقة البصمة (PA ثم بايت عشوائي ثم العمر)
            if data[i] == old_pa and data[i+2] == old_age:
                # لو لقينا مطابقة، نحدث البيانات
                data[i] = new_pa           # تعديل الـ PA
                data[i+2] = new_age        # تعديل العمر
                data[i+6] = new_pace       # تعديل السرعة
                data[i+7] = new_stamina    # تعديل التحمل
                
                found_count += 1
                st.success(f"🎯 تم العثور على اللاعب وتعديله في العنوان: {hex(i)}")
        
        if found_count > 0:
            st.balloons()
            st.download_button(
                label="📥 تحميل ملف الحفظ المعدل",
                data=bytes(data),
                file_name="ismaily_modded_save.fms",
                mime="application/octet-stream"
            )
        else:
            st.error("❌ لم يتم العثور على لاعب بهذه الطاقات. تأكد من الأرقام بدقة من داخل اللعبة.")

st.info("⚠️ ملاحظة: يفضل دائماً الاحتفاظ بنسخة احتياطية من ملف السيف الأصلي قبل التعديل.")
