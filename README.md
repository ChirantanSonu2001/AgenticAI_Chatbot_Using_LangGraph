# 🤖 Agentic Chatbot using LangGraph

An **Agentic AI Chatbot** built using **LangGraph, LangChain, Streamlit, RAG, Tools, Memory, and Human-in-the-Loop (HITL)**.

The application demonstrates how an agent can understand user queries, use appropriate tools, retrieve information from documents, maintain conversation state, and involve a human when approval is required.

---

## 🚀 Features

- 🤖 **Agentic AI workflow** using LangGraph
- 🧠 **LangChain & LangGraph** based agent architecture
- 💬 **Streamlit** interactive chat interface
- 🔄 **Multi-step agent workflow**
- 🛠️ **Tool integration** for external actions
- 📚 **RAG (Retrieval-Augmented Generation)**
- 🧑‍💻 **Human-in-the-Loop (HITL)** approval workflow
- 💾 **Conversation persistence** using SQLite
- 🧠 **Conversation memory**
- 📊 **LangSmith tracing and observability**
- 🔐 Environment-based API key configuration
- 📦 Dependency management using **uv**
- 🐙 Source code management using **Git & GitHub**

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │   Agent Workflow    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌────────────┐   ┌────────────┐
        │    LLM    │    │    Tools   │   │    RAG     │
        └───────────┘    └────────────┘   └────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conversation Memory │
                    │    / SQLite DB      │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangSmith       │
                    │  Tracing & Eval     │
                    └─────────────────────┘

🛠️ Technology Stack
Category	Technologies
Programming Language	Python
Agent Framework	LangGraph
LLM Framework	LangChain
UI	Streamlit
RAG	LangChain RAG
Vector / Retrieval	FAISS
Embeddings	Hugging Face
Database	SQLite
Observability	LangSmith
Package Manager	uv
Version Control	Git, GitHub


📁 Project Structure
AgenticAI_Chatbot_Using_LangGraph/
│
├── app.py
├── backend.py
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
│
└── chatbot.db
chatbot.db is a local database file and is intentionally excluded from Git using .gitignore.

⚙️ Local Setup
1. Clone the repository
git clone https://github.com/ChirantanSonu2001/AgenticAI_Chatbot_Using_LangGraph.git
Navigate to the project:
cd AgenticAI_Chatbot_Using_LangGraph

2. Install uv
Install uv if it is not already installed.

3. Create the project environment
Run:
uv sync

4. Configure environment variables
Create a .env file in the project root.
Example:
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
GOOGLE_API_KEY=your-google-api-key

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=agentic-chatbot-project

Run the Application
Start the Streamlit application using:
uv run streamlit run app.py

The application will be available at:
http://localhost:8501

🧑‍💻 Human-in-the-Loop

The project demonstrates a Human-in-the-Loop (HITL) workflow using LangGraph.
The agent can pause its execution when human approval is required.
Example flow:
User Request
     ↓
LangGraph Agent
     ↓
Decision / Action
     ↓
Human Approval Required
     ↓
┌───────────────┐
│   Approve?    │
│     Y / N     │
└───────┬───────┘
        │
   ┌────┴────┐
   ▼         ▼
Approve     Reject
   │         │
   ▼         ▼
Continue    Stop

This provides an additional control layer before performing sensitive or important agent actions.

📚 RAG Workflow

The application includes a Retrieval-Augmented Generation workflow.
Document
   ↓
Document Loading
   ↓
Text Splitting
   ↓
Embeddings
   ↓
Vector Store
   ↓
Similarity Search
   ↓
Relevant Context
   ↓
LLM
   ↓
Response

RAG allows the chatbot to retrieve relevant information from the available knowledge source before generating a response.

🧠 Conversation Memory

The chatbot maintains conversation state to support multi-turn interactions.
The project uses SQLite for local persistence.
User Message
     ↓
LangGraph
     ↓
Conversation State
     ↓
SQLite Database
     ↓
Previous Messages
     ↓
Context-aware Response

📊 LangSmith

LangSmith is used for tracing and observing the application's LLM and agent workflows.
It helps in understanding:
- Agent execution
- LLM calls
- Tool calls
- Retrieval steps
- Execution flow
- Debugging
Configure LangSmith through the .env file.


🚀 Deployment Status

✅ Currently Implemented
The following components are currently implemented and tested locally:
- Agentic AI chatbot
- LangGraph agent workflow
- LangChain integration
- Streamlit UI
- RAG workflow
- Tool integration
- Human-in-the-Loop workflow
- SQLite conversation persistence
- LangSmith integration
- uv dependency management
- Git version control
- GitHub repository



🔄 Planned / Future Work

The following deployment components are planned for the next phase:
- 🐳 Docker containerization
- 📦 Docker Hub image publishing
- ☁️ AWS EC2 deployment
- ⚙️ GitHub Actions CI/CD pipeline
- 🏃 GitHub Actions self-hosted runner
- 🔄 Automated Docker image build and deployment
- 🌐 Production deployment of the Streamlit application
Note: Docker, Docker Hub, AWS EC2, and GitHub Actions CI/CD deployment have not been implemented yet. The current version of the application is running locally.


📌 Future Architecture

The planned production deployment architecture is:
GitHub Repository
       ↓
GitHub Actions
       ↓
Docker Build
       ↓
Docker Hub
       ↓
AWS EC2
       ↓
Docker Container
       ↓
Streamlit Application
       ↓
Port 8501
This section represents the planned architecture only and is not currently deployed.



👨‍💻 Author
Chirantan Bhatta
GitHub:
https://github.com/ChirantanSonu2001
