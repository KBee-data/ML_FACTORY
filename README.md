# 🏭 ML Factory – Containerized MLOps Pipeline

## 🎯 Project Overview

This project demonstrates a **containerized MLOps architecture** where:

* Models are trained, tracked, and versioned using **MLflow**
* Artifacts are stored in **MinIO (S3-compatible storage)**
* Predictions are served via a **FastAPI backend**
* A **Streamlit frontend** allows easy interaction with the model

The key idea is to **decouple model training, storage, and serving**, enabling flexible and production-like workflows.

---

## 🏗️ Architecture

The system is composed of several independent services orchestrated with Docker:

```
ml-factory-project/
├── data/
│   └── iris_test.csv          # Sample data for testing
├── src/
│   ├── api/                   # FastAPI backend (main.py + Dockerfile)
│   ├── front/                 # Streamlit UI (streamlit_app.py + Dockerfile)
│   └── train/                 # Model training script (train.py)
├── docker-compose.yml         # Multi-service orchestration
├── pyproject.toml             # Dependencies (managed with uv)
├── uv.lock                    # Locked dependencies
├── README.md
└── .env                       # Environment variables
```

### 🔧 Core Components

* **MLflow:** Model registry + experiment tracking


* **MinIO:** Object storage for model artifacts (S3-compatible)

* **PostgreSQL:** Backend database for MLflow metadata

* **FastAPI (API):** Loads the latest model from MLflow and serves predictions

* **Streamlit (Frontend):**  UI for testing predictions

---

## ⚙️ Configuration

### `.env`

Centralized configuration file used by Docker Compose.

Contains variables such as:

* `MLFLOW_TRACKING_URI_DOCKER=http://mlflow:5001`
* `MLFLOW_S3_ENDPOINT_URL_DOCKER=http://minio:9000`
* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`

⚠️ Important:
Inside Docker, services communicate using **service names**, not `localhost`.

---

### `docker-compose.yml`

Defines and connects all services:

* `mlflow` → MLflow server
* `minio` → S3 storage
* `postgres` → MLflow database
* `api` → FastAPI backend
* `streamlit` → frontend UI

Also:

* Injects environment variables into containers
* Maps ports to localhost
* Creates persistent volumes

---

## 🚀 Getting Started

### 1. Prerequisites

* Docker Desktop installed and running
* (Optional) Python 3.11+ for local training

---

### 2. Start the Full Stack

```bash
docker compose up --build
```

This will:

* Build containers
* Start all services
* Initialize networking and volumes

---

## 🌐 Service URLs

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:8501      |
| API Docs | http://localhost:8000/docs |
| MLflow   | http://localhost:5001      |
| MinIO UI | http://localhost:9001      |

MinIO credentials:

```
minioadmin / minioadmin123
```

---

## 🧠 Model Training

### ✅ Recommended (inside Docker)

Run training inside the MLflow container:

```bash
docker exec -it mlflow_server python src/train/train.py
```

This ensures:

* Correct network usage (`minio:9000`, not `localhost`)
* Artifacts are properly stored in MinIO

---

### ⚠️ Important Note

MLflow uses environment variables internally:

* `MLFLOW_TRACKING_URI`
* `MLFLOW_S3_ENDPOINT_URL`

These must point to **Docker services**, not localhost.

---

## 🔄 Inference Flow

1. API queries MLflow for the production model:

   ```
   models:/iris_model_@production
   ```
2. MLflow resolves the alias to a specific model version and returns model location
3. The API downloads model artifacts from MinIO
4. The model is loaded and used to generate predictions via FastAPI

#### ⚠️ Important Note on MLflow Aliases

MLflow UI  **automatically converts aliases to lowercase** when they are set via the UI. This can lead to subtle bugs when trying to set model alias to "Production" manually via MLflow UI.

If your API uses:
```python 
MODEL_ALIAS = "Production"
```
But MLflow stores:
```python
production
```
👉 The API will **fail to find the model**

#### ✅ Solution
Always use **lowercase aliases** in API code:

```python
MODEL_ALIAS = "production"
```
---
## 🔁 Model Promotion Modes (Automatic vs Manual)

This project supports two ways of promoting models to production using MLflow aliases.

---

### ⚡ Automatic Mode (Default)

By default, the training script automatically assigns the latest trained model to the `production` alias.

```python
AUTOMATION_MODE = True
```

After training:

* The newest model version is immediately set as `production`
* The API automatically uses this model for predictions

✔ This ensures a fully automated pipeline

---

### 🧪 Manual Mode (via MLflow UI)

To manually control which model is used in production:

1. Open `src/train/train.py`
2. Set:

```python
AUTOMATION_MODE = False
```

3. Run the training script again in Docker container: 
```bash
docker exec -it mlflow_server python src/train/train.py
```
  → The new model will be registered **without changing the production alias**

4. Open MLflow UI:

```
http://localhost:5001
```

5. Go to:

   * **Models → iris_model_**
   * Select the desired version
   * Assign the alias: `production`


####  Result

* The API dynamically loads:

  ```
  models:/iris_model@production
  ```
* Switching the alias in MLflow instantly updates the model used by the API
* No container restart is required

---

## 🧪 Example Usage

### Test prediction via Swagger:

Go to:

```
http://localhost:8000/docs
```

Use `/predict` endpoint with sample input.

---

## 🛠️ Useful Commands

### View logs

```bash
docker compose logs -f api
docker compose logs -f mlflow
```

---

### Stop everything

```bash
docker compose down
```

---

### Clean volumes (full reset)

```bash
docker compose down -v
```

---

## ⚠️ Common Pitfall (Important)

If you see errors like:

```
Could not connect to http://localhost:9000
```

👉 It means a service is using `localhost` instead of `minio`

✔ Fix by ensuring:

```
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
```

inside Docker containers.

---

## ✅ Key Takeaways

* Docker networking ≠ localhost
* MLflow separates:

  * metadata (PostgreSQL)
  * artifacts (MinIO)
* Training environment must match serving environment
* Correct environment variables are critical

---

## 🎉 Final Result

A fully working **end-to-end MLOps pipeline** with:

* Experiment tracking
* Model registry
* Artifact storage
* API serving
* Frontend interface

All running in Docker 🚀
