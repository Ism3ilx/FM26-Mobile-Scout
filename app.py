import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ismaily SC - Deep Scanner", layout="wide")
st.title("🏹 رادار الدراويش: المسح العميق والمكثف (V3.0)")

uploaded_file = st.file_uploader("📂 ارفع ملف الحفظ (.fms)", type=["fms", "dat", "sav"])

def get_name_from_nearby(data, pos):
    """محاولة استخراج أطول نص منطقي حول مكان اللاعب"""
    start = max(0, pos - 400)
    end = min(len(data), pos + 100)
    chunk = data[start:end]
    # البحث عن نمط الأسماء (تبدأ بحرف كبير)
    matches = re.findall(b"([A-Z][a-z]{2,15}(?:\s[A-Z][a-z]{2,15})?)", chunk)
    if matches:
        # نأخذ أطول اسم وجدناه لضمان الدقة
        names = [n.decode('ascii', errors='ignore') for n in matches if len(n) > 3]
        # استبعاد الكلمات المشهورة غير البشرية
        filtered = [n for n in names if n not in ["City", "United", "Value", "Offset", "None", "West", "East"]]
        return filtered[-1] if filtered else "Unknown"
    return "Unknown"

if uploaded_file:
    data = uploaded_file.read()
    file_size = len(data)
    st.info(f"📁 تم تحميل الملف. حجمه: {file_size / (1024*1024):.2f} ميجابايت.")

    if st.button("🔍 ابدأ الفحص الشامل (Deep Scan)"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        players_found = []
        magic_seq = bytes([255, 255, 255, 255])
        
        # البحث في الملف بالكامل (مش بس أول 30 ميجا)
        # هنمشي بخطوات واسعة عشان السرعة
        start_search = 0
        
        with st.spinner("جاري فحص البايتات..."):
            while True:
                idx = data.find(magic_seq, start_search)
                if idx == -1:
                    break
                
                # تحديث العداد كل فترة
                if len(players_found) % 100 == 0:
                    progress = min(idx / file_size, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"تم فحص {idx // (1024*1024)}MB.. وجدنا حتى الآن {len(players_found)} احتمال لاعب")

                # العمر عند بصمة الـ 255
                age_pos = idx + 4
                if age_pos < file_size:
                    age = data[age_pos]
                    
                    # لو السن منطقي (بين 15 و 50)
                    if 15 <= age <= 50:
                        try:
                            # قراءة الطاقات (الأوفستس الخاصة بك)
                            pa_val = data[idx - 14] # PA (بناءً على ملف كورتوا)
                            speed = data[idx - 6]
                            stamina = data[idx - 2]
                            
                            # لو الطاقة منطقية للاعب
                            if 50 <= pa_val <= 200:
                                name = get_name_from_nearby(data, idx)
                                players_found.append({
                                    "الاسم": name,
                                    "العمر": age,
                                    "الطاقة (PA)": pa_val,
                                    "السرعة": speed,
                                    "التحمل": stamina,
                                    "العنوان (Hex)": hex(idx)
                                })
                        except:
                            pass
                
                start_search = idx + 1
        
        progress_bar.progress(1.0)
        
        if players_found:
            df = pd.DataFrame(players_found).drop_duplicates(subset=['العنوان (Hex)'])
            st.success(f"🎉 تم العثور على {len(df)} لاعب بنجاح!")
            
            # عرض الجدول مرتب حسب الطاقة
            st.dataframe(df.sort_values(by="الطاقة (PA)", ascending=False), use_container_width=True)
            
            # زر التحميل
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل النتائج النهائية", csv, "fm26_deep_scout.csv")
        else:
            st.error("❌ الكود لم يجد أي لاعبين. ده معناه إن ملفك له 'بصمة' مختلفة.")
            st.warning("⚠️ جرب ترفع صورة من 'Hex Editor' لو تقدر لمكان كورتوا في ملفك عشان أشوف الـ 255ات مكانها فين بالظبط.")
        
