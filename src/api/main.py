# src/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import mlflow
from mlflow import MlflowClient

# Load environment variables

load_dotenv() # reads .enc in project root

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI_DOCKER")
MODEL_NAME = "iris_model"
MODEL_ALIAS = "Production"

app = FastAPI(title="ML Factory API")

print(80*"-")
print(MLFLOW_URI)
print(80*"-")

# MLflow client
client = MlflowClient(tracking_uri=MLFLOW_URI)

# cache for hot-reloading
state = {
    "model": None,
    "version": None
}

# Input SCHEMAS for the API
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# utilities
def load_production_model():
    """Load current Production model from MLflow"""

    try:
        alias_info = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        prod_version = alias_info.version

        if state["model"] is None or state["version"] != prod_version:
            print(f"Loading model version {prod_version} from MLflow...")
            model_uri =f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
            state["model"] = mlflow.pyfunc.load_model(model_uri)
            state["version"] = prod_version
        
        return state["model"], state["version"]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"MLflow error:{str(e)}")
    
# routes
@app.get("/")
def api_landing():
    return {"ML Factory API is up and running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(input_data: IrisInput):
    model, version = load_production_model()
    features = [[
        input_data.sepal_length,
        input_data.sepal_width,
        input_data.petal_length,
        input_data.petal_width
    ]]
    prediction = model.predict(features)
    #probabilities = model.predict_proba(features)

    IRIS_CLASSES = ["setosa", "versicolor", "virginica"]

    return {
        "prediction": int(prediction[0]),
        #"probabilities": probabilities[0],
        "species": IRIS_CLASSES[int(prediction[0])],
        "model_version": version
    }
