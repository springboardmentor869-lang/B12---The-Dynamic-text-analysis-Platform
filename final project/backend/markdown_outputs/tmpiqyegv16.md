FIGURES AND TABLES
DISCUSSION
Department of Computer Science and Engineering
MES INSTITUTE OF TECHNOLOGY & MANAGEMENT,CHATHANNOOR Kollam-72,India
30th March  2026
AI-Based Multimodal Autism Screening System Using 
Questionnaire, Facial Analysis and Gaze Tracking
Arafa S¹*, Asna Azad² , Muhammed Yaseen I³ and Muhammed Adhil Ashik4  
¹ Department of Computer Science, MES Institute of Technology and Management, Kerala, India
Project  
Group No: 01
This project presents an AI-based autism 
screening application that uses behavioral 
and visual analysis to assess autism risk in 
c h i l d r e n .  T h e  s y s t e m  c o m b i n e s  a 
questionnaire, facial image analysis using 
deep learning, and gaze tracking through eye 
movement detection. Developed using 
FastAPI and React, it classifies risk into Low, 
Medium, and High levels, serving as an early 
screening tool for preliminary assessment.
•To develop an automated autism screening 
system
•To combine behavioral and visual analysis 
techniques
•To provide early risk assessment using AI 
models
•To create a user-friendly and accessible 
web application
- Uses a multimodal approach combining      
questionnaire, facial analysis, and gaze 
tracking
- Each module generates an individual risk 
score
- Results are combined in a central fusion 
module
- Improves overall accuracy and reliability
- Generates a final comprehensive ASD risk 
report
1. Provides an efficient and accessible method for early autism screening 
using AI
2. Combines questionnaire, facial recognition, and gaze tracking for 
improved reliability
3. Enhances accuracy compared to single-method approaches
4. Scalable and can be extended with real-time monitoring and larger 
datasets
Fig 1 : Three-part framework for risk assessment
Beary M. et al. (2023) – Diagnosis of autism using facial analysis 
Prakash V.G. et al. (2023) – Computer vision assessment of autistic children 
University of Arkansas (2022) – AQ-10, Q-CHAT-10, SRS screening questionnaires 
Krafczyk S. et al. (2020) – Eye-gaze tracking as an early indicator of autism 
- Earlier research mainly focuses on improving the accuracy of individual models, whereas our project 
emphasizes overall usability and complete system integration.
- Many literature works rely on specialized datasets and controlled environments, while our system 
operates in a more practical and user-friendly setting using general inputs.
- Existing approaches often lack user interaction, but our system incorporates active participation through 
questionnaires and gaze-based tasks.
RESULTS
METHODOLOGY
OBJECTIVES
ABSTRACT
CONCLUSIONS
REFERENCES
Acknowledgement
We sincerely thank Prof. Naja M I, our project guide, and Dr. Vineetha Vijayan, 
HOD and project coordinator, for their valuable guidance and support in completing 
this project. 
Fig 2: Comparative analysis of facial features 
(ASD vs Non-ASD )
Fig 3 : Contribution of individual modalities in 
overall screening
Fig 4: Categorization of low, medium, and high 
autism risk  
Aspect
Literature Review
Our Project
Data Input
Static datasets
Real-time user input
Gaze Tracking
Rarely included
Uses MediaPipe + Eyetrax
User Interface
Limited or not available
Web app using React + FastAPI
Security
Not emphasized
Uses AES-256 Encryption
Decision Method
Separate module outputs
Combined (multi-module fusion)
Reporting
Minimal
Charts + downloadable PDF
Table 1 : Comparison between Existing Literature Methods and Proposed Multi-Modal 
Autism Screening System
