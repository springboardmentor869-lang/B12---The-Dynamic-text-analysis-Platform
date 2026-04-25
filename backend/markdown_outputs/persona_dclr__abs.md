# Converted Document

ACKNOWLEDGEMENT

We take this opportunity to express our deep sense of gratitude and sincere thanks to all

who helped us to complete the project successfully.

We are deeply indebted to our guide Prof. Aleema. S. B, Assistant Professor, Department

of Computer Science and Engineering for her excellent guidance, positive criticism and

valuable comments. We are greatly thankful to Dr. Vineetha G R, Head of Computer

Science and Engineering Department for her support and cooperation.

Finally, we thank our parents and friends near and dear ones who directly and indirectly

contributed to the successful completion of our project.

AFRA S (Reg. No: MEK22CS005)

NAZRIN S (Reg. No: MEK22CS037)

RAEESA N (Reg. No: MEK22CS041)

SAFNA SAJEEV (Reg. No: MEK22CS044)

i

ABSTRACT

PersonaVault is a secure digital identity and document management system designed

to provide users with a safe and centralized platform for storing and protecting sensitive

personal data. In recent years, the rapid growth of digital services and online transactions

has increased the risk of data breaches, identity theft, and unauthorized information

exposure, highlighting the need for advanced security solutions. Existing systems mainly

focus on basic storage or authentication mechanisms, lacking an integrated approach that

combines secure data management, intelligent analysis, and proactive threat detection. To

address this gap, the proposed system introduces a unified platform that integrates secure

authentication, encrypted storage, and intelligent monitoring techniques to enhance data

protection. The system implements passwordless authentication using Google OAuth

integrated with Supabase, while user data is managed through a structured PostgreSQL-

based backend for efficient handling of identities, roles, and metadata. PersonaVault

incorporates a secure document vault where users can upload and manage files within

protected environments. The system performs document analysis by extracting content

from uploaded files and applying Natural Language Processing (NLP) and regular

expressions to identify sensitive information such as personally identifiable data and

financial details, along with generating unique data fingerprints for tracking. Additionally,

the platform integrates automated web scanning to detect unauthorized data exposure by

monitoring public sources and cross-referencing stored fingerprints with online content.

A risk scoring mechanism is used to evaluate the severity of detected threats, enabling

prioritized alerts and better decision-making. By combining strong security practices,

intelligent monitoring, and user-friendly design, PersonaVault aims to provide a proactive

and scalable solution for digital data protection, enabling users to maintain control over

their sensitive information and enhance overall privacy and security.

ii
