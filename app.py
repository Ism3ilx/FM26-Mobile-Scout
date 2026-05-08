import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ismaily SC - Data Miner", layout="wide")
st.title("⚽ رادار الإسماعيلي: منقب البيانات (Data Miner)")
st.info("هذه النسخة تبحث عن 'القدرات' مباشرة وتتجاهل هيكل الأسماء المعقد.")

uploaded_file = st.file_uploader("ارفع ملف الحفظ (.fms)", type=["fms", "dat"])

if uploaded_file:
    data = uploaded_file.read()
    results = []
    
    # تحويل الملف لقائمة أرقام للبحث السريع
    raw_bytes = list(data)
    
    # البحث عن "كتلة مهارات بدنية" (تتابع منطقي)
    # بنبحث عن 3 أرقام (8-20) يليهم رقم صغير (العمر) يسبقهم رقم كبير (PA)
    for i in range(100, len(raw_bytes) - 50):
        # النمط: [PA] ثم [فراغ] ثم [CA] ثم [فراغ] ثم [العمر] ثم [سرعة، تحمل، قوة]
        # هذا النمط شائع جداً في ملفات FM Mobile
        if 100 <= raw_bytes[i] <= 200: # احتمال يكون PA
            if 16 <= raw_bytes[i+2] <= 42: # احتمال يكون العمر بعده بـ 2 بايت
                pace = raw_bytes[i+5]
                stamina = raw_bytes[i+6]
                strength = raw_bytes[i+7]
                
                if 5 <= pace <= 20 and 5 <= stamina <= 20 and 5 <= strength <= 20:
                    results.append({
                        "الموقع (Offset)": i,
                        "العمر": raw_bytes[i+2],
                        "السرعة": pace,
                        "التحمل": stamina,
                        "القوة": strength,
                        "PA": raw_bytes[i],
                        "CA": raw_bytes[i-2] if i-2 >= 0 else 0
                    })

    if results:
        df = pd.DataFrame(results)
        # تصفية النتائج المتكررة جداً أو غير المنطقية
        df = df.drop_duplicates(subset=['العمر', 'السرعة', 'التحمل', 'القوة', 'PA']).head(500)
        
        st.success(f"🎯 وجدنا {len(df)} كتلة مهارات محتملة للاعبين!")
        st.write("ملاحظة: بسبب نظام الملف، الأسماء غير مرتبطة حالياً، ابحث عن لاعبك من خلال طاقاته المعروفة:")
        
        st.dataframe(df.sort_values(by="PA", ascending=False), use_container_width=True)
    else:
        st.error("لم نجد نمط مهارات منطقي. الملف قد يكون مشفراً بشكل مختلف.")
        
