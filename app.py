import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Flexible Scout", layout="wide")
st.title("🏹 رادار الدراويش: النسخة المرنة (V2.1)")

st.markdown("""
### 🛡️ التحديثات الجديدة:
* **توسيع نطاق البحث:** الكود أصبح يبحث عن الأسماء في مساحة أكبر حول بيانات اللاعب.
* **إصلاح الأخطاء:** تم تصحيح مسارات المتغيرات لضمان قراءة العمر والطاقات بدقة.
* **نظام التنسيق التلقائي:** الكود يحاول تخمين أقرب اسم منطقي حتى لو لم يتبع النمط التقليدي.
""")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat", "sav"])

def smart_name_finder(data_chunk):
    """تحاول العثور على أفضل اسم متاح في قطعة البيانات"""
    # البحث عن نمط الاسم (كلمة تبدأ بحرف كبير تليها حروف صغيرة)
    matches = re.findall(b"([A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?)", data_chunk)
    if matches:
        # نأخذ أطول اسم وجدناه لأنه غالباً يكون الاسم الكامل للاعب
        best_name = max(matches, key=len).decode('ascii', errors='ignore')
        # فلترة لضمان عدم أخذ كلمات تقنية
        if best_name not in ["City", "United", "Value", "Offset", "None"]:
            return best_name
    return "Unknown Player"

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)
    
    if st.button("🚀 ابدأ المسح الشامل"):
        players_data = []
        # الفاصل الذهبي اللي اكتشفناه في ملف كورتوا
        magic_sequence = bytes([255, 255, 255, 255])
        start_pos = 0
        
        # البحث في أول 30 ميجا لضمان تغطية كل اللاعبين
        limit = min(file_size, 30000000)
        
        with st.spinner("جاري تحليل شفرات اللاعبين..."):
            while True:
                idx = data.find(magic_sequence, start_pos)
                if idx == -1 or idx >= limit:
                    break
                
                # العنوان اللي بعد الفاصل هو العمر (Offset 0)
                age_pos = idx + 4 
                
                if age_pos < file_size:
                    age = data[age_pos]
                    
                    # فلترة العمر (15-45 سنة)
                    if 15 <= age <= 45:
                        try:
                            # استخراج الطاقات بناءً على الأوفستس الخاصة بك (DNA)
                            # PA عند -18، السرعة عند -10، إلخ
                            pa_val    = data[age_pos - 18]
                            strength  = data[age_pos - 12]
                            pace      = data[age_pos - 10]
                            stamina   = data[age_pos - 6]
                            
                            # شرط إضافي لضمان جودة البيانات
                            if 50 <= pa_val <= 200:
                                # البحث عن الاسم في "نافذة" حول اللاعب (200 بايت قبل وبعد)
                                window_start = max(0, age_pos - 250)
                                window_end = min(file_size, age_pos + 50)
                                name_chunk = data[window_start:window_end]
                                
                                player_name = smart_name_finder(name_chunk)
                                
                                players_data.append({
                                    "الاسم": player_name,
                                    "العمر": age,
                                    "الطاقة (PA)": pa_val,
                                    "السرعة": pace,
                                    "التحمل": stamina,
                                    "القوة": strength,
                                    "Hex Address": hex(age_pos)
                                })
                        except IndexError:
                            pass
                
                start_pos = idx + 1

        if players_data:
            df = pd.DataFrame(players_data)
            # حذف التكرارات بناءً على العنوان والاسم
            df = df.drop_duplicates(subset=['Hex Address']).reset_index(drop=True)
            
            st.success(f"🎉 تم العثور على {len(df)} لاعب بنجاح!")
            
            # ترتيب تنازلي حسب القوة
            df = df.sort_values(by="الطاقة (PA)", ascending=False)
            
            st.dataframe(df, use_container_width=True)
            
            # تحميل النتائج
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل قاعدة البيانات المحدثة", csv, "ismaily_scout_v2.csv", "text/csv")
        else:
            st.error("⚠️ لم نجد بيانات مطابقة. جرب التأكد من أن الملف هو ملف الحفظ (Auto-save) أو ملف حفظ يدوي حديث.")

st.info("💡 **نصيحة إضافية:** إذا استمرت المشكلة، جرب رفع الملف الأصلي الذي استخرجت منه كورتوا تحديداً، لنرى إذا كان هناك أي تغير في بنية الملفات الجديدة.")
            
