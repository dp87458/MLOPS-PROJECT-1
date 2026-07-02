import os
import sys
import pandas as pd
import boto3
from sklearn.model_selection import train_test_split

from src.logger import get_logger
from src.custom_exceptions import CustomException

from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        # Extracts specific structural map parameters out of your config object dictionary
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        # Creates the 'artifacts/raw' path directories if they don't exist yet
        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data ingestion started with {self.bucket_name} and file is {self.file_name}")

    def download_csv_from_aws(self):
        """Downloads the raw hotel dataset from AWS S3 storage"""
        try:
            logger.info("Initializing AWS S3 client channel...")
            s3_client = boto3.client('s3') # Establishes your local programmatic access link to AWS

            logger.info(f"Downloading file '{self.file_name}' from bucket '{self.bucket_name}'...")
            
            # Downloads your source data object down locally into RAW_FILE_PATH
            s3_client.download_file(
                Bucket=self.bucket_name,
                Key=self.file_name,
                Filename=RAW_FILE_PATH
            )
            logger.info(f"Successfully downloaded and saved file to: {RAW_FILE_PATH}")
            return RAW_FILE_PATH

        except Exception as e:
            logger.error("Exception hit while pulling file down from AWS S3 bucket")
            raise CustomException(e, sys)

    def split_data(self):
        """Splits the raw download file into independent Train and Test files"""
        try:
            logger.info("Starting the splitting process")
            data = pd.read_csv(RAW_FILE_PATH) # Loads raw data from disk into a DataFrame memory matrix

            # Calculations: 1 - 0.8 leaves exactly 0.20 (20%) allocation for testing
            train_data, test_data = train_test_split(data, test_size=1 - self.train_test_ratio, random_state=42)

            # Saves the split matrices back onto disk safely as CSV format files without adding index numbers
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)

            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")

        except Exception as e:
            logger.error("Error while splitting the data")
            raise CustomException(e, sys)
    
    def run(self):
        """Orchestrates the individual ingestion methods sequentially"""
        try:
            logger.info("Starting data ingestion process")

            self.download_csv_from_aws() # Step 1: Download data
            self.split_data()            # Step 2: Split data

            logger.info("Data Ingestion completed successfully")

        except CustomException as ce:
            logger.error(f"CustomException caught: {str(ce)}")

        finally:
            logger.info("Data Ingestion batch pipeline sequence finished")

if __name__ == "__main__":
    # 1. Reads YAML parameters 2. Boots Ingestion Instance 3. Executes process run
    data_ingestion = DataIngestion(read_yaml(CONFIG.PATH))
    data_ingestion.run()
