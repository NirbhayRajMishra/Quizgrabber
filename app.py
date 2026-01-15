import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="Quiz DB Maker", page_icon="📊")

st.title("📊 Structured Quiz Database")
st.write("PDF अपलोड करें - यह आटोमेटिक A, B, C, D कॉलम बना देगा।")

uploaded_file = st.file_uploader("Upload Hindi/English PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Start Extraction"):
        quiz_data = []
        progress_bar = st.progress(0)
        
        with pdfplumber.open(uploaded_file) as pdf:
            total_pages = len(pdf.pages)
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    # प्रश्न की शुरुआत पहचानना (e.g. 1. या Q1.)
                    segments = re.split(r'\n(?=\d+[\.\)]|Q\d+[\.\)])', text)
                    
                    for segment in segments:
                        if segment.strip():
                            lines = segment.strip().split('\n')
                            q_text = lines[0]
                            opt_a, opt_b, opt_c, opt_d = "", "", "", ""
                            ans, exp = "", ""

                            for line in lines:
                                l = line.strip()
                                # सटीक तरीके से A, B, C, D ऑप्शंस ढूँढना
                                if re.match(r'^[A][\.\)]', l): opt_a = re.sub(r'^[A][\.\)]', '', l).strip()
                                elif re.match(r'^[B][\.\)]', l): opt_b = re.sub(r'^[B][\.\)]', '', l).strip()
                                elif re.match(r'^[C][\.\)]', l): opt_c = re.sub(r'^[C][\.\)]', '', l).strip()
                                elif re.match(r'^[D][\.\)]', l): opt_d = re.sub(r'^[D][\.\)]', '', l).strip()
                                # Answer और Explanation ढूँढना
                                elif any(x in l for x in ["Answer", "Ans", "उत्तर"]): ans = l
                                elif any(x in l for x in ["Explanation", "व्याख्या", "विवरण"]): exp = l

                            quiz_data.append({
                                "Question": q_text,
                                "Option A": opt_a,
                                "Option B": opt_b,
                                "Option C": opt_c,
                                "Option D": opt_d,
                                "Correct Answer": ans,
                                "Explanation": exp
                            })
                progress_bar.progress((i + 1) / total_pages)

        df = pd.DataFrame(quiz_data)
        if not df.empty:
            st.success(f"कुल {len(df)} प्रश्न मिले!")
            st.dataframe(df.head(10)) 
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("Download CSV Database", data=csv, file_name="final_quiz_db.csv", mime="text/csv")
