import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="PDF to Quiz Converter", page_icon="📝")

st.title("📝 PDF Quiz Extractor")
st.write("अपनी PDF अपलोड करें और उसे CSV डेटाबेस में बदलें।")

uploaded_file = st.file_uploader("PDF फाइल चुनें", type="pdf")

if uploaded_file is not None:
    with st.spinner('डेटा निकाला जा रहा है...'):
        all_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"

        # Regex Pattern (इसे आपके PDF के हिसाब से बदला जा सकता है)
        # यहाँ हम मान रहे हैं कि प्रश्न "1. " या "Q1. " से शुरू हो रहे हैं
        segments = re.split(r'\n(?=\d+\.|Q\d+\.)', all_text)
        
        quiz_data = []
        for segment in segments:
            if segment.strip():
                lines = segment.strip().split('\n')
                question = lines[0]
                options = [l for l in lines if re.match(r'^[A-D][\.\)]', l.strip())]
                ans = [l for l in lines if "Answer" in l or "Ans" in l]
                exp = [l for l in lines if "Explanation" in l]

                quiz_data.append({
                    "Question": question,
                    "Options": " | ".join(options),
                    "Correct Answer": ans[0] if ans else "N/A",
                    "Explanation": exp[0] if exp else "N/A"
                })

        df = pd.DataFrame(quiz_data)
        
        st.success("प्रोसेसिंग पूरी हो गई!")
        st.dataframe(df) # टेबल दिखाएं

        # CSV डाउनलोड बटन
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV Database",
            data=csv,
            file_name="quiz_database.csv",
            mime="text/csv",
        )
