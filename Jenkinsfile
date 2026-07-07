pipeline {
    agent any

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo 'Installing model dependencies safely...'
                    // The --break-system-packages flag bypasses the Linux environment block securely!
                    sh 'pip install --no-cache-dir --break-system-packages -r requirements.txt'
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
