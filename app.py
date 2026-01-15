import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re

st.set_page_config(page_title="Pro Quiz Extractor", page_icon="🎯")

def extract_from_column(text_block):
    """एक टेक्स्ट ब्लॉक से प्रश्नों को निकालने का लॉजिक"""
    quiz_data = []
    # प्रश्न की शुरुआत पहचानना (e.g. 1. या Q1. या [1])
    raw_blocks = re.split(r'\n(?=\d+[\.\)]|Q\d+[\.\)]|\[\d+\])', text_block)
    
    for block in raw_blocks:
        if not block.strip(): continue
        lines = block.strip().split('\n')
        
        question_parts = []
        opt_a, opt_b, opt_c, opt_d = "", "", "", ""
        ans, exp = "", ""
        found_options = False

        for line in lines:
            l = line.strip()
            if not l: continue

            # पैटर्न मैचिंग (English & Hindi)
            if re.match(r'^[A|अ][\.\)]', l): 
                opt_a = re.sub(r'^[A|अ][\.\)]', '', l).strip()
                found_options = True
            elif re.match(r'^[B|ब][\.\)]', l): 
                opt_b = re.sub(r'^[B|ब][\.\)]', '', l).strip()
                found_options = True
            elif re.match(r'^[C|स][\.\)]', l): 
                opt_c = re.sub(r'^[C|स][\.\)]', '', l).strip()
                found_options = True
            elif re.match(r'^[D|द][\.\)]', l): 
                opt_d = re.sub(r'^[D|द][\.\)]', '', l).strip()
                found_options = True
            elif any(x in l for x in ["Answer", "Ans", "उत्तर", "Sahi uttar"]): 
                ans = l
                found_options = True
            elif any(x in l for x in ["Explanation", "व्याख्या", "विवरण"]): 
                exp = l
                found_options = True
            elif not found_options:
                question_parts.append(l)

        if question_parts and opt_a: # कम से कम Option A होना ज़रूरी है
            quiz_data.append({
                "Question": " ".join(question_parts),
                "Option A": opt_a,
                "Option B": opt_b,
                "Option C": opt_c,
                "Option D": opt_d,
                "Correct Answer": ans,
                "Explanation": exp
            })
    return quiz_data

st.title("🎯 Pro Quiz Extractor (Double Column Support)")
st.info("यह ऐप डबल कॉलम PDF को भी बाएँ से दाएँ (Left to Right) सही क्रम में पढ़ता है।")

uploaded_file = st.file_uploader("PDF अपलोड करें", type="pdf")

if uploaded_file is not None:
    if st.button("Start Extraction"):
        final_quiz_list = []
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                # पेज को दो हिस्सों में बाँटना (Double Column Logic)
                width = page.rect.width
                height = page.rect.height
                
                # Left Column (बायाँ हिस्सा)
                left_rect = fitz.Rect(0, 0, width/2, height)
                left_text = page.get_text("text", clip=left_rect)
                final_quiz_list.extend(extract_from_column(left_text))
                
                # Right Column (दायाँ हिस्सा)
                right_rect = fitz.Rect(width/2, 0, width, height)
                right_text = page.get_text("text", clip=right_rect)
                final_quiz_list.extend(extract_from_column(right_text))

        df = pd.DataFrame(final_quiz_list)
        if not df.empty:
            st.success(f"कुल {len(df)} सटीक प्रश्न मिले!")
            st.dataframe(df.head(20))
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("Download CSV", data=csv, file_name="pro_quiz_db.csv", mime="text/csv")
