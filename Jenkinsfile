pipeline {
    agent any

    stages {
        stage('Cleanup & Fresh Checkout') {
            steps {
                script {
                    echo 'Force-cleaning old broken workspace cache files...'
                    // This automatically wipes the workspace folder clean every single time!
                    cleanWs()
                }
            }
        }

        stage('Environment Setup') {
            steps {
                script {
                    echo 'Installing model dependencies (LightGBM, Flask, MLflow)...'
                    sh 'pip install --no-cache-dir -r requirements.txt'
                }
            }
        }

        stage('Model Training & MLflow Logging') {
            steps {
                script {
                    echo 'Executing hotel reservation model training pipeline...'
                    sh 'python model_training.py'
                }
            }
        }
    }
}
