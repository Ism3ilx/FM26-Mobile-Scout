import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Decoder Pro", layout="wide")
st.title("🏹 رادار الدراويش: كود كسر الشفرة النهائي")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    st.sidebar.header("🎯 إعدادات البحث")
    player_name = st.text_input("اكتب اسم اللاعب بالانجليزي (مثلاً: Courtois):")

    if player_name:
        # البحث عن مكان الاسم في الملف
        name_bytes = player_name.encode('ascii')
        indices = [i for i, _ in enumerate(data) if data.startswith(name_bytes, i)]
        
        if indices:
            st.success(f"✅ وجدنا اسم {player_name} في {len(indices)} مكان!")
            
            for idx in indices:
                st.write(f"### 📍 تحليل العنوان: {hex(idx)}")
                
                # إستراتيجية البحث "الخلفي": الطاقات دايماً قبل الاسم في FM Mobile
                # هنطلع الـ 100 بايت اللي قبل الاسم ونحللهم
                st.write("🔍 فحص البايتات التي تسبق الاسم (حيث تختبئ الطاقات):")
                
                analysis = []
                for i in range(idx - 60, idx + 10): # 60 بايت قبل و10 بعد
                    if 0 <= i < len(data):
                        val = data[i]
                        analysis.append({
                            "Index": i,
                            "Hex": hex(i),
                            "Value": val,
                            "Distance": i - idx
                        })
                
                df_ana = pd.DataFrame(analysis)
                # عرض البيانات بشكل أفقي لسهولة العثور على البصمة
                st.dataframe(df_ana.T, use_container_width=True)
                
                # محاولة ذكية لاستخراج طاقات اللاعب من هذه المنطقة
                vals = [d['Value'] for d in analysis]
                st.info(f"💡 بصمة المنطقة دي: {vals}")
                
        else:
            st.error("الاسم ده مش موجود كـ 'نص' واضح، جرب اسم لاعب تاني أو اسم فريقك.")

    st.write("---")
    st.subheader("📋 كاشف المواهب الشامل (Global Scout)")
    st.write("بناءً على العناوين اللي اكتشفناها في ملفاتك السابقة:")
    
    # محاولة جرد سريعة بناءً على نمط "العمر + PA"
    scout_list = []
    for i in range(1000, 15000000, 4):
        pa = raw_bytes[i]
        if 150 <= pa <= 200: # لعيبة سوبر
            age = raw_bytes[i+2]
            if 15 <= age <= 21: # مواهب صغيرة
                scout_list.append({
                    "Address": hex(i),
                    "Potential (PA)": pa,
                    "Age": age,
                    "Speed": raw_bytes[i+6],
                    "Stamina": raw_bytes[i+7]
                })
    
    if scout_list:
        df_scout = pd.DataFrame(scout_list).drop_duplicates(subset=['Address'])
        st.dataframe(df_scout.head(100), use_container_width=True)
        
        csv = df_scout.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل قائمة الـ 100 موهبة (CSV)", csv, "ismaily_scout_final.csv")
                        
