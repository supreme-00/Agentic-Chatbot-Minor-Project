**🚀 Agentic AI for Campus**  
**Intelligent FastAPI + AI Chatbot for University Information Access**  

---

## 📌 Overview

**Agentic AI for Campus** is an intelligent, AI-powered system designed to simplify access to academic and administrative information for students, faculty, and administrators.  
It provides:

- Natural language querying  
- Real-time student & faculty info retrieval  
- Timetable and classroom availability tracking  
- General campus queries via LLM  
- Secure login with role-based access  

Built with **FastAPI**, **PostgreSQL**, and **Gemini 2.5 Flash**, the system automatically detects whether a query requires database access or general AI reasoning, enabling instant, accurate responses.

---

## ⭐ Features

### 🔹 General Queries (AI-Powered)
- Address, history, institutes, courses  
- Auto-detected public information via Gemini LLM  
- No SQL processing for public queries

### 🔹 Student Information Module
- Search by:
  - Name  
  - Enrollment number  
  - Phone  
  - Email  
- Single-name search  
- Parent phone fallback  
- Fuzzy matching for ambiguous names  

### 🔹 Faculty Information Module
- Supports full names, partial names, and initials  
- Maps abbreviations like *“MDT”* → Prof. Manan Thakkar  

### 🔹 Timetable Module
- Full batch timetable  
- “Where is this batch right now?”  
- Lab/classroom identification  
- Day-wise timetable querying  

### 🔹 Authentication
- Secure login (admin/student)  
- Role-based access control  

---

## 🧠 System Architecture

<img width="1319" height="130" alt="image" src="https://github.com/user-attachments/assets/13db46d9-f739-40ee-b7bf-57abecde3186" />

## 🛠️ Tech Stack

| Layer | Technology |
|------|------------|
| Backend | FastAPI (Python) |
| AI | Gemini 2.5 Flash |
| Database | PostgreSQL + pgAdmin |
| Auth | Custom Role-Based Login |
| Frontend | HTML, CSS, JS |
| Architecture | Agentic AI + Text-to-SQL |

---

## 📁 Folder Structure
📦 Agentic-AI-for-Campus  
├── backend/  
│ ├── main.py  
│ ├── query_router.py  
│ ├── formatter.py  
│ ├── schema_context.py  
│ ├── db.py  
│ └── requirements.txt  
│  
├── frontend/  
│ ├── index.html  
│ ├── script.js  
│ ├── chatbot-script.js  
│ ├── styles.css  
│  
├── README.md  
└── Project_Report.pdf 

**📌 Current Modules (Completed**)

1. General Campus Queries
2. Student Information Module
3. Teacher Information Module
4. Timetable Module
6. Secure Login System

**🚀 Future Scope**
1. Automated Notifications (exam alerts, attendance shortage, deadlines)
2. Full ERP Integration (Android/iOS app)
3. Academic Modules (CGPA, grades, electives)
4. Faculty Dashboard

**🤝 Contributors - Team 83 – Ganpat University**

**Shashank Singh (22012011105) : Backend Master
Sesha (22012021071) : UI-UX & Documentation Master
Archie (22012011073) : Database Master**

**🏆 Project Status**

✔ Fully working minor project
🔧 Ready to be extended as a full Campus ERP AI system
