# Menggunakan base image Python 3.9
FROM python:3.9

# Menyalin file main.py ke dalam container
COPY main.py /app/main.py

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt /app/requirements.txt

# Mengatur working directory
WORKDIR /app

# Menginstal dependensi Python yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menjalankan aplikasi FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
