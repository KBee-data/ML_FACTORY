# ML_FACTORY/src/train/train.py
import os

if os.getenv("MLFLOW_TRACKING_URI_DOCKER") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Set MLflow env vars properly for both local and Docker
os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI_DOCKER")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL_DOCKER")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")

MLFLOW_TRACKING_URI = os.environ["MLFLOW_TRACKING_URI"]
MLFLOW_S3_ENDPOINT_URL = os.environ["MLFLOW_S3_ENDPOINT_URL"]
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

import mlflow
import mlflow.sklearn
import boto3

from mlflow.tracking import MlflowClient
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
#from sklearn.ensemble import RandomForestClassifier

def prepare_minio():
    """Create bucket if it doesn't exist"""

    s3 = boto3.client(
        "s3", endpoint_url=MLFLOW_S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]

    if "mlflow" not in buckets:
        s3.create_bucket(Bucket="mlflow")
        print("Bucket 'mlflow' created.")

    
def train_and_register():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("iris_experiment_")

    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.25, random_state=42
        )
    
    model_ = LogisticRegression(max_iter=200)
    #model_ = RandomForestClassifier()


    with mlflow.start_run():
        model_.fit(X_train, y_train)

        accuracy = model_.score(X_test, y_test)

        mlflow.log_param("model_type", "logistic_regression")
        mlflow.log_metric("accuracy", accuracy)

        model_name = "iris_model_"

        mlflow.sklearn.log_model(
            sk_model=model_,
            artifact_path="model",
            registered_model_name=model_name
        )

    client = MlflowClient()

    latest_version = client.get_latest_versions(
        model_name,
        stages=["None"]
    )[0].version

    AUTOMATION_MODE = True
    if AUTOMATION_MODE:
        client.set_registered_model_alias(
        model_name,
        "production",
        latest_version
    )


    print(f"Model version {latest_version} set to production")

if __name__ == "__main__":
    prepare_minio()
    train_and_register()