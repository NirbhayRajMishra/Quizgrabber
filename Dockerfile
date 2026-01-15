# पायथन का इमेज इस्तेमाल करें
FROM python:3.10-slim

# सिस्टम डिपेंडेंसी और Tesseract इंस्टॉल करें
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    libtesseract-dev \
    poppler-utils \
    && apt-get clean

# वर्किंग डायरेक्टरी सेट करें
WORKDIR /app

# लाइब्रेरी इंस्टॉल करें
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# सारा कोड कॉपी करें
COPY . .

# स्ट्रीमलिट रन करें
CMD streamlit run app.py --server.port $PORT
