import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Name Merger", layout="wide")
st.title("🏹 رادار الدراويش: دمج الأسماء مع الطاقات")

# رفع ملفين: ملف الحفظ الأصلي وملف الـ CSV اللي إنت لسه مطلعه
col1, col2 = st.columns(2)
with col1:
    save_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat"])
with col2:
    csv_file = st.file_uploader("📄 ارفع ملف CSV اللي استخرجناه", type=["csv"])

if save_file and csv_file:
    # 1. قراءة البيانات
    data = save_file.read()
    df_attributes = pd.read_csv(csv_file)
    
    st.info(f"✅ تم تحميل بيانات {len(df_attributes)} لاعب.")

    if st.button("🔗 ابدأ عملية الربط السحرية"):
        # 2. استخراج مخزن الأسماء (Name Pool)
        # المنطقة دي ثابتة غالباً في FM Mobile
        names_area = data[30000000:45000000] 
        found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
        names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
        names_pool = list(dict.fromkeys(names_pool)) # حذف التكرار
        
        st.write(f"🔍 وجدنا {len(names_pool)} اسم في مخزن الأسماء.")

        # 3. المزامنة (The Sync)
        # هنا التحدي: اللعبة بترتب اللعيبة بنفس ترتيب أساميهم في المخزن
        # هنحاول نربطهم ونخلي المستخدم يظبط الـ "Shift"
        
        shift = st.slider("تعديل المزامنة (Shift Value)", -100, 100, 0)
        
        final_list = []
        # بنفلتر الداتا عشان نشيل القيم الوهمية (زي الـ 255)
        df_filtered = df_attributes[df_attributes['الـ CA/PA'] <= 200].copy()
        
        for i, row in enumerate(df_filtered.itertuples()):
            name_idx = i + shift
            if 0 <= name_idx < len(names_pool):
                final_list.append({
                    "الاسم المتوقع": names_pool[name_idx],
                    "العمر": row.العمر,
                    "الطاقة (PA)": row._3, # الـ CA/PA
                    "السرعة": row.السرعة,
                    "التحمل": row.التحمل,
                    "العنوان": row._1 # العنوان Hex
                })

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.success("🎯 تمت عملية الربط! راجع الأسماء مع الأعمار.")
            st.dataframe(df_final, use_container_width=True)
            
            # زر التحميل النهائي
            csv_final = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل كشاف اللعيبة النهائي", csv_final, "ismaily_fm26_full_scout.csv")
            
