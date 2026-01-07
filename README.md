# AIAgentJudge

A distributed competitive programming and AI judge system with automated code evaluation, real-time scoreboard, and multi-worker architecture.

## 📋 Overview

AIAgentJudge is a comprehensive online judge platform designed to automate the evaluation of competitive programming and AI submissions. It  a robust REST API backend, and a distributed worker system for parallel code execution and testing.

## ✨ Features

- **User Authentication**: Register and login functionality with secure JWT tokens
- **Problem Management**: Create and manage coding problems with multiple test cases
- **Submission Handling**: Support for multiple programming languages with automated judging
- **Real-time Scoreboard**: Track user rankings and submission scores
- **Distributed Judge System**: Multi-worker architecture for parallel code execution
- **REST API**: 
- **Docker Support**: Fully containerized with Docker Compose for easy deployment
- **Contest Support**: Built-in contest management with permission controls

## 🏗️ Project Structure


## 🛠️ Tech Stack

### Backend
- **Django 5.1** - Web framework
- **Django REST Framework** - REST API
- **PostgreSQL** - Database
- **Redis** - Message queue & caching
- **JWT** - Authentication

### Frontend
- **HTML5** - Markup
- **JavaScript** - Interactivity
- **Nginx** - Web server

### Worker
- **Python** - Code execution engine
- **Redis Streams** - Job queue
- **Docker** - Isolated execution environment
- **bwrap** - virtualization of submissions

## 📦 Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for local development)
- PostgreSQL 13+
- Redis 7.0+

## 🚀 Installation & Setup

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AiAgentJudge
   ```

2. **Create environment files**
   ```bash
   # Backend configuration
   cat > .env.backend << EOF
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   API_KEY=your-api-key-here
   DATABASE_URL=postgresql://user:password@postgres:5432/aiagentjudge
   REDIS_URL=redis://redis:6379/0
   EOF

   # Database configuration
   cat > .env.database << EOF
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_DB=aiagentjudge
   EOF

   # Worker configuration
   cat > .env.worker1 << EOF
   REDIS_HOST=redis
   REDIS_PORT=6379
   API_KEY=your-api-key-here
   EOF
   ```


3. **Build and start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000


### Judge Script Template

See `Worker/template/judge.py` for the standard judge implementation.
For costume judge implementation(for example interactive problems and ... ) just overload the functions in the class provided by BaseJudge and upload the script for the problem
