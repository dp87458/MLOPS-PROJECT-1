import os
import sys  # FIXED: Handles custom exceptions properly
import pandas as pd
import joblib
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.logger import get_logger
from src.custom_exceptions import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data
from scipy.stats import randint

import mlflow
import mlflow.sklearn

logger = get_logger(__name__)

class ModelTraining:

    def __init__(self, train_path, test_path, model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        self.params_dist = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

    def load_and_split_data(self):
        try:
            logger.info(f"Loading data from {self.train_path}")
            train_df = load_data(self.train_path)

            logger.info(f"Loading data from {self.test_path}")
            test_df = load_data(self.test_path)

            X_train = train_df.drop(columns=["booking_status"])
            y_train = train_df["booking_status"]

            X_test = test_df.drop(columns=["booking_status"])
            y_test = test_df["booking_status"]

            logger.info("Data split successfully for Model Training")
            return X_train, y_train, X_test, y_test
            
        except Exception as e:
            logger.error(f"Error while loading data {e}")
            raise CustomException(e, sys)
        
    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initializing our model")

            # FIXED 1: Closed the truncated parenthesis and string parameter keys
            lgbm_model = lgb.LGBMClassifier(random_state=self.random_search_params["random_state"])

            logger.info("Starting our Hyperparameter tuning setup")

            random_search = RandomizedSearchCV(
                estimator=lgbm_model,
                param_distributions=self.params_dist,
                n_iter=self.random_search_params["n_iter"],
                cv=self.random_search_params["cv"],
                # FIXED 2: Forced to 1 instead of reading '-1' to prevent your parallel MemoryError crash
                n_jobs=1,
                verbose=self.random_search_params["verbose"],
                random_state=self.random_search_params["random_state"],
                scoring=self.random_search_params["scoring"]
            )

            logger.info("Fitting data matrix into RandomizedSearchCV...")
            random_search.fit(X_train, y_train)

            logger.info("Hyperparameter tuning completed")

            best_params = random_search.best_params_
            best_lgbm_model = random_search.best_estimator_

            logger.info(f"Best parameters are : {best_params}")
            return best_lgbm_model
            
        except Exception as e:
            logger.error(f"Error while training model {e}")
            raise CustomException(e, sys)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating our model")
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            logger.info(f"Accuracy Score : {accuracy}")
            logger.info(f"Precision Score : {precision}")
            logger.info(f"Recall Score : {recall}")
            logger.info(f"F1 Score : {f1}")

            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
        except Exception as e:
            logger.error(f"Error while evaluating model {e}")
            raise CustomException(e, sys)
        
    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)

            logger.info("Saving the model")
            joblib.dump(model, self.model_output_path)
            logger.info(f"Model saved to {self.model_output_path}")
        except Exception as e:
            logger.error(f"Error while saving model {e}")
            raise CustomException(e, sys)
        
    def run(self):
        try:
            # Connect to a named tracking project experiment window inside MLflow dashboard
            mlflow.set_experiment("Hotel_Reservation_Model_Training")
            
            with mlflow.start_run():
                logger.info("Starting our Model Training pipeline")
                logger.info("Starting our MLFLOW experimentation")

                logger.info("Logging the training and testing dataset to MLFLOW")
                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")

                X_train, y_train, X_test, y_test = self.load_and_split_data()
                best_lgbm_model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(best_lgbm_model, X_test, y_test)
                self.save_model(best_lgbm_model)

                logger.info("Logging the model into MLFLOW")
                mlflow.log_artifact(self.model_output_path)

                logger.info("Logging params and metrics to MLFLOW")
                mlflow.log_params(best_lgbm_model.get_params())
                mlflow.log_metrics(metrics)

                logger.info("Model Training successfully completed")

        except Exception as e:
            logger.error(f"Error in model training pipeline {e}")
            raise CustomException(e, sys)
        
if __name__ == "__main__":
    # FIXED 3: Completed the cut-off final run execution parameters line securely
    trainer = ModelTraining(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    trainer.run()
