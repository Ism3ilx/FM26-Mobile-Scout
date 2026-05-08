import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Final Merger Pro", layout="wide")
st.title("🏹 رادار الدراويش: دمج الأسماء (نسخة الإصلاح النهائي)")

# رفع الملفات
col1, col2 = st.columns(2)
with col1:
    save_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat"])
with col2:
    csv_file = st.file_uploader("📄 ارفع ملف CSV المستخرج", type=["csv"])

if save_file and csv_file:
    try:
        # 1. قراءة الملف
        df_raw = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # أخذ أول 7 أعمدة وإعادة تسميتها
        df_attributes = df_raw.iloc[:, :7].copy()
        df_attributes.columns = ["Address", "Age", "CAPA", "Strength", "Pace", "Stamina", "Status"]
        
        # 🛡️ السطر السحري: تحويل كل الأعمدة اللي محتاجينها لأرقام
        # لو فيه أي قيمة مش رقم، هيحولها لـ NaN (قيمة فارغة) عشان الكود ميكرشش
        cols_to_fix = ["Age", "CAPA", "Strength", "Pace", "Stamina"]
        for col in cols_to_fix:
            df_attributes[col] = pd.to_numeric(df_attributes[col], errors='coerce')
        
        # مسح الصفوف اللي فيها قيم فارغة في الـ CAPA عشان نضمن جودة البيانات
        df_attributes = df_attributes.dropna(subset=['CAPA'])
        
        st.success(f"✅ تم تحميل بيانات {len(df_attributes)} لاعب وتحويلها لأرقام بنجاح.")
        
    except Exception as e:
        st.error(f"❌ خطأ في الملف: {e}")
        st.stop()

    data = save_file.read()

    # 2. إعدادات المزامنة
    st.sidebar.header("⚙️ إعدادات المزامنة")
    shift = st.sidebar.slider("تعديل المزامنة (Shift Value)", -500, 500, 0)
    min_capa = st.sidebar.slider("عرض طاقة أعلى من:", 0, 200, 130)

    if st.button("🔗 ربط الأسماء الآن"):
        # 3. سحب الأسماء
        names_area = data[30000000:45000000] 
        found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
        
        names_pool = []
        seen = set()
        for n in found_names:
            name_str = n.decode('ascii', errors='ignore')
            if name_str not in seen:
                names_pool.append(name_str)
                seen.add(name_str)
        
        # 4. المزامنة (بعد التأكد إن CAPA بقت رقم)
        final_results = []
        df_work = df_attributes[(df_attributes['CAPA'] <= 200) & (df_attributes['CAPA'] >= min_capa)].copy()
        
        for i, row in enumerate(df_work.itertuples()):
            name_idx = i + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم المتوقع": names_pool[name_idx],
                    "العمر": int(row.Age),
                    "الطاقة (PA)": int(row.CAPA),
                    "السرعة": int(row.Pace),
                    "التحمل": int(row.Stamina),
                    "القوة": int(row.Strength),
                    "العنوان": row.Address
                })

        if final_results:
            df_final = pd.DataFrame(final_results)
            st.success("🎯 مبروك! الأسماء والبيانات جاهزة.")
            st.dataframe(df_final, use_container_width=True)
            
            csv_out = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل ملف الكشاف النهائي", csv_out, "final_scout_fixed.csv")
        else:
            st.warning("⚠️ لا توجد نتائج. حاول تغيير الـ Shift أو تقليل الـ PA.")
    
