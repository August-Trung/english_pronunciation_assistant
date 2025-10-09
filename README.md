# 🧠 Ứng dụng Chấm Phát Âm Tiếng Anh

Ứng dụng web miễn phí giúp luyện và chấm điểm phát âm tiếng Anh, sử dụng AI (Whisper) để nhận dạng giọng nói và đánh giá độ chính xác.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng chính

-   🎙️ **Ghi âm trực tiếp** ngay trên web
-   📤 **Upload file audio** (hỗ trợ WAV, MP3, M4A, OGG, FLAC)
-   🤖 **AI nhận dạng giọng nói** bằng Whisper (OpenAI)
-   📊 **Chấm điểm tự động** (0-100)
-   ⚠️ **Phát hiện lỗi phát âm** chi tiết
-   📜 **Lưu lịch sử** và xuất CSV
-   🌐 **Chạy offline/online** - Không cần internet sau khi tải model
-   💰 **Hoàn toàn MIỄN PHÍ** - Không dùng API trả phí

## 🚀 Cài đặt nhanh

### 1. Clone repository

```bash
git clone <repo-url>
cd pronunciation-app
```

### 2. Cài đặt FFmpeg

```bash
# Windows (Chocolatey):
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### 3. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng

```bash
streamlit run app.py
```

## 📦 Cấu trúc dự án

```
pronunciation-app/
│
├── app.py              # File chính - Giao diện Streamlit
├── requirements.txt    # Các thư viện Python cần thiết
├── packages.txt        # Các package hệ thống (cho Streamlit Cloud)
└── README.md          # File này
```

## 🎯 Hướng dẫn sử dụng

1. **Nhập câu mẫu**: Gõ câu tiếng Anh bạn muốn luyện phát âm
2. **Ghi âm hoặc Upload**: Chọn một trong hai cách
    - Nhấn nút ghi âm và đọc câu
    - Upload file audio có sẵn
3. **Chấm điểm**: Nhấn nút "Chấm điểm phát âm"
4. **Xem kết quả**: Xem điểm số, từ sai, và đánh giá chi tiết
5. **Lưu lịch sử**: Tải xuống CSV để theo dõi tiến độ

## 🎓 Dành cho ai?

-   👨‍🏫 **Giáo viên tiếng Anh**: Chấm phát âm học sinh nhanh chóng
-   👨‍🎓 **Học sinh/Sinh viên**: Tự luyện phát âm tại nhà
-   🏢 **Trung tâm Anh ngữ**: Công cụ hỗ trợ giảng dạy
-   🌍 **Người tự học**: Cải thiện phát âm mọi lúc mọi nơi

## 🔧 Yêu cầu hệ thống

-   **Python**: 3.8 - 3.11
-   **RAM**: Tối thiểu 2GB (khuyên dùng 4GB+)
-   **FFmpeg**: Cần cài đặt
-   **Microphone**: Nếu dùng chức năng ghi âm

## ☁️ Deploy lên Streamlit Cloud

1. Push code lên GitHub
2. Truy cập https://share.streamlit.io/
3. Kết nối với repo GitHub
4. Deploy (miễn phí!)

**Lưu ý**: Đảm bảo có file `packages.txt` chứa `ffmpeg`

## 📊 Các mô hình Whisper

| Mô hình | Kích thước | Tốc độ     | Độ chính xác      |
| ------- | ---------- | ---------- | ----------------- |
| tiny    | 39 MB      | Rất nhanh  | Trung bình        |
| base    | 74 MB      | Nhanh      | Tốt (khuyên dùng) |
| small   | 244 MB     | Trung bình | Rất tốt           |

## 🛠️ Công nghệ sử dụng

-   **Streamlit**: Framework web app Python
-   **Whisper (OpenAI)**: Mô hình AI nhận dạng giọng nói
-   **FuzzyWuzzy**: So sánh độ tương đồng văn bản
-   **Pydub**: Xử lý file audio
-   **FFmpeg**: Chuyển đổi định dạng audio

## 📈 Roadmap

-   [ ] Thêm đánh giá phát âm theo âm vị (phoneme)
-   [ ] Hỗ trợ nhiều ngôn ngữ (Tiếng Việt, Trung, Nhật...)
-   [ ] Tích hợp Text-to-Speech để phát câu mẫu
-   [ ] Dashboard thống kê tiến độ học tập
-   [ ] Chế độ luyện tập theo chủ đề

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repo này
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

Dự án này được phát hành dưới MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

## 🙏 Lời cảm ơn

-   [OpenAI Whisper](https://github.com/openai/whisper) - Mô hình AI nhận dạng giọng nói
-   [Streamlit](https://streamlit.io/) - Framework tạo web app nhanh chóng
-   Cộng đồng Python và Machine Learning

## 📞 Liên hệ & Hỗ trợ

-   🐛 Báo lỗi: Tạo issue trên GitHub
-   💡 Góp ý tính năng: Tạo issue với label "enhancement"
-   📧 Email: [your-email@example.com]

---

**⭐ Nếu thấy hữu ích, hãy cho repo một ngôi sao nhé!**

Made with ❤️ and Python
