import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Ultimate Merger", layout="wide")
st.title("🏹 رادار الدراويش: دمج الأسماء (نسخة الإصلاح الشامل)")

# رفع الملفات
col1, col2 = st.columns(2)
with col1:
    save_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat"])
with col2:
    csv_file = st.file_uploader("📄 ارفع ملف CSV المستخرج", type=["csv"])

if save_file and csv_file:
    # 1. قراءة الملف بذكاء لتجنب ValueError
    try:
        # قراءة الملف بدون تحديد أسماء أعمدة في البداية
        df_raw = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # التأكد من أننا نأخذ أول 7 أعمدة فقط مهما كان عدد الأعمدة في الملف
        df_attributes = df_raw.iloc[:, :7].copy()
        
        # إعادة التسمية للأعمدة السبعة الأساسية
        df_attributes.columns = ["Address", "Age", "CAPA", "Strength", "Pace", "Stamina", "Status"]
        
        st.success(f"✅ تم تحميل بيانات {len(df_attributes)} لاعب وتجهيزها للربط.")
        
    except Exception as e:
        st.error(f"❌ مشكلة في قراءة ملف CSV: {e}")
        st.stop()

    data = save_file.read()

    # 2. إعدادات المزامنة في الجانب
    st.sidebar.header("⚙️ إعدادات المزامنة")
    shift = st.sidebar.slider("تعديل المزامنة (Shift Value)", -500, 500, 0)
    min_capa = st.sidebar.slider("فلتر أقل طاقة (PA):", 0, 200, 120)

    if st.button("🔗 ربط الأسماء وإظهار القائمة النهائية"):
        # 3. استخراج الأسماء من منطقة الـ Name Pool
        # المنطقة المعتادة في ملفات FM26 Mobile
        names_area = data[30000000:45000000] 
        found_names = re.findall(b"[A-Z][a-z]{3,15}(?:\s[A-Z][a-z]{3,15})?", names_area)
        # تحويل البايتات لنصوص وحذف التكرار مع الحفاظ على الترتيب
        names_pool = []
        seen = set()
        for n in found_names:
            name_str = n.decode('ascii', errors='ignore')
            if name_str not in seen:
                names_pool.append(name_str)
                seen.add(name_str)
        
        st.write(f"🔍 تم العثور على {len(names_pool)} اسم فريد.")

        # 4. المزامنة
        final_results = []
        # فلترة القيم الغريبة (أكبر من 200 هي قيم تقنية مش طاقات لاعيبة)
        df_work = df_attributes[(df_attributes['CAPA'] <= 200) & (df_attributes['CAPA'] >= min_capa)].copy()
        
        for i, row in enumerate(df_work.itertuples()):
            name_idx = i + shift
            if 0 <= name_idx < len(names_pool):
                final_results.append({
                    "الاسم": names_pool[name_idx],
                    "العمر": row.Age,
                    "الطاقة (PA)": row.CAPA,
                    "السرعة": row.Pace,
                    "التحمل": row.Stamina,
                    "القوة": row.Strength,
                    "العنوان (Hex)": row.Address
                })

        if final_results:
            df_final = pd.DataFrame(final_results)
            st.success("🎯 مبروك! الأسماء ظهرت بنجاح.")
            
            # ترتيب حسب الطاقة
            df_final = df_final.sort_values(by="الطاقة (PA)", ascending=False)
            
            st.dataframe(df_final, use_container_width=True)
            
            # زر التحميل
            csv_out = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل الكشاف الكامل بالأسماء", csv_out, "final_scout_names.csv")
        else:
            st.warning("⚠️ لا توجد نتائج. حاول تغيير قيمة الـ Shift.")
            
