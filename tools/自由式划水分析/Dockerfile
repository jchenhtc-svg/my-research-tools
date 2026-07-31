# ── Frontend build stage ─────────────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
# 現地單機使用：API跟前端同一個origin，不用設定REACT_APP_API_URL
ENV REACT_APP_API_URL=/api
RUN npm run build


# ── Backend build stage ───────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ───────────────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# System libraries required by OpenCV / MediaPipe + ffmpeg for re-encoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV / MediaPipe native deps
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    # ffmpeg for H.264 re-encoding (browser compatibility)
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# 拿掉不會用到的前端原始碼，改放編譯好的靜態檔案（單一容器同時提供API+網頁）
RUN rm -rf frontend
COPY --from=frontend-builder /frontend/build ./frontend/build

# Create upload/result directories
RUN mkdir -p backend/uploads backend/results

# HF Spaces injects PORT=7860; Render/Railway override via $PORT env var
EXPOSE 7860

# Single gunicorn worker to avoid OOM on resource-constrained free tiers.
# Use threads for lightweight request concurrency (video jobs run in a ThreadPoolExecutor).
CMD ["sh", "-c", \
     "gunicorn \
       --bind 0.0.0.0:${PORT:-7860} \
       --timeout 600 \
       --workers 1 \
       --threads 4 \
       --worker-class gthread \
       backend.app:app"]
