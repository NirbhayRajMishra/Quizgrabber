import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re

st.set_page_config(page_title="Fast Quiz Extractor", page_icon="⚡")

st.title("⚡ Ultra-Fast Quiz Extractor")
st.write("यह बड़े PDF (UPPCS/SSC) को बहुत तेज़ी से प्रोसेस करेगा।")

uploaded_file = st.file_uploader("PDF अपलोड करें", type="pdf")

if uploaded_file is not None:
    if st.button("Extract Questions Now"):
        quiz_data = []
        
        # PDF को तेज़ी से खोलना
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            total_pages = len(doc)
            progress_bar = st.progress(0)
            
            # हर पेज को तेज़ी से प्रोसेस करना
            for i, page in enumerate(doc):
                text = page.get_text() # PyMuPDF का सुपर-फ़ास्ट एक्सट्रैक्टर
                
                if text:
                    # प्रश्न खोजने का लॉजिक
                    segments = re.split(r'\n(?=\d+[\.\)]|Q\d+[\.\)])', text)
                    
                    for segment in segments:
                        if segment.strip():
                            lines = segment.strip().split('\n')
                            q_text = lines[0]
                            opt_a, opt_b, opt_c, opt_d = "", "", "", ""
                            ans, exp = "", ""

                            for line in lines:
                                l = line.strip()
                                # Patterns for A, B, C, D
                                if re.match(r'^[A][\.\)]', l): opt_a = re.sub(r'^[A][\.\)]', '', l).strip()
                                elif re.match(r'^[B][\.\)]', l): opt_b = re.sub(r'^[B][\.\)]', '', l).strip()
                                elif re.match(r'^[C][\.\)]', l): opt_c = re.sub(r'^[C][\.\)]', '', l).strip()
                                elif re.match(r'^[D][\.\)]', l): opt_d = re.sub(r'^[D][\.\)]', '', l).strip()
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
            st.success(f"प्रोसेसिंग पूरी! {len(df)} प्रश्न मिले।")
            st.dataframe(df.head(10))
            
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("Download CSV", data=csv, file_name="fast_quiz_db.csv", mime="text/csv")
        else:
            st.error("कोई प्रश्न नहीं मिला। कृपया PDF का फॉर्मेट चेक करें।")
