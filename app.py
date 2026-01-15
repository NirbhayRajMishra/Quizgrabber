import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="Universal Quiz Extractor", page_icon="🤖")

# OCR configuration (Language: Hindi + English)
OCR_CONFIG = '--oem 3 --psm 6'

def process_text(text):
    """Text se questions nikalne ka wahi purana accurate logic"""
    quiz_data = []
    raw_blocks = re.split(r'\n(?=\d+[\.\)]|Q\d+[\.\)]|\[\d+\])', text)
    for block in raw_blocks:
        if not block.strip(): continue
        lines = block.strip().split('\n')
        q_parts, opt_a, opt_b, opt_c, opt_d, ans, exp = [], "", "", "", "", "", ""
        found_opts = False
        for line in lines:
            l = line.strip()
            if re.match(r'^[A|अ][\.\)]', l): opt_a = re.sub(r'^[A|अ][\.\)]', '', l).strip(); found_opts = True
            elif re.match(r'^[B|ब][\.\)]', l): opt_b = re.sub(r'^[B|ब][\.\)]', '', l).strip(); found_opts = True
            elif re.match(r'^[C|स][\.\)]', l): opt_c = re.sub(r'^[C|स][\.\)]', '', l).strip(); found_opts = True
            elif re.match(r'^[D|द][\.\)]', l): opt_d = re.sub(r'^[D|द][\.\)]', '', l).strip(); found_opts = True
            elif any(x in l for x in ["Answer", "Ans", "उत्तर"]): ans = l; found_opts = True
            elif any(x in l for x in ["Explanation", "व्याख्या"]): exp = l; found_opts = True
            elif not found_opts: q_parts.append(l)
        if q_parts and opt_a:
            quiz_data.append({"Question": " ".join(q_parts), "Option A": opt_a, "Option B": opt_b, "Option C": opt_c, "Option D": opt_d, "Correct Answer": ans, "Explanation": exp})
    return quiz_data

st.title("🤖 Universal Quiz Extractor (Text + OCR)")
mode = st.radio("Processing Mode Chunein:", ("Fast Text (Digital PDF)", "OCR Mode (Scanned/Symbol PDF)"))

uploaded_file = st.file_uploader("PDF File Upload Karein", type="pdf")

if uploaded_file is not None:
    if st.button("Start Extraction"):
        final_data = []
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        progress = st.progress(0)

        for i, page in enumerate(doc):
            if mode == "Fast Text (Digital PDF)":
                # Double Column Text Logic
                w, h = page.rect.width, page.rect.height
                left_text = page.get_text("text", clip=fitz.Rect(0, 0, w/2, h))
                right_text = page.get_text("text", clip=fitz.Rect(w/2, 0, w, h))
                final_data.extend(process_text(left_text))
                final_data.extend(process_text(right_text))
            else:
                # OCR Mode (Har page ko image bana kar read karega)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Zoom for better OCR
                img = Image.open(io.BytesIO(pix.tobytes()))
                ocr_text = pytesseract.image_to_string(img, lang='hin+eng', config=OCR_CONFIG)
                final_data.extend(process_text(ocr_text))
            
            progress.progress((i + 1) / len(doc))

        df = pd.DataFrame(final_data)
        if not df.empty:
            st.success(f"Success! {len(df)} Questions mil gaye.")
            st.dataframe(df.head(20))
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("Download CSV", data=csv, file_name="universal_quiz_db.csv")
