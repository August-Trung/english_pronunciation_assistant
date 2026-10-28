/**
 * Role-Based Guided Tour System using Driver.js
 * Strictly enforces role separation and persistent localStorage checks.
 */

import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'
import './tours.css'

export const TOUR_KEYS = {
  // Teacher Tours
  TEACHER_WORKSHEET_MODAL: 'fluent_tour_teacher_worksheet_seen',
  TEACHER_HUB: 'fluent_tour_teacher_hub_seen',
  // Student Tours
  STUDENT_HOMEWORK: 'fluent_tour_student_homework_seen',
  STUDENT_SPEAKING: 'fluent_tour_student_speaking_seen',
  STUDENT_SHADOWING: 'fluent_tour_student_shadowing_seen',
  STUDENT_PICTURE: 'fluent_tour_student_picture_seen'
}

/**
 * Filter steps to only include elements that currently exist in the DOM
 */
const getValidSteps = (steps) => {
  return steps.filter(s => {
    if (!s.element) return false
    const el = document.querySelector(s.element)
    return !!el && el.offsetParent !== null
  })
}

/**
 * Executes a guided tour.
 * @param {string} storageKey - Unique key in localStorage.
 * @param {Array} steps - List of Driver.js step definitions.
 * @param {boolean} force - If true, ignores localStorage and forces tour replay.
 */
export const runTour = (storageKey, steps, force = false) => {
  if (typeof window === 'undefined') return null

  // If already seen and not forcing replay, skip
  if (!force && localStorage.getItem(storageKey)) {
    return null
  }

  // Filter steps so non-existing elements don't break the tour
  const validSteps = getValidSteps(steps)
  if (!validSteps.length) return null

  const d = driver({
    showProgress: true,
    animate: true,
    allowClose: true,
    overlayColor: 'rgba(15, 23, 42, 0.70)',
    stagePadding: 5,
    stageRadius: 8,
    popoverClass: 'fluent-driver-popover',
    nextBtnText: 'Tiếp theo →',
    prevBtnText: '← Quay lại',
    doneBtnText: 'Đã hiểu! ✓',
    steps: validSteps,
    onDestroyed: () => {
      localStorage.setItem(storageKey, 'true')
    }
  })

  // Short delay to ensure DOM and animations have settled
  setTimeout(() => {
    try {
      d.drive()
    } catch (e) {
      console.warn('Driver tour notice:', e)
    }
  }, 250)

  return d
}

// =============================================================================
// 1. TEACHER TOUR DEFINITIONS
// =============================================================================

export const TEACHER_WORKSHEET_TOUR_STEPS = [
  {
    element: '#tour-asg-format-worksheet',
    popover: {
      title: '1. Định dạng Dynamic Vocab Worksheet',
      description: 'Hệ thống tự động sinh bài tập đa dạng và chấm điểm tự động dựa trên từ vựng thầy cô nhập vào.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-asg-vocab-input',
    popover: {
      title: '2. Nhập từ vựng mục tiêu',
      description: 'Nhập các từ vựng bài học cần ôn luyện (ví dụ: apple, banana, giraffe...). AI sẽ bám sát các từ này để sinh câu hỏi.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-settings-row',
    popover: {
      title: '3. Khối lớp & Giọng đọc Anh-Anh (en-GB)',
      description: 'Chọn cấp độ của học sinh. Mọi bài tập nghe đều được mặc định ưu tiên giọng đọc chuẩn bản xứ Anh-Anh.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-formats-picker',
    popover: {
      title: '4. Chọn các dạng bài tập sư phạm',
      description: 'Tick chọn các định dạng muốn có trong đề: Nghe (khoanh tròn, tick, nối), Đọc (điền từ, trắc nghiệm), hoặc Viết (sắp xếp câu, đoán từ).',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-generate-btn',
    popover: {
      title: '5. Bấm Sinh đề bài tập AI',
      description: 'Bấm nút này để AI tạo đề bài. Thầy cô được nghe thử phát âm Anh-Anh và chỉnh sửa đề trước khi giao bài cho cả lớp!',
      side: 'top',
      align: 'center'
    }
  }
]

export const TEACHER_HUB_TOUR_STEPS = [
  {
    element: '#tour-teacher-classes-list',
    popover: {
      title: '1. Danh sách lớp học',
      description: 'Nơi hiển thị toàn bộ các lớp học và sĩ số học sinh do thầy cô phụ trách.',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '#tour-teacher-create-class-btn',
    popover: {
      title: '2. Tạo lớp học mới',
      description: 'Bấm vào đây để tạo thêm lớp học mới theo từng khối lớp (Grade 1 đến 5).',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-teacher-join-code',
    popover: {
      title: '3. Mã tham gia & QR Chiếu bảng',
      description: 'Cung cấp mã 6 ký tự cho học sinh, hoặc bấm xem QR để chiếu máy chiếu cho cả lớp quét gia nhập tức thì.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-teacher-assign-btn',
    popover: {
      title: '4. Giao bài tập về nhà',
      description: 'Mở cửa sổ giao bài tập: Giao câu đọc mẫu, Miêu tả tranh AI, hoặc Tạo đề từ vựng Dynamic Worksheet.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-teacher-gradebook',
    popover: {
      title: '5. Sổ điểm điện tử & Xem bài nộp',
      description: 'Theo dõi tiến độ làm bài. Nhấp vào điểm của học sinh để xem chi tiết bài làm đúng/sai từng câu.',
      side: 'top',
      align: 'center'
    }
  }
]

// =============================================================================
// 2. STUDENT TOUR DEFINITIONS
// =============================================================================

export const STUDENT_HOMEWORK_TOUR_STEPS = [
  {
    element: '#tour-student-hw-list',
    popover: {
      title: '1. Danh sách bài tập được giao',
      description: 'Xem toàn bộ bài tập thầy cô đã giao cho lớp của bạn kèm theo trạng thái hạn chót nộp bài.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-student-hw-audio-btn',
    popover: {
      title: '2. Nghe giọng phát âm Anh-Anh',
      description: 'Bấm vào nút loa để nghe giọng đọc bản xứ Anh-Anh của câu hỏi trước khi trả lời.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-student-hw-interactive-area',
    popover: {
      title: '3. Khu vực làm bài tương tác',
      description: 'Khoanh tròn đáp án, bấm Tick/Cross, chọn từ trong ngân hàng từ, hoặc click sắp xếp thẻ từ thành câu hoàn chỉnh.',
      side: 'top',
      align: 'center'
    }
  },
  {
    element: '#tour-student-hw-submit-btn',
    popover: {
      title: '4. Nộp bài & Chấm điểm tức thì',
      description: 'Bấm nộp bài để hệ thống tự động chấm điểm và xem giải thích chi tiết đúng/sai từng câu ngay lập tức.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_SPEAKING_TOUR_STEPS = [
  {
    element: '#tour-speaking-mode-toggle',
    popover: {
      title: '1. Chế độ luyện tập phát âm',
      description: 'Chọn luyện đọc câu mẫu theo khối lớp hoặc nói chuyện tự do với AI.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-speaking-settings-btn',
    popover: {
      title: '2. Giọng Anh-Anh & Sơ đồ IPA',
      description: 'Tùy chọn giọng đọc bản xứ Anh-Anh và mở sơ đồ hướng dẫn chuyển động cơ miệng chuẩn IPA.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-speaking-record-btn',
    popover: {
      title: '3. Thu âm giọng đọc của bạn',
      description: 'Bấm micro và đọc to rõ ràng câu tiếng Anh để hệ thống phân tích phát âm.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_SHADOWING_TOUR_STEPS = [
  {
    element: '#tour-shadowing-level-picker',
    popover: {
      title: '1. Chọn cấp độ nói đuổi',
      description: 'Chọn mức độ phản xạ phù hợp từ câu ngắn đến câu dài (Easy, Medium, Hard).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-shadowing-sample-btn',
    popover: {
      title: '2. Nghe câu mẫu chuẩn Anh-Anh',
      description: 'Nghe mẫu ngữ điệu và ngắt nghỉ tự nhiên của người bản xứ.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-shadowing-record-btn',
    popover: {
      title: '3. Nói đồng thanh theo audio',
      description: 'Bật thu âm và nói đuổi theo mẫu âm thanh (Shadowing) để luyện ngữ điệu mượt mà.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_PICTURE_TOUR_STEPS = [
  {
    element: '#tour-picture-image-card',
    popover: {
      title: '1. Bức tranh tình huống AI',
      description: 'Quan sát các nhân vật, đồ vật và bối cảnh trong bức ảnh sắc nét.',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '#tour-picture-guiding-panel',
    popover: {
      title: '2. Câu hỏi gợi ý & Từ khóa',
      description: 'Tham khảo gợi ý để triển khai bài nói hoàn chỉnh và dùng đúng từ vựng mục tiêu.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-picture-record-btn',
    popover: {
      title: '3. Bấm giờ & Thu âm bài nói',
      description: 'Bấm giờ linh hoạt và thu âm bài miêu tả tranh để nhận điểm đánh giá chuẩn IELTS/TOEIC Speaking.',
      side: 'top',
      align: 'center'
    }
  }
]
