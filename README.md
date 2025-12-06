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

### 🔹 Room Availability Module
- Free classrooms:
  - **Right now**
  - **Between specific time ranges**

### 🔹 Authentication
- Secure login (admin/student)  
- Role-based access control  

---

## 🧠 System Architecture

> ### 🖼️ **System Architecture Diagram**  
> *(Placeholder – image will be added later)*  
>  
> `![System Architecture Diagram](assets/architecture.png)`

---

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

