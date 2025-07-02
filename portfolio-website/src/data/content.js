// Portfolio content data
export const personalInfo = {
  name: "Davoud Nikkhouy",
  title: "Robotics and Embedded Systems Engineer",
  email: "davoudnikkhouy@gmail.com",
  phone: "(+39) 3270694337",
  location: "Viale Carlo Espinasse 104, 20156 Milan (Italy)",
  linkedin: "https://www.linkedin.com/in/sdnt-519072b7/",
  github: "https://github.com/SDNT8810",
  website: "https://davoudnikkhouy.com",
  scholar: "https://scholar.google.com/citations?hl=en&user=d54YIeoAAAAJ",
  about: "Robotics and Embedded Systems Engineer with a strong foundation in mechanical and aerospace engineering, transitioning into advanced embedded software, AI-driven control, and autonomous robotics. Over five years of experience in developing real-time systems (STM32, FreeRTOS), intelligent motion planning (ROS, Gazebo), and machine learning–based controllers for mobile and self-balancing robots. Experienced in combining theoretical research and practical implementation, from firmware architecture to reinforcement learning and predictive control."
};

export const workExperience = [
  {
    id: 1,
    company: "Politecnico di Milano",
    position: "Research Assistant",
    location: "Milan, Italy",
    startDate: "May 2024",
    endDate: "Current",
    description: [
      "Developed deep-fuzzy reinforcement learning algorithms for mobile robot navigation in dynamic and uncertain environments using ROS2 and Gazebo.",
      "Designed predictive controllers for self-balancing two-wheeled robots using deep neural networks and simulation-driven optimization.",
      "Built and tested kino-dynamic simulation pipelines and model predictive controllers (MPC) for trajectory tracking and collision avoidance in real-time."
    ]
  },
  {
    id: 2,
    company: "FanAvin Co.",
    position: "Mechatronics Engineer",
    location: "Tehran, Iran",
    startDate: "March 2019",
    endDate: "December 2023",
    description: [
      "Led development of embedded firmware for an STM32-based autopilot system with RTOS architecture and real-time task scheduling.",
      "Built a camera-guided mobile robot with autonomous navigation using image processing and sensor fusion.",
      "Developed a fuzzy-logic-based controller for a social robot interacting with dynamic moving targets.",
      "Engineered a high-speed autonomous watercraft with real-time obstacle avoidance algorithms.",
      "Designed and launched several electromechanical systems, including a 6-DOF robotic arm for 3D printing and a 3-axis hydraulic robot.",
      "Created a high-temperature smart oven (400°C) with custom embedded control."
    ]
  }
];

export const education = [
  {
    id: 1,
    degree: "Master of Mechanical Engineering",
    institution: "Iran University of Science and Technology",
    location: "Tehran, Iran",
    startDate: "September 2017",
    endDate: "September 2020",
    grade: "15.5 / 20",
    thesis: "Path planning and control of a mobile social robot in an environment with moving obstacles to reach the mobile target using fuzzy control",
    website: "https://www.iust.ac.ir/en"
  },
  {
    id: 2,
    degree: "Bachelor of Aerospace Engineering",
    institution: "Sharif University of Technology",
    location: "Tehran, Iran",
    startDate: "September 2010",
    endDate: "September 2015",
    website: "https://en.sharif.ir"
  }
];

export const skills = {
  "Embedded Software Development": [
    "STM32", "ARM", "ESP32", "Arduino", "PLC", "Keil"
  ],
  "Real Time Operating Systems": [
    "ROS & ROS2", "RTOS", "FreeRTOS", "Nuttx", "Embedded Linux", "Gazebo (Robotics simulator)"
  ],
  "Software Development and Version Control": [
    "C/C++", "Python", "MATLAB", "Git (Github / Gitlab)", "CMake", "Catkin"
  ]
};

export const publications = [
  {
    id: 1,
    year: 2025,
    title: "Fuzzy Q-Learning with Fuzzified Bellman Equation for Unmanned Ground Vehicle Navigation",
    authors: "Davood Nikkhouy; Mohsen Jalaeian Farimani",
    journal: "9th International Conference on Robotics and Automation Sciences (ICRAS 2025)"
  },
  {
    id: 2,
    year: 2025,
    title: "Bi-Level Performance-Safety Consideration in Nonlinear Model Predictive Control",
    authors: "Davood Nikkhouy; Aliasghar Arab; Mohsen Jalaeian Farimani",
    journal: "Proceedings of Machine Learning Research (Preparation for submitting)"
  },
  {
    id: 3,
    year: 2022,
    title: "Use of Artificial Intelligence to Identify Adhesive Joints Defects by Using Ultrasonic",
    authors: "Davoud Nikkhouy, Rastegarmoghaddam, M., rajabi, M",
    journal: "Amirkabir Journal of Mechanical Engineering",
    volume: "54(2), pp. 377-390"
  },
  {
    id: 4,
    year: 2021,
    title: "Path Design and Control of a Moving Social Robot in an Environment with Moving Obstacles to Reach a Moving Target through Fuzzy Control",
    authors: "Davood Nikkhouy; Moharam Habibnejad Korayem; Siavash Fathollahi Dehkordi",
    journal: "Amirkabir Journal of Mechanical Engineering",
    volume: "53, 2, 2021, 993-1014"
  },
  {
    id: 5,
    year: 2018,
    title: "Control a mobile robot in Social environments by considering humans as a moving obstacle",
    authors: "S. D. N. Tanha, S. F. Dehkordi and A. H. Korayem",
    journal: "2018 6th RSI International Conference on Robotics and Mechatronics (IcRoM)",
    volume: "pp. 256-260"
  }
];

export const projects = [
  {
    id: "bilevel-mpc",
    title: "Bi-Level Performance-Safety MPC",
    shortDescription: "Nonlinear Model Predictive Control with performance-safety considerations",
    description: "Advanced control system implementing bi-level optimization for nonlinear model predictive control, balancing performance objectives with safety constraints for autonomous systems.",
    technologies: ["MATLAB", "Control Theory", "Optimization", "MPC"],
    images: ["/src/assets/placeholder-project.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: true
  },
  {
    id: "fuzzy-q-learning",
    title: "Fuzzy Q-Learning Navigation",
    shortDescription: "AI-driven navigation system for unmanned ground vehicles",
    description: "Implementation of fuzzy Q-learning with fuzzified Bellman equation for robust navigation of unmanned ground vehicles in uncertain environments.",
    technologies: ["Python", "ROS2", "Gazebo", "Reinforcement Learning", "Fuzzy Logic"],
    images: ["/src/assets/placeholder-project-2.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: true
  },
  {
    id: "stm32-autopilot",
    title: "STM32 Autopilot System",
    shortDescription: "Real-time embedded autopilot with RTOS architecture",
    description: "Comprehensive autopilot system built on STM32 microcontroller with FreeRTOS, featuring real-time task scheduling and advanced flight control algorithms.",
    technologies: ["STM32", "FreeRTOS", "C/C++", "Embedded Systems", "Real-time Control"],
    images: ["/src/assets/placeholder-project.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: false
  },
  {
    id: "social-robot",
    title: "Social Robot Controller",
    shortDescription: "Fuzzy logic controller for human-robot interaction",
    description: "Intelligent social robot with fuzzy logic-based controller for dynamic interaction with moving targets and obstacle avoidance in human environments.",
    technologies: ["ROS", "Computer Vision", "Fuzzy Logic", "Python", "Sensor Fusion"],
    images: ["/src/assets/placeholder-project-2.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: false
  },
  {
    id: "autonomous-watercraft",
    title: "Autonomous Watercraft",
    shortDescription: "High-speed watercraft with real-time obstacle avoidance",
    description: "Advanced autonomous watercraft system featuring real-time obstacle detection and avoidance algorithms for high-speed navigation in marine environments.",
    technologies: ["Embedded Systems", "Computer Vision", "Real-time Control", "Marine Robotics"],
    images: ["/src/assets/placeholder-project.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: false
  },
  {
    id: "robotic-arm-3d",
    title: "6-DOF Robotic Arm",
    shortDescription: "Multi-axis robotic arm for 3D printing applications",
    description: "Precision 6-degree-of-freedom robotic arm designed for 3D printing applications with advanced kinematics and motion control.",
    technologies: ["Kinematics", "Motion Control", "3D Printing", "Mechanical Design"],
    images: ["/src/assets/placeholder-project-2.jpg"],
    youtubeVideos: [],
    githubUrl: "",
    demoUrl: "",
    featured: false
  }
];

export const references = [
  {
    id: 1,
    name: "Professor Mohsen Jalaeian Farimani",
    title: "PhD, Robotics and Control Engineering",
    position: "Assistant Professor, Politecnico di Milano University",
    email: "mohsen.jalaeian@polimi.it",
    link: "https://www.deib.polimi.it/eng/people/details/2012404",
    period: "April 2024 – Current"
  },
  {
    id: 2,
    name: "Dr Amirarya Ramzgooyan",
    title: "CEO, AFS-Agri (Aseman Faraz Sharif)",
    phone: "+31-6-38339132",
    email: "a.ramzgooyan@cgelectronics.com",
    period: "October 2008 – Current"
  }
];

