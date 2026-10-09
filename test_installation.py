"""
Script kiểm tra cài đặt các thư viện cần thiết
Chạy script này trước khi chạy ứng dụng chính
"""

import sys
import subprocess


def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    print(f"\n{'='*50}")
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")

    if 3.8 <= version.major + version.minor / 10 <= 3.11:
        print("✅ Phiên bản Python phù hợp (3.8 - 3.11)")
        return True
    else:
        print("❌ CẢNH BÁO: Nên dùng Python 3.8 - 3.11")
        return False


def check_module(module_name, import_name=None):
    """Kiểm tra một module có được cài đặt không"""
    if import_name is None:
        import_name = module_name

    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {module_name}: v{version}")
        return True
    except ImportError:
        print(f"❌ {module_name}: CHƯA CÀI ĐẶT")
        return False


def check_ffmpeg():
    """Kiểm tra FFmpeg"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # Lấy dòng đầu tiên có version
            first_line = result.stdout.split("\n")[0]
            print(f"✅ FFmpeg: {first_line}")
            return True
        else:
            print("❌ FFmpeg: Lỗi khi chạy")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg: CHƯA CÀI ĐẶT")
        print("   Hướng dẫn cài đặt:")
        print("   - Windows: choco install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Linux: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ FFmpeg: Lỗi kiểm tra - {e}")
        return False


def main():
    """Hàm chính"""
    print("\n" + "=" * 50)
    print("🔍 KIỂM TRA CÀI ĐẶT ỨNG DỤNG CHẤM PHÁT ÂM")
    print("=" * 50)

    results = {}

    # Kiểm tra Python
    results["python"] = check_python_version()

    # Kiểm tra các module Python
    print(f"\n{'='*50}")
    print("📦 Kiểm tra Python Packages:")
    print("=" * 50)

    modules = [
        ("Streamlit", "streamlit"),
        ("Whisper", "whisper"),
        ("FuzzyWuzzy", "fuzzywuzzy"),
        ("Levenshtein", "Levenshtein"),
        ("Pydub", "pydub"),
        ("Numpy", "numpy"),
    ]

    for display_name, import_name in modules:
        results[import_name] = check_module(display_name, import_name)

    # Kiểm tra FFmpeg
    print(f"\n{'='*50}")
    print("🎵 Kiểm tra FFmpeg:")
    print("=" * 50)
    results["ffmpeg"] = check_ffmpeg()

    # Tổng kết
    print(f"\n{'='*50}")
    print("📊 TỔNG KẾT:")
    print("=" * 50)

    total = len(results)
    passed = sum(results.values())

    print(f"\nĐã kiểm tra: {total} thành phần")
    print(f"✅ Thành công: {passed}")
    print(f"❌ Thất bại: {total - passed}")

    if passed == total:
        print("\n🎉 HOÀN HẢO! Tất cả đã được cài đặt đúng!")
        print("\n▶️  Bạn có thể chạy ứng dụng bằng lệnh:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  CÓ VẤN ĐỀ! Vui lòng cài đặt các thành phần bị thiếu.")
        print("\n📝 Hướng dẫn cài đặt:")
        print("   pip install -r requirements.txt")

        if not results.get("ffmpeg", False):
            print("\n🔧 Đừng quên cài đặt FFmpeg!")

    print("=" * 50 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
