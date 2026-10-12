# Bad Debt Prediction Using Machine Learning

A machine learning application that predicts the likelihood of bad debt for customers using a trained LightGBM classification model. The project includes a FastAPI backend for prediction services, a Streamlit dashboard for customer risk analysis, and Docker containers for deployment.

## Project Overview

The objective of this project is to identify customers who may have a higher risk of bad debt by analyzing customer-related features. The trained machine learning model generates a bad-debt probability, which is used to classify customers into risk categories.

The application provides a web-based dashboard and REST API, making the prediction workflow accessible through an interactive interface.

## Key Features

- **Machine Learning:** LightGBM classification model for bad-debt prediction.
- **Feature Engineering:** Uses a selected set of 50 features for model inference.
- **Customer Risk Analysis:** Generates bad-debt probabilities and risk classifications.
- **REST API:** FastAPI endpoints for health monitoring and customer predictions.
- **Interactive Dashboard:** Streamlit interface for customer-level predictions.
- **Docker Support:** Separate containers for the API and dashboard.
- **Docker Compose:** Runs and manages both services together.
- **Docker Hub:** Published container images for deployment.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.11 |
| Machine Learning | LightGBM, Scikit-learn |
| Data Processing | Pandas, NumPy |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| API Validation | Pydantic |
| Model Serialization | Pickle / Python model artifacts |
| Containerization | Docker, Docker Compose |
| Container Registry | Docker Hub |

## System Architecture

```text
                 User
                   |
                   v
          Streamlit Dashboard
             Port 8501
                   |
                   v
             FastAPI Backend
               Port 8000
                   |
          +--------+---------+
          |                  |
          v                  v
    LightGBM Model      Customer Data
          |                  |
          +--------+---------+
                   |
                   v
       Bad-Debt Probability
       and Risk Classification
```

Docker Compose manages the API and dashboard containers. The dashboard communicates with the API using the internal Docker service address `http://api:8000`.

## Model Information

The final selected model is a LightGBM classifier trained for binary bad-debt prediction.

| Evaluation Metric | Value |
|---|---:|
| Accuracy | 71.74% |
| Precision | 17.18% |
| Recall | 63.06% |
| F1 Score | 27.00% |
| ROC-AUC | 75.49% |

The model prioritizes identifying potential bad-debt cases, with a recall of approximately 63.06%. Its precision of approximately 17.18% indicates that many predicted positive cases may not actually be bad-debt cases. Predictions should therefore support, rather than replace, appropriate business review.

## Project Structure

```text
Bad Debt Prediction/
│
├── deployment/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── config.py
│   │   ├── inference.py
│   │   ├── schemas.py
│   │   └── utils.py
│   │
│   ├── streamlit_app.py
│   └── requirements.txt
│
├── deployment_artifacts/
│   ├── deployment_scoring_data.csv
│   ├── customer_display_data.csv
│   ├── top50_feature_columns.pkl
│   └── deployment_metadata.pkl
│
├── Best_LightGBM_Model.pkl
├── Dockerfile.api
├── Dockerfile.streamlit
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── main.py
├── main.ipynb
├── requirements.txt
└── README.md
```

The structure above describes the intended deployment layout. Include only files that exist in your repository.

## Running the Application Locally

### Prerequisites

- Python 3.11
- Docker Desktop
- Docker Compose

### Option 1: Run with Docker Compose

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Bad_Debt_Prediction
```

Build and start the application:

```bash
docker compose up --build -d
```

Check the container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

### Option 2: Run the FastAPI Backend Locally

Activate your Python environment and install the deployment dependencies:

```bash
pip install -r deployment/requirements.txt
```

Start the backend from the deployment directory:

```bash
cd deployment
python -m uvicorn app.api:app --reload
```

The backend will be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Run the Streamlit Dashboard Locally

Keep the API running in one terminal. Open another terminal, activate the same Python environment, and run:

```bash
cd deployment
python -m streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

When running locally, the dashboard uses `http://127.0.0.1:8000` as its default API address.

## Docker Hub Images

The project has two published Docker images.

### FastAPI Backend

Repository: [omprasathv/bad-debt-api](https://hub.docker.com/r/omprasathv/bad-debt-api)

```bash
docker pull omprasathv/bad-debt-api:latest
```

### Streamlit Dashboard

Repository: [omprasathv/bad-debt-dashboard](https://hub.docker.com/r/omprasathv/bad-debt-dashboard)

```bash
docker pull omprasathv/bad-debt-dashboard:latest
```

To run the application on another computer, configure Docker Compose to use these published images instead of local `build` instructions. Ensure that the required model and data artifacts are available inside the API container and that the dashboard's `API_BASE_URL` is set to `http://api:8000`.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Checks service and model/data loading status |
| `/predict-by-customer` | POST | Predicts bad-debt risk for a customer |

Interactive API documentation is available at `/docs` while the API is running. Use the documented request schema to test the prediction endpoint.

## Deployment

The application is containerized using separate Docker images for the API and dashboard. Docker Compose coordinates service startup, networking, port mapping, and the API health check.

The published images can be pulled onto a cloud virtual machine with Docker installed. A cloud deployment also requires appropriate network security rules and a configuration that exposes the dashboard safely.

For production deployment, use HTTPS, restrict access to backend endpoints, protect sensitive data, and configure appropriate authentication and monitoring.

## Important Considerations

- The model's precision is relatively low, so predicted risk should not be treated as a definitive lending decision.
- Model performance may change when the application receives data that differs from its training data.
- Customer records and serialized model artifacts may contain sensitive information. Do not publish confidential data or credentials in a public repository.
- Keep dependencies and deployment configuration version-controlled so that the environment can be reproduced.

## Future Improvements

- Add model performance monitoring and prediction logging.
- Introduce authentication and authorization.
- Configure HTTPS and a custom domain.
- Automate testing and deployment using CI/CD.
- Monitor model drift and periodically evaluate model performance.
- Improve precision through threshold tuning and model evaluation.

## Author

**Omprasath V**

Aspiring Data Scientist | Machine Learning | Deep Learning | Generative AI

GitHub: [Omprasath26](https://github.com/Omprasath26)

