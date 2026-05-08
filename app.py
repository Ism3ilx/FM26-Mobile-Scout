import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Name Merger", layout="wide")
st.title("🏹 رادار الدراويش: دمج الأسماء (النسخة المستقرة)")

# رفع الملفات
col1, col2 = st.columns(2)
with col1:
    save_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat"])
with col2:
    csv_file = st.file_uploader("📄 ارفع ملف CSV (الذي استخرجناه سابقاً)", type=["csv"])

if save_file and csv_file:
    # 1. قراءة ملف البيانات وتطهير الأعمدة
    # نستخدم encoding='utf-8-sig' للتعامل مع الحروف العربية بشكل أفضل
    df_attributes = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # حيلة ذكية: إعادة تسمية الأعمدة لأسماء إنجليزية لضمان عدم حدوث KeyError
    # الترتيب: العنوان، العمر، الطاقة، القوة، السرعة، التحمل، البصمة
    df_attributes.columns = ["Address", "Age", "CAPA", "Strength", "Pace", "Stamina", "Status"]
    
    data = save_file.read()
    st.info(f"✅ تم تحميل بيانات {len(df_attributes)} لاعب بنجاح.")

    # 2. إعدادات المزامنة
    st.sidebar.header("⚙️ إعدادات المزامنة")
    shift = st.sidebar.slider("تعديل المزامنة (Shift Value)", -200, 200, 0)
    min_capa_filter = st.sidebar.slider("عرض اللاعبين بطاقة أعلى من:", 0, 200, 100)

    if st.button("🔗 ابدأ عملية الربط وإظهار الأسماء"):
        # 3. استخراج الأسماء من الملف الأصلي
        # المنطقة المعتادة للأسماء في FM26 Mobile
        names_area = data[30000000:45000000] 
        found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
        names_pool = [n.decode('ascii', errors='ignore') for n in found_names]
        names_pool = list(dict.fromkeys(names_pool)) # حذف التكرار
        
        st.write(f"🔍 وجدنا {len(names_pool)} اسم فريد في مخزن الأسماء.")

        # 4. المزامنة والفلترة
        final_list = []
        # نفلتر القيم الوهمية (أكبر من 200) والقيم الضعيفة (أقل من المختار في السلايدر)
        df_filtered = df_attributes[(df_attributes['CAPA'] <= 200) & (df_attributes['CAPA'] >= min_capa_filter)].copy()
        
        for i, row in enumerate(df_filtered.itertuples()):
            name_idx = i + shift
            if 0 <= name_idx < len(names_pool):
                final_list.append({
                    "الاسم المتوقع": names_pool[name_idx],
                    "العمر": row.Age,
                    "الطاقة (PA/CA)": row.CAPA,
                    "السرعة": row.Pace,
                    "التحمل": row.Stamina,
                    "القوة": row.Strength,
                    "عنوان الـ Hex": row.Address
                })

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.success("🎯 تمت عملية الربط بنجاح!")
            
            # عرض الجدول النهائي
            st.dataframe(df_final, use_container_width=True)
            
            # زر تحميل الملف النهائي
            csv_final = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل كشاف اللعيبة النهائي الكامل",
                data=csv_final,
                file_name="ismaily_fm26_full_scout.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ لم يتم العثور على نتائج مطابقة. جرب تغيير قيمة الـ Shift أو الـ Filter.")

