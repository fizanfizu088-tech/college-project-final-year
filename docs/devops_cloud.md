# DevOps & Cloud Deployment Guide
# NLI Manufacturing Infrastructure Chatbot

---

## 1. DOCKER — Containerization

### What is Docker?
Docker packages your application and all its dependencies into a 
single portable unit called a **container**.
This means the chatbot runs identically on any machine — your 
laptop, a server, or the cloud.

### Why Docker for this project?
- No "it works on my machine" problems
- Easy to deploy on any server
- Isolated environment — Python version, libraries all locked in

### Dockerfile
Create a file called `Dockerfile` in your project root:
```dockerfile
# Use official Python base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy project files into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir colorama

# Run the chatbot
CMD ["python", "main.py"]
```

### Docker Commands
```bash
# Build the container image
docker build -t nli-manufacturing-chatbot .

# Run the container
docker run -it nli-manufacturing-chatbot

# Stop the container
docker stop <container_id>
```

### Docker Architecture for this project:
```
Developer Machine
      │
      ▼
┌─────────────────────────────┐
│        Docker Container      │
│  ┌───────────────────────┐  │
│  │   Python 3.12 runtime │  │
│  │   colorama library    │  │
│  │   chatbot/ package    │  │
│  │   data/ JSON files    │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
      │
      ▼
  Factory Terminal / Server
```

---

## 2. CI/CD PIPELINE — Continuous Integration & Deployment

### What is CI/CD?
CI/CD automates the process of testing and deploying your code
every time you make a change.

- **CI (Continuous Integration)** — automatically runs your tests
- **CD (Continuous Deployment)** — automatically deploys if tests pass

### Why CI/CD for this project?
- Every code change is automatically tested (47 tests)
- Prevents broken code from reaching production
- Professional industry standard practice

### GitHub Actions Pipeline
Create this file: `.github/workflows/ci.yml`
```yaml
name: NLI Chatbot CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install colorama pytest

    - name: Run unit tests
      run: |
        python -m pytest tests/ -v

    - name: Check test results
      run: echo "All tests passed. Ready for deployment."
```

### CI/CD Flow:
```
Developer pushes code to GitHub
          │
          ▼
  GitHub Actions triggered
          │
          ▼
  ┌───────────────────┐
  │  1. Setup Python  │
  │  2. Install libs  │
  │  3. Run 47 tests  │
  └───────────────────┘
          │
     ┌────┴────┐
     ▼         ▼
  PASS        FAIL
     │         │
     ▼         ▼
  Deploy    Notify
  to cloud  developer
```

---

## 3. CLOUD DEPLOYMENT — AWS & GCP

### Option A: AWS (Amazon Web Services)

#### Recommended Service: AWS EC2
EC2 is a virtual server in the cloud where you can run your chatbot.
```
Steps to deploy on AWS EC2:

1. Create an AWS account
2. Launch an EC2 instance (choose Ubuntu, t2.micro — free tier)
3. Connect via SSH:
   ssh -i "your-key.pem" ubuntu@your-ec2-ip

4. Install Python on the server:
   sudo apt update
   sudo apt install python3 python3-pip

5. Upload your project:
   scp -r nli_manufacturing/ ubuntu@your-ec2-ip:~/

6. Install dependencies:
   pip3 install colorama

7. Run the chatbot:
   python3 main.py
```

#### AWS Architecture:
```
Internet / Factory Network
          │
          ▼
  ┌───────────────┐
  │   AWS EC2     │
  │   Instance    │
  │               │
  │  Ubuntu OS    │
  │  Python 3.12  │
  │  NLI Chatbot  │
  └───────────────┘
          │
          ▼
   Factory Operator
     Terminal/CLI
```

#### Other Useful AWS Services:
| Service | Use in this Project |
|---|---|
| EC2 | Host the chatbot server |
| S3 | Store log files and JSON data |
| CloudWatch | Monitor chatbot performance |
| IAM | Manage access permissions |

---

### Option B: GCP (Google Cloud Platform)

#### Recommended Service: Google Cloud Run
Cloud Run runs your Docker container without managing servers.
```
Steps to deploy on GCP Cloud Run:

1. Create a GCP account
2. Install Google Cloud SDK
3. Build and push Docker image:
   gcloud builds submit --tag gcr.io/PROJECT_ID/nli-chatbot

4. Deploy to Cloud Run:
   gcloud run deploy nli-chatbot \
     --image gcr.io/PROJECT_ID/nli-chatbot \
     --platform managed \
     --region us-central1
```

#### GCP Architecture:
```
Developer
    │
    ▼
Cloud Build ──► Container Registry
                      │
                      ▼
               Google Cloud Run
               ┌──────────────┐
               │ NLI Chatbot  │
               │  Container   │
               └──────────────┘
                      │
                      ▼
              Factory Operators
```

---

## 4. FULL DEPLOYMENT ARCHITECTURE
```
┌─────────────────────────────────────────────────────┐
│                   DEVELOPMENT                        │
│                                                      │
│  Developer → VS Code → Git Commit → GitHub Push     │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│               CI/CD PIPELINE (GitHub Actions)        │
│                                                      │
│  Pull Code → Install Deps → Run 47 Tests → Pass?    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              CONTAINERIZATION (Docker)               │
│                                                      │
│  Build Image → Tag → Push to Container Registry     │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│           CLOUD DEPLOYMENT (AWS / GCP)               │
│                                                      │
│  EC2 Instance / Cloud Run → Live Chatbot             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              FACTORY FLOOR USAGE                     │
│                                                      │
│  Operators → Terminal → NLI Chatbot → Data          │
└─────────────────────────────────────────────────────┘
```

---

## 5. SUMMARY TABLE

| Technology | Purpose | Benefit |
|---|---|---|
| Docker | Containerize the chatbot | Portable, consistent environment |
| GitHub Actions | Automate testing | Catch bugs before deployment |
| AWS EC2 | Host on cloud server | Always available, scalable |
| AWS S3 | Store logs and data | Persistent, backed up storage |
| GCP Cloud Run | Serverless deployment | No server management needed |
| CloudWatch | Monitor performance | Real-time alerts and metrics |