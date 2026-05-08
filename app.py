import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Name Decryptor", layout="wide")
st.title("🏹 رادار الدراويش: كاشف الأسماء المطور")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])
search_query = st.text_input("🔍 ابحث عن اسم لاعب تعرفه (مثلاً: Endrick) لمعايرة الرادار:")

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # ميزة البحث عن اسم محدد لمعرفة موقعه
    if search_query:
        # البحث بالنظام العادي والنظام المشفر (UTF-16)
        query_bytes = search_query.encode('ascii', errors='ignore')
        matches = [m.start() for m in re.finditer(query_bytes, data)]
        if matches:
            st.info(f"📍 وجدنا الاسم '{search_query}' في المواقع التالية: {matches}")
        else:
            st.warning("لم نجد هذا الاسم، حاول كتابة الاسم الأول فقط.")

    results = []
    # المسح لاستخراج البيانات
    for i in range(1000, len(raw_bytes) - 100):
        pa = raw_bytes[i]
        if 150 <= pa <= 200:
            age = raw_bytes[i+2]
            if 15 <= age <= 40:
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                strength = raw_bytes[i+8]
                
                if 5 <= pace <= 20 and 5 <= stamina <= 20:
                    # محاولة استخراج الاسم بذكاء أكبر
                    player_name = "Unknown"
                    # فحص الـ 400 بايت اللي قبل الطاقة
                    search_area = data[max(0, i-400):i]
                    
                    # البحث عن نمط الأسماء (تبدأ بحرف كبير وبعدها حروف صغيرة)
                    # جربنا الأنماط العادية، دلوقت هنجرب نشيل الأصفار (Null bytes)
                    cleaned_area = search_area.replace(b'\x00', b'')
                    names = re.findall(b"[A-Z][a-z]{2,15}", cleaned_area)
                    
                    if names:
                        try:
                            # بناخد آخر اسم ظهر قبل الأرقام
                            player_name = names[-1].decode('ascii')
                        except:
                            pass

                    results.append({
                        "الاسم المتوقع": player_name,
                        "الـ PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "ID": i
                    })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['ID'])
        # تصفية الأسماء اللي طلعت أندية أو كلمات غير مفيدة
        filter_list = ['Strasbourg', 'Juventus', 'Gent', 'Club', 'Team', 'Stadium']
        df = df[~df['الاسم المتوقع'].isin(filter_list)]
        
        top_df = df.sort_values(by="الـ PA", ascending=False)
        st.success(f"🎯 تم رصد {len(top_df)} لاعب.")
        st.dataframe(top_df, use_container_width=True)
        
        csv = top_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير", csv, "ismaily_names_fixed.csv", "text/csv")
        
