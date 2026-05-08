import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - The Ultimate Extractor", layout="wide")
st.title("🏆 حاصد الأرواح: المستخرج النهائي لبيانات FM26")

st.markdown("""
### 💡 كيف يعمل؟
الكود الآن يستخدم **"الخريطة الجينية الحقيقية"** التي اكتشفناها:
السمات تسبق العمر بمسافات ثابتة (-6 للتحمل، -10 للسرعة، -18 للـ PA/CA).
""")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms / .dat)", type=["dat", "fms", "sav"])

if uploaded_file:
    data = uploaded_file.read()
    raw_bytes = list(data)
    file_size = len(data)
    
    if st.button("🚀 استخراج قاعدة بيانات اللاعبين"):
        players_data = []
        
        with st.spinner("جاري حصاد اللاعبين بناءً على الشفرة المكتشفة..."):
            # البحث عن الفاصل السحري 255, 255, 255, 255
            magic_sequence = bytes([255, 255, 255, 255])
            start_pos = 0
            
            while True:
                # العثور على مكان الفاصل
                idx = data.find(magic_sequence, start_pos)
                if idx == -1 or idx > 20000000: # نبحث في أول 20 ميجا
                    break
                
                # العنوان اللي بعد الفاصل مباشرة هو "العمر" (Index 0 في خريطتنا)
                age_idx = idx + 4 
                
                if age_idx < len(raw_bytes):
                    age = raw_bytes[age_idx]
                    
                    # فلترة منطقية: العمر لازم يكون بين 15 و 45
                    if 15 <= age <= 45:
                        try:
                            # استخراج البيانات باستخدام الإزاحات (Offsets) اللي اكتشفناها
                            ca_pa_val = raw_bytes[age_idx - 18]
                            strength  = raw_bytes[age_idx - 12]
                            pace      = raw_bytes[age_idx - 10]
                            stamina   = raw_bytes[age_idx - 6]
                            
                            # فلترة إضافية عشان نتأكد إن ده لاعب بجد مش بيانات عشوائية
                            if ca_pa_val > 50 and pace <= 20 and stamina <= 20 and strength <= 20:
                                players_data.append({
                                    "العنوان (Hex)": hex(age_idx),
                                    "العمر": age,
                                    "الـ CA/PA": ca_pa_val,
                                    "القوة": strength,
                                    "السرعة": pace,
                                    "التحمل": stamina,
                                    "بصمة التأكيد": "✅"
                                })
                        except IndexError:
                            pass
                
                # تحريك نقطة البحث
                start_pos = idx + 1

        if players_data:
            st.success(f"🎉 الله أكبر! تم استخراج بيانات {len(players_data)} لاعب بنجاح!")
            df = pd.DataFrame(players_data)
            
            # ترتيب اللاعبين من الأعلى طاقة للأقل
            df = df.sort_values(by="الـ CA/PA", ascending=False).reset_index(drop=True)
            
            st.dataframe(df, use_container_width=True)
            
            # تحميل الملف
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل قاعدة البيانات (CSV)", csv, "ismaily_fm26_database.csv", "text/csv")
        else:
            st.error("لم يتم العثور على بيانات مطابقة. تأكد من الملف.")

st.info("💡 **ملاحظة:** الجدول هيطلع لك كل اللعيبة بأعمارهم وطاقاتهم. خطوتنا الجاية هي دمج الأسامي معاهم، بس خلينا نحتفل بإننا كسرنا التشفير الرقمي الأول!")
                            
