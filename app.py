import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Super Scanner", layout="wide")
st.title("🚀 كشاف الإسماعيلي: النسخة الشاملة (البحث العميق)")

# نصيحة للمستخدم
st.info("إذا لم يظهر لاعبون، حاول تقليل قيمة PA في الفلتر بالأسفل.")

uploaded_file = st.file_uploader("ارفع ملف الحفظ لدراسته", type=["dat", "fms"])

if uploaded_file:
    data = uploaded_file.read()
    
    # تحسين نمط البحث عن الأسماء ليكون أكثر مرونة (البحث عن أي اسمين يبدآن بحرف كبير)
    # هذا النمط سيصطاد كارفخال وفالفيردي وكورتوا مهما كان طول الاسم
    player_pattern = re.compile(b"([A-Z][a-z]{1,15}\s[A-Z][a-z]{1,15})")
    
    results = []
    seen_offsets = set()

    # البحث في الملف بالكامل
    for match in player_pattern.finditer(data):
        start_offset = match.start()
        
        try:
            # محاولة فك تشفير الاسم
            name = match.group(1).decode('latin-1').strip()
        except:
            continue

        # استبعاد الكلمات المكررة أو القصيرة جداً
        if start_offset in seen_offsets: continue

        # سحب بلوك بيانات كبير بعد الاسم (250 بايت)
        if start_offset + 250 <= len(data):
            record = list(data[start_offset : start_offset + 250])
            
            # --- المحرك الديناميكي الجديد بناءً على اكتشافك ---
            found_age = None
            age_idx = -1
            
            # البحث عن العمر في نطاق واسع جداً (من بعد الاسم بـ 40 خانة وحتى 150)
            # نحن نبحث عن رقم منطقي للعمر (16-43)
            for i in range(40, 150):
                val = record[i]
                if 16 <= val <= 43:
                    # التأكد من "البصمة البدنية" بعد العمر بـ 29 خانة (اكتشافك الذهبي)
                    # نتأكد أن السرعة والتحمل أرقام منطقية (بين 1 و 20)
                    if i + 31 < len(record):
                        p_check = record[i + 29]
                        s_check = record[i + 30]
                        if 1 <= p_check <= 20 and 1 <= s_check <= 20:
                            found_age = val
                            age_idx = i
                            break
            
            if found_age:
                # تطبيق إحداثياتك الدقيقة
                pace = record[age_idx + 29]
                stamina = record[age_idx + 30]
                strength = record[age_idx + 31]
                
                # استخراج PA (القدرة الكامنة) - غالباً قبل العمر بـ 11 خانة
                pa = record[age_idx - 11]
                ca = record[age_idx - 13]

                # تنظيف القيم لعرضها
                results.append({
                    "الاسم": name,
                    "العمر": found_age,
                    "السرعة": pace,
                    "التحمل": stamina,
                    "القوة": strength,
                    "PA": pa if 100 <= pa <= 200 else "N/A",
                    "CA": ca if 100 <= ca <= 200 else "N/A"
                })
                seen_offsets.add(start_offset)

    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['الاسم', 'العمر'])
        
        st.success(f"✅ تم العثور على {len(df)} لاعب بنجاح!")
        
        # فلتر البحث
        search = st.text_input("🔍 ابحث عن لاعب محدد (مثال: Carvajal):")
        if search:
            df = df[df['الاسم'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.error("❌ لم يتم العثور على أي لاعب. قد يكون نظام تشفير الأسماء في ملفك مختلفاً.")
        st.write("نصيحة: تأكد أنك رفعت ملف الحفظ الصحيح (Save Game) وليس ملف اللعبة الأساسي.")

