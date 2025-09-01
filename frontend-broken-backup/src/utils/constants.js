// Constants and mock data
export const MOCK_COURSES = [
  {
    uuid: '1',
    title: 'AI for Marketing Professionals',
    partner_primary: 'Google',
    subject_primary: 'Artificial Intelligence',
    level: 'Beginner',
    platform: 'Coursera',
    primary_description: 'Learn how to leverage AI tools in marketing campaigns and customer analysis',
    img_url: 'https://via.placeholder.com/300x200/6366f1/white?text=AI+Marketing',
    enrol_cnt: 25431,
    skills: 'ChatGPT, Marketing Automation, Data Analysis',
    url: 'https://coursera.org/learn/ai-marketing',
    similarity_score: 0.92,
    duration: '4 weeks',
    effort: '3-5 hours/week'
  },
  {
    uuid: '2',
    title: 'Introduction to Machine Learning',
    partner_primary: 'Stanford University',
    subject_primary: 'Machine Learning',
    level: 'Intermediate',
    platform: 'edX',
    primary_description: 'Comprehensive introduction to machine learning algorithms and applications',
    img_url: 'https://via.placeholder.com/300x200/10b981/white?text=ML+Intro',
    enrol_cnt: 18765,
    skills: 'Python, Scikit-learn, Data Science',
    url: 'https://edx.org/course/machine-learning',
    similarity_score: 0.87,
    duration: '6 weeks',
    effort: '4-6 hours/week'
  },
  {
    uuid: '3',
    title: 'ChatGPT for Business Professionals',
    partner_primary: 'LinkedIn Learning',
    subject_primary: 'Artificial Intelligence',
    level: 'Beginner',
    platform: 'Udemy',
    primary_description: 'Master ChatGPT and other AI tools to enhance productivity and creativity',
    img_url: 'https://via.placeholder.com/300x200/f59e0b/white?text=ChatGPT+Business',
    enrol_cnt: 12089,
    skills: 'ChatGPT, Prompt Engineering, AI Tools',
    url: 'https://udemy.com/course/chatgpt-business',
    similarity_score: 0.95,
    duration: '3 weeks',
    effort: '2-3 hours/week'
  },
  {
    uuid: '4',
    title: 'Excel Automation with AI',
    partner_primary: 'Microsoft',
    subject_primary: 'Productivity',
    level: 'Beginner',
    platform: 'LinkedIn Learning',
    primary_description: 'Automate Excel tasks using AI-powered tools and formulas',
    img_url: 'https://via.placeholder.com/300x200/059669/white?text=Excel+AI',
    enrol_cnt: 15432,
    skills: 'Excel, Automation, AI Tools',
    url: 'https://linkedin.com/learning/excel-ai',
    similarity_score: 0.89,
    duration: '2 weeks',
    effort: '2-4 hours/week'
  },
  {
    uuid: '5',
    title: 'Design Thinking with AI',
    partner_primary: 'IDEO',
    subject_primary: 'Design',
    level: 'Intermediate',
    platform: 'Coursera',
    primary_description: 'Integrate AI tools into your design thinking process for enhanced creativity',
    img_url: 'https://via.placeholder.com/300x200/dc2626/white?text=Design+AI',
    enrol_cnt: 8976,
    skills: 'Design Thinking, AI Tools, Creativity',
    url: 'https://coursera.org/learn/design-thinking-ai',
    similarity_score: 0.84,
    duration: '5 weeks',
    effort: '3-4 hours/week'
  }
];

export const QUICK_START_OPTIONS = [
  {
    id: 'ai-fundamentals',
    title: 'AI Fundamentals',
    description: 'Start your AI journey with beginner-friendly courses',
    query: 'AI tools for beginners'
  },
  {
    id: 'productivity',
    title: 'Productivity & Automation',
    description: 'Learn to automate tasks and boost efficiency',
    query: 'productivity tools automation'
  },
  {
    id: 'data-analytics',
    title: 'Data & Analytics',
    description: 'Master data skills for better decision making',
    query: 'data analysis for non-technical professionals'
  }
];

export const USER_ROLES = [
  'Marketing Manager',
  'Project Manager',
  'HR Specialist',
  'Sales Representative',
  'Content Creator',
  'Business Analyst',
  'Operations Manager',
  'Customer Success Manager'
];

export const SKILL_LEVELS = [
  'Beginner',
  'Intermediate',
  'Advanced'
];

export const LEARNING_GOALS = [
  'AI Tools Proficiency',
  'Data Analysis',
  'Automation',
  'Digital Marketing',
  'Project Management',
  'Communication Skills',
  'Leadership',
  'Technical Writing'
];