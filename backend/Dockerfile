FROM python:3.11-slim

WORKDIR /app

# 安裝 curl 以便支援 Docker 健康檢查，並安裝編譯必要組件
RUN apt-get update && apt-get install -y curl build-essential gfortran && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 確保目錄存在
RUN mkdir -p /data/cache /data/logs /data/snapshots /app/static

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
