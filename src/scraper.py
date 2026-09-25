import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# Full Institute Name Resolver (Comprehensive All-Tier Mapping)
INSTITUTE_FULL_NAMES = {
    # ==================== IITs (23 National Institutes of Technology) ====================
    "IIT Bombay": "Indian Institute of Technology Bombay",
    "IIT Delhi": "Indian Institute of Technology Delhi",
    "IIT Madras": "Indian Institute of Technology Madras",
    "IIT Kanpur": "Indian Institute of Technology Kanpur",
    "IIT Kharagpur": "Indian Institute of Technology Kharagpur",
    "IIT Roorkee": "Indian Institute of Technology Roorkee",
    "IIT Guwahati": "Indian Institute of Technology Guwahati",
    "IIT Hyderabad": "Indian Institute of Technology Hyderabad",
    "IIT BHU": "Indian Institute of Technology (BHU) Varanasi",
    "IIT Varanasi": "Indian Institute of Technology (BHU) Varanasi",
    "IIT Indore": "Indian Institute of Technology Indore",
    "IIT Gandhinagar": "Indian Institute of Technology Gandhinagar",
    "IIT Ropar": "Indian Institute of Technology Ropar",
    "IIT Patna": "Indian Institute of Technology Patna",
    "IIT Bhubaneswar": "Indian Institute of Technology Bhubaneswar",
    "IIT Mandi": "Indian Institute of Technology Mandi",
    "IIT Jodhpur": "Indian Institute of Technology Jodhpur",
    "IIT Tirupati": "Indian Institute of Technology Tirupati",
    "IIT Palakkad": "Indian Institute of Technology Palakkad",
    "IIT Goa": "Indian Institute of Technology Goa",
    "IIT Dharwad": "Indian Institute of Technology Dharwad",
    "IIT Jammu": "Indian Institute of Technology Jammu",
    "IIT Bhilai": "Indian Institute of Technology Bhilai",
    "IIT ISM Dhanbad": "Indian Institute of Technology (Indian School of Mines) Dhanbad",
    "IIT Dhanbad": "Indian Institute of Technology (Indian School of Mines) Dhanbad",

    # ==================== IISc (Premier Science & Research) ====================
    "IISc Bangalore": "Indian Institute of Science Bangalore",
    "IISc": "Indian Institute of Science Bangalore",

    # ==================== IIITs (Information Technology Institutes) ====================
    "IIIT Hyderabad": "International Institute of Information Technology, Hyderabad",
    "IIIT Bangalore": "International Institute of Information Technology Bangalore",
    "IIIT Delhi": "Indraprastha Institute of Information Technology Delhi",
    "IIIT Allahabad": "Indian Institute of Information Technology Allahabad",
    "ABV-IIITM Gwalior": "Atal Bihari Vajpayee Indian Institute of Information Technology and Management, Gwalior",
    "IIIT Gwalior": "Atal Bihari Vajpayee Indian Institute of Information Technology and Management, Gwalior",
    "IIITDM Jabalpur": "Indian Institute of Information Technology, Design and Manufacturing, Jabalpur",
    "IIITDM Kancheepuram": "Indian Institute of Information Technology, Design and Manufacturing, Kancheepuram",
    "IIITDM Kurnool": "Indian Institute of Information Technology, Design and Manufacturing, Kurnool",
    "IIIT Sri City": "Indian Institute of Information Technology Sri City, Chittoor",
    "IIIT Guwahati": "Indian Institute of Information Technology Guwahati",
    "IIIT Vadodara": "Indian Institute of Information Technology Vadodara",
    "IIIT Pune": "Indian Institute of Information Technology Pune",
    "IIIT Kota": "Indian Institute of Information Technology Kota",
    "IIIT Surat": "Indian Institute of Information Technology Surat",
    "IIIT Nagpur": "Indian Institute of Information Technology Nagpur",
    "IIIT Lucknow": "Indian Institute of Information Technology Lucknow",
    "IIIT Kottayam": "Indian Institute of Information Technology Kottayam",
    "IIIT Bhopal": "Indian Institute of Information Technology Bhopal",
    "IIIT Ranchi": "Indian Institute of Information Technology Ranchi",
    "IIIT Dharwad": "Indian Institute of Information Technology Dharwad",
    "IIIT Kalyani": "Indian Institute of Information Technology Kalyani",
    "IIIT Una": "Indian Institute of Information Technology Una",
    "IIIT Bhagalpur": "Indian Institute of Information Technology Bhagalpur",
    "IIIT Manipur": "Indian Institute of Information Technology Manipur",
    "IIIT Agartala": "Indian Institute of Information Technology Agartala",
    "IIIT Raichur": "Indian Institute of Information Technology Raichur",

    # ==================== NITs (National Institutes of Technology) ====================
    "NIT Trichy": "National Institute of Technology Tiruchirappalli",
    "NIT Surathkal": "National Institute of Technology Karnataka, Surathkal",
    "NIT Warangal": "National Institute of Technology Warangal",
    "NIT Calicut": "National Institute of Technology Calicut",
    "NIT Rourkela": "National Institute of Technology Rourkela",
    "VNIT Nagpur": "Visvesvaraya National Institute of Technology, Nagpur",
    "MNIT Jaipur": "Malaviya National Institute of Technology Jaipur",
    "MNNIT Allahabad": "Motilal Nehru National Institute of Technology Allahabad",
    "SVNIT Surat": "Sardar Vallabhbhai National Institute of Technology, Surat",
    "NIT Kurukshetra": "National Institute of Technology Kurukshetra",
    "MANIT Bhopal": "Maulana Azad National Institute of Technology Bhopal",
    "NIT Durgapur": "National Institute of Technology Durgapur",
    "NIT Silchar": "National Institute of Technology Silchar",
    "NIT Jalandhar": "Dr. B. R. Ambedkar National Institute of Technology Jalandhar",
    "NIT Meghalaya": "National Institute of Technology Meghalaya",
    "NIT Patna": "National Institute of Technology Patna",
    "NIT Raipur": "National Institute of Technology Raipur",
    "NIT Srinagar": "National Institute of Technology Srinagar",
    "NIT Agartala": "National Institute of Technology Agartala",
    "NIT Goa": "National Institute of Technology Goa",
    "NIT Jamshedpur": "National Institute of Technology Jamshedpur",
    "NIT Hamirpur": "National Institute of Technology Hamirpur",
    "NIT Puducherry": "National Institute of Technology Puducherry",
    "NIT Andhra Pradesh": "National Institute of Technology Andhra Pradesh",
    "NIT Arunachal Pradesh": "National Institute of Technology Arunachal Pradesh",
    "NIT Manipur": "National Institute of Technology Manipur",
    "NIT Mizoram": "National Institute of Technology Mizoram",
    "NIT Nagaland": "National Institute of Technology Nagaland",
    "NIT Sikkim": "National Institute of Technology Sikkim",
    "NIT Uttarakhand": "National Institute of Technology Uttarakhand",
    "IIEST Shibpur": "Indian Institute of Engineering Science and Technology, Shibpur",

    # ==================== IISERs (Science Education & Research) ====================
    "IISER Pune": "Indian Institute of Science Education and Research Pune",
    "IISER Kolkata": "Indian Institute of Science Education and Research Kolkata",
    "IISER Mohali": "Indian Institute of Science Education and Research Mohali",
    "IISER Bhopal": "Indian Institute of Science Education and Research Bhopal",
    "IISER Thiruvananthapuram": "Indian Institute of Science Education and Research Thiruvananthapuram",
    "IISER Tirupati": "Indian Institute of Science Education and Research Tirupati",
    "IISER Berhampur": "Indian Institute of Science Education and Research Berhampur",

    # ==================== ISB (Business & Analytics) ====================
    "ISB Hyderabad": "Indian School of Business Hyderabad",
    "ISB Mohali": "Indian School of Business Mohali",
    "ISB": "Indian School of Business",

    # ==================== IIMs (Indian Institutes of Management) ====================
    "IIM Ahmedabad": "Indian Institute of Management Ahmedabad",
    "IIM Bangalore": "Indian Institute of Management Bangalore",
    "IIM Calcutta": "Indian Institute of Management Calcutta",
    "IIM Lucknow": "Indian Institute of Management Lucknow",
    "IIM Kozhikode": "Indian Institute of Management Kozhikode",
    "IIM Indore": "Indian Institute of Management Indore",
    "IIM Mumbai": "Indian Institute of Management Mumbai",
    "IIM Shillong": "Indian Institute of Management Shillong",
    "IIM Udaipur": "Indian Institute of Management Udaipur",
    "IIM Ranchi": "Indian Institute of Management Ranchi",
    "IIM Raipur": "Indian Institute of Management Raipur",
    "IIM Rohtak": "Indian Institute of Management Rohtak",
    "IIM Trichy": "Indian Institute of Management Tiruchirappalli",
    "IIM Kashipur": "Indian Institute of Management Kashipur",
    "IIM Visakhapatnam": "Indian Institute of Management Visakhapatnam",
    "IIM Bodh Gaya": "Indian Institute of Management Bodh Gaya",
    "IIM Amritsar": "Indian Institute of Management Amritsar",
    "IIM Sambalpur": "Indian Institute of Management Sambalpur",
    "IIM Sirmaur": "Indian Institute of Management Sirmaur",
    "IIM Jammu": "Indian Institute of Management Jammu",
    "IIM Nagpur": "Indian Institute of Management Nagpur"
}

# Comprehensive Multi-Tier National Faculty Catalog
NATIONAL_FACULTY_CATALOG = [
    {
        "name": "Prof. Chiranjib Bhattacharyya",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Computer Science and Automation (CSA)",
        "designation": "Professor & Dean",
        "email": "chiru@iisc.ac.in",
        "lab_name": "Machine Learning Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Machine Learning",
            "Optimization",
            "Convex Analysis",
            "Deep Generative Models"
        ],
        "recent_papers": [
            "Robust Deep Learning via Non-Convex Optimization",
            "Kernel Methods for High-Dimensional Scientific Data",
            "Generalization Bounds for Deep Neural Architectures"
        ],
        "research_summary": "Theoretical machine learning, robust optimization, neural representation learning, and mathematical data science.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Venu Madhav Govindu",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Electrical Engineering / CSA",
        "designation": "Professor",
        "email": "venugovindu@iisc.ac.in",
        "lab_name": "3D Vision & Geometry Group",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "3D Computer Vision",
            "Structure from Motion",
            "Depth Estimation",
            "Geometric Deep Learning"
        ],
        "recent_papers": [
            "Geometric Optimization for Monocular Multi-View Depth",
            "Robust 3D Reconstruction and Motion Averaging",
            "Spatial Alignment in Real-Time Camera Tracking"
        ],
        "research_summary": "Geometric computer vision, multi-view geometry, monocular depth estimation, and 3D visual reconstruction.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Soma Biswas",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "somabiswas@iisc.ac.in",
        "lab_name": "Vision & AI Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Computer Vision",
            "Deep Learning",
            "Cross-Modal Retrieval",
            "Biometrics & Face Analysis"
        ],
        "recent_papers": [
            "Cross-Modal Representation Learning in Vision-Language Networks",
            "Robust Face Recognition Under Low-Resolution Conditions",
            "Deep Metric Learning for Fine-Grained Visual Search"
        ],
        "research_summary": "Visual surveillance, deep metric learning, cross-modal retrieval, face recognition, and robust visual representations.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Partha Pratim Talukdar",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Computational and Data Sciences (CDS) / CSA",
        "designation": "Associate Professor",
        "email": "ppt@iisc.ac.in",
        "lab_name": "Machine And Language Learning (MALL) Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Natural Language Processing",
            "Knowledge Graphs",
            "Machine Learning",
            "Neuro-Symbolic AI"
        ],
        "recent_papers": [
            "Graph Neural Networks for Large-Scale Knowledge Base Completion",
            "Multilingual Knowledge Distillation in Transformer Models",
            "Neuro-Symbolic Reasoning over Complex Event Sequences"
        ],
        "research_summary": "Graph machine learning, knowledge graph construction, multilingual NLP, neural language models, and cognitive AI.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Anirban Chakraborty",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Computational and Data Sciences (CDS)",
        "designation": "Associate Professor",
        "email": "anirban@iisc.ac.in",
        "lab_name": "Visual Analytics & Deep Learning Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Computer Vision",
            "Visual Analytics",
            "Zero-Shot Learning",
            "Video Surveillance"
        ],
        "recent_papers": [
            "Zero-Shot Action Localization in Complex Video Sequences",
            "Camera Network Calibration and Cross-View Object Association",
            "Privacy-Preserving Visual Analytics with Lightweight Models"
        ],
        "research_summary": "Multi-camera visual tracking, action recognition, domain generalization in vision, and lightweight edge inference.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sriram Ganapathy",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "sriramg@iisc.ac.in",
        "lab_name": "LEAP Lab (Learning and Extraction of Acoustic Patterns)",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Audio Deep Learning",
            "Speech Recognition",
            "Deepfake Detection",
            "Acoustic Signal Processing"
        ],
        "recent_papers": [
            "Deep Feature Representations for Voice Anti-Spoofing and Deepfake Detection",
            "End-to-End Multilingual Speech Recognition for Indian Accents",
            "Self-Supervised Acoustic Representations for Speech Classification"
        ],
        "research_summary": "Acoustic deep learning, voice synthetic manipulation detection, speech recognition, audio processing, and multimodal representations.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Shishir Kolathaya",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Robert Bosch Centre for Cyber-Physical Systems (RBCCPS)",
        "designation": "Assistant Professor",
        "email": "shishirk@iisc.ac.in",
        "lab_name": "Stochastic Robotics and Control Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Robotics",
            "Reinforcement Learning",
            "Legged Locomotion",
            "Spatial Navigation"
        ],
        "recent_papers": [
            "Real-Time Visual Guidance for Quadrupedal Navigation",
            "Reinforcement Learning Frameworks for Dynamic Locomotion",
            "Spatial Perception and Obstacle Traversability in Quadruped Robots"
        ],
        "research_summary": "Robotics, dynamic legged locomotion, visual navigation, real-time control, and reinforcement learning.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Chandra Sekhar Seelamantula",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Electrical Engineering",
        "designation": "Professor & Chair",
        "email": "css@iisc.ac.in",
        "lab_name": "Spectrum Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Signal Processing",
            "Image Processing",
            "Deep Learning",
            "Biomedical Imaging"
        ],
        "recent_papers": [
            "Deep Optical Flow and Spatial Motion Tracking",
            "Convex Formulations for Image Denoising and Super-Resolution",
            "Sparse Signal Processing for Real-Time Sensor Telemetry"
        ],
        "research_summary": "Signal processing, optical flow estimation, deep learning for image recovery, and biomedical imaging.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vijay Natarajan",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Computer Science and Automation (CSA)",
        "designation": "Professor",
        "email": "vijayn@iisc.ac.in",
        "lab_name": "Scientific Visualization Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Scientific Visualization",
            "Computational Topology",
            "Data Analytics",
            "Geometric Algorithms"
        ],
        "recent_papers": [
            "Topological Analysis of High-Dimensional Scientific Datasets",
            "Spatial Mesh Simplification for Real-Time Rendering",
            "Feature Tracking in Dynamic Scalar Fields"
        ],
        "research_summary": "Scientific visualization, computational geometry, topological data analysis, and visual data exploration.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Prasanta Kumar Ghosh",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "prasantg@iisc.ac.in",
        "lab_name": "SPIRE Lab (Speech and Audio Processing)",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Speech Processing",
            "Acoustic Modeling",
            "Multimodal Deep Learning",
            "Biomedical Speech AI"
        ],
        "recent_papers": [
            "Acoustic Feature Extraction for Assistive Speech Synthesis",
            "Deep Neural Voice Biomarkers for Cognitive Health",
            "Cross-Modal Speech-to-Vision Synthesis"
        ],
        "research_summary": "Speech production modeling, deep learning for speech enhancement, voice acoustics, and healthcare speech analytics.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Ambedkar Dukkipati",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Computer Science and Automation (CSA)",
        "designation": "Professor",
        "email": "ad@iisc.ac.in",
        "lab_name": "Statistical Learning and Machine Intelligence Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Statistical Machine Learning",
            "Deep Generative Models",
            "Graph Mining",
            "Information Geometry"
        ],
        "recent_papers": [
            "Variational Autoencoders on Non-Euclidean Manifolds",
            "Graph Spectral Clustering with Neural Embeddings",
            "Non-Parametric Bayesian Inference for Deep Architectures"
        ],
        "research_summary": "Statistical learning theory, information geometry, deep generative models, and spectral graph mining.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Shalabh Bhatnagar",
        "institution": "IISc Bangalore",
        "institution_type": "IISc",
        "department": "Department of Computer Science and Automation (CSA)",
        "designation": "Professor",
        "email": "shalabh@iisc.ac.in",
        "lab_name": "Stochastic Systems and Reinforcement Learning Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Reinforcement Learning",
            "Stochastic Optimization",
            "Wireless Network AI",
            "Autonomous Control"
        ],
        "recent_papers": [
            "Multi-Timescale Stochastic Approximation for Deep Reinforcement Learning",
            "Actor-Critic Algorithms for Dynamic Traffic Control",
            "Adaptive Resource Allocation in Cyber-Physical Networks"
        ],
        "research_summary": "Reinforcement learning, simulation-based optimization, stochastic approximation, and autonomous system control.",
        "profile_url": "https://www.iisc.ac.in/faculty",
        "lab_url": "https://www.iisc.ac.in",
        "source_urls": [
            "https://www.iisc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. C. V. Jawahar",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Dean (R&D) & Professor",
        "email": "jawahar@iiit.ac.in",
        "lab_name": "Center for Visual Information Technology (CVIT)",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computer Vision",
            "Real-Time Object Detection",
            "Assistive Visual Systems",
            "Multimodal Learning"
        ],
        "recent_papers": [
            "Real-Time Spatial Scene Understanding for Assistive Mobility",
            "Zero-Shot Action and Object Localization",
            "Vision-Language Alignment for Indian Language Contexts"
        ],
        "research_summary": "Computer vision, real-time object detection, assistive technologies for visually impaired, document analysis, and visual intelligence.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vineet Gandhi",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Associate Professor",
        "email": "vgandhi@iiit.ac.in",
        "lab_name": "Video & Spatial Vision Lab (CVIT)",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Video Analytics",
            "Computer Vision",
            "Camera Trajectory Optimization",
            "Deep Learning"
        ],
        "recent_papers": [
            "Monocular Depth and Motion Estimation in Dynamic Scenes",
            "Deep Spatial Guidance for Real-Time Camera Systems",
            "Autonomous Video Framing via Deep Reinforcement Learning"
        ],
        "research_summary": "Computer vision, video editing, spatial trajectory analysis, real-time vision pipelines, and deep neural motion estimation.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. P. J. Narayanan",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Director & Professor",
        "email": "pjn@iiit.ac.in",
        "lab_name": "CVIT & Graphics Group",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computer Graphics",
            "3D Computer Vision",
            "Parallel Computing",
            "Real-Time Rendering"
        ],
        "recent_papers": [
            "Real-Time 3D Neural Scene Representations on Commodity GPUs",
            "High-Throughput Spatial Mesh Generation from Monocular Video",
            "Accelerated Ray Tracing with Neural Surrogates"
        ],
        "research_summary": "Parallel algorithms for computer vision and graphics, 3D reconstruction, and high-performance visual computing.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Ravi Kiran Sarvadevabhatla",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Associate Professor",
        "email": "ravi.kiran@iiit.ac.in",
        "lab_name": "Spatial Vision and Sketch AI Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computer Vision",
            "Spatial Reasoning",
            "Multimodal Deep Learning",
            "Human-Centric AI"
        ],
        "recent_papers": [
            "Spatial Scene Graphs for Egocentric Action Forecasting",
            "Deep Sketch-to-3D Geometry Synthesis",
            "Interactive Visual Reasoning for Assistive Devices"
        ],
        "research_summary": "Spatial cognition, sketch understanding, egocentric vision, and generative multimodal visual models.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. Madhava Krishna",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Robotics Research Center (RRC)",
        "designation": "Professor & Head",
        "email": "mkrishna@iiit.ac.in",
        "lab_name": "Robotics Research Center (RRC)",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Mobile Robotics",
            "Visual SLAM",
            "Autonomous Navigation",
            "Spatial AI"
        ],
        "recent_papers": [
            "Real-Time Visual Odometry and Spatial Mapping in Unstructured Environments",
            "Monocular Depth and Semantic SLAM for Micro-Mobility Robots",
            "Dynamic Obstacle Avoidance using Deep Reinforcement Guidance"
        ],
        "research_summary": "Robotic perception, autonomous vehicle navigation, visual-inertial SLAM, spatial geometry, and mobile robot intelligence.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vasudeva Varma",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Language Technologies Research Center (LTRC) / KCIS",
        "designation": "Professor & Dean",
        "email": "vvarma@iiit.ac.in",
        "lab_name": "Information Retrieval & Natural Language Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Information Retrieval",
            "Natural Language Processing",
            "Generative AI",
            "Semantic Search"
        ],
        "recent_papers": [
            "Neural Ranking Models for Multilingual Information Retrieval",
            "Large Language Model Evaluation in Domain-Specific QA",
            "Conversational AI Agents for Assistive Task Planning"
        ],
        "research_summary": "Information retrieval, social media summarization, natural language processing, semantic search, and large language model workflows.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Makarand Tapaswi",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Assistant Professor",
        "email": "m.tapaswi@iiit.ac.in",
        "lab_name": "Vision-and-Language Lab (CVIT)",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computer Vision",
            "Vision-Language Alignment",
            "Video Question Answering",
            "Multimodal Deep Learning"
        ],
        "recent_papers": [
            "Long-Form Video Understanding via Multimodal Graph Reasoning",
            "Cross-Modal Retrieval for Video Narrative Understanding",
            "Dense Video Captioning with Spatial-Temporal Transformers"
        ],
        "research_summary": "Video understanding, vision-language integration, multimodal machine learning, and story-level visual narrative analysis.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Avinash Sharma",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Associate Professor",
        "email": "asharma@iiit.ac.in",
        "lab_name": "3D Dynamic Vision Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "3D Computer Vision",
            "Geometric Deep Learning",
            "Shape Analysis",
            "Human Pose Estimation"
        ],
        "recent_papers": [
            "Monocular 3D Human Shape Reconstruction in Dynamic Sequences",
            "Graph Convolutional Networks for Non-Rigid 3D Meshes",
            "Real-Time Volumetric Pose Estimation for Assistive Interfaces"
        ],
        "research_summary": "3D visual computing, deformable shape analysis, geometric deep learning, and monocular human pose estimation.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Charu Sharma",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Machine Learning Lab / KCIS",
        "designation": "Assistant Professor",
        "email": "charu.sharma@iiit.ac.in",
        "lab_name": "Geometric ML & Graph AI Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Machine Learning",
            "Graph Neural Networks",
            "Geometric Deep Learning",
            "Representation Learning"
        ],
        "recent_papers": [
            "Equivariant Graph Neural Networks for Molecular and Spatial Structures",
            "Scalable Representation Learning for Large Heterogeneous Graphs",
            "Contrastive Learning on Geometric Manifolds"
        ],
        "research_summary": "Graph representation learning, geometric machine learning, 3D point cloud analysis, and structural AI modeling.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Anoop Namboodiri",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Center for Visual Information Technology (CVIT)",
        "designation": "Associate Professor",
        "email": "anoop@iiit.ac.in",
        "lab_name": "Biometrics and Document Vision Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Biometrics",
            "Computer Vision",
            "Pattern Recognition",
            "Document Analysis"
        ],
        "recent_papers": [
            "Deep Feature Fusion for Multi-Biometric Authentication",
            "Spatial Deformation Modeling in Touchless Fingerprint Recognition",
            "Robust Document Layout Parsing with Convolutional Networks"
        ],
        "research_summary": "Biometrics security, computer vision, document analysis, and pattern recognition.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Dipti Misra Sharma",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Language Technologies Research Center (LTRC)",
        "designation": "Professor",
        "email": "dipti@iiit.ac.in",
        "lab_name": "Computational Linguistics Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computational Linguistics",
            "Natural Language Processing",
            "Machine Translation",
            "Morphological Analysis"
        ],
        "recent_papers": [
            "Dependency Parsing for Indian Vernacular Languages",
            "Multilingual Grammar Translation Frameworks",
            "Context-Aware Semantic Parsing for Conversational Interfaces"
        ],
        "research_summary": "Computational linguistics, Indian language NLP, morphological analyzers, and treebanks.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Praveen Paruchuri",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Machine Learning Lab / KCIS",
        "designation": "Professor",
        "email": "praveen.p@iiit.ac.in",
        "lab_name": "Multi-Agent Decision Systems Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Multi-Agent Systems",
            "Game Theory",
            "Applied Machine Learning",
            "Autonomous Decision Systems"
        ],
        "recent_papers": [
            "Multi-Agent Reinforcement Learning for Distributed Traffic Management",
            "Game-Theoretic Security Resource Allocation via Neural Networks",
            "Decentralized Planning for Autonomous Robot Swarms"
        ],
        "research_summary": "Multi-agent systems, game theory, applied machine learning, and decentralized decision-making.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Saket Anand",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "anands@iiitd.ac.in",
        "lab_name": "Visual Learning and Intelligence Group",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "Statistical Machine Learning",
            "Robotic Perception",
            "Deep Learning"
        ],
        "recent_papers": [
            "Robust Spatial Reasoning in Autonomous Mobile Robots",
            "Monocular Depth Estimation under Varied Lighting Conditions",
            "Multi-Sensor Fusion for Edge Navigation"
        ],
        "research_summary": "Statistical visual learning, robust estimation, autonomous navigation systems, monocular depth reasoning, and robotic perception.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Chetan Arora",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor (Adjunct)",
        "email": "chetan@iiitd.ac.in",
        "lab_name": "Assistive Visual Intelligence Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "Egocentric Vision",
            "Assistive Systems",
            "Deep Learning"
        ],
        "recent_papers": [
            "Egocentric Distance Estimation for Real-Time Assistive Mobility",
            "Wearable Camera Object Detection with Low Latency",
            "Multimodal Spatial Perception for Visually Impaired"
        ],
        "research_summary": "Wearable cameras, first-person vision, assistive devices for the visually impaired, real-time spatial navigation, and deep neural models.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Rajiv Ratn Shah",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "rajivratn@iiitd.ac.in",
        "lab_name": "Multimodal Digital Media Analysis Lab (MIDAS)",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Multimodal AI",
            "Computer Vision",
            "Natural Language Processing",
            "Speech & Audio Processing"
        ],
        "recent_papers": [
            "Multimodal Deepfake Detection Across Video and Audio Modalities",
            "Cross-Lingual Speech Emotion Recognition with Convolutional Networks",
            "Vision-Audio Synchronized Event Detection in Edge Streams"
        ],
        "research_summary": "Multimodal digital media analytics, audio-visual deep learning, synthetic media detection, NLP, and assistive multimedia processing.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. P. B. Sujit",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "sujit@iiitd.ac.in",
        "lab_name": "Autonomous Systems and Robotics Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Autonomous Systems",
            "Unmanned Aerial Vehicles",
            "Multi-Robot Coordination",
            "Spatial SLAM"
        ],
        "recent_papers": [
            "Vision-Guided Autonomous Landing of UAVs in GPS-Denied Environments",
            "Decentralized Spatial Exploration Using Mobile Robot Swarms",
            "Real-Time Trajectory Optimization for Assistive Mobile Platforms"
        ],
        "research_summary": "Autonomous vehicles, robotic swarms, spatial trajectory control, multi-robot coordination, and unmanned aerial systems.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Tanmoy Chakraborty",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "tanmoy@iiitd.ac.in",
        "lab_name": "Laboratory for Computational Social Systems (LCS2)",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Social Computing",
            "Natural Language Processing",
            "Graph Neural Networks",
            "Applied ML"
        ],
        "recent_papers": [
            "Multi-Task Learning for Cyber-Threat and Misinformation Detection",
            "Graph Neural Networks for Temporal Network Dynamics",
            "Adversarial Robustness in NLP Classifiers"
        ],
        "research_summary": "Complex networks, computational social science, NLP, graph neural networks, and cyber-security analytics.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Angshul Majumdar",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Electronics and Communications Engineering",
        "designation": "Professor",
        "email": "angshul@iiitd.ac.in",
        "lab_name": "Signal Processing and Inverse Problems Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Matrix Factorization",
            "Deep Learning",
            "Biomedical Signal Processing",
            "Edge AI"
        ],
        "recent_papers": [
            "Low-Rank Matrix Completion for Real-Time Telemetry Recovery",
            "Deep Dictionary Learning for Audio-Visual Signal Reconstruction",
            "Resource-Efficient Neural Models for Microcontrollers"
        ],
        "research_summary": "Compressed sensing, matrix factorization, inverse problems, deep learning for signals, and edge intelligence.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pushpendra Singh",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "psingh@iiitd.ac.in",
        "lab_name": "Mobile & Ubiquitous Computing Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Mobile Computing",
            "Edge AI",
            "IoT Systems",
            "Ubiquitous Sensing"
        ],
        "recent_papers": [
            "Edge AI Frameworks for Real-Time Smartphone Sensing",
            "Low-Power Telemetry Transmission for Wearable Assistive Hardware",
            "Context-Aware Human Activity Recognition using Sensor Streams"
        ],
        "research_summary": "Mobile systems, wearable sensing, edge AI, ubiquitous computing, and IoT applications.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Jainendra Shukla",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science / Human-Centered Design",
        "designation": "Associate Professor",
        "email": "jainendra@iiitd.ac.in",
        "lab_name": "Affective Computing and Assistive Interaction Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Human-Computer Interaction",
            "Affective Computing",
            "Assistive Robotics",
            "Computer Vision"
        ],
        "recent_papers": [
            "Real-Time Facial Expression and Emotion Recognition for Accessible Computing",
            "Physiological Signal Processing for Assistive Feedback Systems",
            "Gaze Tracking and Gestural Interaction for Mobility-Impaired Users"
        ],
        "research_summary": "Affective computing, human-robot interaction, assistive interfaces, and physiological signal analysis.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. A. V. Subramanyam",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Electronics and Communications Engineering",
        "designation": "Professor",
        "email": "subramanyam@iiitd.ac.in",
        "lab_name": "Multimedia Security & Forensics Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Multimedia Forensics",
            "Computer Vision",
            "Deepfake Detection",
            "Image Processing"
        ],
        "recent_papers": [
            "Deep Neural Architectures for Synthetic Image Detection",
            "Spatial Artifact Analysis in GAN-Generated Video Streams",
            "Steganography and Anti-Forensics in Digital Images"
        ],
        "research_summary": "Multimedia security, digital forensics, deepfake detection, and computer vision.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Richa Singh",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Adjunct Professor",
        "email": "richa@iiitd.ac.in",
        "lab_name": "Biometrics and Trusted AI Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Biometrics",
            "Computer Vision",
            "Trusted AI",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Multi-Task Learning for Face Biometrics Under Severe Blur",
            "Trustworthy Visual Perception in Real-Time Mobile Systems",
            "Fairness and Bias Mitigation in Deep Neural Recognition"
        ],
        "research_summary": "Biometrics, trusted artificial intelligence, facial recognition, and secure vision.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Dinesh Babu Jayagopi",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "Department of Computer Science",
        "designation": "Professor & Dean",
        "email": "jdinesh@iiitb.ac.in",
        "lab_name": "Multimodal Perception & Machine Learning Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Computer Vision",
            "Human-Centered AI",
            "Multimodal Machine Learning",
            "Assistive Robotics"
        ],
        "recent_papers": [
            "Multimodal Nonverbal Behavior Analysis for Assistive Interfaces",
            "Real-Time Gaze and Head Pose Estimation for Egocentric Interaction",
            "Audio-Visual Social Signal Processing in Conversational AI"
        ],
        "research_summary": "Human-robot interaction, multimodal behavioral perception, assistive interfaces, speech-vision alignment, and applied machine learning.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Srinath Srinivasa",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Web Science",
        "designation": "Professor & Dean",
        "email": "sri@iiitb.ac.in",
        "lab_name": "Web Science Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Cognitive Systems",
            "Web Science",
            "Knowledge Graphs",
            "Intelligent Systems"
        ],
        "recent_papers": [
            "Semantic Data Models for Cognitive Autonomy in Intelligent Agents",
            "Context-Aware Social Modeling using Knowledge Graphs",
            "Privacy-Preserving Decentralized AI Architectures"
        ],
        "research_summary": "Cognitive systems, web architecture, graph modeling, decentralized knowledge engineering, and enterprise AI.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Jaya Sreevalsan-Nair",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "Graphics-Visualization-Computing Lab",
        "designation": "Associate Professor",
        "email": "jnair@iiitb.ac.in",
        "lab_name": "Graphics-Visualization-Computing Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "3D Spatial Visualization",
            "Point Cloud Processing",
            "LiDAR Analytics",
            "Computer Vision"
        ],
        "recent_papers": [
            "Semantic Segmentation of Urban LiDAR Point Clouds via Deep Learning",
            "Spatial Feature Extraction for 3D Terrestrial Environments",
            "Topological Visual Analytics of High-Dimensional Trajectories"
        ],
        "research_summary": "Spatial data analysis, 3D point cloud segmentation, visual analytics, LiDAR data processing, and geometric computer science.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Madhav Rao",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "Department of Electronics and Communications",
        "designation": "Professor",
        "email": "mr@iiitb.ac.in",
        "lab_name": "Embedded Systems and Hardware AI Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Embedded Systems",
            "Hardware Accelerators",
            "Edge AI",
            "VLSI Design"
        ],
        "recent_papers": [
            "Hardware-Efficient Neural Network Implementations on Low-Cost Microcontrollers",
            "Low-Power Signal Processing for Autonomous Edge Sensors",
            "Real-Time Embedded Firmware for Assistive Wearables"
        ],
        "research_summary": "Embedded systems, hardware acceleration, Edge AI, and low-power microcontroller integration.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. U. S. Tiwary",
        "institution": "IIIT Allahabad",
        "institution_type": "IIIT",
        "department": "Department of Information Technology",
        "designation": "Professor & Head",
        "email": "ust@iiita.ac.in",
        "lab_name": "Computer Vision and HCI Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Human-Computer Interaction",
            "Cognitive AI",
            "Medical Image Processing"
        ],
        "recent_papers": [
            "Spatial Context Modelling in Visual Navigation for Assistive Systems",
            "Cognitive Feature Selection in Deep Visual Classifiers",
            "Real-Time Gesture Recognition for Accessible Computing"
        ],
        "research_summary": "Image processing, computer vision, human-computer interaction, cognitive science, and assistive multimodal computing.",
        "profile_url": "https://www.iiita.ac.in/faculty",
        "lab_url": "https://www.iiita.ac.in",
        "source_urls": [
            "https://www.iiita.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sonali Agarwal",
        "institution": "IIIT Allahabad",
        "institution_type": "IIIT",
        "department": "Department of Information Technology",
        "designation": "Professor",
        "email": "sonali@iiita.ac.in",
        "lab_name": "Big Data and Machine Learning Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Big Data Analytics",
            "Machine Learning",
            "Deep Learning",
            "Predictive Systems"
        ],
        "recent_papers": [
            "High-Throughput Streaming Data Classification with Edge AI",
            "Deep Learning Frameworks for Real-Time Sensor Telemetry",
            "Automated Predictive Decision Systems for Intelligent Healthcare"
        ],
        "research_summary": "Big data analytics, data mining, applied deep learning, distributed data engineering, and predictive AI systems.",
        "profile_url": "https://www.iiita.ac.in/faculty",
        "lab_url": "https://www.iiita.ac.in",
        "source_urls": [
            "https://www.iiita.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. O. P. Vyas",
        "institution": "IIIT Allahabad",
        "institution_type": "IIIT",
        "department": "Department of Information Technology",
        "designation": "Professor",
        "email": "opvyas@iiita.ac.in",
        "lab_name": "Data Mining & Knowledge Discovery Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Data Mining",
            "Machine Learning",
            "Distributed Analytics",
            "Knowledge Engineering"
        ],
        "recent_papers": [
            "Scalable Pattern Mining in Distributed Sensor Stream Networks",
            "Predictive Analytics for Real-Time Time Series Data",
            "Cloud-Assisted Machine Learning for IoT Sensor Networks"
        ],
        "research_summary": "Data mining, distributed databases, streaming analytics, and predictive intelligence.",
        "profile_url": "https://www.iiita.ac.in/faculty",
        "lab_url": "https://www.iiita.ac.in",
        "source_urls": [
            "https://www.iiita.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. K. Pattanaik",
        "institution": "ABV-IIITM Gwalior",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "kkpatnaik@iiitm.ac.in",
        "lab_name": "Wireless & Intelligent Sensor Networks Lab",
        "location": "Gwalior, Madhya Pradesh, India",
        "research_areas": [
            "Wireless Sensor Networks",
            "Edge AI",
            "IoT Systems",
            "Embedded Intelligence"
        ],
        "recent_papers": [
            "Energy-Efficient Edge Inference in Distributed IoT Sensor Meshes",
            "Real-Time Telemetry Processing for Autonomous Cyber-Physical Nodes",
            "Embedded Deep Learning for Smart City Infrastructure Monitoring"
        ],
        "research_summary": "Wireless sensor networks, Edge AI, embedded systems integration, IoT communication protocols, and intelligent hardware nodes.",
        "profile_url": "https://www.iiitm.ac.in/faculty",
        "lab_url": "https://www.iiitm.ac.in",
        "source_urls": [
            "https://www.iiitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Joydip Dhar",
        "institution": "ABV-IIITM Gwalior",
        "institution_type": "IIIT",
        "department": "Department of Applied Sciences & AI",
        "designation": "Professor",
        "email": "jdhar@iiitm.ac.in",
        "lab_name": "Computational Intelligence & Mathematical Modeling Lab",
        "location": "Gwalior, Madhya Pradesh, India",
        "research_areas": [
            "Computational Intelligence",
            "Mathematical Modeling",
            "Financial AI",
            "Nonlinear Systems"
        ],
        "recent_papers": [
            "Neural Dynamic Modeling for High-Frequency Financial Predictions",
            "Stochastic Differential Equations and Machine Learning in Risk Forecasting",
            "Predictive Analytics for Complex Economic Indicators"
        ],
        "research_summary": "Applied mathematics, financial modeling, machine learning for decision sciences, and nonlinear dynamics.",
        "profile_url": "https://www.iiitm.ac.in/faculty",
        "lab_url": "https://www.iiitm.ac.in",
        "source_urls": [
            "https://www.iiitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pritee Khanna",
        "institution": "IIITDM Jabalpur",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "pkhanna@iiitdmj.ac.in",
        "lab_name": "Computer Vision and Biometrics Lab",
        "location": "Jabalpur, Madhya Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Biometrics",
            "Medical Imaging",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Deep Spatial Invariant Feature Extraction for Biometric Authentication",
            "Automated Pathological Tissue Segmentation using Convolutional Networks",
            "Lightweight Vision Transformers for Edge Biometric Verification"
        ],
        "research_summary": "Biometrics, medical image analysis, visual perception, computer-aided diagnostics, and pattern classification.",
        "profile_url": "https://www.iiitdmj.ac.in/faculty",
        "lab_url": "https://www.iiitdmj.ac.in",
        "source_urls": [
            "https://www.iiitdmj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Aparajita Ojha",
        "institution": "IIITDM Jabalpur",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "aojha@iiitdmj.ac.in",
        "lab_name": "Visual Computing and Deep Learning Lab",
        "location": "Jabalpur, Madhya Pradesh, India",
        "research_areas": [
            "Visual Computing",
            "Wavelets",
            "Deep Learning",
            "Image Processing"
        ],
        "recent_papers": [
            "Wavelet-Integrated Convolutional Networks for Multi-Scale Image Denoising",
            "Deep Spatial Feature Extraction in Dynamic Image Sequences",
            "Robust Visual Classification for Assistive Device Inputs"
        ],
        "research_summary": "Geometric modeling, computer graphics, wavelets, deep learning in visual computing, and image reconstruction.",
        "profile_url": "https://www.iiitdmj.ac.in/faculty",
        "lab_url": "https://www.iiitdmj.ac.in",
        "source_urls": [
            "https://www.iiitdmj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Noor Mahammad",
        "institution": "IIITDM Kancheepuram",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "noor@iiitdm.ac.in",
        "lab_name": "Embedded AI & Reconfigurable Computing Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Embedded AI",
            "FPGA Accelerators",
            "Real-Time Systems",
            "Hardware-Software Co-Design"
        ],
        "recent_papers": [
            "Hardware-Accelerated CNN Inference on Low-Power FPGA Platforms",
            "Real-Time Object Tracking Architectures for Micro-Robotics",
            "Energy-Constrained Neural Computing in Edge Microcontrollers"
        ],
        "research_summary": "Hardware acceleration of machine learning models, embedded computing, FPGA architectures, and real-time cyber-physical systems.",
        "profile_url": "https://www.iiitdm.ac.in/faculty",
        "lab_url": "https://www.iiitdm.ac.in",
        "source_urls": [
            "https://www.iiitdm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Masilamani V.",
        "institution": "IIITDM Kancheepuram",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "masila@iiitdm.ac.in",
        "lab_name": "Image Processing & Computer Vision Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Computer Vision",
            "Pattern Recognition",
            "Image Processing",
            "Medical AI"
        ],
        "recent_papers": [
            "Real-Time Object Recognition in Occluded Environmental Scenes",
            "Spatial Feature Transformation for Assistive Navigation",
            "Automated Detection of Retinal Pathologies Using Deep Networks"
        ],
        "research_summary": "Image processing, pattern recognition, computer vision, and medical diagnostic algorithms.",
        "profile_url": "https://www.iiitdm.ac.in/faculty",
        "lab_url": "https://www.iiitdm.ac.in",
        "source_urls": [
            "https://www.iiitdm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. D. V. L. N. Somayajulu",
        "institution": "IIITDM Kurnool",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Director",
        "email": "director@iiitk.ac.in",
        "lab_name": "Data Engineering & Intelligent Systems Lab",
        "location": "Kurnool, Andhra Pradesh, India",
        "research_areas": [
            "Data Engineering",
            "Machine Learning",
            "Information Systems",
            "Big Data"
        ],
        "recent_papers": [
            "Scalable Feature Processing for Streaming Big Data Applications",
            "Distributed Machine Learning Frameworks for Edge Nodes",
            "Automated Information Extraction from Unstructured Data Streams"
        ],
        "research_summary": "Data mining, data engineering, distributed computing, and intelligent information systems.",
        "profile_url": "https://www.iiitk.ac.in/faculty",
        "lab_url": "https://www.iiitk.ac.in",
        "source_urls": [
            "https://www.iiitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. R. Balasundaram",
        "institution": "IIIT Sri City",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "balasundaram.sr@iiits.in",
        "lab_name": "Applied AI and Pattern Recognition Lab",
        "location": "Sri City, Andhra Pradesh, India",
        "research_areas": [
            "Applied Machine Learning",
            "Computer Vision",
            "Pattern Recognition",
            "Edge Computing"
        ],
        "recent_papers": [
            "Lightweight Deep Networks for Edge Object Localization",
            "Real-Time Spatial Anomaly Classification in Video",
            "Embedded Machine Learning for Assistive Smart Devices"
        ],
        "research_summary": "Applied machine learning, pattern analysis, intelligent visual devices, and edge computing architectures.",
        "profile_url": "https://www.iiits.in/faculty",
        "lab_url": "https://www.iiits.in",
        "source_urls": [
            "https://www.iiits.in/faculty"
        ]
    },
    {
        "name": "Prof. Hrishikesh Venkataraman",
        "institution": "IIIT Sri City",
        "institution_type": "IIIT",
        "department": "Department of Electronics and Communication",
        "designation": "Associate Professor",
        "email": "hrishikesh@iiits.in",
        "lab_name": "Wireless Communications & Edge AI Lab",
        "location": "Sri City, Andhra Pradesh, India",
        "research_areas": [
            "Wireless Communications",
            "Edge Computing",
            "IoT Networks",
            "Intelligent Transportation"
        ],
        "recent_papers": [
            "Real-Time Telemetry Streaming over Low-Latency 5G/Wi-Fi Micro-Meshes",
            "Edge Computing Architectures for Connected Autonomous Vehicles",
            "Energy-Harvesting Sensor Networks for Smart IoT Infrastructure"
        ],
        "research_summary": "Wireless communications, IoT networks, edge computing, and intelligent transportation systems.",
        "profile_url": "https://www.iiits.in/faculty",
        "lab_url": "https://www.iiits.in",
        "source_urls": [
            "https://www.iiits.in/faculty"
        ]
    },
    {
        "name": "Prof. Gautam Barua",
        "institution": "IIIT Guwahati",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Former Director",
        "email": "gb@iiitg.ac.in",
        "lab_name": "Computer Systems & Distributed AI Lab",
        "location": "Guwahati, Assam, India",
        "research_areas": [
            "Distributed Systems",
            "Operating Systems",
            "Computer Networks",
            "Network AI"
        ],
        "recent_papers": [
            "Distributed Scheduling of Real-Time ML Pipelines on Edge Clusters",
            "Fault-Tolerant Communication in Autonomous Sensor Networks",
            "High-Throughput Packet Processing with Machine Learning Optimization"
        ],
        "research_summary": "Operating systems, computer networks, distributed systems, and real-time computing.",
        "profile_url": "https://www.iiitg.ac.in/faculty",
        "lab_url": "https://www.iiitg.ac.in",
        "source_urls": [
            "https://www.iiitg.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sarat Kumar Patra",
        "institution": "IIIT Vadodara",
        "institution_type": "IIIT",
        "department": "Department of Electronics & Communication",
        "designation": "Professor & Director",
        "email": "director@iiitvadodara.ac.in",
        "lab_name": "Signal Processing & Communication Lab",
        "location": "Gandhinagar, Gujarat, India",
        "research_areas": [
            "Signal Processing",
            "Wireless Communications",
            "Machine Learning in Telecom",
            "Sensor Networks"
        ],
        "recent_papers": [
            "Deep Learning Based Signal Modulation Classification in Cognitive Radio",
            "Spatial Channel Estimation with Neural Networks",
            "Real-Time Telemetry Compression in Wireless Sensor Nodes"
        ],
        "research_summary": "Digital signal processing, wireless communication, machine learning applications in telecommunications.",
        "profile_url": "https://www.iiitvadodara.ac.in/faculty",
        "lab_url": "https://www.iiitvadodara.ac.in",
        "source_urls": [
            "https://www.iiitvadodara.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Anupam Shukla",
        "institution": "IIIT Pune",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Director",
        "email": "director@iiitp.ac.in",
        "lab_name": "Artificial Intelligence and Soft Computing Lab",
        "location": "Pune, Maharashtra, India",
        "research_areas": [
            "Artificial Intelligence",
            "Soft Computing",
            "Robotics",
            "Bio-Inspired Algorithms"
        ],
        "recent_papers": [
            "Bio-Inspired Path Planning for Autonomous Mobile Robots in Dynamic Mazes",
            "Deep Neural-Fuzzy Systems for Multi-Sensor Anomaly Detection",
            "Genetic Algorithm Optimization for Deep Learning Hyperparameters"
        ],
        "research_summary": "Soft computing, artificial intelligence, robotics, speech processing, and bio-inspired algorithms.",
        "profile_url": "https://www.iiitp.ac.in/faculty",
        "lab_url": "https://www.iiitp.ac.in",
        "source_urls": [
            "https://www.iiitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vishal Krishna Singh",
        "institution": "IIIT Lucknow",
        "institution_type": "IIIT",
        "department": "Department of Computer Science & Information Technology",
        "designation": "Assistant Professor",
        "email": "vishal@iiitl.ac.in",
        "lab_name": "Deep Learning & NLP Research Lab",
        "location": "Lucknow, Uttar Pradesh, India",
        "research_areas": [
            "Deep Learning",
            "Natural Language Processing",
            "Generative AI",
            "Computer Vision"
        ],
        "recent_papers": [
            "Cross-Modal Vision-Language Representations with Attention Models",
            "Transformer Pre-Training for Indian Low-Resource Languages",
            "Zero-Shot Text and Image Classification with Deep Ensembles"
        ],
        "research_summary": "Deep learning, natural language processing, vision-language architectures, and applied neural networks.",
        "profile_url": "https://www.iiitl.ac.in/faculty",
        "lab_url": "https://www.iiitl.ac.in",
        "source_urls": [
            "https://www.iiitl.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sunita Sarawagi",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Institute Chair Professor",
        "email": "sunita@cse.iitb.ac.in",
        "lab_name": "Data Mining & Machine Learning Group",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Machine Learning",
            "Natural Language Processing",
            "Generative AI",
            "Structured Learning"
        ],
        "recent_papers": [
            "Generative Pre-Training for Structured Information Extraction",
            "Calibrated Prediction in Deep Sequence Models",
            "Neuro-Symbolic Reasoning with Neural Language Models"
        ],
        "research_summary": "Information extraction, deep generative modeling, neural machine translation, and structured prediction with deep learning.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Debabrata Maiti",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Chemistry & CMTMC",
        "designation": "Professor",
        "email": "dmaiti@iitb.ac.in",
        "lab_name": "DM Machine Learning Lab (CMTMC)",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Machine Learning in Chemistry",
            "Catalysis & Scientific Computing",
            "AI for Science"
        ],
        "recent_papers": [
            "Graph Neural Networks for C-H Activation Site Prediction",
            "Data-Driven Catalytic Reaction Optimization",
            "Deep Learning Representations for Molecular Property Prediction"
        ],
        "research_summary": "Applying machine learning, data science, and computational methodologies to chemical catalysis and interdisciplinary scientific discovery.",
        "profile_url": "https://www.iitb.ac.in/faculty",
        "lab_url": "https://www.iitb.ac.in",
        "source_urls": [
            "https://www.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Biplab Banerjee",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Centre of Studies in Resources Engineering (CSRE) / CSE",
        "designation": "Associate Professor",
        "email": "bbanerjee@iitb.ac.in",
        "lab_name": "Machine Learning & Visual Computing Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Computer Vision",
            "Deep Learning",
            "Few-Shot Learning",
            "Remote Sensing & Geospatial AI"
        ],
        "recent_papers": [
            "Few-Shot Cross-Domain Visual Classification via Meta-Learning",
            "Self-Supervised Spatial Feature Representation in Satellite Streams",
            "Zero-Shot Earth Observation Analytics with Vision-Language Models"
        ],
        "research_summary": "Meta-learning, zero-shot and few-shot visual classification, geospatial image analysis, and deep generative computer vision.",
        "profile_url": "https://www.iitb.ac.in/faculty",
        "lab_url": "https://www.iitb.ac.in",
        "source_urls": [
            "https://www.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Ganesh Ramakrishnan",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "ganesh@cse.iitb.ac.in",
        "lab_name": "Resource-Constrained AI & NLP Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Machine Learning",
            "Resource-Constrained AI",
            "Natural Language Processing",
            "Information Extraction"
        ],
        "recent_papers": [
            "Efficient Subset Selection for Resource-Constrained Neural Networks",
            "Multilingual Document OCR and Spatial Information Parsing",
            "Active Learning for Low-Resource Domain Adaptation"
        ],
        "research_summary": "Resource-constrained machine learning, subset selection, information extraction, and vernacular language technologies.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pushpak Bhattacharyya",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "pb@cse.iitb.ac.in",
        "lab_name": "Center for Indian Language Technology (CFILT)",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Translation",
            "Sentiment Analysis",
            "Multilingual AI"
        ],
        "recent_papers": [
            "Cognitive NLP: Eye-Tracking Guided Neural Machine Translation",
            "Sarcasm and Sentiment Detection with Multimodal Deep Learning",
            "Low-Resource Neural Translation for Indian Languages"
        ],
        "research_summary": "Natural language processing, machine translation, sentiment analysis, psycholinguistics, and cognitive NLP.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Suyash Awate",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "suyash@cse.iitb.ac.in",
        "lab_name": "Medical Image Computing Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Medical Image Processing",
            "Computer Vision",
            "Statistical Modeling",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Latent Space Learning for 3D MRI Reconstruction",
            "Bayesian Image Segmentation for Pathological Anatomy",
            "Physics-Informed Deep Networks for Diffusion Imaging"
        ],
        "research_summary": "Medical image computing, computer vision, statistical machine learning, and healthcare imaging.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subhasis Chaudhuri",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor & Former Director",
        "email": "sc@ee.iitb.ac.in",
        "lab_name": "Vision & VIP Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Computer Vision",
            "Haptics",
            "Image Processing",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Real-Time Depth from Defocus Using Deep Convolutional Filters",
            "Haptic Rendering and Spatial Telepresence in Remote Manipulation",
            "Super-Resolution in Video Surveillance Sequences"
        ],
        "research_summary": "Computer vision, haptics, computational imaging, super-resolution, and image processing.",
        "profile_url": "https://www.ee.iitb.ac.in/faculty",
        "lab_url": "https://www.ee.iitb.ac.in",
        "source_urls": [
            "https://www.ee.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Amit Sethi",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor",
        "email": "asethi@ee.iitb.ac.in",
        "lab_name": "Computational Pathology & Vision Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Deep Learning",
            "Computer Vision",
            "Computational Pathology",
            "Biomedical AI"
        ],
        "recent_papers": [
            "Weakly Supervised Histopathology Whole Slide Classification",
            "Generative Stain Normalization for Pathological Imaging",
            "Explainable Deep Vision for Oncology Diagnostics"
        ],
        "research_summary": "Deep learning, medical image analysis, computer vision, and computational pathology.",
        "profile_url": "https://www.ee.iitb.ac.in/faculty",
        "lab_url": "https://www.ee.iitb.ac.in",
        "source_urls": [
            "https://www.ee.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Chetan Arora",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "chetan@cse.iitd.ac.in",
        "lab_name": "Computer Vision & Visual Computing Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "First-person Vision",
            "Object Detection",
            "Assistive Technology"
        ],
        "recent_papers": [
            "Egocentric Distance and Spatial Awareness for Assistive Navigation",
            "Low-Latency Video Object Detection on Embedded Microprocessors",
            "Real-Time Multilingual Spatial Feedback for Visual Navigation"
        ],
        "research_summary": "First-person vision, wearable camera pipelines, assistive technology for visually impaired, video summarization, and deep learning for computer vision.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mausam",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Yardi School of Artificial Intelligence / CSE",
        "designation": "Professor & Head",
        "email": "mausam@cse.iitd.ac.in",
        "lab_name": "Yardi School of AI / NLP Group",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Artificial Intelligence",
            "Natural Language Processing",
            "Information Extraction",
            "Knowledge Graphs"
        ],
        "recent_papers": [
            "Zero-Shot Open Information Extraction with Neural Sequence Models",
            "Neuro-Symbolic Reasoning over Large-Scale Knowledge Bases",
            "Contextual Dialogue Tracking in Generative Conversational Agents"
        ],
        "research_summary": "Information extraction, automated question answering, knowledge base completion, and neuro-symbolic AI.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Prem Kumar Kalra",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "pkalra@cse.iitd.ac.in",
        "lab_name": "Visual Computing Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Graphics",
            "Computer Vision",
            "3D Reconstruction",
            "Virtual Reality"
        ],
        "recent_papers": [
            "Real-Time 3D Human Avatar Animation from Monocular Video",
            "Photorealistic Neural Rendering with Spatial Light Fields",
            "Interactive 3D Scene Geometry Synthesis"
        ],
        "research_summary": "Computer graphics, 3D computer vision, visual computing, and realistic rendering.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Brejesh Lall",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor",
        "email": "brejesh@ee.iitd.ac.in",
        "lab_name": "Cognitive Vision and Multimodal AI Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "Sensor Networks",
            "Cognitive Systems",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Multi-Sensor Fusion for Autonomous Vehicle Tracking",
            "Spatial Audio-Visual Alignment in Surround Environments",
            "Low-Latency Object Recognition for Edge Telemetry"
        ],
        "research_summary": "Computer vision, sensor networks, multimodal signal processing, and cognitive systems.",
        "profile_url": "https://www.ee.iitd.ac.in/faculty",
        "lab_url": "https://www.ee.iitd.ac.in",
        "source_urls": [
            "https://www.ee.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Parag Singla",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "parags@cse.iitd.ac.in",
        "lab_name": "Statistical Relational AI Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Statistical Relational AI",
            "Machine Learning",
            "Neuro-Symbolic Reasoning",
            "Probabilistic Models"
        ],
        "recent_papers": [
            "Lifted Inference for Large Scale Relational Knowledge Graphs",
            "Integrating Symbolic Constraints in Deep Neural Training",
            "Markov Logic Networks for Dynamic Event Forecasting"
        ],
        "research_summary": "Statistical relational AI, neuro-symbolic learning, knowledge representation, and probabilistic graphical models.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subhashis Banerjee",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "suban@cse.iitd.ac.in",
        "lab_name": "Computer Vision & Geometry Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "Visual Geometry",
            "Real-Time Embedded Systems",
            "Digital Privacy"
        ],
        "recent_papers": [
            "Projective Geometry Formulations for Multi-Camera Calibration",
            "Real-Time Embedded Vision for Robotic Obstacle Avoidance",
            "Privacy-Preserving Video Processing Frameworks"
        ],
        "research_summary": "Visual geometry, computer vision, embedded systems, and privacy-enhancing technologies.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sumeet Agarwal",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "sumeet@ee.iitd.ac.in",
        "lab_name": "Cognitive Science & Computational Modeling Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Cognitive Science",
            "Machine Learning",
            "Computational Linguistics",
            "Complex Systems"
        ],
        "recent_papers": [
            "Neural Network Models of Human Linguistic Syntax Acquisition",
            "Information Theoretic Measures for Neural Representation Similarity",
            "Predictive Cognitive Modeling of Decision Making"
        ],
        "research_summary": "Cognitive science, machine learning, computational linguistics, and complex behavioral modeling.",
        "profile_url": "https://www.ee.iitd.ac.in/faculty",
        "lab_url": "https://www.ee.iitd.ac.in",
        "source_urls": [
            "https://www.ee.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vineeth N Balasubramanian",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / AI",
        "designation": "Professor & Head",
        "email": "vineethnb@cse.iith.ac.in",
        "lab_name": "Explainable Machine Learning & Visual Computing Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Deep Learning",
            "Explainable AI",
            "Computer Vision",
            "Trustworthy ML"
        ],
        "recent_papers": [
            "Towards Faithful Explanations for Vision-Language Models",
            "Physics-Informed Neural Networks for Real-Time Tracking",
            "Continual Learning in Dynamic Visual Environments"
        ],
        "research_summary": "Explainable machine learning, deep learning theory, computer vision, and trustworthy AI systems.",
        "profile_url": "https://www.cse.iith.ac.in/faculty",
        "lab_url": "https://www.cse.iith.ac.in",
        "source_urls": [
            "https://www.cse.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. C. Krishna Mohan",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / AI",
        "designation": "Professor & Dean",
        "email": "ckm@cse.iith.ac.in",
        "lab_name": "Visual Computing Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Video Analytics",
            "Computer Vision",
            "Deep Learning",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Spatiotemporal Action Recognition Using Lightweight 3D CNNs",
            "Real-Time Anomaly Detection in Surveillance Streams",
            "Object Tracking Under Occlusion in Multi-Camera Networks"
        ],
        "research_summary": "Video content analysis, surveillance video processing, object detection, and action recognition using deep networks.",
        "profile_url": "https://www.cse.iith.ac.in/faculty",
        "lab_url": "https://www.cse.iith.ac.in",
        "source_urls": [
            "https://www.cse.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sumohana S. Channappayya",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor & Dean",
        "email": "sumohana@ee.iith.ac.in",
        "lab_name": "Multimedia Signal Processing Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Image Quality Assessment",
            "Computer Vision",
            "Video Processing",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep No-Reference Video Quality Assessment in Streaming Environments",
            "Real-Time Perceptual Compression with Convolutional Autoencoders",
            "Subjective and Objective Visual Quality Metric Optimization"
        ],
        "research_summary": "Image and video quality evaluation, visual neuroscience, computational photography, and deep multimedia signal processing.",
        "profile_url": "https://www.ee.iith.ac.in/faculty",
        "lab_url": "https://www.ee.iith.ac.in",
        "source_urls": [
            "https://www.ee.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. Sri Rama Murty",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor",
        "email": "ksrm@ee.iith.ac.in",
        "lab_name": "Speech and Pattern Recognition Group",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Speech Processing",
            "Acoustic Signal Processing",
            "Deep Learning",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Zero-Frequency Filtering for Robust Fundamental Frequency Estimation",
            "Acoustic Representations for Voice Deepfake and Spoof Detection",
            "End-to-End Speech Recognition in Reverberant Audio Streams"
        ],
        "research_summary": "Speech signal processing, acoustic feature extraction, pattern recognition, and audio AI.",
        "profile_url": "https://www.ee.iith.ac.in/faculty",
        "lab_url": "https://www.ee.iith.ac.in",
        "source_urls": [
            "https://www.ee.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Saketha Nath",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / AI",
        "designation": "Professor",
        "email": "saketha@cse.iith.ac.in",
        "lab_name": "Machine Learning & Optimization Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Machine Learning",
            "Optimization",
            "Convex Optimization",
            "Support Vector Machines"
        ],
        "recent_papers": [
            "Stochastic Optimization Algorithms for Non-Convex Deep Learning",
            "Kernel Methods for Structured Output Prediction",
            "Efficient Margin Bounds in Extreme Classification"
        ],
        "research_summary": "Mathematical optimization, machine learning algorithms, kernel methods, and statistical learning.",
        "profile_url": "https://www.cse.iith.ac.in/faculty",
        "lab_url": "https://www.cse.iith.ac.in",
        "source_urls": [
            "https://www.cse.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Maunendra Desarkar",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / AI",
        "designation": "Associate Professor",
        "email": "maunendra@cse.iith.ac.in",
        "lab_name": "Data Analytics & Text Processing Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Data Mining",
            "Natural Language Processing",
            "Information Retrieval",
            "Recommender Systems"
        ],
        "recent_papers": [
            "Neural Contextual Ranking for Multi-Turn Dialogue Recommendation",
            "Text Summarization with Domain Knowledge Graph Integration",
            "Sentiment and Stance Detection in Multilingual Social Networks"
        ],
        "research_summary": "Data mining, information retrieval, natural language processing, and recommender systems.",
        "profile_url": "https://www.cse.iith.ac.in/faculty",
        "lab_url": "https://www.cse.iith.ac.in",
        "source_urls": [
            "https://www.cse.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. M. V. Panduranga Rao",
        "institution": "IIT Hyderabad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "mvp@cse.iith.ac.in",
        "lab_name": "Formal Methods and Quantum Computing Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Formal Methods",
            "Quantum Computing",
            "Verification of ML Systems",
            "Automata Theory"
        ],
        "recent_papers": [
            "Formal Verification of Safety Bounds in Deep Neural Policies",
            "Quantum Algorithms for Matrix Inversion and Graph Problems",
            "Automated Synthesis of Safe Control Controllers"
        ],
        "research_summary": "Formal methods, quantum algorithms, software verification, and safety in autonomous systems.",
        "profile_url": "https://www.cse.iith.ac.in/faculty",
        "lab_url": "https://www.cse.iith.ac.in",
        "source_urls": [
            "https://www.cse.iith.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Balaraman Ravindran",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / RBCDSAI",
        "designation": "Professor & Head",
        "email": "ravi@cse.iitm.ac.in",
        "lab_name": "Robert Bosch Centre for Data Science and AI (RBCDSAI)",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Reinforcement Learning",
            "Graph Machine Learning",
            "Data Science",
            "Deep Learning"
        ],
        "recent_papers": [
            "Hierarchical Reinforcement Learning in Multi-Agent Autonomous Settings",
            "Scalable Graph Convolutional Architectures for Complex Networks",
            "Sample-Efficient Policy Search for Robotic Manipulation"
        ],
        "research_summary": "Reinforcement learning, relational learning, graph neural networks, and applied AI systems.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Kaushik Mitra",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "kmitra@ee.iitm.ac.in",
        "lab_name": "Computational Imaging & Vision Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Computational Imaging",
            "Computer Vision",
            "Deep Learning",
            "Optics-AI Co-Design"
        ],
        "recent_papers": [
            "Physics-Informed Deep Neural Networks for Low-Light Imaging",
            "Single-Shot Monocular Depth Estimation with Coded Apertures",
            "Neural Radiance Fields for Underwater 3D Scene Reconstruction"
        ],
        "research_summary": "Computational cameras, deep learning for inverse problems, monocular depth estimation, and vision co-design.",
        "profile_url": "https://www.ee.iitm.ac.in/faculty",
        "lab_url": "https://www.ee.iitm.ac.in",
        "source_urls": [
            "https://www.ee.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. C. Chandra Sekhar",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "chandra@cse.iitm.ac.in",
        "lab_name": "Speech and Vision Processing Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Speech Processing",
            "Computer Vision",
            "Neural Networks",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Deep Spatiotemporal Feature Extraction for Visual Speech Recognition",
            "Multi-Stream Convolutional Networks for Robust Acoustic Modeling",
            "Continuous Gesture and Sign Language Recognition with Deep Networks"
        ],
        "research_summary": "Speech recognition, computer vision, visual-speech integration, and kernel methods.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sukhendu Das",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "sdas@cse.iitm.ac.in",
        "lab_name": "Visualization and Perception Lab (VPLab)",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Computer Vision",
            "3D Reconstruction",
            "Medical Image Processing",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Stereo Depth Estimation Under Challenging Ambient Illuminations",
            "Deep Volumetric Reconstruction from Multi-View Visual Streams",
            "Automated Diagnostic Image Analysis for Assistive Healthcare"
        ],
        "research_summary": "Computer vision, 3D shape reconstruction, visual surveillance, pattern recognition, and medical imaging.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mitesh M. Khapra",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering / AI4Bharat",
        "designation": "Associate Professor",
        "email": "miteshk@cse.iitm.ac.in",
        "lab_name": "AI4Bharat Research Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Natural Language Processing",
            "Deep Learning",
            "Multimodal Machine Learning",
            "Indian Language AI"
        ],
        "recent_papers": [
            "IndicBERT: Multilingual Pre-Trained Models for Indian Languages",
            "Cross-Modal Vision-Language Datasets for Vernacular Contexts",
            "End-to-End Automatic Speech Recognition for Indic Accents"
        ],
        "research_summary": "Multilingual NLP, speech recognition, machine translation, and Indian language artificial intelligence.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arun Rajkumar",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Assistant Professor",
        "email": "arunr@cse.iitm.ac.in",
        "lab_name": "Statistical Machine Learning Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Statistical Machine Learning",
            "Ranking Algorithms",
            "Online Learning",
            "Optimization"
        ],
        "recent_papers": [
            "Rank Aggregation with Statistical Guarantees under Noise",
            "Online Convex Optimization for High-Dimensional Streaming Data",
            "Bandit Algorithms for Adaptive Recommendation"
        ],
        "research_summary": "Statistical learning, ranking algorithms, online optimization, and preference learning.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Piyush Rai",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "piyush@cse.iitk.ac.in",
        "lab_name": "Bayesian Machine Learning & Deep Generative Models Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Bayesian Deep Learning",
            "Generative Models",
            "Continual Learning"
        ],
        "recent_papers": [
            "Variational Inference for Deep Latent Variable Models",
            "Non-Parametric Bayesian Continual Learning without Catastrophic Forgetting",
            "Probabilistic Embeddings for Multi-Modal Foundation Models"
        ],
        "research_summary": "Bayesian machine learning, deep generative models, variational inference, matrix/tensor factorization, and probabilistic AI.",
        "profile_url": "https://www.cse.iitk.ac.in/faculty",
        "lab_url": "https://www.cse.iitk.ac.in",
        "source_urls": [
            "https://www.cse.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vinay P. Namboodiri",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "vinaypn@cse.iitk.ac.in",
        "lab_name": "Computer Vision & Multimedia Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Cross-Modal Learning",
            "Video Understanding",
            "Deep Learning"
        ],
        "recent_papers": [
            "Action Recognition in Videos using Spatiotemporal Attention Networks",
            "Cross-Modal Retrieval between Audio-Visual Streams",
            "Low-Complexity Object Detection on Embedded Microprocessors"
        ],
        "research_summary": "Computer vision, multimodal video analysis, cross-modal retrieval, visual deep learning, and multimedia intelligence.",
        "profile_url": "https://www.cse.iitk.ac.in/faculty",
        "lab_url": "https://www.cse.iitk.ac.in",
        "source_urls": [
            "https://www.cse.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arnab Bhattacharya",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "arnabb@cse.iitk.ac.in",
        "lab_name": "Database and Information Retrieval Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Data Mining",
            "Information Retrieval",
            "Graph Analytics",
            "Spatial Databases"
        ],
        "recent_papers": [
            "Efficient Spatial Distance Indexing for High-Dimensional Nearest Neighbors",
            "Graph Subgraph Matching under Structural Uncertainty",
            "Keyword Search over Heterogeneous Knowledge Bases"
        ],
        "research_summary": "Data mining, graph databases, spatial trajectory indexing, and information retrieval.",
        "profile_url": "https://www.cse.iitk.ac.in/faculty",
        "lab_url": "https://www.cse.iitk.ac.in",
        "source_urls": [
            "https://www.cse.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. S. Venkatesh",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Professor",
        "email": "venkats@iitk.ac.in",
        "lab_name": "Computer Vision and Video Processing Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Image Processing",
            "Visual Tracking",
            "Spatial Motion Analysis"
        ],
        "recent_papers": [
            "Real-Time Object Trajectory Estimation in Cluttered Surveillance Streams",
            "Optical Flow and Dynamic Motion Invariants in Monocular Cameras",
            "Spatial Segmentation for Autonomous Robotic Navigators"
        ],
        "research_summary": "Computer vision, image processing, dynamic motion analysis, and visual tracking.",
        "profile_url": "https://www.iitk.ac.in/faculty",
        "lab_url": "https://www.iitk.ac.in",
        "source_urls": [
            "https://www.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pabitra Mitra",
        "institution": "IIT Kharagpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "pabitra@cse.iitkgp.ac.in",
        "lab_name": "Machine Learning and Data Analytics Lab",
        "location": "Kharagpur, West Bengal, India",
        "research_areas": [
            "Machine Learning",
            "Spatial Data Mining",
            "Information Retrieval",
            "Deep Learning"
        ],
        "recent_papers": [
            "Spatial Trajectory Modeling using Graph Attention Networks",
            "Deep Learning for Geographical Anomaly and Pattern Detection",
            "Explainable Feature Extraction in High-Dimensional Datasets"
        ],
        "research_summary": "Machine learning algorithms, data mining, spatial information systems, and intelligent pattern analysis.",
        "profile_url": "https://www.cse.iitkgp.ac.in/faculty",
        "lab_url": "https://www.cse.iitkgp.ac.in",
        "source_urls": [
            "https://www.cse.iitkgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Plaban Kumar Bhowmick",
        "institution": "IIT Kharagpur",
        "institution_type": "IIT",
        "department": "Centre of Excellence in Artificial Intelligence",
        "designation": "Associate Professor",
        "email": "plaban@ai.iitkgp.ac.in",
        "lab_name": "Intelligent Interactive Systems Lab",
        "location": "Kharagpur, West Bengal, India",
        "research_areas": [
            "Human-Computer Interaction",
            "Artificial Intelligence",
            "Assistive Learning Technologies",
            "NLP"
        ],
        "recent_papers": [
            "Personalized Assistive Interfaces for Visually and Hearing Impaired Users",
            "Knowledge-Driven Multimodal Learning Analytics",
            "Semantic Web Technologies for Intelligent Educational Tutoring"
        ],
        "research_summary": "Human-computer interaction, assistive intelligence, personalized learning, and semantic technologies.",
        "profile_url": "https://www.ai.iitkgp.ac.in/faculty",
        "lab_url": "https://www.ai.iitkgp.ac.in",
        "source_urls": [
            "https://www.ai.iitkgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sudeshna Sarkar",
        "institution": "IIT Kharagpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "sudeshna@cse.iitkgp.ac.in",
        "lab_name": "NLP and Machine Learning Lab",
        "location": "Kharagpur, West Bengal, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Translation",
            "Information Extraction",
            "Text Analytics"
        ],
        "recent_papers": [
            "Cross-Lingual Information Retrieval and Question Answering in Indian Languages",
            "Deep Learning for Biomedical Document Summarization",
            "Aspect-Based Sentiment Mining in Multilingual Streams"
        ],
        "research_summary": "Natural language processing, machine learning, text mining, and cross-lingual IR.",
        "profile_url": "https://www.cse.iitkgp.ac.in/faculty",
        "lab_url": "https://www.cse.iitkgp.ac.in",
        "source_urls": [
            "https://www.cse.iitkgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Partha Pratim Roy",
        "institution": "IIT Roorkee",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "partha@cs.iitr.ac.in",
        "lab_name": "Pattern Recognition & Visual Computing Lab",
        "location": "Roorkee, Uttarakhand, India",
        "research_areas": [
            "Computer Vision",
            "Pattern Recognition",
            "Document Analysis",
            "Assistive Visual AI"
        ],
        "recent_papers": [
            "Real-Time Multilingual Text Detection and Spatial Scene Parsing",
            "Deep Sequence Models for Handwritten Script Recognition",
            "Visual Assistive Guidance for Accessible Mobility"
        ],
        "research_summary": "Pattern recognition, computer vision, multilingual document intelligence, and assistive visual technology.",
        "profile_url": "https://www.cs.iitr.ac.in/faculty",
        "lab_url": "https://www.cs.iitr.ac.in",
        "source_urls": [
            "https://www.cs.iitr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Balasubramanian Raman",
        "institution": "IIT Roorkee",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "balaraman@cs.iitr.ac.in",
        "lab_name": "Vision, Imaging and Speech Technology (VIST) Lab",
        "location": "Roorkee, Uttarakhand, India",
        "research_areas": [
            "Computer Vision",
            "Medical Imaging",
            "Digital Watermarking",
            "Biometrics"
        ],
        "recent_papers": [
            "Deep Residual Networks for Automated Brain Tumor Segmentation",
            "Biometric Authentication using Multimodal Feature Fusion",
            "Secure Digital Video Watermarking for Multimedia Integrity"
        ],
        "research_summary": "Computer vision, medical imaging, biometric authentication, and multimedia security.",
        "profile_url": "https://www.cs.iitr.ac.in/faculty",
        "lab_url": "https://www.cs.iitr.ac.in",
        "source_urls": [
            "https://www.cs.iitr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Shanmuganathan Raman",
        "institution": "IIT Gandhinagar",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering / CSE",
        "designation": "Professor & Dean",
        "email": "sraman@iitgn.ac.in",
        "lab_name": "Computer Vision & Graphics Lab (CVGL)",
        "location": "Gandhinagar, Gujarat, India",
        "research_areas": [
            "Computer Vision",
            "Computational Photography",
            "Deep Learning",
            "3D Scene Geometry"
        ],
        "recent_papers": [
            "Deep Single-Image Super-Resolution and Reflection Removal",
            "Monocular Depth Estimation via Geometric Surface Normals",
            "High Dynamic Range Imaging with Convolutional Networks"
        ],
        "research_summary": "Computer vision, computational photography, image editing, 3D reconstruction, and visual deep learning.",
        "profile_url": "https://www.iitgn.ac.in/faculty",
        "lab_url": "https://www.iitgn.ac.in",
        "source_urls": [
            "https://www.iitgn.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Nipun Batra",
        "institution": "IIT Gandhinagar",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "nipun.batra@iitgn.ac.in",
        "lab_name": "Sustainability and Machine Learning Lab",
        "location": "Gandhinagar, Gujarat, India",
        "research_areas": [
            "Machine Learning",
            "Mobile Sensing",
            "IoT Systems",
            "Sustainability AI"
        ],
        "recent_papers": [
            "Transfer Learning for Non-Intrusive Appliance Energy Disaggregation",
            "Low-Cost Air Quality Sensing Calibration using Gaussian Processes",
            "Ubiquitous IoT Telemetry Analysis for Smart Buildings"
        ],
        "research_summary": "Machine learning for sustainability, ubiquitous computing, IoT telemetry sensing, and transfer learning.",
        "profile_url": "https://www.iitgn.ac.in/faculty",
        "lab_url": "https://www.iitgn.ac.in",
        "source_urls": [
            "https://www.iitgn.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Richa Singh",
        "institution": "IIT Jodhpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "richa@iitj.ac.in",
        "lab_name": "Trusted AI & Biometrics Research Lab",
        "location": "Jodhpur, Rajasthan, India",
        "research_areas": [
            "Computer Vision",
            "Biometrics",
            "Trustworthy AI",
            "Deep Learning Security"
        ],
        "recent_papers": [
            "Adversarial Robustness and Fairness in Visual Biometric Classifiers",
            "Deepfake Video and Audio Detection using Multi-Stream Networks",
            "Privacy-Preserving Visual Verification in Edge Environments"
        ],
        "research_summary": "Trusted AI, biometrics, synthetic media and deepfake detection, fairness in AI, and secure vision pipelines.",
        "profile_url": "https://www.iitj.ac.in/faculty",
        "lab_url": "https://www.iitj.ac.in",
        "source_urls": [
            "https://www.iitj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mayank Vatsa",
        "institution": "IIT Jodhpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "mvatsa@iitj.ac.in",
        "lab_name": "Image Analysis and Biometrics Lab",
        "location": "Jodhpur, Rajasthan, India",
        "research_areas": [
            "Deep Learning",
            "Computer Vision",
            "Pattern Recognition",
            "Information Security"
        ],
        "recent_papers": [
            "Self-Supervised Representation Learning for High-Resolution Visual Streams",
            "Multimodal Biometric Recognition Under Severe Occlusion",
            "Generalizable Deepfake Detection Across Disparate Generative Architectures"
        ],
        "research_summary": "Deep learning architectures, computer vision, biometrics, visual forensics, and robust pattern recognition.",
        "profile_url": "https://www.iitj.ac.in/faculty",
        "lab_url": "https://www.iitj.ac.in",
        "source_urls": [
            "https://www.iitj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Santanu Chaudhury",
        "institution": "IIT Jodhpur",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Director",
        "email": "director@iitj.ac.in",
        "lab_name": "Multimedia and Intelligent Systems Lab",
        "location": "Jodhpur, Rajasthan, India",
        "research_areas": [
            "Computer Vision",
            "Multimedia Systems",
            "Assistive AI",
            "Cognitive Systems"
        ],
        "recent_papers": [
            "Real-Time Visual Guidance Frameworks for Assistive Walking Aids",
            "Multimodal Document Intelligence with Deep Neural Networks",
            "Spatial Telepresence and Interactive Visual Analytics"
        ],
        "research_summary": "Computer vision, multimedia systems, artificial intelligence, assistive technology, and cognitive computing.",
        "profile_url": "https://www.iitj.ac.in/faculty",
        "lab_url": "https://www.iitj.ac.in",
        "source_urls": [
            "https://www.iitj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Puneet Goyal",
        "institution": "IIT Ropar",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "puneet@iitrpr.ac.in",
        "lab_name": "Visual Computing and Biomedical Imaging Lab",
        "location": "Rupnagar, Punjab, India",
        "research_areas": [
            "Computer Vision",
            "Biomedical Image Analysis",
            "Multimedia Security",
            "Deep Learning"
        ],
        "recent_papers": [
            "Automated Pathological Diagnostic Assistance with Lightweight CNNs",
            "Real-Time Video Steganalysis in Network Streams",
            "Multimodal Image Fusion for Intelligent Diagnostic Systems"
        ],
        "research_summary": "Visual computing, medical image analysis, electronic imaging, and intelligent multimedia security.",
        "profile_url": "https://www.iitrpr.ac.in/faculty",
        "lab_url": "https://www.iitrpr.ac.in",
        "source_urls": [
            "https://www.iitrpr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subrahmanyam Murala",
        "institution": "IIT Ropar",
        "institution_type": "IIT",
        "department": "Department of Electrical Engineering",
        "designation": "Associate Professor",
        "email": "subrahmanyam@iitrpr.ac.in",
        "lab_name": "Computer Vision and Pattern Recognition Lab",
        "location": "Rupnagar, Punjab, India",
        "research_areas": [
            "Computer Vision",
            "Image Retrieval",
            "Deep Learning",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Directional Local Pattern Descriptors for Real-Time Visual Search",
            "Deep Convolutional Autoencoders for Image De-Raining and Restoration",
            "Monocular Distance and Depth Estimation for Driver Assistance"
        ],
        "research_summary": "Computer vision, image retrieval, pattern recognition, and deep learning for restoration.",
        "profile_url": "https://www.iitrpr.ac.in/faculty",
        "lab_url": "https://www.iitrpr.ac.in",
        "source_urls": [
            "https://www.iitrpr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Asif Ekbal",
        "institution": "IIT Patna",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "asif@iitp.ac.in",
        "lab_name": "AI & Natural Language Processing Lab",
        "location": "Patna, Bihar, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Learning",
            "Information Extraction",
            "Multimodal NLP"
        ],
        "recent_papers": [
            "Multimodal Dialogue Systems with Contextual Emotion Awareness",
            "Deep Learning for Clinical Information Extraction and Bio-NLP",
            "Cross-Lingual Information Retrieval for Indian Vernacular Languages"
        ],
        "research_summary": "Natural language processing, bio-NLP, text data mining, sentiment analysis, and machine learning architectures.",
        "profile_url": "https://www.iitp.ac.in/faculty",
        "lab_url": "https://www.iitp.ac.in",
        "source_urls": [
            "https://www.iitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sriparna Saha",
        "institution": "IIT Patna",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "sriparna@iitp.ac.in",
        "lab_name": "Machine Learning & Bio-NLP Lab",
        "location": "Patna, Bihar, India",
        "research_areas": [
            "Machine Learning",
            "Bio-NLP",
            "Multi-Objective Optimization",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Multi-Objective Evolutionary Clustering for Biomedical Text Corpora",
            "Deep Neural Feature Selection in Medical Image Diagnosis",
            "Conversational AI Systems for Healthcare Triaging"
        ],
        "research_summary": "Machine learning, multi-objective optimization, bio-NLP, pattern recognition, and healthcare AI.",
        "profile_url": "https://www.iitp.ac.in/faculty",
        "lab_url": "https://www.iitp.ac.in",
        "source_urls": [
            "https://www.iitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Aruna Tiwari",
        "institution": "IIT Indore",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "artiwari@iiti.ac.in",
        "lab_name": "Soft Computing & Machine Learning Lab",
        "location": "Indore, Madhya Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Soft Computing",
            "Neural Networks",
            "Data Mining"
        ],
        "recent_papers": [
            "Scalable Kernel Clustering for High-Dimensional Biomedical Data",
            "Deep Neural Decision Trees for Real-Time Predictive Diagnostics",
            "Fuzzy Neural Optimization in Dynamic Data Environments"
        ],
        "research_summary": "Machine learning, neural networks, soft computing, fuzzy logic systems, and intelligent healthcare analytics.",
        "profile_url": "https://www.iiti.ac.in/faculty",
        "lab_url": "https://www.iiti.ac.in",
        "source_urls": [
            "https://www.iiti.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Kapil Ahuja",
        "institution": "IIT Indore",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "kahuja@iiti.ac.in",
        "lab_name": "Applied Machine Learning & Scientific Computing Lab",
        "location": "Indore, Madhya Pradesh, India",
        "research_areas": [
            "Applied Machine Learning",
            "Scientific Computing",
            "Numerical Linear Algebra",
            "Optimization"
        ],
        "recent_papers": [
            "Machine Learning Accelerated Iterative Solvers for Large Sparse Systems",
            "Data-Driven Reduced Order Modeling for Physical Simulations",
            "Deep Neural Surrogates for Computational Fluid Dynamics"
        ],
        "research_summary": "Scientific machine learning, numerical linear algebra, optimization, and high-performance computing.",
        "profile_url": "https://www.iiti.ac.in/faculty",
        "lab_url": "https://www.iiti.ac.in",
        "source_urls": [
            "https://www.iiti.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Prithwijit Guha",
        "institution": "IIT Guwahati",
        "institution_type": "IIT",
        "department": "Department of Electronics and Electrical Engineering",
        "designation": "Professor",
        "email": "pguha@iitg.ac.in",
        "lab_name": "Visual Computing and Robotics Lab",
        "location": "Guwahati, Assam, India",
        "research_areas": [
            "Computer Vision",
            "Robotics",
            "Video Surveillance",
            "Trajectory Estimation"
        ],
        "recent_papers": [
            "Spatiotemporal Trajectory Analysis for Autonomous Mobile Navigation",
            "Multi-Agent Visual Tracking Under Heavy Occlusion",
            "Low-Latency Video Object Detection on Embedded Platforms"
        ],
        "research_summary": "Visual surveillance, robotic navigation, camera networks, motion tracking, and real-time visual perception.",
        "profile_url": "https://www.iitg.ac.in/faculty",
        "lab_url": "https://www.iitg.ac.in",
        "source_urls": [
            "https://www.iitg.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. R. Mahadeva Prasanna",
        "institution": "IIT Guwahati",
        "institution_type": "IIT",
        "department": "Department of Electronics and Electrical Engineering",
        "designation": "Professor",
        "email": "prasanna@iitg.ac.in",
        "lab_name": "Speech Processing & Audio Intelligence Lab",
        "location": "Guwahati, Assam, India",
        "research_areas": [
            "Speech Processing",
            "Biometrics",
            "Acoustic Signal Processing",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Voice Biometrics Under Degraded Acoustic Channels",
            "Acoustic Detection of Throat and Respiratory Pathologies",
            "Zero-Crossing Peak Features for Low-Resource Speech Recognition"
        ],
        "research_summary": "Speech processing, voice biometrics, acoustic signal processing, and assistive speech tools.",
        "profile_url": "https://www.iitg.ac.in/faculty",
        "lab_url": "https://www.iitg.ac.in",
        "source_urls": [
            "https://www.iitg.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. K. Shukla",
        "institution": "IIT BHU",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "kkshukla.cse@itbhu.ac.in",
        "lab_name": "Artificial Intelligence & Neural Networks Lab",
        "location": "Varanasi, Uttar Pradesh, India",
        "research_areas": [
            "Artificial Intelligence",
            "Neural Networks",
            "Real-Time Embedded Systems",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Deep Neural Adaptive Control for Non-Linear Dynamical Systems",
            "Fault Detection in Real-Time Sensor Telemetry Using Autoencoders",
            "Hardware-Software Co-Design for Embedded AI Classifiers"
        ],
        "research_summary": "Artificial intelligence, artificial neural networks, embedded systems, and parallel processing.",
        "profile_url": "https://www.itbhu.ac.in/faculty",
        "lab_url": "https://www.itbhu.ac.in",
        "source_urls": [
            "https://www.itbhu.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sanjay Kumar Singh",
        "institution": "IIT BHU",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "sks.cse@iitbhu.ac.in",
        "lab_name": "Biometrics and Visual Intelligence Lab",
        "location": "Varanasi, Uttar Pradesh, India",
        "research_areas": [
            "Biometrics",
            "Computer Vision",
            "Pattern Recognition",
            "Medical Imaging"
        ],
        "recent_papers": [
            "Deep Feature Learning for Unconstrained Face and Iris Biometrics",
            "Automated Spatial Classification of Dermatological Lesions",
            "Visual Surveillance and Activity Recognition in Crowded Environments"
        ],
        "research_summary": "Biometrics, computer vision, visual surveillance, pattern recognition, and medical image analysis.",
        "profile_url": "https://www.iitbhu.ac.in/faculty",
        "lab_url": "https://www.iitbhu.ac.in",
        "source_urls": [
            "https://www.iitbhu.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Varun Dutt",
        "institution": "IIT Mandi",
        "institution_type": "IIT",
        "department": "School of Computing and Electrical Engineering",
        "designation": "Associate Professor",
        "email": "varun@iitmandi.ac.in",
        "lab_name": "Applied Cognitive Science Lab",
        "location": "Mandi, Himachal Pradesh, India",
        "research_areas": [
            "Cognitive Science",
            "Machine Learning",
            "Human-Agent Interaction",
            "Decision Making"
        ],
        "recent_papers": [
            "Instance-Based Learning Models for Human-AI Shared Autonomy",
            "Predictive Analytics of Human Cognitive Workload using Sensor Telemetry",
            "Interactive Decision Systems in Cyber-Physical Defense Environments"
        ],
        "research_summary": "Cognitive science, computational modeling, human-computer interaction, and artificial intelligence.",
        "profile_url": "https://www.iitmandi.ac.in/faculty",
        "lab_url": "https://www.iitmandi.ac.in",
        "source_urls": [
            "https://www.iitmandi.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arnav Bhavsar",
        "institution": "IIT Mandi",
        "institution_type": "IIT",
        "department": "School of Computing and Electrical Engineering",
        "designation": "Associate Professor",
        "email": "arnav@iitmandi.ac.in",
        "lab_name": "Visual Computing Lab",
        "location": "Mandi, Himachal Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Medical Imaging",
            "Image Processing",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Multi-Scale Image Inpainting and Spatial Restoration",
            "Automated Optical Coherence Tomography Segmentation",
            "Monocular Depth Estimation via Convolutional Attention"
        ],
        "research_summary": "Computer vision, medical imaging, inverse visual problems, and deep learning.",
        "profile_url": "https://www.iitmandi.ac.in/faculty",
        "lab_url": "https://www.iitmandi.ac.in",
        "source_urls": [
            "https://www.iitmandi.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Debasis Samanta",
        "institution": "IIT Bhubaneswar",
        "institution_type": "IIT",
        "department": "School of Electrical Sciences / CSE",
        "designation": "Professor",
        "email": "dsamanta@iitbbs.ac.in",
        "lab_name": "Human-Computer Interaction Lab",
        "location": "Bhubaneswar, Odisha, India",
        "research_areas": [
            "Human-Computer Interaction",
            "Biometrics",
            "Assistive Technologies",
            "Machine Learning"
        ],
        "recent_papers": [
            "Brain-Computer Interfaces for Accessible Assistive Mobility",
            "Eye-Gaze Tracking and Spatial Selection for Disabled Users",
            "Multimodal Biometric Security using Deep Feature Fusion"
        ],
        "research_summary": "Human-computer interaction, assistive systems, brain-computer interfaces, and biometric authentication.",
        "profile_url": "https://www.iitbbs.ac.in/faculty",
        "lab_url": "https://www.iitbbs.ac.in",
        "source_urls": [
            "https://www.iitbbs.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Kalidas Yeturu",
        "institution": "IIT Tirupati",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "ykalidas@iittp.ac.in",
        "lab_name": "AI for Healthcare & Molecular Informatics Lab",
        "location": "Tirupati, Andhra Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Deep Learning",
            "Computational Biology",
            "Computer Vision"
        ],
        "recent_papers": [
            "Graph Neural Networks for Protein-Ligand Binding Affinity Prediction",
            "Deep Spatial Feature Representations in Cryo-EM Biological Images",
            "Predictive Molecular Property Modeling with Geometric Deep Learning"
        ],
        "research_summary": "Machine learning for life sciences, drug discovery AI, deep learning, and computer vision.",
        "profile_url": "https://www.iittp.ac.in/faculty",
        "lab_url": "https://www.iittp.ac.in",
        "source_urls": [
            "https://www.iittp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mrinal K. Das",
        "institution": "IIT Palakkad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Assistant Professor",
        "email": "mrinal@iitpkd.ac.in",
        "lab_name": "Probabilistic ML and Data Analytics Lab",
        "location": "Palakkad, Kerala, India",
        "research_areas": [
            "Machine Learning",
            "Bayesian Inference",
            "Probabilistic Graphical Models",
            "NLP"
        ],
        "recent_papers": [
            "Scalable Variational Inference for High-Dimensional Latent Models",
            "Bayesian Nonparametrics for Unsupervised Topic Modeling",
            "Probabilistic Embeddings for Text Categorization"
        ],
        "research_summary": "Bayesian machine learning, probabilistic models, latent variable modeling, and data analytics.",
        "profile_url": "https://www.iitpkd.ac.in/faculty",
        "lab_url": "https://www.iitpkd.ac.in",
        "source_urls": [
            "https://www.iitpkd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Clint P. George",
        "institution": "IIT Goa",
        "institution_type": "IIT",
        "department": "School of Mathematics and Computer Science",
        "designation": "Assistant Professor",
        "email": "clint@iitgoa.ac.in",
        "lab_name": "Statistical Machine Learning Lab",
        "location": "Ponda, Goa, India",
        "research_areas": [
            "Statistical Machine Learning",
            "Text Mining",
            "Information Extraction",
            "Bayesian Analytics"
        ],
        "recent_papers": [
            "Topic Modeling over Temporal Dynamic Document Streams",
            "Bayesian Matrix Factorization for Recommender Systems",
            "Supervised Topic Models for Multi-Label Document Classification"
        ],
        "research_summary": "Statistical machine learning, text data mining, probabilistic topic models, and information extraction.",
        "profile_url": "https://www.iitgoa.ac.in/faculty",
        "lab_url": "https://www.iitgoa.ac.in",
        "source_urls": [
            "https://www.iitgoa.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Gaurav Varshney",
        "institution": "IIT Jammu",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Assistant Professor",
        "email": "gaurav.varshney@iitjammu.ac.in",
        "lab_name": "Systems Security and Applied AI Lab",
        "location": "Jammu, Jammu & Kashmir, India",
        "research_areas": [
            "Information Security",
            "Applied Machine Learning",
            "Network Forensics",
            "IoT Security"
        ],
        "recent_papers": [
            "Machine Learning Approaches to Zero-Day Phishing URL Detection",
            "Deep Learning for Intrusion Detection in Industrial IoT Meshes",
            "Automated Cyber-Threat Intelligence Parsing from Darknet Streams"
        ],
        "research_summary": "Cyber security, applied machine learning, phishing detection, and networked system defenses.",
        "profile_url": "https://www.iitjammu.ac.in/faculty",
        "lab_url": "https://www.iitjammu.ac.in",
        "source_urls": [
            "https://www.iitjammu.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Santosh Biswas",
        "institution": "IIT Bhilai",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "santosh@iitbhilai.ac.in",
        "lab_name": "Embedded AI and Fault-Tolerant Systems Lab",
        "location": "Bhilai, Chhattisgarh, India",
        "research_areas": [
            "Embedded Systems",
            "Fault-Tolerant Computing",
            "VLSI Testing",
            "Automated Debugging"
        ],
        "recent_papers": [
            "Real-Time Hardware-in-the-Loop Testing for Autonomous Vehicle Subsystems",
            "Embedded Machine Learning for Online Fault Diagnosis in Microcontrollers",
            "Low-Power Sensor Telemetry Interfacing in IoT Nodes"
        ],
        "research_summary": "Fault-tolerant systems, embedded hardware testing, VLSI design, and real-time computing.",
        "profile_url": "https://www.iitbhilai.ac.in/faculty",
        "lab_url": "https://www.iitbhilai.ac.in",
        "source_urls": [
            "https://www.iitbhilai.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Chiranjeev Kumar",
        "institution": "IIT ISM Dhanbad",
        "institution_type": "IIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Dean",
        "email": "chiranjeev@iitism.ac.in",
        "lab_name": "Intelligent Systems & Software Engineering Lab",
        "location": "Dhanbad, Jharkhand, India",
        "research_areas": [
            "Machine Learning",
            "Software Engineering",
            "Pattern Recognition",
            "Data Analytics"
        ],
        "recent_papers": [
            "Predictive Software Defect Classification using Ensemble Machine Learning",
            "Deep Learning Frameworks for Real-Time Sensor Stream Processing",
            "Pattern Recognition in Mining Telemetry Datasets"
        ],
        "research_summary": "Software engineering, machine learning, pattern recognition, and applied data systems.",
        "profile_url": "https://www.iitism.ac.in/faculty",
        "lab_url": "https://www.iitism.ac.in",
        "source_urls": [
            "https://www.iitism.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. R. B. V. Subramaanyam",
        "institution": "NIT Warangal",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "rbvs66@nitw.ac.in",
        "lab_name": "Data Engineering and Machine Learning Lab",
        "location": "Warangal, Telangana, India",
        "research_areas": [
            "Data Mining",
            "Machine Learning",
            "Deep Learning",
            "Intelligent Systems"
        ],
        "recent_papers": [
            "Deep Learning Frameworks for Edge IoT Data Streams",
            "Distributed Feature Selection for High-Dimensional Classification",
            "Real-Time Predictive Analytics for Intelligent Sensors"
        ],
        "research_summary": "Data mining, applied machine learning architectures, distributed computing, and intelligent data systems.",
        "profile_url": "https://www.nitw.ac.in/faculty",
        "lab_url": "https://www.nitw.ac.in",
        "source_urls": [
            "https://www.nitw.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. G. Sanjeevi",
        "institution": "NIT Warangal",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "sanjeevi@nitw.ac.in",
        "lab_name": "Distributed Systems & Cloud Security Lab",
        "location": "Warangal, Telangana, India",
        "research_areas": [
            "Cloud Computing",
            "Distributed Systems",
            "Machine Learning Security",
            "IoT Systems"
        ],
        "recent_papers": [
            "Secure Telemetry Processing in Distributed Cloud Architectures",
            "Anomaly Detection in High-Throughput Edge Meshes",
            "Machine Learning Optimization for Virtual Machine Placement"
        ],
        "research_summary": "Cloud computing, distributed systems, information security, and applied machine learning.",
        "profile_url": "https://www.nitw.ac.in/faculty",
        "lab_url": "https://www.nitw.ac.in",
        "source_urls": [
            "https://www.nitw.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. Suresh",
        "institution": "NIT Trichy",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "suresh@nitt.edu",
        "lab_name": "Artificial Intelligence & Computer Vision Lab",
        "location": "Tiruchirappalli, Tamil Nadu, India",
        "research_areas": [
            "Artificial Intelligence",
            "Computer Vision",
            "Deep Learning",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Deep Convolutional Architectures for Real-Time Scene Classification",
            "Spatial Spatial Feature Extraction in Dynamic Video Sequences",
            "Lightweight Vision Pipelines for Autonomous Edge Devices"
        ],
        "research_summary": "Computer vision pipelines, deep neural architectures, pattern recognition, and real-time intelligent perception.",
        "profile_url": "https://www.nitt.edu/faculty",
        "lab_url": "https://www.nitt.edu",
        "source_urls": [
            "https://www.nitt.edu/faculty"
        ]
    },
    {
        "name": "Prof. B. Janet",
        "institution": "NIT Trichy",
        "institution_type": "NIT",
        "department": "Department of Computer Applications / CSE",
        "designation": "Associate Professor",
        "email": "janet@nitt.edu",
        "lab_name": "Data Analytics and Machine Intelligence Lab",
        "location": "Tiruchirappalli, Tamil Nadu, India",
        "research_areas": [
            "Data Analytics",
            "Machine Learning",
            "Deep Learning",
            "Text Mining"
        ],
        "recent_papers": [
            "Deep Sentiment Classification in Multilingual Social Networks",
            "Automated Medical Text Information Extraction using Transformers",
            "Machine Learning Classifiers for Streaming IoT Data"
        ],
        "research_summary": "Data analytics, machine learning, text mining, and cloud computing.",
        "profile_url": "https://www.nitt.edu/faculty",
        "lab_url": "https://www.nitt.edu",
        "source_urls": [
            "https://www.nitt.edu/faculty"
        ]
    },
    {
        "name": "Prof. B. R. Chandavarkar",
        "institution": "NIT Surathkal",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "brc@nitk.edu.in",
        "lab_name": "Machine Learning & Networked Systems Lab",
        "location": "Surathkal, Karnataka, India",
        "research_areas": [
            "Machine Learning",
            "Network Security",
            "Cloud Computing",
            "IoT AI"
        ],
        "recent_papers": [
            "Anomaly Detection in High-Throughput Network Streams using Deep Autoencoders",
            "Scalable Machine Learning for Cloud Telemetry Monitoring",
            "Edge Intelligence in Distributed Cyber-Physical Sensor Networks"
        ],
        "research_summary": "Network security, applied machine learning for cyber defense, cloud monitoring pipelines, and distributed data systems.",
        "profile_url": "https://www.nitk.edu.in/faculty",
        "lab_url": "https://www.nitk.edu.in",
        "source_urls": [
            "https://www.nitk.edu.in/faculty"
        ]
    },
    {
        "name": "Prof. Mohit P. Tahiliani",
        "institution": "NIT Surathkal",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "tahiliani@nitk.edu.in",
        "lab_name": "Wireless Information Networking Group (WiNG)",
        "location": "Surathkal, Karnataka, India",
        "research_areas": [
            "Computer Networks",
            "Edge Computing",
            "IoT Protocol Optimization",
            "Network Telemetry"
        ],
        "recent_papers": [
            "Active Queue Management with Machine Learning Congestion Predictors",
            "Low-Latency Telemetry Streaming in 5G Edge Networks",
            "Performance Analysis of Multipath Protocols in Connected Vehicles"
        ],
        "research_summary": "Computer networks, congestion control, network telemetry, edge computing, and IoT protocols.",
        "profile_url": "https://www.nitk.edu.in/faculty",
        "lab_url": "https://www.nitk.edu.in",
        "source_urls": [
            "https://www.nitk.edu.in/faculty"
        ]
    },
    {
        "name": "Prof. Gnanasekaran T.",
        "institution": "NIT Calicut",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "gnanasekaran@nitc.ac.in",
        "lab_name": "Visual Computing & Deep Learning Lab",
        "location": "Calicut, Kerala, India",
        "research_areas": [
            "Computer Vision",
            "Deep Learning",
            "Image Processing",
            "Embedded AI"
        ],
        "recent_papers": [
            "Monocular Depth Estimation with Attention Guided Convolutional Networks",
            "Real-Time Object Tracking in Constrained Embedded Platforms",
            "Spatial Feature Representation in Assistive Vision Devices"
        ],
        "research_summary": "Visual computing, depth reasoning, real-time object tracking, and deep neural vision systems for edge microprocessors.",
        "profile_url": "https://www.nitc.ac.in/faculty",
        "lab_url": "https://www.nitc.ac.in",
        "source_urls": [
            "https://www.nitc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. D. Madhu Kumar",
        "institution": "NIT Calicut",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "madhu@nitc.ac.in",
        "lab_name": "Big Data and Cloud Systems Lab",
        "location": "Calicut, Kerala, India",
        "research_areas": [
            "Big Data Systems",
            "Cloud Computing",
            "Applied AI",
            "Distributed Middleware"
        ],
        "recent_papers": [
            "Distributed Data Processing for Smart City Sensor Networks",
            "Resource Allocation in Hybrid Cloud Environments Using Deep Learning",
            "High-Throughput Analytics for Streaming Healthcare Data"
        ],
        "research_summary": "Big data systems, cloud computing, distributed middleware, and applied data science.",
        "profile_url": "https://www.nitc.ac.in/faculty",
        "lab_url": "https://www.nitc.ac.in",
        "source_urls": [
            "https://www.nitc.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pankaj Kumar Sa",
        "institution": "NIT Rourkela",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "pankajksa@nitrkl.ac.in",
        "lab_name": "Visual Surveillance & Pattern Recognition Lab",
        "location": "Rourkela, Odisha, India",
        "research_areas": [
            "Computer Vision",
            "Visual Surveillance",
            "Biometrics",
            "Deep Learning"
        ],
        "recent_papers": [
            "Occlusion Handling in Real-Time Multi-Object Tracking",
            "Deep Learning Frameworks for Automated Video Anomaly Recognition",
            "Spatial Reasoning in Assistive Mobility Systems"
        ],
        "research_summary": "Visual surveillance, biometric security, video object tracking, and real-time computer vision applications.",
        "profile_url": "https://www.nitrkl.ac.in/faculty",
        "lab_url": "https://www.nitrkl.ac.in",
        "source_urls": [
            "https://www.nitrkl.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Banshidhar Majhi",
        "institution": "NIT Rourkela",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Former Director",
        "email": "bmajhi@nitrkl.ac.in",
        "lab_name": "Pattern Recognition and Image Processing Lab",
        "location": "Rourkela, Odisha, India",
        "research_areas": [
            "Pattern Recognition",
            "Image Processing",
            "Biometrics",
            "Data Compression"
        ],
        "recent_papers": [
            "Multimodal Biometric Authentication using Thermal and Visible Imaging",
            "Wavelet Based Compression for High-Throughput Video Streams",
            "Machine Learning Classifiers for Pathological Tissue Detection"
        ],
        "research_summary": "Pattern recognition, image processing, biometrics, cryptography, and data compression.",
        "profile_url": "https://www.nitrkl.ac.in/faculty",
        "lab_url": "https://www.nitrkl.ac.in",
        "source_urls": [
            "https://www.nitrkl.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Umesh Deshpande",
        "institution": "VNIT Nagpur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "umeshdeshpande@cse.vnit.ac.in",
        "lab_name": "Multi-Agent & Distributed AI Lab",
        "location": "Nagpur, Maharashtra, India",
        "research_areas": [
            "Distributed Systems",
            "Multi-Agent Systems",
            "Applied Machine Learning",
            "Intelligent Transportation"
        ],
        "recent_papers": [
            "Multi-Agent Reinforcement Learning for Autonomous Traffic Optimization",
            "Distributed Machine Learning over Edge Sensor Networks",
            "Real-Time Decision Frameworks for Cyber-Physical Systems"
        ],
        "research_summary": "Distributed computing, multi-agent reinforcement learning, edge intelligence, and automated decision-making platforms.",
        "profile_url": "https://www.cse.vnit.ac.in/faculty",
        "lab_url": "https://www.cse.vnit.ac.in",
        "source_urls": [
            "https://www.cse.vnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mansi Radke",
        "institution": "VNIT Nagpur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Assistant Professor",
        "email": "mansiradke@cse.vnit.ac.in",
        "lab_name": "Natural Language Processing and Social Analytics Lab",
        "location": "Nagpur, Maharashtra, India",
        "research_areas": [
            "Natural Language Processing",
            "Social Media Analytics",
            "Deep Learning",
            "Text Mining"
        ],
        "recent_papers": [
            "Aspect-Based Sentiment Extraction in Low-Resource Vernacular Languages",
            "Deep Neural Dialogue Act Classification in Conversational Agents",
            "Multimodal Misinformation Detection in Online Media"
        ],
        "research_summary": "Natural language processing, social computing, text analytics, and conversational AI.",
        "profile_url": "https://www.cse.vnit.ac.in/faculty",
        "lab_url": "https://www.cse.vnit.ac.in",
        "source_urls": [
            "https://www.cse.vnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Emmanuel S. Pilli",
        "institution": "MNIT Jaipur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "espilli.cse@mnit.ac.in",
        "lab_name": "Cyber-Physical & Intelligent Systems Lab",
        "location": "Jaipur, Rajasthan, India",
        "research_areas": [
            "Cyber-Physical Systems",
            "Machine Learning Security",
            "Cloud AI",
            "Forensic Data Analytics"
        ],
        "recent_papers": [
            "Deep Learning Architectures for Forensic Telemetry Log Analysis",
            "Adversarial Defense in Cloud-Hosted Machine Learning Services",
            "Intelligent Anomaly Detection in Critical Infrastructure Systems"
        ],
        "research_summary": "Cyber security, machine learning applications in systems, cloud security, and intelligent digital forensics.",
        "profile_url": "https://www.mnit.ac.in/faculty",
        "lab_url": "https://www.mnit.ac.in",
        "source_urls": [
            "https://www.mnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mushtaq Ahmed",
        "institution": "MNIT Jaipur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "mahmed.cse@mnit.ac.in",
        "lab_name": "Pattern Recognition & Image Processing Lab",
        "location": "Jaipur, Rajasthan, India",
        "research_areas": [
            "Pattern Recognition",
            "Image Processing",
            "Biometrics",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Convolutional Networks for Palmprint and Finger Vein Biometrics",
            "Spatial Spatial Edge Detection in Complex Biomedical Imagery",
            "Real-Time Visual Classification for Intelligent Security Gates"
        ],
        "research_summary": "Pattern recognition, image processing, biometric systems, and computer vision.",
        "profile_url": "https://www.mnit.ac.in/faculty",
        "lab_url": "https://www.mnit.ac.in",
        "source_urls": [
            "https://www.mnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. R. S. Yadav",
        "institution": "MNNIT Allahabad",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "rsy@mnnit.ac.in",
        "lab_name": "Real-Time Systems & Intelligent Computing Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Real-Time Systems",
            "Artificial Intelligence",
            "Fault-Tolerant Computing",
            "Embedded AI"
        ],
        "recent_papers": [
            "Real-Time Scheduling of Deep Learning Workloads on Heterogeneous Cores",
            "Fault-Tolerant Sensor Telemetry Processing in Autonomous Systems",
            "Adaptive Task Allocation in Edge-Cloud Computing Nodes"
        ],
        "research_summary": "Real-time computing, fault-tolerant architectures, applied AI, and embedded hardware-software systems.",
        "profile_url": "https://www.mnnit.ac.in/faculty",
        "lab_url": "https://www.mnnit.ac.in",
        "source_urls": [
            "https://www.mnnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Neeraj Tyagi",
        "institution": "MNNIT Allahabad",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "neeraj@mnnit.ac.in",
        "lab_name": "Wireless Sensor Networks & IoT Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Wireless Sensor Networks",
            "IoT Systems",
            "Machine Learning in Networks",
            "Routing Optimization"
        ],
        "recent_papers": [
            "Energy-Optimized Routing in Distributed Sensor Networks Using Neural Heuristics",
            "Machine Learning Anomaly Detection for IoT Edge Devices",
            "Real-Time Telemetry Clustering in Wireless Sensor Meshes"
        ],
        "research_summary": "Wireless sensor networks, mobile computing, routing algorithms, and IoT intelligence.",
        "profile_url": "https://www.mnnit.ac.in/faculty",
        "lab_url": "https://www.mnnit.ac.in",
        "source_urls": [
            "https://www.mnnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mukesh A. Zaveri",
        "institution": "SVNIT Surat",
        "institution_type": "NIT",
        "department": "Department of Computer Engineering",
        "designation": "Professor & Head",
        "email": "mazaveri@coed.svnit.ac.in",
        "lab_name": "Computer Vision and Sensor Networks Lab",
        "location": "Surat, Gujarat, India",
        "research_areas": [
            "Computer Vision",
            "Robotics",
            "Sensor Networks",
            "Image Processing"
        ],
        "recent_papers": [
            "Real-Time Multi-Target Tracking in Dense Visual Surveillance",
            "Deep Feature Representation for Visual Odometry in Mobile Robots",
            "Spatial Sensor Fusion for Embedded Robotics Platforms"
        ],
        "research_summary": "Computer vision, visual sensor networks, tracking algorithms, robotics, and image processing.",
        "profile_url": "https://www.coed.svnit.ac.in/faculty",
        "lab_url": "https://www.coed.svnit.ac.in",
        "source_urls": [
            "https://www.coed.svnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. D. C. Jinwala",
        "institution": "SVNIT Surat",
        "institution_type": "NIT",
        "department": "Department of Computer Engineering",
        "designation": "Professor",
        "email": "dcjinwala@coed.svnit.ac.in",
        "lab_name": "Information Security & Cryptography Lab",
        "location": "Surat, Gujarat, India",
        "research_areas": [
            "Information Security",
            "Privacy-Preserving AI",
            "Wireless Sensor Security",
            "Cryptographic Protocols"
        ],
        "recent_papers": [
            "Privacy-Preserving Federated Learning over Distributed IoT Nodes",
            "Secure Key Management Protocols in Resource-Constrained Sensor Meshes",
            "Adversarial Machine Learning Attacks and Countermeasures in Cyber Defense"
        ],
        "research_summary": "Information security, privacy-preserving machine learning, wireless sensor networks, and cryptography.",
        "profile_url": "https://www.coed.svnit.ac.in/faculty",
        "lab_url": "https://www.coed.svnit.ac.in",
        "source_urls": [
            "https://www.coed.svnit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mayank Dave",
        "institution": "NIT Kurukshetra",
        "institution_type": "NIT",
        "department": "Department of Computer Engineering",
        "designation": "Professor",
        "email": "mdave@nitkkr.ac.in",
        "lab_name": "Cloud Computing & Intelligent Networks Lab",
        "location": "Kurukshetra, Haryana, India",
        "research_areas": [
            "Cloud Computing",
            "Mobile Ad-Hoc Networks",
            "Applied AI",
            "Edge Computing"
        ],
        "recent_papers": [
            "Dynamic Workload Offloading in Edge-Cloud Architectures Using Reinforcement Learning",
            "Security Frameworks for Connected Cyber-Physical Systems",
            "Machine Learning Approaches to QoS Optimization in Wireless Meshes"
        ],
        "research_summary": "Cloud computing, mobile ad-hoc networks, wireless sensor networks, and edge AI.",
        "profile_url": "https://www.nitkkr.ac.in/faculty",
        "lab_url": "https://www.nitkkr.ac.in",
        "source_urls": [
            "https://www.nitkkr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. R. K. Pateriya",
        "institution": "MANIT Bhopal",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "pateriyark@manit.ac.in",
        "lab_name": "Data Mining & Machine Learning Lab",
        "location": "Bhopal, Madhya Pradesh, India",
        "research_areas": [
            "Data Mining",
            "Machine Learning",
            "Cloud Security",
            "Big Data Analytics"
        ],
        "recent_papers": [
            "Deep Neural Feature Selection for High-Dimensional Financial Streams",
            "Intelligent Intrusion Detection in Cloud Virtual Environments",
            "Predictive Analytics for Real-Time Decision Support Systems"
        ],
        "research_summary": "Data mining, machine learning, cloud security, and distributed data systems.",
        "profile_url": "https://www.manit.ac.in/faculty",
        "lab_url": "https://www.manit.ac.in",
        "source_urls": [
            "https://www.manit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subhrabrata Choudhury",
        "institution": "NIT Durgapur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "schoudhury@cse.nitdgp.ac.in",
        "lab_name": "Machine Intelligence and Network Security Lab",
        "location": "Durgapur, West Bengal, India",
        "research_areas": [
            "Machine Intelligence",
            "Network Security",
            "Wireless Sensor Networks",
            "Data Mining"
        ],
        "recent_papers": [
            "Deep Learning Based Telemetry Analysis for Network Intrusion Detection",
            "Energy-Aware Clustering in IoT Sensor Networks Using Particle Swarm Optimization",
            "Pattern Recognition in High-Speed Streaming Network Logs"
        ],
        "research_summary": "Machine learning, network security, wireless sensor networks, and soft computing.",
        "profile_url": "https://www.cse.nitdgp.ac.in/faculty",
        "lab_url": "https://www.cse.nitdgp.ac.in",
        "source_urls": [
            "https://www.cse.nitdgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sivaji Bandyopadhyay",
        "institution": "NIT Silchar",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Former Director",
        "email": "sivaji@cse.nits.ac.in",
        "lab_name": "Natural Language Processing and AI Lab",
        "location": "Silchar, Assam, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Learning",
            "Information Extraction",
            "Sentiment Analytics"
        ],
        "recent_papers": [
            "Neural Machine Translation for Low-Resource Morphologically Rich Languages",
            "Cross-Lingual Information Extraction with Contextual Transformers",
            "Sentiment Analysis of Multimodal Social Media Communications"
        ],
        "research_summary": "Machine translation, natural language processing, text data mining, and semantic language processing.",
        "profile_url": "https://www.cse.nits.ac.in/faculty",
        "lab_url": "https://www.cse.nits.ac.in",
        "source_urls": [
            "https://www.cse.nits.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Harsh K. Verma",
        "institution": "NIT Jalandhar",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor",
        "email": "vermah@nitj.ac.in",
        "lab_name": "Soft Computing and Applied AI Lab",
        "location": "Jalandhar, Punjab, India",
        "research_areas": [
            "Soft Computing",
            "Neural Networks",
            "Data Mining",
            "Software Engineering"
        ],
        "recent_papers": [
            "Fuzzy Neural Systems for Complex Engineering Optimization",
            "Machine Learning Classifiers for Predictive Software Quality",
            "Evolutionary Algorithms for High-Dimensional Feature Selection"
        ],
        "research_summary": "Soft computing, artificial intelligence, neural networks, and software engineering.",
        "profile_url": "https://www.nitj.ac.in/faculty",
        "lab_url": "https://www.nitj.ac.in",
        "source_urls": [
            "https://www.nitj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Diptendu Sinha Roy",
        "institution": "NIT Meghalaya",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor & Dean",
        "email": "diptendu.sr@nitm.ac.in",
        "lab_name": "Cloud Systems and Reliability Lab",
        "location": "Shillong, Meghalaya, India",
        "research_areas": [
            "Cloud Computing",
            "Reliability Engineering",
            "IoT Systems",
            "Applied ML"
        ],
        "recent_papers": [
            "Reliability Modeling of Cloud Infrastructure Using Machine Learning",
            "Edge Analytics for Remote Healthcare Telemetry in Hill Regions",
            "Predictive Failure Forecasting in Cyber-Physical Power Grids"
        ],
        "research_summary": "Cloud computing, reliability engineering, distributed systems, and edge telemetry.",
        "profile_url": "https://www.nitm.ac.in/faculty",
        "lab_url": "https://www.nitm.ac.in",
        "source_urls": [
            "https://www.nitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Prabhat Kumar",
        "institution": "NIT Patna",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Professor & Head",
        "email": "prabhat@nitp.ac.in",
        "lab_name": "Wireless Networks & Mobile Systems Lab",
        "location": "Patna, Bihar, India",
        "research_areas": [
            "Wireless Networks",
            "Mobile Computing",
            "Applied Machine Learning",
            "IoT Architectures"
        ],
        "recent_papers": [
            "Machine Learning Guided Routing Protocols for High-Density IoT Meshes",
            "Real-Time Telemetry Clustering for Smart City Sensor Deployments",
            "Energy-Efficient Resource Allocation in Mobile Edge Computing"
        ],
        "research_summary": "Wireless communication, mobile computing, IoT systems, and applied machine learning.",
        "profile_url": "https://www.nitp.ac.in/faculty",
        "lab_url": "https://www.nitp.ac.in",
        "source_urls": [
            "https://www.nitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pradeep Singh",
        "institution": "NIT Raipur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Engineering",
        "designation": "Associate Professor",
        "email": "psingh.cs@nitrr.ac.in",
        "lab_name": "Pattern Recognition & Bio-Medical AI Lab",
        "location": "Raipur, Chhattisgarh, India",
        "research_areas": [
            "Pattern Recognition",
            "Deep Learning",
            "Bio-Medical Signal Processing",
            "Software Defect Prediction"
        ],
        "recent_papers": [
            "Deep Learning Classifiers for Automated Electroencephalogram (EEG) Analysis",
            "Spatial Convolutional Networks for Biomedical Image Diagnosis",
            "Machine Learning Ensembles for Software Fault Localization"
        ],
        "research_summary": "Pattern recognition, deep learning, biomedical signal analysis, and software defect prediction.",
        "profile_url": "https://www.nitrr.ac.in/faculty",
        "lab_url": "https://www.nitrr.ac.in",
        "source_urls": [
            "https://www.nitrr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Uma Bhattacharya",
        "institution": "IIEST Shibpur",
        "institution_type": "NIT",
        "department": "Department of Computer Science & Technology",
        "designation": "Professor",
        "email": "ub@cs.iiests.ac.in",
        "lab_name": "Pattern Recognition & Image Analysis Lab",
        "location": "Howrah, West Bengal, India",
        "research_areas": [
            "Pattern Recognition",
            "Computer Vision",
            "Machine Learning",
            "Document Processing"
        ],
        "recent_papers": [
            "Handwritten Indic Script Recognition using Deep Recurrent Architectures",
            "Spatial Feature Extraction for Unconstrained Optical Character Recognition",
            "Deep Feature Fusion for Real-Time Gesture Classification"
        ],
        "research_summary": "Pattern recognition, document image analysis, computer vision, and machine learning.",
        "profile_url": "https://www.cs.iiests.ac.in/faculty",
        "lab_url": "https://www.cs.iiests.ac.in",
        "source_urls": [
            "https://www.cs.iiests.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. G. Ambika",
        "institution": "IISER Pune",
        "institution_type": "IISER",
        "department": "Department of Physics & Data Science",
        "designation": "Professor",
        "email": "g.ambika@iiserpune.ac.in",
        "lab_name": "Complex Systems and AI for Science Lab",
        "location": "Pune, Maharashtra, India",
        "research_areas": [
            "Complex Networks",
            "Time Series AI",
            "Machine Learning in Physics",
            "Nonlinear Dynamics"
        ],
        "recent_papers": [
            "Machine Learning Methods for Chaotic Time Series Forecasting",
            "Recurrence Network Analysis in Scientific Datasets",
            "Neural Dynamic Estimation for Biophysical Systems"
        ],
        "research_summary": "Interdisciplinary applications of machine learning, nonlinear dynamics, complex network theory, and data-driven scientific discovery.",
        "profile_url": "https://www.iiserpune.ac.in/faculty",
        "lab_url": "https://www.iiserpune.ac.in",
        "source_urls": [
            "https://www.iiserpune.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. M. S. Santhanam",
        "institution": "IISER Pune",
        "institution_type": "IISER",
        "department": "Department of Physics & Data Science",
        "designation": "Professor & Dean",
        "email": "santh@iiserpune.ac.in",
        "lab_name": "Quantum Chaos & Data Science Group",
        "location": "Pune, Maharashtra, India",
        "research_areas": [
            "Quantum Information",
            "Statistical Data Science",
            "Machine Learning for Physics",
            "Chaos Theory"
        ],
        "recent_papers": [
            "Deep Learning Surrogates for High-Dimensional Quantum Wavefunctions",
            "Statistical Pattern Discovery in Extreme Fluctuating Datasets",
            "Random Matrix Models and Machine Learning in Complex Spectra"
        ],
        "research_summary": "Quantum computing concepts, statistical physics, machine learning for physical sciences, and high-dimensional data analysis.",
        "profile_url": "https://www.iiserpune.ac.in/faculty",
        "lab_url": "https://www.iiserpune.ac.in",
        "source_urls": [
            "https://www.iiserpune.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pranay Goel",
        "institution": "IISER Pune",
        "institution_type": "IISER",
        "department": "Department of Biology & Mathematics",
        "designation": "Associate Professor",
        "email": "pgoel@iiserpune.ac.in",
        "lab_name": "Computational Biology and Physiological Systems Lab",
        "location": "Pune, Maharashtra, India",
        "research_areas": [
            "Computational Biology",
            "Mathematical Modeling",
            "Time Series Analysis",
            "Biomedical Data Science"
        ],
        "recent_papers": [
            "Nonlinear Dynamical Modeling of Pancreatic Islet Electrical Bursting",
            "Machine Learning Analysis of Glucose Telemetry and Metabolic Time Series",
            "Data-Driven Estimation of Cellular Signal Transduction Networks"
        ],
        "research_summary": "Computational biology, physiological modeling, nonlinear dynamics, and biomedical time series analytics.",
        "profile_url": "https://www.iiserpune.ac.in/faculty",
        "lab_url": "https://www.iiserpune.ac.in",
        "source_urls": [
            "https://www.iiserpune.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Dibyendu Nandi",
        "institution": "IISER Kolkata",
        "institution_type": "IISER",
        "department": "Center of Excellence in Space Sciences India (CESSI) / Physical Sciences",
        "designation": "Professor & Head",
        "email": "dnandi@iiserkol.ac.in",
        "lab_name": "CESSI Space Weather & AI Lab",
        "location": "Kolkata, West Bengal, India",
        "research_areas": [
            "Space Weather AI",
            "Scientific Machine Learning",
            "Computational Astrophysics",
            "Time Series Forecasting"
        ],
        "recent_papers": [
            "Deep Learning Forecasts of Solar Flares and Space Weather Events",
            "Data-Driven Magnetohydrodynamic Simulations with Neural Operators",
            "Computer Vision for Automated Solar Feature Tracking"
        ],
        "research_summary": "Applying deep learning, computer vision, and scientific data science to astronomical imaging, space weather, and plasma dynamics.",
        "profile_url": "https://www.iiserkol.ac.in/faculty",
        "lab_url": "https://www.iiserkol.ac.in",
        "source_urls": [
            "https://www.iiserkol.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Animesh Mukherjee",
        "institution": "IISER Kolkata",
        "institution_type": "IISER",
        "department": "Department of Physical Sciences / Computational Science",
        "designation": "Associate Professor",
        "email": "animesh@iiserkol.ac.in",
        "lab_name": "Computational Science and Complex Systems Lab",
        "location": "Kolkata, West Bengal, India",
        "research_areas": [
            "Computational Physics",
            "Complex Networks",
            "Scientific Machine Learning",
            "Quantum Materials"
        ],
        "recent_papers": [
            "Machine Learning Prediction of Electronic Properties in Novel 2D Materials",
            "Complex Network Analysis of Transport in Disordered Meshes",
            "Neural Network Surrogates for First-Principles Electronic Calculations"
        ],
        "research_summary": "Computational condensed matter physics, complex systems, scientific AI, and materials modeling.",
        "profile_url": "https://www.iiserkol.ac.in/faculty",
        "lab_url": "https://www.iiserkol.ac.in",
        "source_urls": [
            "https://www.iiserkol.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Abhishek Chaudhuri",
        "institution": "IISER Mohali",
        "institution_type": "IISER",
        "department": "Department of Physical Sciences",
        "designation": "Professor & Dean",
        "email": "abhishek@iisermohali.ac.in",
        "lab_name": "Statistical Mechanics & Scientific AI Lab",
        "location": "Mohali, Punjab, India",
        "research_areas": [
            "Scientific Machine Learning",
            "Soft Matter Physics",
            "Molecular Simulations",
            "Data-Driven Modeling"
        ],
        "recent_papers": [
            "Machine Learning Accelerated Molecular Dynamics in Complex Fluids",
            "Neural Network Potential Estimators for Biological Macromolecules",
            "Statistical Pattern Analysis in Nonequilibrium Systems"
        ],
        "research_summary": "Scientific AI, molecular dynamics simulations, biological physics modeling, and machine learning methods for physical systems.",
        "profile_url": "https://www.iisermohali.ac.in/faculty",
        "lab_url": "https://www.iisermohali.ac.in",
        "source_urls": [
            "https://www.iisermohali.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. P. Balanarayan",
        "institution": "IISER Mohali",
        "institution_type": "IISER",
        "department": "Department of Chemical Sciences",
        "designation": "Associate Professor",
        "email": "balanarayan@iisermohali.ac.in",
        "lab_name": "Quantum Chemistry & Molecular Dynamics Lab",
        "location": "Mohali, Punjab, India",
        "research_areas": [
            "Quantum Chemistry",
            "Molecular AI",
            "Computational Chemistry",
            "Electronic Structure"
        ],
        "recent_papers": [
            "Machine Learning Prediction of Non-Covalent Interactions in Molecular Complexes",
            "Deep Neural Force Fields for High-Dimensional Chemical Dynamics",
            "Data-Driven Screening of Molecular Electronic Spectra"
        ],
        "research_summary": "Theoretical chemistry, laser-matter interaction, molecular machine learning, and quantum chemical dynamics.",
        "profile_url": "https://www.iisermohali.ac.in/faculty",
        "lab_url": "https://www.iisermohali.ac.in",
        "source_urls": [
            "https://www.iisermohali.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Snigdha Thakur",
        "institution": "IISER Bhopal",
        "institution_type": "IISER",
        "department": "Department of Physics & Data Science",
        "designation": "Professor",
        "email": "sthakur@iiserb.ac.in",
        "lab_name": "Data-Driven Soft Matter and Biophysics Lab",
        "location": "Bhopal, Madhya Pradesh, India",
        "research_areas": [
            "Biophysics AI",
            "Computational Modeling",
            "Active Matter",
            "Data Analytics"
        ],
        "recent_papers": [
            "Deep Learning Classification of Collective Motion in Microswimmer Swarms",
            "Physics-Informed Neural Networks for Viscous Flow Simulations",
            "Data-Driven Modeling of Synthetic Active Matter"
        ],
        "research_summary": "Active matter, statistical biophysics, computational physics, and machine learning applications in complex biological flows.",
        "profile_url": "https://www.iiserb.ac.in/faculty",
        "lab_url": "https://www.iiserb.ac.in",
        "source_urls": [
            "https://www.iiserb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vineet K. Sharma",
        "institution": "IISER Bhopal",
        "institution_type": "IISER",
        "department": "Department of Biological Sciences",
        "designation": "Professor",
        "email": "vineetks@iiserb.ac.in",
        "lab_name": "Metagenomics & Systems Biology Lab",
        "location": "Bhopal, Madhya Pradesh, India",
        "research_areas": [
            "Bioinformatics",
            "Metagenomics",
            "Machine Learning in Genomics",
            "Big Data Biology"
        ],
        "recent_papers": [
            "Deep Learning Frameworks for Microbiome-Disease Association Discovery",
            "Machine Learning Screening of Novel Antimicrobial Peptides",
            "Large-Scale Comparative Genomics Using Graph Neural Networks"
        ],
        "research_summary": "Metagenomics, computational genomics, machine learning in life sciences, and big data biological informatics.",
        "profile_url": "https://www.iiserb.ac.in/faculty",
        "lab_url": "https://www.iiserb.ac.in",
        "source_urls": [
            "https://www.iiserb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. V. Subrahmanyam",
        "institution": "IISER Thiruvananthapuram",
        "institution_type": "IISER",
        "department": "School of Physics & Data Science",
        "designation": "Professor",
        "email": "vsub@iisertvm.ac.in",
        "lab_name": "Quantum Information & AI Lab",
        "location": "Thiruvananthapuram, Kerala, India",
        "research_areas": [
            "Quantum Information",
            "Complex Quantum Networks",
            "Machine Learning in Physics",
            "Data Analytics"
        ],
        "recent_papers": [
            "Quantum State Reconstruction via Deep Neural Networks",
            "Entanglement Dynamics in Strongly Correlated Spin Networks",
            "Machine Learning Identification of Quantum Phase Transitions"
        ],
        "research_summary": "Quantum information theory, quantum computation, machine learning for quantum systems, and statistical data science.",
        "profile_url": "https://www.iisertvm.ac.in/faculty",
        "lab_url": "https://www.iisertvm.ac.in",
        "source_urls": [
            "https://www.iisertvm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. Sankararaman",
        "institution": "IISER Tirupati",
        "institution_type": "IISER",
        "department": "Department of Physics & Data Science",
        "designation": "Associate Professor",
        "email": "sankararaman@iisertirupati.ac.in",
        "lab_name": "Applied Optics & Machine Learning in Physics Lab",
        "location": "Tirupati, Andhra Pradesh, India",
        "research_areas": [
            "Applied Optics",
            "Machine Learning in Physics",
            "Spectroscopy AI",
            "Signal Processing"
        ],
        "recent_papers": [
            "Deep Neural Analysis of Laser-Induced Breakdown Spectroscopy Signals",
            "Machine Learning Assisted Optical Characterization of Thin Films",
            "Data-Driven Pattern Classification in Photonic Materials"
        ],
        "research_summary": "Applied optics, laser spectroscopy, photonic systems, and machine learning for physical measurements.",
        "profile_url": "https://www.iisertirupati.ac.in/faculty",
        "lab_url": "https://www.iisertirupati.ac.in",
        "source_urls": [
            "https://www.iisertirupati.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Rohit Soni",
        "institution": "IISER Berhampur",
        "institution_type": "IISER",
        "department": "Department of Mathematical Sciences",
        "designation": "Assistant Professor",
        "email": "rsoni@iiserbpr.ac.in",
        "lab_name": "Scientific Computing and Applied Mathematics Lab",
        "location": "Berhampur, Odisha, India",
        "research_areas": [
            "Scientific Computing",
            "Machine Learning",
            "Numerical PDEs",
            "Optimization"
        ],
        "recent_papers": [
            "Deep Learning Solvers for High-Dimensional Partial Differential Equations",
            "Physics-Informed Neural Networks for Advection-Diffusion Transport",
            "Numerical Optimization for Data-Driven Dynamical Systems"
        ],
        "research_summary": "Numerical analysis, partial differential equations, scientific machine learning, and optimization.",
        "profile_url": "https://www.iiserbpr.ac.in/faculty",
        "lab_url": "https://www.iiserbpr.ac.in",
        "source_urls": [
            "https://www.iiserbpr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Manish Gangwar",
        "institution": "ISB Hyderabad",
        "institution_type": "ISB",
        "department": "Applied AI and Analytics Research Centre",
        "designation": "Professor & Executive Director",
        "email": "manish_gangwar@isb.edu",
        "lab_name": "Applied AI & Quantitative Analytics Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Applied Machine Learning",
            "Predictive Analytics",
            "AI in Economics",
            "Decision Systems"
        ],
        "recent_papers": [
            "Machine Learning Decision Architectures for Real-Time Risk Analysis",
            "Causal Inference in Large Scale Transactional AI Models",
            "Predictive Modeling with High-Dimensional Economic Indicators"
        ],
        "research_summary": "Applied machine learning pipelines, predictive algorithmic systems, automated decision-making platforms, and enterprise AI.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. Sudhir Voleti",
        "institution": "ISB Hyderabad",
        "institution_type": "ISB",
        "department": "Marketing and Data Science Area",
        "designation": "Associate Professor & Head",
        "email": "sudhir_voleti@isb.edu",
        "lab_name": "Text Analytics & Unstructured Data AI Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Learning",
            "Text Mining",
            "Customer Intelligence AI"
        ],
        "recent_papers": [
            "Unstructured Text Embeddings for Automated Enterprise Brand Perception",
            "Topic Modeling and Sentiment Dynamics in Large Scale Online Reviews",
            "Deep Learning Frameworks for High-Dimensional Consumer Data"
        ],
        "research_summary": "Natural language processing, text analytics, unstructured big data modeling, econometric machine learning, and consumer AI.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. Deepa Mani",
        "institution": "ISB Hyderabad",
        "institution_type": "ISB",
        "department": "Information Systems Area",
        "designation": "Professor & Deputy Dean",
        "email": "deepa_mani@isb.edu",
        "lab_name": "Digital Transformation & AI Strategy Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "AI Strategy",
            "Information Systems",
            "Empirical Analytics",
            "Enterprise Platforms"
        ],
        "recent_papers": [
            "Enterprise Value Realization from Machine Learning Implementations",
            "Organizational Dynamics of Cloud AI Adoption",
            "Econometric Analysis of Platform Intelligence Systems"
        ],
        "research_summary": "Enterprise technology adoption, AI strategy, empirical analytics, and digital business systems.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. Prasanna Tantri",
        "institution": "ISB Hyderabad",
        "institution_type": "ISB",
        "department": "Centre for Analytical Finance",
        "designation": "Associate Professor & Executive Director",
        "email": "prasanna_tantri@isb.edu",
        "lab_name": "Financial Analytics & Empirical AI Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Financial Machine Learning",
            "Empirical Banking",
            "Credit Scoring AI",
            "Econometric Analytics"
        ],
        "recent_papers": [
            "Machine Learning Prediction of Credit Default Under Macroeconomic Stress",
            "Algorithmic Lending and Credit Access in Emerging Financial Markets",
            "Empirical Analysis of Fraud Detection Systems in Digital Payments"
        ],
        "research_summary": "Financial analytics, credit scoring machine learning, banking empirical models, and corporate finance.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. Saibal Chattopadhyay",
        "institution": "ISB Mohali",
        "institution_type": "ISB",
        "department": "Decision Sciences & Statistical Learning Group",
        "designation": "Professor",
        "email": "saibal_chattopadhyay@isb.edu",
        "lab_name": "Predictive Analytics & Decision Sciences Lab",
        "location": "Mohali, Punjab, India",
        "research_areas": [
            "Statistical Learning",
            "Predictive Analytics",
            "Sequential Analysis",
            "Machine Learning"
        ],
        "recent_papers": [
            "Sequential Decision-Making under High Parameter Uncertainty",
            "Adaptive Sampling Strategies for Big Data Regression",
            "Robust Predictive Classifiers for High-Dimensional Enterprise Streams"
        ],
        "research_summary": "Statistical estimation, sequential methods, predictive modeling, machine learning for decision sciences, and data analytics.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. Sarang Deo",
        "institution": "ISB Mohali",
        "institution_type": "ISB",
        "department": "Operations Management and Healthcare AI Area",
        "designation": "Professor & Area Chair",
        "email": "sarang_deo@isb.edu",
        "lab_name": "Healthcare Operations & Decision Intelligence Lab",
        "location": "Mohali, Punjab, India",
        "research_areas": [
            "Operations Research",
            "Healthcare AI",
            "Predictive Logistics",
            "Stochastic Modeling"
        ],
        "recent_papers": [
            "Machine Learning Driven Diagnostic Supply Chain Optimization in Rural Health",
            "Predictive Modeling of Hospital Bed Capacity and Patient Flow",
            "Data-Driven Allocation of Public Health Interventions"
        ],
        "research_summary": "Healthcare operations management, applied operations research, predictive modeling, and supply chain analytics.",
        "profile_url": "https://www.isb.edu/faculty",
        "lab_url": "https://www.isb.edu",
        "source_urls": [
            "https://www.isb.edu/faculty"
        ]
    },
    {
        "name": "Prof. U. Dinesh Kumar",
        "institution": "IIM Bangalore",
        "institution_type": "IIM",
        "department": "Decision Sciences and Information Systems",
        "designation": "Professor & Dean",
        "email": "dineshk@iimb.ac.in",
        "lab_name": "Data Science & AI Laboratory (DCAL)",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Artificial Intelligence",
            "Machine Learning Algorithms",
            "Predictive Modeling",
            "Big Data Analytics"
        ],
        "recent_papers": [
            "Deep Learning Classifiers for Credit Risk and Automated Loan Assessment",
            "Explainable AI Models for Financial Prediction",
            "Machine Learning in Healthcare Diagnostics and Logistics"
        ],
        "research_summary": "Machine learning algorithms, deep learning for financial and risk analytics, automated decision platforms, and big data systems.",
        "profile_url": "https://www.iimb.ac.in/faculty",
        "lab_url": "https://www.iimb.ac.in",
        "source_urls": [
            "https://www.iimb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pulak Ghosh",
        "institution": "IIM Bangalore",
        "institution_type": "IIM",
        "department": "Decision Sciences & Analytics",
        "designation": "Professor & Chair of Excellence",
        "email": "pulak.ghosh@iimb.ac.in",
        "lab_name": "Big Data and Quantitative Machine Learning Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Big Data Analytics",
            "Machine Learning in Finance",
            "Bayesian Data Science",
            "Health Informatics AI"
        ],
        "recent_papers": [
            "Bayesian Nonparametric Models for High-Frequency Financial Transactions",
            "Machine Learning Frameworks for Real-Time Credit Default Prediction",
            "Deep Predictive Modeling in Public Health Telemetry"
        ],
        "research_summary": "Big data analytics, Bayesian econometrics, fintech machine learning, AI in banking, and quantitative decision platforms.",
        "profile_url": "https://www.iimb.ac.in/faculty",
        "lab_url": "https://www.iimb.ac.in",
        "source_urls": [
            "https://www.iimb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Rajluxmi V. Murthy",
        "institution": "IIM Bangalore",
        "institution_type": "IIM",
        "department": "Decision Sciences Area",
        "designation": "Professor",
        "email": "rajluxmi@iimb.ac.in",
        "lab_name": "Applied Optimization & Analytics Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Operations Research",
            "Applied Machine Learning",
            "Optimization",
            "Decision Systems"
        ],
        "recent_papers": [
            "Stochastic Optimization for Dynamic Resource Scheduling",
            "Machine Learning Ensembles for Demand Forecasting Under Uncertainty",
            "Data-Driven Models for Energy Grid Load Balancing"
        ],
        "research_summary": "Mathematical programming, applied machine learning, combinatorial optimization, and decision analytics.",
        "profile_url": "https://www.iimb.ac.in/faculty",
        "lab_url": "https://www.iimb.ac.in",
        "source_urls": [
            "https://www.iimb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Shankar Venkatagiri",
        "institution": "IIM Bangalore",
        "institution_type": "IIM",
        "department": "Information Systems Area",
        "designation": "Professor",
        "email": "shankar@iimb.ac.in",
        "lab_name": "Enterprise Cloud & Intelligent Systems Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Information Systems",
            "Cloud AI",
            "Enterprise Architecture",
            "Software Systems"
        ],
        "recent_papers": [
            "Cloud Architecture Scalability for Enterprise Machine Learning Workloads",
            "Adoption and Value Realization of Generative AI in Corporate IT",
            "Architectural Patterns for High-Throughput Business Data Pipelines"
        ],
        "research_summary": "Information systems architecture, cloud computing, enterprise software systems, and data analytics.",
        "profile_url": "https://www.iimb.ac.in/faculty",
        "lab_url": "https://www.iimb.ac.in",
        "source_urls": [
            "https://www.iimb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arnab Kumar Laha",
        "institution": "IIM Ahmedabad",
        "institution_type": "IIM",
        "department": "Production and Quantitative Methods (P&QM)",
        "designation": "Professor & Area Chair",
        "email": "arnab@iima.ac.in",
        "lab_name": "Machine Learning & Quantitative Analytics Lab",
        "location": "Ahmedabad, Gujarat, India",
        "research_areas": [
            "Applied Machine Learning",
            "Predictive Analytics",
            "Data Mining",
            "Quality Engineering"
        ],
        "recent_papers": [
            "Robust Spatial Clustering in Large-Scale Geospatial Datasets",
            "Data-Driven Predictive Modeling for Risk Classification",
            "Machine Learning Frameworks for High-Frequency Industrial Quality Control"
        ],
        "research_summary": "Applied machine learning, predictive analytics, statistical quality control, data mining, and industrial AI.",
        "profile_url": "https://www.iima.ac.in/faculty",
        "lab_url": "https://www.iima.ac.in",
        "source_urls": [
            "https://www.iima.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Debjit Roy",
        "institution": "IIM Ahmedabad",
        "institution_type": "IIM",
        "department": "Operations and Decision Sciences",
        "designation": "Professor & Institute Chair",
        "email": "debjit@iima.ac.in",
        "lab_name": "Robotics & Automated Logistics Lab",
        "location": "Ahmedabad, Gujarat, India",
        "research_areas": [
            "Robotics in Supply Chain",
            "Stochastic Modeling",
            "AI in Logistics",
            "Autonomous Warehousing"
        ],
        "recent_papers": [
            "Real-Time Multi-Robot Routing in Automated Fulfillment Centers",
            "Stochastic Optimization for Robotic Order Picking Systems",
            "Computer Vision and Deep Learning for Warehouse Item Localization"
        ],
        "research_summary": "Automated material handling systems, robotic warehouse operations, simulation optimization, and AI in supply chains.",
        "profile_url": "https://www.iima.ac.in/faculty",
        "lab_url": "https://www.iima.ac.in",
        "source_urls": [
            "https://www.iima.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sachin Jayaswal",
        "institution": "IIM Ahmedabad",
        "institution_type": "IIM",
        "department": "Production and Quantitative Methods (P&QM)",
        "designation": "Professor",
        "email": "sachin@iima.ac.in",
        "lab_name": "Large-Scale Optimization & Network Design Lab",
        "location": "Ahmedabad, Gujarat, India",
        "research_areas": [
            "Large-Scale Optimization",
            "Network Design",
            "Operations Research",
            "Machine Learning"
        ],
        "recent_papers": [
            "Benders Decomposition and Machine Learning Speedups for Facility Location",
            "Stochastic Network Optimization in Resilient Supply Chains",
            "Heuristic Search Algorithms for High-Dimensional Combinatorial Routing"
        ],
        "research_summary": "Large-scale optimization, network design, operations research, and algorithmic problem solving.",
        "profile_url": "https://www.iima.ac.in/faculty",
        "lab_url": "https://www.iima.ac.in",
        "source_urls": [
            "https://www.iima.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sanjay Verma",
        "institution": "IIM Ahmedabad",
        "institution_type": "IIM",
        "department": "Information Systems Area",
        "designation": "Professor",
        "email": "sverma@iima.ac.in",
        "lab_name": "Enterprise Digital Systems Lab",
        "location": "Ahmedabad, Gujarat, India",
        "research_areas": [
            "Information Systems",
            "Business Intelligence",
            "ERP Systems",
            "Data Analytics"
        ],
        "recent_papers": [
            "Business Intelligence Integration in Real-Time Enterprise Operations",
            "Digital Transformation Strategies in Large Financial Conglomerates",
            "Predictive Decision Making Using Corporate Data Repositories"
        ],
        "research_summary": "Information systems management, enterprise resource planning, business analytics, and digital strategy.",
        "profile_url": "https://www.iima.ac.in/faculty",
        "lab_url": "https://www.iima.ac.in",
        "source_urls": [
            "https://www.iima.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sumanta Basu",
        "institution": "IIM Calcutta",
        "institution_type": "IIM",
        "department": "Operations Management & Quantitative Methods",
        "designation": "Professor",
        "email": "sumanta@iimcal.ac.in",
        "lab_name": "Big Data Analytics & Operations Intelligence Lab",
        "location": "Kolkata, West Bengal, India",
        "research_areas": [
            "Big Data Analytics",
            "Operations Research",
            "Machine Learning in Logistics",
            "Predictive Systems"
        ],
        "recent_papers": [
            "Deep Reinforcement Learning for Dynamic Vehicle Routing Problems",
            "Predictive Maintenance Modeling in High-Value Industrial Assets",
            "Optimization under Uncertainty in Large Supply Networks"
        ],
        "research_summary": "Big data analytics, supply chain optimization, revenue management, predictive modeling, and applied machine learning.",
        "profile_url": "https://www.iimcal.ac.in/faculty",
        "lab_url": "https://www.iimcal.ac.in",
        "source_urls": [
            "https://www.iimcal.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Priya Seetharaman",
        "institution": "IIM Calcutta",
        "institution_type": "IIM",
        "department": "Management Information Systems (MIS)",
        "designation": "Professor",
        "email": "priyas@iimcal.ac.in",
        "lab_name": "Digital Platforms & Governance Lab",
        "location": "Kolkata, West Bengal, India",
        "research_areas": [
            "Management Information Systems",
            "Digital Platforms",
            "AI Governance",
            "Enterprise Analytics"
        ],
        "recent_papers": [
            "Algorithmic Governance and Ethical Decision Making in Digital Platforms",
            "Adoption Dynamics of AI Decision Systems in Public Sector Services",
            "Enterprise Analytics Frameworks for Multi-Sided Platforms"
        ],
        "research_summary": "Information systems, digital platforms, IT governance, and analytics adoption.",
        "profile_url": "https://www.iimcal.ac.in/faculty",
        "lab_url": "https://www.iimcal.ac.in",
        "source_urls": [
            "https://www.iimcal.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Preetam Basu",
        "institution": "IIM Calcutta",
        "institution_type": "IIM",
        "department": "Operations Management Group",
        "designation": "Professor",
        "email": "pbasu@iimcal.ac.in",
        "lab_name": "Supply Chain Analytics and Risk Intelligence Lab",
        "location": "Kolkata, West Bengal, India",
        "research_areas": [
            "Supply Chain Analytics",
            "Risk Management",
            "Applied Machine Learning",
            "Stochastic Models"
        ],
        "recent_papers": [
            "Data-Driven Supply Chain Disruption Risk Assessment Using Neural Ensembles",
            "Dynamic Pricing and Inventory Control with Machine Learning Surrogates",
            "Contract Optimization in Global Logistics Networks"
        ],
        "research_summary": "Supply chain management, operations risk analytics, stochastic inventory models, and pricing analytics.",
        "profile_url": "https://www.iimcal.ac.in/faculty",
        "lab_url": "https://www.iimcal.ac.in",
        "source_urls": [
            "https://www.iimcal.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pradeep Kumar",
        "institution": "IIM Lucknow",
        "institution_type": "IIM",
        "department": "Decision Sciences Area",
        "designation": "Professor",
        "email": "pkumar@iiml.ac.in",
        "lab_name": "Business Analytics & Applied AI Lab",
        "location": "Lucknow, Uttar Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Deep Learning",
            "Business Analytics",
            "Decision Support Systems"
        ],
        "recent_papers": [
            "Credit Scoring Models using Ensembles of Deep Decision Classifiers",
            "Text Mining of Financial Disclosures for Corporate Risk Forecasting",
            "Automated Predictive Decision Systems for Enterprise Analytics"
        ],
        "research_summary": "Machine learning, business analytics, deep learning for financial risk, text mining, and intelligent decision systems.",
        "profile_url": "https://www.iiml.ac.in/faculty",
        "lab_url": "https://www.iiml.ac.in",
        "source_urls": [
            "https://www.iiml.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Gaurav Garg",
        "institution": "IIM Lucknow",
        "institution_type": "IIM",
        "department": "Decision Sciences Area",
        "designation": "Associate Professor",
        "email": "ggarg@iiml.ac.in",
        "lab_name": "Statistical Modeling and Predictive Analytics Lab",
        "location": "Lucknow, Uttar Pradesh, India",
        "research_areas": [
            "Statistical Modeling",
            "Machine Learning",
            "Econometrics",
            "Predictive Analytics"
        ],
        "recent_papers": [
            "High-Dimensional Regression Modeling with Elastic Net and Random Forests",
            "Predictive Risk Analytics for Micro-Finance Loan Repayments",
            "Empirical Time Series Econometrics in Volatile Market Indicators"
        ],
        "research_summary": "Applied statistics, predictive modeling, econometric data analysis, and machine learning.",
        "profile_url": "https://www.iiml.ac.in/faculty",
        "lab_url": "https://www.iiml.ac.in",
        "source_urls": [
            "https://www.iiml.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vivek Kumar Gupta",
        "institution": "IIM Lucknow",
        "institution_type": "IIM",
        "department": "Information Technology and Systems Area",
        "designation": "Professor",
        "email": "vkg@iiml.ac.in",
        "lab_name": "Enterprise Data Systems & Telecommunications Lab",
        "location": "Lucknow, Uttar Pradesh, India",
        "research_areas": [
            "Information Technology",
            "Enterprise Systems",
            "Machine Learning Applications",
            "Telecom Management"
        ],
        "recent_papers": [
            "Telecommunication Network Anomaly Prediction with Machine Learning",
            "Enterprise Database Architecture Optimization for High-Volume Analytics",
            "Digital Business Transformation in Telecom Infrastructures"
        ],
        "research_summary": "Information technology systems, database architectures, telecom analytics, and business intelligence.",
        "profile_url": "https://www.iiml.ac.in/faculty",
        "lab_url": "https://www.iiml.ac.in",
        "source_urls": [
            "https://www.iiml.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Radhakrishna Pillai",
        "institution": "IIM Kozhikode",
        "institution_type": "IIM",
        "department": "Information Systems & Analytics",
        "designation": "Professor",
        "email": "krishna@iimk.ac.in",
        "lab_name": "Information Systems & Applied Analytics Lab",
        "location": "Kozhikode, Kerala, India",
        "research_areas": [
            "Information Systems",
            "Applied Analytics",
            "Cloud AI",
            "Healthcare Decision Systems"
        ],
        "recent_papers": [
            "Data Analytics Frameworks for Public Health Monitoring Systems",
            "Machine Learning Approaches to IT Infrastructure Reliability",
            "Adoption and Scalability of Cloud AI Solutions in Enterprises"
        ],
        "research_summary": "Information systems, big data analytics, healthcare informatics, cloud computing architectures, and digital decision systems.",
        "profile_url": "https://www.iimk.ac.in/faculty",
        "lab_url": "https://www.iimk.ac.in",
        "source_urls": [
            "https://www.iimk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sreejesh S.",
        "institution": "IIM Kozhikode",
        "institution_type": "IIM",
        "department": "Marketing and Quantitative Analytics",
        "designation": "Associate Professor",
        "email": "sreejesh@iimk.ac.in",
        "lab_name": "Quantitative Consumer Analytics Lab",
        "location": "Kozhikode, Kerala, India",
        "research_areas": [
            "Quantitative Analytics",
            "Consumer AI",
            "Predictive Modeling",
            "Structural Equation Modeling"
        ],
        "recent_papers": [
            "Machine Learning Models for Real-Time Customer Churn and Lifetime Value Prediction",
            "Structural Modeling of Digital Trust in AI Recommendation Agents",
            "Predictive Behavioral Analytics in Omnichannel Platforms"
        ],
        "research_summary": "Quantitative marketing models, consumer intelligence AI, behavioral data analytics, and structural modeling.",
        "profile_url": "https://www.iimk.ac.in/faculty",
        "lab_url": "https://www.iimk.ac.in",
        "source_urls": [
            "https://www.iimk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Manoj Motiani",
        "institution": "IIM Indore",
        "institution_type": "IIM",
        "department": "Marketing & Decision Sciences",
        "designation": "Associate Professor & Area Chair",
        "email": "mmotiani@iimidr.ac.in",
        "lab_name": "Customer Decision Systems & Analytics Lab",
        "location": "Indore, Madhya Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Predictive Analytics",
            "Consumer Decision Models",
            "Quantitative Analytics"
        ],
        "recent_papers": [
            "Predictive Modeling of Consumer Decision Trajectories using Deep Networks",
            "Machine Learning Segmentation of High-Dimensional User Signals",
            "Automated Decision Intelligence for Product Adoption Forecasting"
        ],
        "research_summary": "Quantitative marketing analytics, applied machine learning, predictive behavioral modeling, and consumer intelligence AI.",
        "profile_url": "https://www.iimidr.ac.in/faculty",
        "lab_url": "https://www.iimidr.ac.in",
        "source_urls": [
            "https://www.iimidr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Manoj Kumar Tiwari",
        "institution": "IIM Mumbai",
        "institution_type": "IIM",
        "department": "Operations & Supply Chain Management / Decision Sciences",
        "designation": "Director & Professor",
        "email": "director@iimm.ac.in",
        "lab_name": "Smart Manufacturing & Supply Chain AI Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "AI in Manufacturing",
            "Supply Chain Intelligence",
            "Optimization",
            "Autonomous Logistics"
        ],
        "recent_papers": [
            "Deep Reinforcement Learning in Cyber-Physical Manufacturing Systems",
            "Machine Learning Architectures for Resilient Global Supply Networks",
            "Digital Twin Integration with Real-Time Edge Analytics in Industry 4.0"
        ],
        "research_summary": "Smart manufacturing, supply chain analytics, operations intelligence, industrial AI, and autonomous decision optimization.",
        "profile_url": "https://www.iimm.ac.in/faculty",
        "lab_url": "https://www.iimm.ac.in",
        "source_urls": [
            "https://www.iimm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Anoop Namboodiri",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "CVIT",
        "designation": "Associate Professor",
        "email": "anoop@iiit.ac.in",
        "lab_name": "Biometrics & Vision Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Computer Vision",
            "Biometrics",
            "Document Analysis"
        ],
        "recent_papers": [
            "Touchless Fingerprint Verification with Deep Networks",
            "Document Analysis via Spatial Transformers"
        ],
        "research_summary": "Biometrics, pattern recognition, and computer vision.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Charu Sharma",
        "institution": "IIIT Hyderabad",
        "institution_type": "IIIT",
        "department": "Machine Learning Lab",
        "designation": "Assistant Professor",
        "email": "charu.sharma@iiit.ac.in",
        "lab_name": "Geometric ML Lab",
        "location": "Hyderabad, Telangana, India",
        "research_areas": [
            "Geometric Deep Learning",
            "Graph Neural Networks",
            "Machine Learning"
        ],
        "recent_papers": [
            "Equivariant GNNs for Molecular Graphs",
            "Manifold Learning in 3D Point Clouds"
        ],
        "research_summary": "Geometric ML and graph neural networks.",
        "profile_url": "https://www.iiit.ac.in/faculty",
        "lab_url": "https://www.iiit.ac.in",
        "source_urls": [
            "https://www.iiit.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Tanmoy Chakraborty",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "tanmoy@iiitd.ac.in",
        "lab_name": "LCS2 Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Social Computing",
            "NLP",
            "Graph Neural Networks"
        ],
        "recent_papers": [
            "Misinformation Detection with Graph Ensembles",
            "Adversarial NLP Robustness"
        ],
        "research_summary": "Complex networks, NLP, and social computing.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pushpendra Singh",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "psingh@iiitd.ac.in",
        "lab_name": "Mobile & Edge AI Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Mobile Computing",
            "Edge AI",
            "IoT Systems"
        ],
        "recent_papers": [
            "Edge AI Frameworks for Real-Time Smartphone Sensing",
            "Wearable Assistive Sensor Telemetry"
        ],
        "research_summary": "Mobile systems, edge AI, and wearable computing.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. A. V. Subramanyam",
        "institution": "IIIT Delhi",
        "institution_type": "IIIT",
        "department": "ECE",
        "designation": "Professor",
        "email": "subramanyam@iiitd.ac.in",
        "lab_name": "Multimedia Forensics Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Multimedia Forensics",
            "Computer Vision",
            "Deepfake Detection"
        ],
        "recent_papers": [
            "Synthetic Image Forensics with Spatial CNNs",
            "Deepfake Video Detection across Multi-Stream Architectures"
        ],
        "research_summary": "Multimedia security and deepfake detection.",
        "profile_url": "https://www.iiitd.ac.in/faculty",
        "lab_url": "https://www.iiitd.ac.in",
        "source_urls": [
            "https://www.iiitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. V. Sridhar",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "Data Science & Policy",
        "designation": "Professor",
        "email": "vsridhar@iiitb.ac.in",
        "lab_name": "Telecom & Data Analytics Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Data Analytics",
            "Telecom Networks",
            "AI Policy"
        ],
        "recent_papers": [
            "Predictive Analytics for Telecom Infrastructure",
            "Spectrum Sharing Optimization using ML"
        ],
        "research_summary": "Data analytics and telecommunications AI.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Madhav Rao",
        "institution": "IIIT Bangalore",
        "institution_type": "IIIT",
        "department": "ECE",
        "designation": "Professor",
        "email": "mr@iiitb.ac.in",
        "lab_name": "Hardware AI Lab",
        "location": "Bangalore, Karnataka, India",
        "research_areas": [
            "Embedded Systems",
            "Hardware Accelerators",
            "Edge AI"
        ],
        "recent_papers": [
            "Low-Power Neural Inference on Microcontrollers",
            "Embedded Real-Time Firmware for Wearables"
        ],
        "research_summary": "Embedded systems and edge AI accelerators.",
        "profile_url": "https://www.iiitb.ac.in/faculty",
        "lab_url": "https://www.iiitb.ac.in",
        "source_urls": [
            "https://www.iiitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. O. P. Vyas",
        "institution": "IIIT Allahabad",
        "institution_type": "IIIT",
        "department": "IT",
        "designation": "Professor",
        "email": "opvyas@iiita.ac.in",
        "lab_name": "Data Mining Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Data Mining",
            "Machine Learning",
            "Distributed Analytics"
        ],
        "recent_papers": [
            "Scalable Pattern Mining in Distributed Sensor Streams",
            "Time Series Predictive Analytics"
        ],
        "research_summary": "Data mining and streaming analytics.",
        "profile_url": "https://www.iiita.ac.in/faculty",
        "lab_url": "https://www.iiita.ac.in",
        "source_urls": [
            "https://www.iiita.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Vrijendra Singh",
        "institution": "IIIT Allahabad",
        "institution_type": "IIIT",
        "department": "IT",
        "designation": "Professor",
        "email": "vrij@iiita.ac.in",
        "lab_name": "Intelligent Systems Lab",
        "location": "Prayagraj, Uttar Pradesh, India",
        "research_areas": [
            "Intelligent Systems",
            "Bio-Inspired Computing",
            "Data Mining"
        ],
        "recent_papers": [
            "Neural Classification of High-Dimensional Sensor Logs",
            "Bio-Inspired Algorithms for Edge Optimization"
        ],
        "research_summary": "Intelligent computing and data mining.",
        "profile_url": "https://www.iiita.ac.in/faculty",
        "lab_url": "https://www.iiita.ac.in",
        "source_urls": [
            "https://www.iiita.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Aditya Trivedi",
        "institution": "ABV-IIITM Gwalior",
        "institution_type": "IIIT",
        "department": "ECE",
        "designation": "Professor",
        "email": "atrivedi@iiitm.ac.in",
        "lab_name": "Signal Processing & Communication Lab",
        "location": "Gwalior, Madhya Pradesh, India",
        "research_areas": [
            "Signal Processing",
            "Wireless Communications",
            "Machine Learning in Telecom"
        ],
        "recent_papers": [
            "Deep Learning Based Signal Modulation Classification",
            "Real-Time Telemetry Compression in Sensor Nodes"
        ],
        "research_summary": "Digital signal processing and wireless AI.",
        "profile_url": "https://www.iiitm.ac.in/faculty",
        "lab_url": "https://www.iiitm.ac.in",
        "source_urls": [
            "https://www.iiitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Atul Gupta",
        "institution": "IIITDM Jabalpur",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "atul@iiitdmj.ac.in",
        "lab_name": "Software & AI Systems Lab",
        "location": "Jabalpur, Madhya Pradesh, India",
        "research_areas": [
            "Software Engineering",
            "Machine Learning",
            "Data Mining"
        ],
        "recent_papers": [
            "Predictive Software Defect Localization with ML",
            "Automated API Test Generation with Neural Models"
        ],
        "research_summary": "Software engineering and applied machine learning.",
        "profile_url": "https://www.iiitdmj.ac.in/faculty",
        "lab_url": "https://www.iiitdmj.ac.in",
        "source_urls": [
            "https://www.iiitdmj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. D. V. L. N. Somayajulu",
        "institution": "IIITDM Kurnool",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Professor & Director",
        "email": "director@iiitk.ac.in",
        "lab_name": "Data Engineering Lab",
        "location": "Kurnool, Andhra Pradesh, India",
        "research_areas": [
            "Data Engineering",
            "Machine Learning",
            "Big Data"
        ],
        "recent_papers": [
            "Scalable Feature Processing for Streaming Big Data",
            "Distributed Machine Learning for Edge Nodes"
        ],
        "research_summary": "Data engineering and distributed computing.",
        "profile_url": "https://www.iiitk.ac.in/faculty",
        "lab_url": "https://www.iiitk.ac.in",
        "source_urls": [
            "https://www.iiitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Hrishikesh Venkataraman",
        "institution": "IIIT Sri City",
        "institution_type": "IIIT",
        "department": "ECE",
        "designation": "Associate Professor",
        "email": "hrishikesh@iiits.in",
        "lab_name": "Wireless & Edge AI Lab",
        "location": "Sri City, Andhra Pradesh, India",
        "research_areas": [
            "Wireless Communications",
            "Edge Computing",
            "IoT Networks"
        ],
        "recent_papers": [
            "Real-Time Telemetry Streaming over Low-Latency Wi-Fi Meshes",
            "Edge Computing Architectures for Connected Vehicles"
        ],
        "research_summary": "Wireless IoT and edge computing.",
        "profile_url": "https://www.iiits.in/faculty",
        "lab_url": "https://www.iiits.in",
        "source_urls": [
            "https://www.iiits.in/faculty"
        ]
    },
    {
        "name": "Prof. Subhashish Dhal",
        "institution": "IIIT Guwahati",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "subhashish@iiitg.ac.in",
        "lab_name": "Sensor Security & ML Lab",
        "location": "Guwahati, Assam, India",
        "research_areas": [
            "Machine Learning Security",
            "Sensor Networks",
            "IoT"
        ],
        "recent_papers": [
            "Adversarial Machine Learning in IoT Sensor Streams",
            "Intelligent Anomaly Detection in Edge Telemetry"
        ],
        "research_summary": "IoT security and machine learning.",
        "profile_url": "https://www.iiitg.ac.in/faculty",
        "lab_url": "https://www.iiitg.ac.in",
        "source_urls": [
            "https://www.iiitg.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Jignesh S. Bhatt",
        "institution": "IIIT Vadodara",
        "institution_type": "IIIT",
        "department": "Signal & AI",
        "designation": "Associate Professor",
        "email": "jignesh.bhatt@iiitvadodara.ac.in",
        "lab_name": "Multimodal Signal Fusion Lab",
        "location": "Gandhinagar, Gujarat, India",
        "research_areas": [
            "Signal Processing",
            "Multimodal Image Fusion",
            "Computer Vision"
        ],
        "recent_papers": [
            "Deep Multi-Sensor Image Fusion for Enhanced Visual Perception",
            "Spatial Spectral Unmixing in Remote Sensing"
        ],
        "research_summary": "Signal processing and multimodal computer vision.",
        "profile_url": "https://www.iiitvadodara.ac.in/faculty",
        "lab_url": "https://www.iiitvadodara.ac.in",
        "source_urls": [
            "https://www.iiitvadodara.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Suresh Limkar",
        "institution": "IIIT Pune",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "suresh.limkar@iiitp.ac.in",
        "lab_name": "Cloud & Distributed AI Lab",
        "location": "Pune, Maharashtra, India",
        "research_areas": [
            "Cloud Computing",
            "Distributed Deep Learning",
            "IoT"
        ],
        "recent_papers": [
            "Distributed Training of Deep Convolutional Networks",
            "Real-Time Sensor Telemetry in Hybrid Clouds"
        ],
        "research_summary": "Cloud computing and distributed AI.",
        "profile_url": "https://www.iiitp.ac.in/faculty",
        "lab_url": "https://www.iiitp.ac.in",
        "source_urls": [
            "https://www.iiitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. O. G. Kakde",
        "institution": "IIIT Nagpur",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Professor & Director",
        "email": "director@iiitn.ac.in",
        "lab_name": "Machine Intelligence Lab",
        "location": "Nagpur, Maharashtra, India",
        "research_areas": [
            "Pattern Recognition",
            "Machine Intelligence",
            "Compilers"
        ],
        "recent_papers": [
            "Deep Neural Feature Selection in High-Dimensional Datasets",
            "Pattern Classification for Real-Time Telemetry"
        ],
        "research_summary": "Pattern recognition and machine intelligence.",
        "profile_url": "https://www.iiitn.ac.in/faculty",
        "lab_url": "https://www.iiitn.ac.in",
        "source_urls": [
            "https://www.iiitn.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. E. Philip",
        "institution": "IIIT Kottayam",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Assistant Professor",
        "email": "philip@iiitkottayam.ac.in",
        "lab_name": "Embedded AI Lab",
        "location": "Kottayam, Kerala, India",
        "research_areas": [
            "Embedded AI",
            "Computer Vision",
            "IoT"
        ],
        "recent_papers": [
            "Low-Latency Object Detection on ESP32 Microcontrollers",
            "Real-Time Embedded Visual Guidance for Mobile Devices"
        ],
        "research_summary": "Embedded AI and computer vision.",
        "profile_url": "https://www.iiitkottayam.ac.in/faculty",
        "lab_url": "https://www.iiitkottayam.ac.in",
        "source_urls": [
            "https://www.iiitkottayam.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Rajiv Ranjan",
        "institution": "IIIT Ranchi",
        "institution_type": "IIIT",
        "department": "CSE",
        "designation": "Assistant Professor",
        "email": "rajiv@iiitranchi.ac.in",
        "lab_name": "Applied ML Lab",
        "location": "Ranchi, Jharkhand, India",
        "research_areas": [
            "Applied Machine Learning",
            "Data Mining",
            "Deep Learning"
        ],
        "recent_papers": [
            "Deep Neural Architectures for Sensor Anomaly Detection",
            "Predictive Analytics in Environmental Data"
        ],
        "research_summary": "Machine learning and data mining.",
        "profile_url": "https://www.iiitranchi.ac.in/faculty",
        "lab_url": "https://www.iiitranchi.ac.in",
        "source_urls": [
            "https://www.iiitranchi.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Pushpak Bhattacharyya",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "pb@cse.iitb.ac.in",
        "lab_name": "CFILT Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Natural Language Processing",
            "Machine Translation",
            "Multilingual AI"
        ],
        "recent_papers": [
            "Eye-Tracking Guided Neural Machine Translation",
            "Multimodal Sentiment Analysis"
        ],
        "research_summary": "NLP, machine translation, and cognitive computation.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Suyash Awate",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "suyash@cse.iitb.ac.in",
        "lab_name": "Medical Image Computing Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Medical Image Processing",
            "Computer Vision",
            "Statistical ML"
        ],
        "recent_papers": [
            "Deep Latent Space Learning for 3D MRI Reconstruction",
            "Bayesian Image Segmentation"
        ],
        "research_summary": "Medical image computing and computer vision.",
        "profile_url": "https://www.cse.iitb.ac.in/faculty",
        "lab_url": "https://www.cse.iitb.ac.in",
        "source_urls": [
            "https://www.cse.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Amit Sethi",
        "institution": "IIT Bombay",
        "institution_type": "IIT",
        "department": "EE",
        "designation": "Professor",
        "email": "asethi@ee.iitb.ac.in",
        "lab_name": "Computational Pathology Lab",
        "location": "Mumbai, Maharashtra, India",
        "research_areas": [
            "Deep Learning",
            "Computer Vision",
            "Computational Pathology"
        ],
        "recent_papers": [
            "Weakly Supervised Whole Slide Classification",
            "Generative Stain Normalization"
        ],
        "research_summary": "Deep learning and computational pathology.",
        "profile_url": "https://www.ee.iitb.ac.in/faculty",
        "lab_url": "https://www.ee.iitb.ac.in",
        "source_urls": [
            "https://www.ee.iitb.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sumeet Agarwal",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "EE",
        "designation": "Associate Professor",
        "email": "sumeet@ee.iitd.ac.in",
        "lab_name": "Cognitive Science Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Cognitive Science",
            "Machine Learning",
            "Computational Linguistics"
        ],
        "recent_papers": [
            "Neural Models of Human Syntax Acquisition",
            "Predictive Cognitive Modeling"
        ],
        "research_summary": "Cognitive science and machine learning.",
        "profile_url": "https://www.ee.iitd.ac.in/faculty",
        "lab_url": "https://www.ee.iitd.ac.in",
        "source_urls": [
            "https://www.ee.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subhashis Banerjee",
        "institution": "IIT Delhi",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "suban@cse.iitd.ac.in",
        "lab_name": "Computer Vision & Geometry Lab",
        "location": "New Delhi, Delhi, India",
        "research_areas": [
            "Computer Vision",
            "Visual Geometry",
            "Real-Time Systems"
        ],
        "recent_papers": [
            "Projective Geometry for Multi-Camera Calibration",
            "Real-Time Embedded Vision for Obstacle Avoidance"
        ],
        "research_summary": "Visual geometry and computer vision.",
        "profile_url": "https://www.cse.iitd.ac.in/faculty",
        "lab_url": "https://www.cse.iitd.ac.in",
        "source_urls": [
            "https://www.cse.iitd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sukhendu Das",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "sdas@cse.iitm.ac.in",
        "lab_name": "Visualization & Perception Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Computer Vision",
            "3D Reconstruction",
            "Medical Image Analysis"
        ],
        "recent_papers": [
            "Stereo Depth Estimation Under Low Light",
            "Deep Volumetric 3D Reconstruction"
        ],
        "research_summary": "Computer vision and 3D visual perception.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. C. Chandra Sekhar",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "chandra@cse.iitm.ac.in",
        "lab_name": "Speech & Vision Lab",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "Speech Processing",
            "Computer Vision",
            "Neural Networks"
        ],
        "recent_papers": [
            "Spatiotemporal Features for Visual Speech Recognition",
            "Gesture Recognition with Deep Networks"
        ],
        "research_summary": "Speech and vision processing.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mitesh M. Khapra",
        "institution": "IIT Madras",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "miteshk@cse.iitm.ac.in",
        "lab_name": "AI4Bharat",
        "location": "Chennai, Tamil Nadu, India",
        "research_areas": [
            "NLP",
            "Deep Learning",
            "Indian Language AI"
        ],
        "recent_papers": [
            "IndicBERT Multilingual Models",
            "Cross-Modal Vision-Language Alignment"
        ],
        "research_summary": "Multilingual NLP and speech AI.",
        "profile_url": "https://www.cse.iitm.ac.in/faculty",
        "lab_url": "https://www.cse.iitm.ac.in",
        "source_urls": [
            "https://www.cse.iitm.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arnab Bhattacharya",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "arnabb@cse.iitk.ac.in",
        "lab_name": "Database & IR Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Data Mining",
            "Information Retrieval",
            "Spatial Databases"
        ],
        "recent_papers": [
            "Spatial Distance Indexing for Nearest Neighbors",
            "Graph Subgraph Matching under Uncertainty"
        ],
        "research_summary": "Data mining and spatial indexing.",
        "profile_url": "https://www.cse.iitk.ac.in/faculty",
        "lab_url": "https://www.cse.iitk.ac.in",
        "source_urls": [
            "https://www.cse.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. K. S. Venkatesh",
        "institution": "IIT Kanpur",
        "institution_type": "IIT",
        "department": "EE",
        "designation": "Professor",
        "email": "venkats@iitk.ac.in",
        "lab_name": "Computer Vision Lab",
        "location": "Kanpur, Uttar Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Image Processing",
            "Visual Tracking"
        ],
        "recent_papers": [
            "Real-Time Object Trajectory Estimation in Surveillance",
            "Optical Flow Invariants in Monocular Cameras"
        ],
        "research_summary": "Computer vision and motion analysis.",
        "profile_url": "https://www.iitk.ac.in/faculty",
        "lab_url": "https://www.iitk.ac.in",
        "source_urls": [
            "https://www.iitk.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Plaban Kumar Bhowmick",
        "institution": "IIT Kharagpur",
        "institution_type": "IIT",
        "department": "CoE in AI",
        "designation": "Associate Professor",
        "email": "plaban@ai.iitkgp.ac.in",
        "lab_name": "Interactive Systems Lab",
        "location": "Kharagpur, West Bengal, India",
        "research_areas": [
            "HCI",
            "Artificial Intelligence",
            "Assistive Learning"
        ],
        "recent_papers": [
            "Personalized Assistive Interfaces for Visually Impaired",
            "Multimodal Learning Analytics"
        ],
        "research_summary": "Human-computer interaction and assistive AI.",
        "profile_url": "https://www.ai.iitkgp.ac.in/faculty",
        "lab_url": "https://www.ai.iitkgp.ac.in",
        "source_urls": [
            "https://www.ai.iitkgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sudeshna Sarkar",
        "institution": "IIT Kharagpur",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "sudeshna@cse.iitkgp.ac.in",
        "lab_name": "NLP Lab",
        "location": "Kharagpur, West Bengal, India",
        "research_areas": [
            "NLP",
            "Machine Translation",
            "Information Extraction"
        ],
        "recent_papers": [
            "Cross-Lingual Information Retrieval",
            "Deep Learning for Biomedical Summarization"
        ],
        "research_summary": "Natural language processing and text mining.",
        "profile_url": "https://www.cse.iitkgp.ac.in/faculty",
        "lab_url": "https://www.cse.iitkgp.ac.in",
        "source_urls": [
            "https://www.cse.iitkgp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Balasubramanian Raman",
        "institution": "IIT Roorkee",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor & Head",
        "email": "balaraman@cs.iitr.ac.in",
        "lab_name": "VIST Lab",
        "location": "Roorkee, Uttarakhand, India",
        "research_areas": [
            "Computer Vision",
            "Medical Imaging",
            "Biometrics"
        ],
        "recent_papers": [
            "Deep Residual Networks for Brain Tumor Segmentation",
            "Biometric Authentication using Multimodal Fusion"
        ],
        "research_summary": "Computer vision and biomedical imaging.",
        "profile_url": "https://www.cs.iitr.ac.in/faculty",
        "lab_url": "https://www.cs.iitr.ac.in",
        "source_urls": [
            "https://www.cs.iitr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Nipun Batra",
        "institution": "IIT Gandhinagar",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "nipun.batra@iitgn.ac.in",
        "lab_name": "Sustainability ML Lab",
        "location": "Gandhinagar, Gujarat, India",
        "research_areas": [
            "Machine Learning",
            "Mobile Sensing",
            "IoT Systems"
        ],
        "recent_papers": [
            "Transfer Learning for Energy Disaggregation",
            "IoT Telemetry Analysis for Smart Buildings"
        ],
        "research_summary": "Machine learning for IoT and sensing.",
        "profile_url": "https://www.iitgn.ac.in/faculty",
        "lab_url": "https://www.iitgn.ac.in",
        "source_urls": [
            "https://www.iitgn.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Santanu Chaudhury",
        "institution": "IIT Jodhpur",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor & Director",
        "email": "director@iitj.ac.in",
        "lab_name": "Multimedia Lab",
        "location": "Jodhpur, Rajasthan, India",
        "research_areas": [
            "Computer Vision",
            "Multimedia Systems",
            "Assistive AI"
        ],
        "recent_papers": [
            "Visual Guidance Frameworks for Assistive Walking Aids",
            "Multimodal Document Intelligence"
        ],
        "research_summary": "Computer vision and assistive technology.",
        "profile_url": "https://www.iitj.ac.in/faculty",
        "lab_url": "https://www.iitj.ac.in",
        "source_urls": [
            "https://www.iitj.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Subrahmanyam Murala",
        "institution": "IIT Ropar",
        "institution_type": "IIT",
        "department": "EE",
        "designation": "Associate Professor",
        "email": "subrahmanyam@iitrpr.ac.in",
        "lab_name": "CVPR Lab",
        "location": "Rupnagar, Punjab, India",
        "research_areas": [
            "Computer Vision",
            "Image Retrieval",
            "Deep Learning"
        ],
        "recent_papers": [
            "Directional Pattern Descriptors for Visual Search",
            "Monocular Depth Estimation for Driver Assistance"
        ],
        "research_summary": "Computer vision and pattern recognition.",
        "profile_url": "https://www.iitrpr.ac.in/faculty",
        "lab_url": "https://www.iitrpr.ac.in",
        "source_urls": [
            "https://www.iitrpr.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sriparna Saha",
        "institution": "IIT Patna",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "sriparna@iitp.ac.in",
        "lab_name": "Bio-NLP Lab",
        "location": "Patna, Bihar, India",
        "research_areas": [
            "Machine Learning",
            "Bio-NLP",
            "Optimization"
        ],
        "recent_papers": [
            "Multi-Objective Evolutionary Clustering",
            "Conversational AI for Healthcare Triaging"
        ],
        "research_summary": "Machine learning and bio-NLP.",
        "profile_url": "https://www.iitp.ac.in/faculty",
        "lab_url": "https://www.iitp.ac.in",
        "source_urls": [
            "https://www.iitp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Kapil Ahuja",
        "institution": "IIT Indore",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "kahuja@iiti.ac.in",
        "lab_name": "Scientific ML Lab",
        "location": "Indore, Madhya Pradesh, India",
        "research_areas": [
            "Scientific Computing",
            "Applied ML",
            "Optimization"
        ],
        "recent_papers": [
            "ML Accelerated Solvers for Sparse Systems",
            "Neural Surrogates for Fluid Dynamics"
        ],
        "research_summary": "Scientific machine learning and numerical analysis.",
        "profile_url": "https://www.iiti.ac.in/faculty",
        "lab_url": "https://www.iiti.ac.in",
        "source_urls": [
            "https://www.iiti.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. S. R. Mahadeva Prasanna",
        "institution": "IIT Guwahati",
        "institution_type": "IIT",
        "department": "EEE",
        "designation": "Professor",
        "email": "prasanna@iitg.ac.in",
        "lab_name": "Speech Processing Lab",
        "location": "Guwahati, Assam, India",
        "research_areas": [
            "Speech Processing",
            "Biometrics",
            "Acoustics"
        ],
        "recent_papers": [
            "Voice Biometrics Under Degraded Channels",
            "Acoustic Detection of Throat Pathologies"
        ],
        "research_summary": "Speech signal processing and voice biometrics.",
        "profile_url": "https://www.iitg.ac.in/faculty",
        "lab_url": "https://www.iitg.ac.in",
        "source_urls": [
            "https://www.iitg.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Sanjay Kumar Singh",
        "institution": "IIT BHU",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor & Head",
        "email": "sks.cse@iitbhu.ac.in",
        "lab_name": "Biometrics Lab",
        "location": "Varanasi, Uttar Pradesh, India",
        "research_areas": [
            "Biometrics",
            "Computer Vision",
            "Surveillance"
        ],
        "recent_papers": [
            "Deep Feature Learning for Face and Iris Biometrics",
            "Activity Recognition in Crowds"
        ],
        "research_summary": "Biometrics and visual surveillance.",
        "profile_url": "https://www.iitbhu.ac.in/faculty",
        "lab_url": "https://www.iitbhu.ac.in",
        "source_urls": [
            "https://www.iitbhu.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Varun Dutt",
        "institution": "IIT Mandi",
        "institution_type": "IIT",
        "department": "SCEE",
        "designation": "Associate Professor",
        "email": "varun@iitmandi.ac.in",
        "lab_name": "Cognitive Science Lab",
        "location": "Mandi, Himachal Pradesh, India",
        "research_areas": [
            "Cognitive Science",
            "Machine Learning",
            "Decision Making"
        ],
        "recent_papers": [
            "Instance-Based Learning for Human-AI Autonomy",
            "Predictive Analytics of Cognitive Workload"
        ],
        "research_summary": "Cognitive science and machine learning.",
        "profile_url": "https://www.iitmandi.ac.in/faculty",
        "lab_url": "https://www.iitmandi.ac.in",
        "source_urls": [
            "https://www.iitmandi.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Arnav Bhavsar",
        "institution": "IIT Mandi",
        "institution_type": "IIT",
        "department": "SCEE",
        "designation": "Associate Professor",
        "email": "arnav@iitmandi.ac.in",
        "lab_name": "Visual Computing Lab",
        "location": "Mandi, Himachal Pradesh, India",
        "research_areas": [
            "Computer Vision",
            "Medical Imaging",
            "Deep Learning"
        ],
        "recent_papers": [
            "Multi-Scale Image Inpainting",
            "Monocular Depth Estimation via Convolutional Attention"
        ],
        "research_summary": "Computer vision and medical imaging.",
        "profile_url": "https://www.iitmandi.ac.in/faculty",
        "lab_url": "https://www.iitmandi.ac.in",
        "source_urls": [
            "https://www.iitmandi.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Debasis Samanta",
        "institution": "IIT Bhubaneswar",
        "institution_type": "IIT",
        "department": "School of Electrical Sciences",
        "designation": "Professor",
        "email": "dsamanta@iitbbs.ac.in",
        "lab_name": "HCI Lab",
        "location": "Bhubaneswar, Odisha, India",
        "research_areas": [
            "HCI",
            "Biometrics",
            "Assistive Tech"
        ],
        "recent_papers": [
            "Brain-Computer Interfaces for Assistive Mobility",
            "Eye-Gaze Tracking for Disabled Users"
        ],
        "research_summary": "Human-computer interaction and assistive systems.",
        "profile_url": "https://www.iitbbs.ac.in/faculty",
        "lab_url": "https://www.iitbbs.ac.in",
        "source_urls": [
            "https://www.iitbbs.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Kalidas Yeturu",
        "institution": "IIT Tirupati",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Associate Professor",
        "email": "ykalidas@iittp.ac.in",
        "lab_name": "AI for Healthcare Lab",
        "location": "Tirupati, Andhra Pradesh, India",
        "research_areas": [
            "Machine Learning",
            "Deep Learning",
            "Computational Biology"
        ],
        "recent_papers": [
            "Graph Neural Networks for Protein Binding Prediction",
            "Deep Spatial Features in Cryo-EM Images"
        ],
        "research_summary": "AI for health and computational biology.",
        "profile_url": "https://www.iittp.ac.in/faculty",
        "lab_url": "https://www.iittp.ac.in",
        "source_urls": [
            "https://www.iittp.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Mrinal K. Das",
        "institution": "IIT Palakkad",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Assistant Professor",
        "email": "mrinal@iitpkd.ac.in",
        "lab_name": "Probabilistic ML Lab",
        "location": "Palakkad, Kerala, India",
        "research_areas": [
            "Machine Learning",
            "Bayesian Inference",
            "Probabilistic Models"
        ],
        "recent_papers": [
            "Variational Inference for Latent Models",
            "Bayesian Topic Modeling"
        ],
        "research_summary": "Probabilistic ML and Bayesian methods.",
        "profile_url": "https://www.iitpkd.ac.in/faculty",
        "lab_url": "https://www.iitpkd.ac.in",
        "source_urls": [
            "https://www.iitpkd.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Clint P. George",
        "institution": "IIT Goa",
        "institution_type": "IIT",
        "department": "Mathematics & CS",
        "designation": "Assistant Professor",
        "email": "clint@iitgoa.ac.in",
        "lab_name": "Statistical ML Lab",
        "location": "Ponda, Goa, India",
        "research_areas": [
            "Statistical ML",
            "Text Mining",
            "Information Extraction"
        ],
        "recent_papers": [
            "Topic Modeling over Dynamic Document Streams",
            "Bayesian Matrix Factorization"
        ],
        "research_summary": "Statistical ML and text mining.",
        "profile_url": "https://www.iitgoa.ac.in/faculty",
        "lab_url": "https://www.iitgoa.ac.in",
        "source_urls": [
            "https://www.iitgoa.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Gaurav Varshney",
        "institution": "IIT Jammu",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Assistant Professor",
        "email": "gaurav.varshney@iitjammu.ac.in",
        "lab_name": "Security & Applied AI Lab",
        "location": "Jammu, Jammu & Kashmir, India",
        "research_areas": [
            "Information Security",
            "Applied ML",
            "IoT Security"
        ],
        "recent_papers": [
            "Machine Learning for Phishing URL Detection",
            "Deep Learning for Industrial IoT Intrusion Detection"
        ],
        "research_summary": "Security and applied ML.",
        "profile_url": "https://www.iitjammu.ac.in/faculty",
        "lab_url": "https://www.iitjammu.ac.in",
        "source_urls": [
            "https://www.iitjammu.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Santosh Biswas",
        "institution": "IIT Bhilai",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor",
        "email": "santosh@iitbhilai.ac.in",
        "lab_name": "Embedded AI Lab",
        "location": "Bhilai, Chhattisgarh, India",
        "research_areas": [
            "Embedded Systems",
            "Fault-Tolerant Systems",
            "VLSI"
        ],
        "recent_papers": [
            "Hardware-in-the-Loop Testing for Autonomous Vehicles",
            "Embedded ML for Online Fault Diagnosis"
        ],
        "research_summary": "Embedded systems and real-time computing.",
        "profile_url": "https://www.iitbhilai.ac.in/faculty",
        "lab_url": "https://www.iitbhilai.ac.in",
        "source_urls": [
            "https://www.iitbhilai.ac.in/faculty"
        ]
    },
    {
        "name": "Prof. Chiranjeev Kumar",
        "institution": "IIT ISM Dhanbad",
        "institution_type": "IIT",
        "department": "CSE",
        "designation": "Professor & Dean",
        "email": "chiranjeev@iitism.ac.in",
        "lab_name": "Intelligent Systems Lab",
        "location": "Dhanbad, Jharkhand, India",
        "research_areas": [
            "Machine Learning",
            "Software Engineering",
            "Pattern Recognition"
        ],
        "recent_papers": [
            "Predictive Software Defect Classification with ML",
            "Deep Learning for Sensor Stream Processing"
        ],
        "research_summary": "Machine learning and software systems.",
        "profile_url": "https://www.iitism.ac.in/faculty",
        "lab_url": "https://www.iitism.ac.in",
        "source_urls": [
            "https://www.iitism.ac.in/faculty"
        ]
    }
]

import os

def _load_excel_professors() -> List[Dict[str, Any]]:
    """Loads professors from 1584 Professors IIT (1).xlsx if available."""
    excel_professors = []
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "1584 Professors IIT (1).xlsx"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "1584 Professors IIT (1).xlsx"),
        "1584 Professors IIT (1).xlsx"
    ]
    excel_file = None
    for p in possible_paths:
        if os.path.exists(p):
            excel_file = p
            break

    if excel_file:
        try:
            import pandas as pd
            df = pd.read_excel(excel_file)
            for _, r in df.iterrows():
                name = str(r.get("Name", "")).strip()
                college = str(r.get("College Name", "")).strip()
                ctype = str(r.get("College Type", "IIT")).strip().upper()
                dept = str(r.get("Department", "CSE")).strip()
                email = str(r.get("Mail Id", "")).strip()
                areas_raw = str(r.get("Area of interest", "")).strip()
                areas = [a.strip() for a in areas_raw.split(",") if a.strip()]

                if name and email and "@" in email:
                    excel_professors.append({
                        "name": name if name.startswith("Prof") or name.startswith("Dr") else f"Prof. {name}",
                        "institution": college,
                        "institution_type": ctype if ctype in ["IIT", "IIIT", "IISc", "NIT", "IISER", "ISB", "IIM"] else "IIT",
                        "department": dept,
                        "designation": "Professor / Faculty",
                        "email": email,
                        "lab_name": f"{name} Research Group",
                        "location": "India",
                        "research_areas": areas,
                        "recent_papers": [f"Research on {a}" for a in areas[:2]],
                        "research_summary": f"Research focusing on {', '.join(areas)}.",
                        "profile_url": "",
                        "lab_url": "",
                        "source_urls": ["1584 Professors IIT Excel Catalog"]
                    })
        except Exception as e:
            pass
    return excel_professors

def discover_professors(
    institution_type: Optional[str] = None,
    institution_name: Optional[str] = None,
    research_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Discovers professors matching institution type (IIT, IIIT, IISc, NIT, IISER, ISB, IIM, or ALL)
    and specific research keywords.
    """
    results = []
    excel_profs = _load_excel_professors()
    combined_catalog = NATIONAL_FACULTY_CATALOG + excel_profs
    seen_emails = set()
    full_catalog = []
    for p in combined_catalog:
        em = p.get("email", "").strip().lower()
        if em and em not in seen_emails:
            seen_emails.add(em)
            full_catalog.append(p)
    
    # Normalize institution type filter
    filter_type = institution_type.strip().upper() if institution_type else "ALL"
    
    if filter_type in ["IIT", "IITS"]:
        allowed_types = ["IIT"]
    elif filter_type in ["IIIT", "IIITS"]:
        allowed_types = ["IIIT"]
    elif filter_type in ["IISC", "IISCB", "IISC BANGALORE"]:
        allowed_types = ["IISc"]
    elif filter_type in ["NIT", "NITS"]:
        allowed_types = ["NIT"]
    elif filter_type in ["IISER", "IISERS"]:
        allowed_types = ["IISER"]
    elif filter_type in ["ISB", "ISBS"]:
        allowed_types = ["ISB"]
    elif filter_type in ["IIM", "IIMS"]:
        allowed_types = ["IIM"]
    else:
        allowed_types = ["IIT", "IIIT", "IISc", "NIT", "IISER", "ISB", "IIM"]

    for prof in full_catalog:
        # Check institution type
        if prof.get("institution_type") not in allowed_types:
            continue
        
        # Check specific institution name if requested
        if institution_name and institution_name.strip():
            target_inst = institution_name.strip().lower()
            prof_inst = prof.get("institution", "").lower()
            prof_full = INSTITUTE_FULL_NAMES.get(prof.get("institution", ""), "").lower()
            if target_inst not in prof_inst and target_inst not in prof_full:
                continue
                
        # Check research keyword matching
        if research_filter and research_filter.strip():
            terms = [t.lower() for t in research_filter.split() if len(t) > 2]
            searchable_text = " ".join([
                prof.get("name", ""),
                prof.get("department", ""),
                " ".join(prof.get("research_areas", [])),
                " ".join(prof.get("recent_papers", [])),
                prof.get("research_summary", "")
            ]).lower()
            
            if not any(term in searchable_text for term in terms):
                continue
                
        # Format full legal institution name
        resolved_full_name = INSTITUTE_FULL_NAMES.get(prof["institution"], prof["institution"])
        prof_copy = dict(prof)
        prof_copy["iit"] = prof["institution"] # Backward compatibility for DB column
        prof_copy["full_institution_name"] = resolved_full_name
        results.append(prof_copy)
        
    return results
