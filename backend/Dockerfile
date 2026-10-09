FROM python:3.9-slim

# Cài đặt các công cụ hệ thống (FFmpeg là bắt buộc cho Whisper và Pydub)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập user không có quyền root (Yêu cầu bắt buộc bởi Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /code

# Sao chép và cài đặt các thư viện Python
COPY --chown=user requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Tải sẵn mô hình Whisper 'base' để lưu cache trong Docker Image
# Giúp loại bỏ thời gian tải mô hình khi khởi chạy container (tối ưu hóa Cold Start)
RUN python -c "import whisper; whisper.load_model('base')"

# Sao chép toàn bộ mã nguồn backend vào container
COPY --chown=user . /code

# Cổng mặc định Hugging Face Spaces yêu cầu chạy là 7860
EXPOSE 7860

# Khởi chạy FastAPI backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
