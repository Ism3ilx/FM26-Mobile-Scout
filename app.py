import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Final Protocol", layout="wide")
st.title("🏹 بروتوكول فك الحصار النهائي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    
    st.subheader("🔎 البحث عن بصمة اللاعب بالاسم")
    player_name = st.text_input("اكتب اسم اللاعب بالانجليزي (مثلاً: Courtois):")

    if player_name:
        # البحث عن الاسم كـ Bytes في الملف
        name_bytes = player_name.encode('ascii')
        start_pos = 0
        matches = []
        
        # هندور على كل الأماكن اللي ظهر فيها الاسم ده
        while True:
            idx = data.find(name_bytes, start_pos)
            if idx == -1: break
            matches.append(idx)
            start_pos = idx + 1
        
        if matches:
            st.success(f"✅ تم العثور على اسم {player_name} في {len(matches)} مكان!")
            
            for m_idx in matches:
                st.write(f"---")
                st.write(f"📍 **العنوان المكتشف (Hex):** `{hex(m_idx)}` | **Index:** `{m_idx}`")
                
                # تحليل المنطقة المحيطة بالاسم (100 بايت قبل وبعد)
                # غالباً الطاقات بتكون "قبل" الاسم في ملفات الـ Mobile
                st.write("📊 تحليل القيم المحيطة (القيم اللي ممكن تكون هي الطاقات):")
                
                context_data = []
                # هنعرض 50 بايت قبل الاسم و 50 بعده
                for i in range(m_idx - 60, m_idx + 20, 1):
                    if 0 <= i < len(data):
                        val = data[i]
                        context_data.append({
                            "الـ Index": i,
                            "العنوان (Hex)": hex(i),
                            "القيمة (Value)": val,
                            "المسافة من الاسم": i - m_idx
                        })
                
                df_context = pd.DataFrame(context_data)
                st.dataframe(df_context.T) # عرض بالعرض عشان سهولة القراءة
                
                # استخراج القيم المحتملة (لو لقيت 33 و 11 و 8 قريبين من بعض)
                potential_stats = [d['القيمة (Value)'] for d in context_data]
                st.write(f"🔍 **قيم البحث السريع في هذه المنطقة:** `{potential_stats}`")
        else:
            st.error("الاسم ده مش موجود في ملف الحفظ بصيغة النص. ده معناه إن الأسماء مشفرة كمان!")

    st.write("---")
    st.info("💡 **الخطة دلوقتي:** اكتب اسم لاعب 'نادر' عندك في الفريق مش متكرر، وشوف الجدول اللي هيطلع. لو لقيت أرقام طاقاته (عمره، سرعته) موجودة في الجدول 'قبل' الاسم بمسافة معينة، يبقى إحنا مسكنا الشفرة خلاص.")
    
