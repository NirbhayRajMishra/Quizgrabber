import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="Big PDF Quiz Extractor", page_icon="📖")

st.title("📖 Advanced PDF Quiz Extractor")
st.write("यह 250+ पेज और हिंदी/इंग्लिश दोनों भाषाओं को सपोर्ट करता है।")

uploaded_file = st.file_uploader("PDF फाइल अपलोड करें", type="pdf")

if uploaded_file is not None:
    process_button = st.button("डेटा निकालना शुरू करें")
    
    if process_button:
        quiz_data = []
        progress_bar = st.progress(0)
        
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                total_pages = len(pdf.pages)
                st.info(f"कुल पेज: {total_pages}. कृपया धैर्य रखें...")

                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        # हिंदी और इंग्लिश दोनों के लिए Regex पैटर्न
                        # यह पैटर्न प्रश्न संख्या (जैसे 1. या २.) को पहचानता है
                        segments = re.split(r'\n(?=\d+\.|Q\d+\.)', text)
                        
                        for segment in segments:
                            if segment.strip():
                                lines = segment.strip().split('\n')
                                question = lines[0]
                                
                                # ऑप्शंस, उत्तर और व्याख्या ढूँढना
                                options = [l for l in lines if re.match(r'^[A-D][\.\)]', l.strip())]
                                ans = [l for l in lines if any(x in l for x in ["Answer", "Ans", "उत्तर", "अंश"])]
                                exp = [l for l in lines if any(x in l for x in ["Explanation", "व्याख्या", "विवरण"])]

                                quiz_data.append({
                                    "Page": i + 1,
                                    "Question": question,
                                    "Options": " | ".join(options),
                                    "Correct Answer": ans[0] if ans else "N/A",
                                    "Explanation": exp[0] if exp else "N/A"
                                })
                    
                    # प्रोग्रेस बार अपडेट करें
                    progress_bar.progress((i + 1) / total_pages)

            df = pd.DataFrame(quiz_data)
            
            if not df.empty:
                st.success(f"सफलतापूर्वक {len(df)} प्रश्न निकाले गए!")
                st.dataframe(df.head(20)) # केवल पहले 20 दिखाएं ताकि ब्राउज़र हैंग न हो

                # CSV Download - UTF-8 BOM के साथ ताकि हिंदी Excel में सही दिखे
                csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="Download Full CSV Database",
                    data=csv,
                    file_name="mega_quiz_database.csv",
                    mime="text/csv",
                )
            else:
                st.warning("कोई प्रश्न नहीं मिल सका। कृपया चेक करें कि PDF टेक्स्ट-आधारित है या नहीं।")

        except Exception as e:
            st.error(f"Error: {e}")
