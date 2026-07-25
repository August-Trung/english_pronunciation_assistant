// Thư viện phân loại theo cấp lớp - Chuẩn SGK GDPT 2018

export const GRADE_LEVELS = [
  {
    id: 'primary',
    name: 'Tiểu học (Lớp 1 - 5)',
    shortName: 'Tiểu học',
    icon: 'mdi-school-outline',
    color: 'success',
    badge: 'Khung A1.1',
    description: 'Các câu ngắn đơn giản (3 - 7 từ), tập trung phát âm tròn vành rõ chữ.'
  },
  {
    id: 'secondary',
    name: 'THCS (Lớp 6 - 9)',
    shortName: 'THCS',
    icon: 'mdi-book-open-page-variant-outline',
    color: 'primary',
    badge: 'Khung A1.2 - A2',
    description: 'Các câu giao tiếp hàng ngày (10 - 18 từ), kết hợp từ nối và thì ngữ pháp cơ bản.'
  },
  {
    id: 'highschool',
    name: 'THPT & IELTS (Lớp 10 - 12)',
    shortName: 'THPT & IELTS',
    icon: 'mdi-certificate-outline',
    color: 'purple',
    badge: 'Khung B1 - B2',
    description: 'Các câu phức nghị luận (18 - 30 từ), ngữ pháp nâng cao và từ vựng học thuật.'
  }
]

// 1. Danh sách Chủ đề / Câu hỏi giao tiếp (Dùng cho Chế độ Nói tự do - Speaking Mode)
export const SPEAKING_TOPICS = {
  primary: [
    "What is your name?",
    "How old are you?",
    "What is your favorite color?",
    "Tell me about your pet",
    "What food do you like best?"
  ],
  secondary: [
    "Tell me about your family",
    "What do you like to do after school?",
    "Describe your best friend",
    "How do you protect the environment?",
    "What is your favorite holiday?"
  ],
  highschool: [
    "What are the benefits of artificial intelligence in education?",
    "How can students maintain a healthy lifestyle?",
    "What role does online learning play in modern society?",
    "Why is gender equality important in the workplace?"
  ]
}

// 2. Thư viện Câu mẫu văn bản chi tiết (Dùng cho Chế độ Đọc theo mẫu - Reading Mode)
export const READING_LIBRARY = {
  primary: [
    {
      topic: 'Giới thiệu bản thân & Gia đình',
      sentences: [
        'Hello, my name is Nam.',
        'I am eight years old.',
        'This is my happy family.',
        'My father is a doctor.',
        'I love my mother very much.'
      ]
    },
    {
      topic: 'Sở thích & Trường học',
      sentences: [
        'I like cats and dogs.',
        'My favorite color is blue.',
        'I go to school every day.',
        'I am playing football now.',
        'English is my favorite subject.'
      ]
    }
  ],
  secondary: [
    {
      topic: 'Sở thích & Đời sống hàng ngày',
      sentences: [
        'In my free time, I enjoy reading books because it helps me relax.',
        'My family usually goes to the park together on Sunday mornings.',
        'Learning English helps me communicate with people all over the world.'
      ]
    },
    {
      topic: 'Môi trường & Cộng đồng',
      sentences: [
        'We should reduce plastic waste to protect our environment and oceans.',
        'Doing morning exercise regularly keeps us healthy and full of energy.',
        'Last weekend, my class joined a campaign to clean up the school yard.'
      ]
    }
  ],
  highschool: [
    {
      topic: 'Công nghệ & Giáo dục hiện đại',
      sentences: [
        'Artificial intelligence is transforming traditional education by providing personalized learning experiences.',
        'Online learning platforms allow students to access valuable educational resources from anywhere.',
        'Developing critical thinking skills is essential for solving complex problems in the modern world.'
      ]
    },
    {
      topic: 'Xã hội & Sự phát triển bản thân',
      sentences: [
        'Protecting endangered species is crucial for maintaining global ecological balance.',
        'Equal job opportunities should be provided for both men and women in modern society.',
        'A healthy lifestyle requires a balanced diet and regular physical exercise.'
      ]
    }
  ]
}
