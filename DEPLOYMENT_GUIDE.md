# 🌐 Deployment Guide

Complete guide to deploying your RAG Embedding Visualizer using Docker.

## 🎯 Deployment Options

| Platform                  | Difficulty    | Cost                | Best For                  |
| ------------------------- | ------------- | ------------------- | ------------------------- |
| Docker (Local)            | ⭐ Easy       | Free                | Development, testing      |
| Google Cloud Run          | ⭐⭐ Medium   | Pay-as-you-go       | Scalability, auto-scaling |
| AWS ECS/Fargate           | ⭐⭐⭐ Medium | Pay-as-you-go       | Enterprise, AWS ecosystem |
| Azure Container Instances | ⭐⭐ Medium   | Pay-as-you-go       | Azure ecosystem           |
| Render                    | ⭐⭐ Easy     | Free tier available | Quick deployments         |

---

## 🐳 Docker Deployment (Recommended)

**Best for**: Full control, consistency across environments, scalable

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (included with Docker Desktop)
- Basic Docker knowledge

### Local Development

#### 1. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The app will be available at `http://localhost:8501`

#### 2. Or Build Manually

```bash
# Build the Docker image
docker build -t rag-visualizer .

# Run the container
docker run -p 8501:8501 rag-visualizer

# Run in background
docker run -d -p 8501:8501 --name rag-viz rag-visualizer

# Stop the container
docker stop rag-viz
docker rm rag-viz
```

### Docker Configuration

#### Dockerfile Details

- **Base**: Python 3.11-slim (lightweight)
- **Package Manager**: uv (10-100x faster than pip)
- **Size**: ~2GB (includes PyTorch and models)
- **Health Check**: Automatic via Streamlit endpoint
- **Port**: 8501

#### Customization

Edit `Dockerfile` to:

- Change Python version
- Add system dependencies
- Modify entrypoint

Edit `docker-compose.yml` to:

- Change port mapping
- Add environment variables
- Configure restart policy

### Troubleshooting Docker

**Issue**: Container won't start

```bash
# Check logs
docker logs rag-visualizer

# Rebuild without cache
docker-compose up -d --build --force-recreate
```

**Issue**: Port already in use

```bash
# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead
```

**Issue**: Out of memory

```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use OpenAI embeddings (Cloud) in the app to avoid loading a local model
```

---

## ☁️ Google Cloud Run

**Best for**: Auto-scaling, pay-per-use, Google Cloud ecosystem

### Prerequisites

- Google Cloud account
- gcloud CLI installed
- Project created in GCP

### Deployment Steps

#### 1. Install and Configure gcloud

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Enable Required APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

#### 3. Build and Deploy

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-visualizer

# Deploy to Cloud Run
gcloud run deploy rag-visualizer \
  --image gcr.io/YOUR_PROJECT_ID/rag-visualizer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8501 \
  --timeout 300 \
  --max-instances 10
```

#### 4. Access Your App

Your app will be available at: `https://rag-visualizer-XXXXX-uc.a.run.app`

### Cloud Run Configuration

**Memory & CPU**:

- Minimum: 1Gi memory, 1 CPU (MiniLM model)
- Recommended: 2Gi memory, 2 CPU (all models)

**Scaling**:

```bash
# Set min/max instances
gcloud run services update rag-visualizer \
  --min-instances 0 \
  --max-instances 10
```

**Custom Domain**:

```bash
gcloud run domain-mappings create \
  --service rag-visualizer \
  --domain yourdomain.com
```

### Cost Optimization

- Set `--min-instances 0` for true pay-per-use
- Use smaller model (MiniLM) to reduce memory
- Set `--timeout 60` for faster cold starts
- Monitor usage in GCP Console

---

## 🐳 Docker Deployment

**Best for**: Full control, custom infrastructure

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY app.py .
COPY .streamlit .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Build and Test Locally

```bash
# Build image
docker build -t rag-visualizer .

# Run container
docker run -p 8501:8501 rag-visualizer

# Test at http://localhost:8501
```

### 3. Deploy to Google Cloud Run

```bash
# Install Google Cloud SDK
# Configure project: gcloud config set project YOUR_PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-visualizer

# Deploy
gcloud run deploy rag-visualizer \
  --image gcr.io/YOUR_PROJECT_ID/rag-visualizer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

## 🔧 Environment Variables

For sensitive configurations, use environment variables:

### Streamlit Cloud

Settings → Secrets → Add:

```toml
# .streamlit/secrets.toml (for local dev)
# Secrets (for Streamlit Cloud)

[default]
model_cache_dir = "./models"
max_file_size = 10
```

Access in code:

```python
import streamlit as st
cache_dir = st.secrets.get("default", {}).get("model_cache_dir", "./models")
```

### Hugging Face Spaces

Settings → Repository secrets:

- Add `KEY=VALUE` pairs
- Access via `os.environ['KEY']`

---

## 📊 Performance Optimization

### For All Platforms

**1. Model Caching**

```python
@st.cache_resource
def load_model(model_name: str):
    return SentenceTransformer(model_name)
```

**2. Reduce Model Size**

- Use `all-MiniLM-L6-v2` (80MB) instead of larger models
- Quantize models if needed

**3. Limit Upload Size**

```python
# In app.py
st.file_uploader("Upload", type=['txt'],
                 help="Max 5MB")
```

**4. Add Loading States**

```python
with st.spinner("Processing..."):
    # expensive operation
```

### Platform-Specific

**Streamlit Cloud**:

- Use `@st.cache_data` for data operations
- Keep dependencies minimal
- Monitor app usage in dashboard

**Hugging Face**:

- Consider GPU for large models
- Use persistent storage for frequently used models

**Docker**:

- Multi-stage builds to reduce image size
- Use `.dockerignore` to exclude unnecessary files

---

## 🔒 Security Best Practices

1. **No hardcoded secrets**: Use environment variables
2. **Input validation**: Limit file sizes and types
3. **Rate limiting**: Prevent abuse (add if needed)
4. **HTTPS**: Enabled by default on most platforms
5. **Dependencies**: Keep requirements.txt updated

---

## 📈 Monitoring

### Streamlit Cloud

- Built-in analytics dashboard
- View logs in real-time
- Monitor resource usage

### Custom Monitoring

Add to your app:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Processed {len(chunks)} chunks")
```

---

## 🚀 Post-Deployment Checklist

- [ ] Test all features on deployed version
- [ ] Verify model downloads work
- [ ] Check file upload functionality
- [ ] Test on mobile browser
- [ ] Update README with live URL
- [ ] Add deployment badge
- [ ] Share on social media
- [ ] Monitor for first week

---

## 🆘 Common Deployment Issues

### Memory Errors

```python
# Solution: Use smaller model or upgrade plan
model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Smallest
```

### Timeout During Build

```python
# Solution: Increase timeout or reduce dependencies
# Streamlit Cloud: Contact support
# Docker: Adjust build args
```

### Model Download Fails

```python
# Solution: Pre-download models
# Add to Dockerfile:
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## 🎉 You're Live!

Congratulations! Your app is now deployed. Don't forget to:

1. **Share your URL** on social media
2. **Add to your portfolio**
3. **Collect feedback** from users
4. **Iterate and improve**

Need help? Open an issue on GitHub! 🚀
