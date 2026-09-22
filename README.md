# AgenticAI_Chatbot_Using_LangGraph

# 🚀 CI/CD Deployment of Agentic Chatbot on AWS

This project demonstrates the deployment of an **Agentic Chatbot built with LangGraph** using **Docker, GitHub Actions, Docker Hub, and AWS EC2**.

The CI/CD pipeline automates the process of building the Docker image, pushing it to Docker Hub, and deploying the application on an AWS EC2 instance.

## 🏗️ Deployment Architecture

GitHub Repository
        ↓
GitHub Actions
        ↓
Build Docker Image
        ↓
Push Image to Docker Hub
        ↓
AWS EC2 (Ubuntu)
        ↓
Pull Docker Image
        ↓
Run Docker Container
        ↓
Streamlit Application :8501

## 🔄 Deployment Steps

### 1. Login to AWS Console

Login to your AWS account and open the AWS Management Console.

### 2. Create IAM User for Deployment

Create an IAM user with the required permissions for deployment.

Example policy:

```text
AmazonEC2FullAccess

3. Create an EC2 Machine
Create an Ubuntu-based AWS EC2 instance.
Configure the required security group rules and allow application traffic on:

Port: 8501



4. Install Docker on EC2
Connect to the EC2 instance and execute:

sudo apt-get update -y

sudo apt-get upgrade

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker


5. Configure GitHub Actions Self-Hosted Runner
Configure the EC2 instance as a GitHub Actions self-hosted runner.
Navigate to:

GitHub Repository
    → Settings
    → Actions
    → Runners
    → New self-hosted runner


6. Configure GitHub Actions Secrets
Add the required secrets under:

GitHub Repository
    → Settings
    → Secrets and variables
    → Actions
    → New repository secret



REGISTRY=docker.io

DOCKER_USERNAME=<your-dockerhub-username>

DOCKER_PASSWORD=<your-dockerhub-access-token>

IMAGE_NAME=agentic-chatbot

AWS_ACCESS_KEY_ID=<your-aws-access-key>

AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>

AWS_REGION=us-east-1

OPENAI_API_KEY=<your-openai-api-key>

TAVILY_API_KEY=<your-tavily-api-key>

OPENWEATHER_API_KEY=<your-openweather-api-key>

GOOGLE_API_KEY=<your-google-api-key>

LANGSMITH_TRACING=true

LANGSMITH_ENDPOINT=https://api.smith.langchain.com

LANGSMITH_API_KEY=<your-langsmith-api-key>

LANGSMITH_PROJECT=agentic-chatbot-project



🐳 Docker Deployment

The application is packaged into a Docker image and pushed to Docker Hub.
On the EC2 instance, the Docker image can then be pulled using:

docker pull <dockerhub-username>/agentic-chatbot:latest

Run the container with port mapping:

docker run -d \
  -p 8501:8501 \
  --name agentic-chatbot \
  <dockerhub-username>/agentic-chatbot:latest

EC2 Port 8501 → Docker Container Port 8501


🔑 Technologies Used
- Python
- LangGraph
- LangChain
- Streamlit
- Docker
- Docker Hub
- GitHub Actions
- GitHub Self-Hosted Runner
- AWS EC2
- AWS IAM
- OpenAI API
- Tavily API
- OpenWeather API
- Google API
- LangSmith