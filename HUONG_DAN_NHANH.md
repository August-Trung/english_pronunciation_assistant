# ⚡ HƯỚNG DẪN NHANH - 5 PHÚT BẮT ĐẦU

## 🎯 Chạy ngay trong 5 phút!

### Bước 1: Cài đặt FFmpeg (bắt buộc)

```bash
# Windows (cần Chocolatey):
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### Bước 2: Cài đặt thư viện Python

```bash
pip install streamlit openai-whisper fuzzywuzzy python-Levenshtein pydub numpy ffmpeg-python
```

### Bước 3: Lưu code

Sao chép file `app.py` đã được tạo ở trên

### Bước 4: Chạy!

```bash
streamlit run app.py
```

✅ **XONG!** App sẽ tự động mở trên trình duyệt tại http://localhost:8501

---

## 🎮 Cách sử dụng cơ bản

### 1. Nhập câu cần luyện

```
Ví dụ: "I want to eat an apple"
```

### 2. Chọn 1 trong 2 cách:

**Cách A - Ghi âm ngay:**

-   Nhấn nút ghi âm 🎙️
-   Đọc câu tiếng Anh
-   Nhấn Stop

**Cách B - Upload file:**

-   Chọn file audio (.wav, .mp3, .m4a...)
-   Upload lên

### 3. Chấm điểm

-   Nhấn nút **"Chấm điểm phát âm"**
-   Đợi 5-10 giây
-   Xem kết quả!

---

## 📊 Hiểu kết quả

| Điểm   | Ý nghĩa                          |
| ------ | -------------------------------- |
| 90-100 | 🟢 Xuất sắc - Gần như hoàn hảo!  |
| 75-89  | 🟡 Khá - Tốt, cố gắng thêm nhé!  |
| 60-74  | 🟠 Trung bình - Cần luyện thêm   |
| 0-59   | 🔴 Cần cải thiện - Đừng bỏ cuộc! |

---

## 💡 Mẹo luyện phát âm hiệu quả

1. **Nói chậm, rõ ràng** hơn nói nhanh
2. **Luyện từng từ** trước khi luyện cả câu
3. **Nghe và bắt chước** người bản ngữ
4. **Luyện tập đều đặn** mỗi ngày 10-15 phút
5. **Ghi âm và nghe lại** để tự đánh giá

---

## ❓ Câu hỏi thường gặp

### Q: Lần đầu chạy lâu quá?

**A:** Model Whisper đang tải xuống (1-3 phút), lần sau sẽ nhanh hơn!

### Q: Không ghi âm được?

**A:**

-   Kiểm tra quyền microphone trên trình duyệt
-   Dùng Chrome/Edge (khuyên dùng)
-   Hoặc dùng Upload file thay vì ghi âm

### Q: Nhận dạng sai?

**A:**

-   Nói rõ ràng, chậm rãi hơn
-   Đảm bảo môi trường yên tĩnh
-   Thử đổi model sang `small` (chính xác hơn)

### Q: Muốn chạy offline hoàn toàn?

**A:** Được! Sau khi tải model lần đầu, không cần internet nữa.

### Q: Có mất phí không?

**A:** Hoàn toàn MIỄN PHÍ! Không có API trả phí.

---

## 🚀 Deploy lên web (miễn phí)

### Cách 1: Streamlit Cloud (Khuyên dùng)

1. Đẩy code lên GitHub
2. Vào https://share.streamlit.io/
3. Kết nối repo
4. Nhấn Deploy
5. Đợi 5-10 phút → XONG!

**Lưu ý:** Nhớ tạo file `packages.txt` chứa dòng `ffmpeg`

### Cách 2: Heroku / Railway / Render

-   Tương tự, nhưng cần config thêm
-   Streamlit Cloud dễ nhất!

---

## 🎓 Dành cho giáo viên

### Ứng dụng trong giảng dạy:

1. **Kiểm tra phát âm học sinh** nhanh chóng
2. **Bài tập về nhà**: Học sinh ghi âm và nộp link kết quả
3. **Theo dõi tiến độ**: Export CSV để phân tích
4. **Tạo bài tập tùy chỉnh**: Đổi câu mẫu theo chủ đề bài học
5. **Luyện tập nhóm**: Cả lớp cùng luyện, so sánh điểm

### Gợi ý câu mẫu theo cấp độ:

**Beginner (Mới bắt đầu):**

-   "Hello, my name is John"
-   "I like apples"
-   "This is a book"
-   "Good morning teacher"

**Intermediate (Trung cấp):**

-   "I want to eat an apple"
-   "She is reading a book in the library"
-   "The weather is nice today"
-   "Can you help me with this problem?"

**Advanced (Nâng cao):**

-   "I would like to introduce myself to everyone here"
-   "The quick brown fox jumps over the lazy dog"
-   "She sells seashells by the seashore"
-   "Peter Piper picked a peck of pickled peppers"

---

## 📱 Sử dụng trên điện thoại

✅ **Hoàn toàn hỗ trợ mobile!**

1. Mở trình duyệt (Chrome/Safari)
2. Truy cập địa chỉ app
3. Ghi âm hoặc upload từ điện thoại
4. Chấm điểm bình thường!

**Lưu ý**: Ghi âm trên Safari (iOS) có thể cần refresh trang.

---

## 🔧 Tùy chỉnh nâng cao

### Thay đổi model Whisper trong code:

```python
# Trong file app.py, dòng load model:
model = whisper.load_model("base")  # Đổi thành: tiny, small, medium, large
```

### Các model và đặc điểm:

| Model  | Dung lượng | Tốc độ     | RAM cần | Độ chính xác |
| ------ | ---------- | ---------- | ------- | ------------ |
| tiny   | 39 MB      | ⚡⚡⚡⚡⚡ | ~1 GB   | ⭐⭐⭐       |
| base   | 74 MB      | ⚡⚡⚡⚡   | ~1.5 GB | ⭐⭐⭐⭐     |
| small  | 244 MB     | ⚡⚡⚡     | ~2.5 GB | ⭐⭐⭐⭐⭐   |
| medium | 769 MB     | ⚡⚡       | ~5 GB   | ⭐⭐⭐⭐⭐   |
| large  | 1.5 GB     | ⚡         | ~10 GB  | ⭐⭐⭐⭐⭐   |

**Khuyến nghị**:

-   Máy yếu: `tiny`
-   Cân bằng: `base` (mặc định)
-   Độ chính xác cao: `small` hoặc `medium`

---

## 📦 Cấu trúc thư mục đề xuất

```
pronunciation-app/
│
├── app.py                    # File chính
├── requirements.txt          # Thư viện Python
├── packages.txt             # Cho Streamlit Cloud
├── README.md                # Tài liệu
├── HUONG_DAN_NHANH.md      # File này
├── test_installation.py     # Test cài đặt
│
├── .streamlit/              # Cấu hình Streamlit (tùy chọn)
│   └── config.toml
│
└── data/                    # Lưu lịch sử (tự động tạo)
    └── history.csv
```

---

## 🎨 Tùy chỉnh giao diện (theme)

Tạo file `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

Hoặc chọn Dark theme:

```toml
[theme]
base = "dark"
primaryColor = "#FF4B4B"
```

---

## 🔐 Bảo mật & Quyền riêng tư

✅ **Dữ liệu của bạn an toàn 100%!**

-   ❌ KHÔNG gửi audio lên server bên ngoài
-   ❌ KHÔNG dùng API của bên thứ 3
-   ✅ Mọi xử lý đều LOCAL (trên máy bạn)
-   ✅ Lịch sử chỉ lưu trong session
-   ✅ Xóa lịch sử bất cứ lúc nào

---

## 💾 Backup & Export dữ liệu

### Xuất lịch sử:

1. Click **"Tải xuống lịch sử (CSV)"** ở sidebar
2. File CSV chứa:
    - Thời gian chấm
    - Câu mẫu
    - Câu nhận dạng
    - Điểm số
    - Từ sai

### Mở file CSV:

-   Excel
-   Google Sheets
-   LibreOffice Calc

---

## 🌟 Tính năng sắp ra mắt

-   [ ] 🎯 Phân tích chi tiết từng âm (phoneme-level)
-   [ ] 🔊 Text-to-Speech để nghe câu mẫu
-   [ ] 📊 Dashboard theo dõi tiến độ
-   [ ] 🌐 Hỗ trợ nhiều ngôn ngữ (Tiếng Việt, Trung, Nhật...)
-   [ ] 🎮 Chế độ game hóa với điểm thưởng
-   [ ] 👥 Chế độ nhiều người dùng
-   [ ] 📚 Thư viện câu mẫu có sẵn
-   [ ] 🎓 Bài tập theo chủ đề (IELTS, TOEIC...)

---

## 🤝 Đóng góp

Muốn cải thiện app? Chào mừng!

1. Fork repository
2. Tạo branch mới
3. Code tính năng mới
4. Tạo Pull Request
5. Chờ review & merge

**Ý tưởng tính năng?** Tạo Issue trên GitHub!

---

## 📞 Liên hệ & Hỗ trợ

### Gặp lỗi?

1. Xem [Hướng dẫn xử lý lỗi](TROUBLESHOOTING.md)
2. Chạy `python test_installation.py`
3. Tạo Issue trên GitHub với:
    - Mô tả lỗi
    - Error message
    - OS & Python version

### Góp ý tính năng?

-   Tạo Issue với tag "enhancement"
-   Mô tả chi tiết tính năng mong muốn

### Báo lỗi bảo mật?

-   Email riêng (không public issue)

---

## 📚 Tài nguyên học thêm

### Về Whisper:

-   [OpenAI Whisper GitHub](https://github.com/openai/whisper)
-   [Whisper Paper](https://arxiv.org/abs/2212.04356)

### Về Streamlit:

-   [Streamlit Documentation](https://docs.streamlit.io/)
-   [Streamlit Gallery](https://streamlit.io/gallery)

### Về phát âm tiếng Anh:

-   Forvo (nghe phát âm từ)
-   YouGlish (nghe từ trong video)
-   IPA Chart (bảng phiên âm quốc tế)

---

## ⚖️ License

MIT License - Tự do sử dụng, sửa đổi, và phân phối!

---

## 🙏 Lời cảm ơn

**Công nghệ sử dụng:**

-   🤖 [OpenAI Whisper](https://github.com/openai/whisper) - Nhận dạng giọng nói
-   🎨 [Streamlit](https://streamlit.io/) - Framework web app
-   🐍 Python & cộng đồng Open Source

**Cảm ơn bạn đã sử dụng app!** ❤️

Nếu thấy hữu ích, hãy:

-   ⭐ Star trên GitHub
-   📢 Chia sẻ với bạn bè
-   💬 Để lại feedback

---

## 🎯 Bắt đầu ngay!

```bash
# 1. Cài đặt
pip install -r requirements.txt

# 2. Chạy
streamlit run app.py

# 3. Thành công! 🎉
```

**Chúc bạn luyện phát âm hiệu quả!** 🚀

---

<div align="center">
  <p><strong>Made with ❤️ and Python</strong></p>
  <p>Miễn phí • Mã nguồn mở • Không giới hạn</p>
</div>
