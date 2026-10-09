// Grade Level Categorization Library - International CEFR Standard

export const GRADE_LEVELS = [
  {
    id: 'primary',
    name: 'Elementary (Grades 1 - 5)',
    shortName: 'Elementary',
    icon: 'mdi-school-outline',
    color: 'success',
    badge: 'CEFR A1.1',
    description: 'Short simple sentences (3 - 7 words), focusing on clear articulation.'
  },
  {
    id: 'secondary',
    name: 'Middle School (Grades 6 - 9)',
    shortName: 'Middle School',
    icon: 'mdi-book-open-page-variant-outline',
    color: 'primary',
    badge: 'CEFR A1.2 - A2',
    description: 'Daily conversational sentences (10 - 18 words) with basic connectors and tenses.'
  },
  {
    id: 'highschool',
    name: 'High School & IELTS (Grades 10 - 12)',
    shortName: 'High School',
    icon: 'mdi-certificate-outline',
    color: 'purple',
    badge: 'CEFR B1 - B2',
    description: 'Complex academic sentences (18 - 30 words) with advanced vocabulary.'
  }
]

// 1. Conversational Speaking Topics (Free Topic Mode)
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

// 2. Model Sentences Library (Sentence Reading Mode)
export const READING_LIBRARY = {
  primary: [
    {
      topic: 'Self-Introduction & Family',
      sentences: [
        'Hello, my name is Nam.',
        'I am eight years old.',
        'This is my happy family.',
        'My father is a doctor.',
        'I love my mother very much.'
      ]
    },
    {
      topic: 'Hobbies & School Life',
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
      topic: 'Hobbies & Daily Routine',
      sentences: [
        'In my free time, I enjoy reading books because it helps me relax.',
        'My family usually goes to the park together on Sunday mornings.',
        'Learning English helps me communicate with people all over the world.'
      ]
    },
    {
      topic: 'Environment & Community',
      sentences: [
        'We should reduce plastic waste to protect our environment and oceans.',
        'Doing morning exercise regularly keeps us healthy and full of energy.',
        'Last weekend, my class joined a campaign to clean up the school yard.'
      ]
    }
  ],
  highschool: [
    {
      topic: 'Technology & Modern Education',
      sentences: [
        'Artificial intelligence is transforming traditional education by providing personalized learning experiences.',
        'Online learning platforms allow students to access valuable educational resources from anywhere.',
        'Developing critical thinking skills is essential for solving complex problems in the modern world.'
      ]
    },
    {
      topic: 'Society & Personal Growth',
      sentences: [
        'Protecting endangered species is crucial for maintaining global ecological balance.',
        'Equal job opportunities should be provided for both men and women in modern society.',
        'A healthy lifestyle requires a balanced diet and regular physical exercise.'
      ]
    }
  ]
}
