import streamlit as st
import pandas as pd
import struct

st.set_page_config(page_title="Ismaily SC - Full Decoder", layout="wide")
st.title("🏹 مستخرج بيانات FM26 الشامل")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    file_size = len(data)
    
    st.info(f"⏳ جاري مسح {file_size / (1024*1024):.2f} ميجابايت... انتظر قليلاً.")

    all_players = []
    
    # هنمشي على الملف بايت بايت عشان ميفوتناش هفوة
    # منطقة طاقات اللاعبين عادة بتبدأ بعد أول 1000 بايت
    for i in range(1000, min(file_size, 25000000), 1):
        try:
            # قراءة الـ PA (البايت الحالي)
            pa = data[i]
            
            # لو الـ PA في نطاق النجوم (150 لـ 200)
            if 150 <= pa <= 200:
                # التأكد من العمر (موجود بعد الـ PA بـ 2 بايت)
                age = data[i+2]
                if 15 <= age <= 40:
                    # قراءة باقي الخصائص (بافتراض المسافات القياسية في FM Mobile)
                    pace = data[i+6]
                    stamina = data[i+7]
                    strength = data[i+8]
                    
                    # فلتر إضافي للتأكد إن دي بيانات لاعب مش أرقام عشوائية
                    if 1 <= pace <= 20 and 1 <= stamina <= 20:
                        all_players.append({
                            "العنوان (Hex)": hex(i),
                            "PA": pa,
                            "العمر": age,
                            "السرعة": pace,
                            "التحمل": stamina,
                            "القوة": strength,
                            "البيانات الخام": data[i:i+10].hex() # عشان لو حبيت تراجعها بالـ Hex Editor
                        })
        except IndexError:
            break

    if all_players:
        df = pd.DataFrame(all_players).drop_duplicates(subset=['العنوان (Hex)'])
        st.success(f"✅ تم العثور على {len(df)} بصمة لاعب محتملة!")
        
        # عرض عينة
        st.subheader("🔍 عينة من البيانات المستخرجة")
        st.dataframe(df.head(50), use_container_width=True)
        
        # أهم جزء: تحميل البيانات
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل كافة البيانات المستخرجة (CSV)",
            data=csv,
            file_name="ismaily_full_dump.csv",
            mime="text/csv",
        )
        
        st.write("---")
        st.markdown("""
        ### 💡 إزاي تلاقي كورتوا أو إندريك في الملف ده؟
        1. حمل ملف الـ **CSV** وافتحه ببرنامج **Excel**.
        2. اعمل **Filter** لعمود 'العمر' واختار (33) لكورتوا أو (19) لإندريك.
        3. بص على عمود 'السرعة' و 'التحمل' وقارنهم باللي عندك في اللعبة.
        4. أول ما تلاقي كورتوا، شوف **العنوان (Hex)** بتاعه.. ده اللي هيخلينا نربط الأسامي صح المرة الجاية.
        """)
    else:
        st.error("❌ لم يتم العثور على أي بيانات تطابق المواصفات. حاول رفع ملف حفظ آخر.")
        
