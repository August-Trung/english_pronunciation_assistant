/**
 * Role-Based Guided Tour System using Driver.js
 * Strictly enforces role separation, synchronized step numbering, and persistent localStorage checks.
 */

import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'
import './tours.css'

export const TOUR_KEYS = {
  // Teacher Tours
  TEACHER_WORKSHEET_MODAL: 'fluent_tour_teacher_worksheet_seen',
  TEACHER_ASSIGN_SENTENCE: 'fluent_tour_teacher_assign_sentence_seen',
  TEACHER_ASSIGN_PICTURE: 'fluent_tour_teacher_assign_picture_seen',
  TEACHER_HUB: 'fluent_tour_teacher_hub_seen',
  STUDENT_PICTURE_EMPTY: 'fluent_tour_student_picture_empty_seen',
  PICTURE_SCENARIO_MODAL: 'fluent_tour_picture_scenario_modal_seen',
  FLASHCARD_CREATE_MODAL: 'fluent_tour_flashcard_create_modal_seen',
  FLASHCARD_WEAK_WORDS: 'fluent_tour_flashcard_weak_words_seen',
  // Student Studios & Homework
  STUDENT_SPEAKING: 'fluent_tour_student_speaking_seen',
  STUDENT_SHADOWING: 'fluent_tour_student_shadowing_seen',
  STUDENT_PICTURE: 'fluent_tour_student_picture_seen',
  STUDENT_HOMEWORK: 'fluent_tour_student_homework_seen',
  // Student Tools & Portfolio
  STUDENT_HISTORY: 'fluent_tour_student_history_seen',
  STUDENT_LEADERBOARD: 'fluent_tour_student_leaderboard_seen',
  STUDENT_FLASHCARDS: 'fluent_tour_student_flashcards_seen',
  STUDENT_STATS: 'fluent_tour_student_stats_seen',
  STUDENT_JOIN: 'fluent_tour_student_join_seen',
  STUDENT_PROFILE: 'fluent_tour_student_profile_seen',
  STUDENT_SETTINGS: 'fluent_tour_student_settings_seen',
  // Specialized Portals
  PARENT_PORTAL: 'fluent_tour_parent_portal_seen',
  ADMIN_PORTAL: 'fluent_tour_admin_portal_seen'
}

/**
 * Filter steps to only include elements that currently exist and are visible in the DOM
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
  const rawValidSteps = getValidSteps(steps)
  if (!rawValidSteps.length) return null

  // Dynamically synchronize title numbering with valid step order (1. ..., 2. ..., etc.)
  // Guaranteeing that top header number ALWAYS matches Driver.js bottom progress indicator (e.g. "2 of 4" -> "2. ...")
  const validSteps = rawValidSteps.map((step, idx) => {
    const rawTitle = step.popover?.title
      ? step.popover.title.replace(/^(\d+[\.\:\)\-]\s*|bước\s*\d+[\.\:\-]\s*)/i, '').trim()
      : ''
    return {
      ...step,
      popover: {
        ...step.popover,
        title: `${idx + 1}. ${rawTitle}`
      }
    }
  })

  const d = driver({
    showProgress: true,
    animate: true,
    allowClose: true,
    overlayColor: 'rgba(15, 23, 42, 0.70)',
    stagePadding: 6,
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
      title: 'Định dạng Dynamic Vocab Worksheet',
      description: 'Hệ thống tự động sinh bài tập đa dạng và chấm điểm tự động dựa trên từ vựng thầy cô cung cấp.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-asg-vocab-input',
    popover: {
      title: 'Nhập từ vựng mục tiêu',
      description: 'Nhập các từ vựng bài học cần ôn luyện (ví dụ: apple, banana, giraffe...). AI sẽ bám sát các từ này để sinh câu hỏi.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-settings-row',
    popover: {
      title: 'Khối lớp & Giọng đọc Anh-Anh (en-GB)',
      description: 'Chọn cấp độ của học sinh. Mọi bài tập nghe đều được mặc định ưu tiên giọng đọc chuẩn bản xứ Anh-Anh.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-formats-picker',
    popover: {
      title: 'Chọn các dạng bài tập sư phạm',
      description: 'Tick chọn các định dạng muốn có trong đề: Nghe (khoanh tròn, tick, nối), Đọc (điền từ, trắc nghiệm), hoặc Viết (sắp xếp câu, đoán từ).',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-generate-btn',
    popover: {
      title: 'Bấm Sinh đề bài tập AI',
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
      title: 'Danh sách lớp học',
      description: 'Nơi hiển thị toàn bộ các lớp học và sĩ số học sinh do thầy cô phụ trách.',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '#tour-teacher-create-class-btn',
    popover: {
      title: 'Tạo lớp học mới',
      description: 'Bấm vào đây để tạo thêm lớp học mới theo từng khối lớp (Grade 1 đến 5).',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-teacher-join-code',
    popover: {
      title: 'Mã tham gia & QR Chiếu bảng',
      description: 'Cung cấp mã 6 ký tự cho học sinh, hoặc bấm xem QR để chiếu máy chiếu cho cả lớp quét gia nhập tức thì.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-teacher-assign-btn',
    popover: {
      title: 'Giao bài tập về nhà',
      description: 'Mở cửa sổ giao bài tập: Giao câu đọc mẫu, Miêu tả tranh AI, hoặc Tạo đề từ vựng Dynamic Worksheet.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-teacher-gradebook',
    popover: {
      title: 'Sổ điểm điện tử & Xem bài nộp',
      description: 'Theo dõi tiến độ làm bài. Nhấp vào điểm của học sinh để xem chi tiết bài làm đúng/sai từng câu.',
      side: 'top',
      align: 'center'
    }
  }
]

// =============================================================================
// 2. STUDENT STUDIOS & HOMEWORK TOURS
// =============================================================================

export const STUDENT_HOMEWORK_TOUR_STEPS = [
  {
    element: '#tour-student-hw-list',
    popover: {
      title: 'Danh sách bài tập được giao',
      description: 'Xem toàn bộ bài tập thầy cô đã giao cho lớp của bạn kèm theo trạng thái hạn chót nộp bài.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-student-hw-audio-btn',
    popover: {
      title: 'Nghe giọng phát âm Anh-Anh',
      description: 'Bấm vào nút loa để nghe giọng đọc bản xứ Anh-Anh của câu hỏi trước khi trả lời.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-student-hw-interactive-area',
    popover: {
      title: 'Khu vực làm bài tương tác',
      description: 'Khoanh tròn đáp án, bấm Tick/Cross, chọn từ trong ngân hàng từ, hoặc click sắp xếp thẻ từ thành câu hoàn chỉnh.',
      side: 'top',
      align: 'center'
    }
  },
  {
    element: '#tour-student-hw-submit-btn',
    popover: {
      title: 'Nộp bài & Chấm điểm tức thì',
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
      title: 'Chế độ luyện tập phát âm',
      description: 'Chọn luyện đọc câu mẫu theo khối lớp hoặc nói chuyện tự do với AI.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-speaking-settings-btn',
    popover: {
      title: 'Giọng Anh-Anh & Sơ đồ IPA',
      description: 'Tùy chọn giọng đọc bản xứ Anh-Anh và mở sơ đồ hướng dẫn chuyển động cơ miệng chuẩn IPA.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-speaking-record-btn',
    popover: {
      title: 'Thu âm giọng đọc của bạn',
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
      title: 'Chọn cấp độ nói đuổi',
      description: 'Chọn mức độ phản xạ phù hợp từ câu ngắn đến câu dài (Easy, Medium, Hard).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-shadowing-sample-btn',
    popover: {
      title: 'Nghe câu mẫu chuẩn Anh-Anh',
      description: 'Nghe mẫu ngữ điệu và ngắt nghỉ tự nhiên của người bản xứ.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-shadowing-record-btn',
    popover: {
      title: 'Nói đồng thanh theo audio',
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
      title: 'Bức tranh tình huống AI',
      description: 'Quan sát các nhân vật, đồ vật và bối cảnh trong bức ảnh sắc nét.',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '#tour-picture-guiding-panel',
    popover: {
      title: 'Câu hỏi gợi ý & Từ khóa',
      description: 'Tham khảo gợi ý để triển khai bài nói hoàn chỉnh và dùng đúng từ vựng mục tiêu.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-picture-record-btn',
    popover: {
      title: 'Bấm giờ & Thu âm bài nói',
      description: 'Bấm giờ linh hoạt và thu âm bài miêu tả tranh để nhận điểm đánh giá chuẩn IELTS/TOEIC Speaking.',
      side: 'top',
      align: 'center'
    }
  }
]

// =============================================================================
// 3. STUDENT TOOLS & PORTFOLIO TOURS
// =============================================================================

export const STUDENT_HISTORY_TOUR_STEPS = [
  {
    element: '#tour-history-header',
    popover: {
      title: 'Nhật ký luyện tập & Hồ sơ năng lực',
      description: 'Lưu trữ toàn bộ bản ghi âm phát âm, điểm số 5 kỹ năng và lịch sử học tập cá nhân.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-history-exports',
    popover: {
      title: 'Xuất báo cáo PDF & Tải tệp nén ZIP',
      description: 'Tải trọn bộ bản ghi âm dạng file ZIP hoặc xuất phiếu đánh giá PDF chi tiết để lưu trữ.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-history-filters',
    popover: {
      title: 'Bộ lọc theo mốc thời gian',
      description: 'Xem các bài đã luyện tập Hôm nay, 30 ngày qua hoặc tùy chỉnh khoảng ngày mong muốn.',
      side: 'bottom',
      align: 'start'
    }
  }
]

export const STUDENT_LEADERBOARD_TOUR_STEPS = [
  {
    element: '#tour-leaderboard-banner',
    popover: {
      title: 'Đấu trường Phát âm & Bảng Vinh danh',
      description: 'Xem thứ hạng và tranh tài cùng các bạn trong lớp học hoặc toàn thể cộng đồng người học.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-leaderboard-podium',
    popover: {
      title: 'Bục vinh quang Top 3 xuất sắc',
      description: 'Vinh danh 3 gương mặt dẫn đầu có điểm số phát âm và chuỗi chuyên cần cao nhất.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-leaderboard-list',
    popover: {
      title: 'Bảng xếp hạng chi tiết',
      description: 'Theo dõi điểm trung bình, huy hiệu và số lượt phát âm để cùng nhau tiến bộ mỗi ngày.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_FLASHCARDS_TOUR_STEPS = [
  {
    element: '#tour-flashcards-banner',
    popover: {
      title: 'Thẻ từ vựng thông minh Flashcards',
      description: 'Ôn tập từ vựng kèm hình ảnh trực quan và nghe phát âm chuẩn giọng bản xứ Anh-Anh.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-flashcards-create-btn',
    popover: {
      title: 'Tạo bộ thẻ AI mới',
      description: 'Tự tạo bộ thẻ từ vựng mới theo chủ đề yêu thích với hình ảnh minh họa do AI tự động vẽ.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-flashcards-tabs',
    popover: {
      title: 'Bộ thẻ AI & Ngân hàng từ yếu (SRS)',
      description: 'Chuyển đổi giữa các bộ thẻ theo chủ đề và danh sách các từ bạn phát âm còn yếu để ôn luyện lặp lại ngắt quãng.',
      side: 'bottom',
      align: 'start'
    }
  }
]

export const STUDENT_STATS_TOUR_STEPS = [
  {
    element: '#tour-stats-header',
    popover: {
      title: 'Báo cáo Phân tích Tiến độ AI',
      description: 'Tổng hợp dữ liệu học tập chuyên sâu, đánh giá chi tiết quá trình cải thiện phát âm.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-stats-streak',
    popover: {
      title: 'Chuỗi ngày học liên tục (Streak)',
      description: 'Duy trì học phát âm mỗi ngày để thắp sáng ngọn lửa học tập và nhận thêm điểm thưởng.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-stats-overview',
    popover: {
      title: 'Các chỉ số tổng quan',
      description: 'Theo dõi tổng thời gian luyện tập, số câu đã đọc và điểm trung bình đạt được.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-stats-charts',
    popover: {
      title: 'Biểu đồ phát âm trực quan',
      description: 'Biểu đồ đường thể hiện phong độ và biểu đồ radar phân tích 5 khía cạnh phát âm của bạn.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_JOIN_TOUR_STEPS = [
  {
    element: '#tour-join-card',
    popover: {
      title: 'Cổng tham gia lớp học dành cho học sinh',
      description: 'Dễ dàng gia nhập lớp của thầy cô mà không cần tài khoản Google hay email phức tạp.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-join-code-field',
    popover: {
      title: 'Nhập mã lớp học',
      description: 'Nhập mã 6 ký tự (ví dụ: CLS-586-57) được giáo viên cung cấp trên lớp hoặc quét mã QR.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-join-auth-box',
    popover: {
      title: 'Đăng nhập hoặc Đăng ký nhanh',
      description: 'Chỉ cần chọn tên tài khoản và mật khẩu đơn giản để bắt đầu làm bài và nhận điểm số.',
      side: 'top',
      align: 'center'
    }
  }
]

export const STUDENT_PROFILE_TOUR_STEPS = [
  {
    element: '#tour-profile-banner',
    popover: {
      title: 'Hồ sơ cá nhân & Thông tin tài khoản',
      description: 'Quản lý thông tin học sinh, ảnh đại diện và trạng thái liên kết lớp học.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-profile-identity',
    popover: {
      title: 'Huy hiệu & Lớp học tham gia',
      description: 'Xem các danh hiệu đã mở khóa và mã lớp học đang theo học.',
      side: 'right',
      align: 'start'
    }
  },
  {
    element: '#tour-profile-parent-code',
    popover: {
      title: 'Mã kết nối phụ huynh',
      description: 'Cung cấp mã này cho ba mẹ để ba mẹ theo dõi điểm số và nghe lại bài nói của bạn tại Cổng Phụ huynh.',
      side: 'top',
      align: 'start'
    }
  }
]

export const STUDENT_SETTINGS_TOUR_STEPS = [
  {
    element: '#tour-settings-profile',
    popover: {
      title: 'Hồ sơ người học & Mục tiêu hàng ngày',
      description: 'Đặt tên hiển thị và điều chỉnh mục tiêu số câu luyện đọc phát âm mỗi ngày.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-settings-faq',
    popover: {
      title: 'Câu hỏi thường gặp & Giải đáp sư phạm',
      description: 'Tìm hiểu cơ chế chấm điểm IPA 3 tầng, chuẩn đánh giá phát âm và bảo mật dữ liệu giọng nói.',
      side: 'top',
      align: 'start'
    }
  }
]

// =============================================================================
// 4. SPECIALIZED PORTALS TOURS
// =============================================================================

export const PARENT_PORTAL_TOUR_STEPS = [
  {
    element: '#tour-parent-banner',
    popover: {
      title: 'Cổng thông tin & Theo dõi tiến độ cho Phụ huynh',
      description: 'Đồng hành cùng con: Xem kết quả học tập, điểm chuẩn IPA và nghe các đoạn thu âm giọng đọc thực tế.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-parent-code-input',
    popover: {
      title: 'Nhập mã theo dõi của học sinh',
      description: 'Nhập mã theo dõi (ví dụ: PA-9842 lấy từ trang Cá nhân của con) để xem hồ sơ học tập.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-parent-report-card',
    popover: {
      title: 'Bảng đánh giá & Nhận xét từ Giáo viên',
      description: 'Theo dõi điểm phát âm, bài tập đã hoàn thành và lời nhận xét chi tiết của thầy cô.',
      side: 'top',
      align: 'center'
    }
  }
]

export const ADMIN_PORTAL_TOUR_STEPS = [
  {
    element: '#tour-admin-banner',
    popover: {
      title: 'Bảng điều khiển Quản trị Hệ thống',
      description: 'Quản lý toàn diện tổ chức trường học, phân bổ giáo viên, học sinh và bản quyền phần mềm.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-admin-kpis',
    popover: {
      title: 'Chỉ số KPI & Bản quyền tài khoản',
      description: 'Theo dõi số lượng trường học, tài khoản giáo viên và số ghế học sinh đang hoạt động.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-admin-tabs',
    popover: {
      title: 'Các phân hệ quản lý',
      description: 'Dễ dàng chuyển đổi giữa phân hệ Trường học, Quản lý tài khoản Người dùng và Nhật ký bảo mật.',
      side: 'top',
      align: 'center'
    }
  }
]

export const TEACHER_ASSIGN_SENTENCE_TOUR_STEPS = [
  {
    element: '#tour-asg-format-switcher',
    popover: {
      title: 'Chọn định dạng bài tập',
      description: 'Chuyển đổi giữa 3 định dạng: Đọc câu mẫu, Miêu tả tranh tình huống hoặc Dynamic Vocab Worksheet.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-title',
    popover: {
      title: 'Tiêu đề bài tập',
      description: 'Đặt tiêu đề bài tập rõ ràng cho học sinh dễ nhận biết (ví dụ: Unit 3 - Practice Daily Routine Sentence).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-sentence-input',
    popover: {
      title: 'Câu văn tiếng Anh mẫu',
      description: 'Nhập câu văn tiếng Anh để học sinh luyện đọc to và nhận phản hồi chấm điểm phát âm từng âm vị IPA.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-due-date',
    popover: {
      title: 'Hạn chót nộp bài',
      description: 'Chọn ngày hạn nộp bài. Học sinh sẽ nhận thông báo hạn chót ngay trên trang làm bài tập.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-submit-btn',
    popover: {
      title: 'Giao bài cho cả lớp',
      description: 'Bấm nút này để giao bài tập ngay cho toàn bộ học sinh trong lớp học đã chọn.',
      side: 'top',
      align: 'end'
    }
  }
]

export const TEACHER_ASSIGN_PICTURE_TOUR_STEPS = [
  {
    element: '#tour-asg-format-switcher',
    popover: {
      title: 'Định dạng Miêu tả Tranh (Describe Picture)',
      description: 'Giao bài luyện nói miêu tả tranh theo chuẩn định dạng thi IELTS Speaking Part 2 & TOEIC Speaking.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-pic-topic',
    popover: {
      title: 'Chủ đề bức tranh tình huống',
      description: 'Nhập chủ đề bức tranh hoặc bối cảnh cần mô tả (ví dụ: Family Picnic, Zoo, Science Lab...).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-pic-themes',
    popover: {
      title: 'Gợi ý chủ đề nhanh',
      description: 'Bấm vào các chủ đề chương trình có sẵn để AI tự động vẽ tranh và sinh bộ câu hỏi gợi ý phù hợp.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-due-date',
    popover: {
      title: 'Hạn chót nộp bài',
      description: 'Đặt ngày hết hạn bài nộp để nhắc nhở học sinh hoàn thành đúng hạn.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-asg-submit-btn',
    popover: {
      title: 'Giao bài tập tranh',
      description: 'Hoàn tất và giao bài tập miêu tả tranh cho lớp học.',
      side: 'top',
      align: 'end'
    }
  }
]

export const STUDENT_PICTURE_EMPTY_TOUR_STEPS = [
  {
    element: '#tour-picture-banner',
    popover: {
      title: 'Describe The Picture Studio',
      description: 'Phòng luyện nói miêu tả tranh đa phương thức theo chuẩn IELTS Speaking Part 2 & TOEIC Speaking.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-picture-empty-card',
    popover: {
      title: 'Chưa có tình huống tranh',
      description: 'Hiện tại chưa có bức tranh nào được tạo. Bạn có thể tự tạo tình huống bằng AI hoặc tải ảnh lên.',
      side: 'bottom',
      align: 'center'
    }
  },
  {
    element: '#tour-picture-empty-btn',
    popover: {
      title: 'Bấm Tạo tình huống tranh',
      description: 'Nhấp vào đây để mở cửa sổ tạo bức tranh tình huống và bộ câu hỏi gợi ý luyện nói.',
      side: 'top',
      align: 'center'
    }
  }
]

export const PICTURE_SCENARIO_MODAL_TOUR_STEPS = [
  {
    element: '#tour-scenario-tabs',
    popover: {
      title: '3 Chế độ tạo tranh đa dạng',
      description: 'Chọn vẽ tranh 3D bằng AI Prompt, tìm kiếm ảnh thật trên Unsplash hoặc tải ảnh bài học từ máy tính.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-scenario-prompt-input',
    popover: {
      title: 'Nhập mô tả ý tưởng bức tranh',
      description: 'Mô tả khung cảnh bạn muốn luyện nói (ví dụ: A family having a picnic in the park with a cute puppy...).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-scenario-sparks',
    popover: {
      title: 'Gợi ý chủ đề nhanh',
      description: 'Nhấp vào các chủ đề mẫu sinh động như Chuyến thăm sở thú, Phòng thí nghiệm trường học để điền nhanh prompt.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-scenario-level',
    popover: {
      title: 'Cấp độ nói mục tiêu',
      description: 'Chọn trình độ Beginner (Cơ bản), Intermediate (Trung cấp) hoặc Advanced (Nâng cao) để AI cá nhân hóa câu hỏi.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-scenario-generate-btn',
    popover: {
      title: 'Bấm Sinh tình huống tranh AI',
      description: 'AI sẽ vẽ tranh và tạo trọn bộ câu hỏi gợi ý cùng từ khóa trọng tâm để bạn bắt đầu bấm giờ luyện nói!',
      side: 'top',
      align: 'end'
    }
  }
]

export const FLASHCARD_CREATE_MODAL_TOUR_STEPS = [
  {
    element: '#tour-deck-topic-input',
    popover: {
      title: 'Chủ đề bộ thẻ từ vựng',
      description: 'Nhập chủ đề bạn muốn ôn tập (ví dụ: IELTS Environment, Airport Travel, Job Interview...).',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-deck-suggestions',
    popover: {
      title: 'Chủ đề gợi ý nhanh',
      description: 'Bấm nhanh vào các chủ đề phổ biến có sẵn để tiết kiệm thời gian nhập liệu.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-deck-settings-row',
    popover: {
      title: 'Cấp độ & Số lượng thẻ',
      description: 'Chọn cấp độ phù hợp và số lượng từ vựng muốn học trong một bộ thẻ (từ 3 đến 10 từ).',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-deck-illustrate-check',
    popover: {
      title: 'Hình ảnh minh họa AI',
      description: 'Tick chọn để AI tự động vẽ tranh minh họa sinh động cho từng từ vựng giúp ghi nhớ lâu hơn.',
      side: 'top',
      align: 'start'
    }
  },
  {
    element: '#tour-deck-generate-btn',
    popover: {
      title: 'Bấm Tạo bộ thẻ Flashcards',
      description: 'Hệ thống tự động sinh từ, nghĩa tiếng Việt, câu ví dụ, phiên âm IPA chuẩn và audio bản xứ Anh-Anh!',
      side: 'top',
      align: 'end'
    }
  }
]

export const FLASHCARD_WEAK_WORDS_TOUR_STEPS = [
  {
    element: '#tour-weak-words-banner',
    popover: {
      title: 'Ngân hàng từ phát âm yếu (SRS)',
      description: 'Tự động tổng hợp tất cả các từ bạn từng phát âm dưới 8.0 điểm từ mọi bài tập để ôn luyện ngắt quãng.',
      side: 'bottom',
      align: 'start'
    }
  },
  {
    element: '#tour-weak-words-remedial-btn',
    popover: {
      title: 'Luyện tập phục hồi với AI',
      description: 'Bấm vào đây để AI hướng dẫn sửa lỗi phát âm và luyện lại các từ còn phát âm sai.',
      side: 'bottom',
      align: 'end'
    }
  },
  {
    element: '#tour-weak-words-list',
    popover: {
      title: 'Danh sách từ & Phiên âm IPA',
      description: 'Nghe lại phát âm bản xứ chuẩn Anh-Anh, xem phiên âm IPA và số lần bạn đã luyện tập từ này.',
      side: 'top',
      align: 'center'
    }
  }
]
