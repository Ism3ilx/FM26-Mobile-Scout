import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Scout", layout="wide")
st.title("🏹 رادار الدراويش: كاشف المواهب النهائي (Yamal Edition)")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    
    # 1. استخراج كل الأسماء من "منطقة يامال" (الأسماء بتبدأ تظهر بكثافة بعد الموقع 30 مليون)
    st.info("🔍 جاري جرد كشف الأسماء من مخزن اللعبة...")
    names_pool = []
    # بنعمل مسح للمنطقة اللي ظهر فيها يامال
    search_area_names = data[30000000:] 
    # استخراج الكلمات اللي بتبدأ بحرف كبير (نظام الأسماء في FM)
    found_names = re.findall(b"[A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?", search_area_names)
    for n in found_names:
        name_str = n.decode('ascii', errors='ignore')
        if name_str not in names_pool:
            names_pool.append(name_str)

    # 2. استخراج الطاقات (النمط اللي نجحنا فيه قبل كده)
    results = []
    for i in range(1000, 10000000): # بنركز في أول 10 مليون بايت للطاقات
        pa = raw_bytes[i]
        if 150 <= pa <= 200:
            age = raw_bytes[i+2]
            if 15 <= age <= 21: # بنركز على المواهب الصغيرة فقط
                pace = raw_bytes[i+6]
                stamina = raw_bytes[i+7]
                
                if 5 <= pace <= 20 and 5 <= stamina <= 20:
                    results.append({
                        "PA": pa,
                        "العمر": age,
                        "السرعة": pace,
                        "التحمل": stamina,
                        "ID": i
                    })

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['ID'])
        df = df.sort_values(by="ID") # ترتيب حسب الظهور في الملف للربط مع الأسماء
        
        # ربط الأسماء بالترتيب (تقريبي)
        final_list = []
        for index, row in df.iterrows():
            # بناخد اسم من المخزن بناءً على ترتيب اللاعب (محاولة ربط تسلسلي)
            name_idx = len(final_list) % len(names_pool) if names_pool else 0
            name = names_pool[name_idx] if names_pool else "Unknown"
            
            final_list.append({
                "الاسم المتوقع": name,
                "الـ PA": row['PA'],
                "العمر": row['العمر'],
                "السرعة": row['السرعة'],
                "التحمل": row['التحمل'],
                "موقع البيانات": row['ID']
            })

        final_df = pd.DataFrame(final_list)
        st.success(f"🎯 تم الربط! وجدنا {len(final_df)} موهبة محتملة.")
        
        # عرض قائمة "الصفوة" (PA > 180)
        st.subheader("⭐ قائمة الصفوة (مواهب عالمية)")
        st.dataframe(final_df[final_df['الـ PA'] >= 180], use_container_width=True)
        
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير الكامل", csv, "ismaily_yamal_scout.csv", "text/csv")
    else:
        st.error("⚠️ لم نجد بيانات طاقات متوافقة.")
