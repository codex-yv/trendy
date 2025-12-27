# 🚀 BeeHive - Open Source Collaboration Platform

## 💡 Project Overview

BeeHive is a web-based collaboration and team management system designed to help startups, freelancers, hackathon teams, and coding groups work efficiently under a single, unified platform. Built using HTML, CSS, JavaScript, and Python, the system focuses on **clarity, collaboration, and momentum** — three essential elements every growing team needs.

## 🎯 What Problem Does It Solve?

Managing teams becomes difficult when:
- **Tasks are scattered** across multiple tools(like paper, excel, etc.)
- **Communication lacks structure** and organization
- **Team leaders can't track progress** clearly
- **Remote collaboration feels disconnected**

This project solves these challenges by providing **integrated task management, leadership hierarchy, and real-time collaboration** in one cohesive platform.

## ✨ Key Features

### 👥 Team & Leadership Management
- Create teams with one or multiple team leaders
- Assign roles and responsibilities clearly
- Visual organization and team directories

### 📋 Task & Project Assignment
- Assign tasks and projects to specific team members
- Track progress with visual indicators
- Set deadlines and priority levels
- Get real-time notifications for task/project updates

### 💬 Community Chat Room
- Built-in real-time team chat system
- File sharing and media support [Currently working on it]
- Encourages open discussion, brainstorming, and problem-solving
- Centralized and transparent communication

### 🔓 Fully Open Source & Self-Hostable
- 100% open source — no vendor lock-in
- Deploy it for your own team or organization
- Host locally or on your preferred cloud platform
- Customize, extend, and scale freely
- Community-driven development

## 🎯 Target Users

This system is especially useful for:

- **🚀 Startups** managing small to medium teams
- **💼 Freelancing teams** working remotely
- **🧑‍💻 Hackathon groups** collaborating under time pressure
- **👨‍👩‍👧‍👦 Coding communities & student teams**
- **📚 Educational groups** working on projects together

## 🛠️ Tech Stack

### Frontend
- **HTML5** 
- **CSS3** 
- **JavaScript (ES6+)** 

### Backend
- **Python** 
- **FastAPI** 

### Architecture
- Lightweight and modular design
- RESTful API architecture
- Real-time communication capabilities
- Extensible plugin system

## 🌱 Project Vision

The goal of BeeHive is to create a simple yet powerful collaboration tool that:

- **Reduces friction** in teamwork and coordination
- **Encourages transparency** and open communication
- **Empowers teams** without forcing them into closed ecosystems
- **Adapts to various workflows** and team structures
- **Thrives on community contributions** and shared innovation

## 📦 Getting Started
### Setup

- **Step-1**: Clone the repository
- **Step-2**: Navigate to project directory
- **Step-3**: Create a .env file
- **Step-4**: Add the following variables to the .env file

```
MONGO_URI = "mongodb://localhost:27017"
SENDGRID_API_KEY = "your_sendgrid_api_key"
EMAIL = "your_email" 
DOC_USERNAME = "your_doc_username" # it can be anything
DOC_PASSWORD = "your_doc_password" # it can be anything

ADMIN_USERNAME = "admin" # create a admin username
ADMIN_PASSWORD = "admin" # create a admin password

DEV_ID = "your_dev_id" # it can be anything

```
- **Step-5**: Create a virtual environment (optional but recommended)
- **Step-6**: Activate the virtual environment
- **Step-7**: Install dependencies
- **Step-8**: Run the application

### Installation
```bash
# Clone the repository
git clone https://github.com/codex-yv/bee_hive.git

# Navigate to project directory
cd bee_hive

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On macOS and Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

## 🤝 Contributing
We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
- 🐛 Bug Fixes - Identify and fix issues
- ✨ New Features - Add requested or innovative features
- 🎨 UI Improvements - Enhance the user experience
- 📚 Documentation - Improve guides and documentation
- 🔧 Performance Optimizations - Make the platform faster

**Built with ❤️ by the open source community**

**Star this repository if you find it helpful!**
