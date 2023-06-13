# Menggunakan base image Python 3.9
FROM python:3.9

# Menyalin file main.py ke dalam container
COPY main.py /app/main.py

# Menyalin file model_v2.h5 ke dalam container
copy model_v2.h5 /app/model_v2.h5

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt /app/requirements.txt

# Menyalin file serviceAccountkey.json
copy serviceAccountKey.json /app/serviceAccountKey.json

# Mengatur working directory
WORKDIR /app

# Menginstal dependensi Python yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menjalankan aplikasi FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
