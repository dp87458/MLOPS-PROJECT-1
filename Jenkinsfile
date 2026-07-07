pipeline {
    agent any

    options {
        // Tells Jenkins to skip its default automatic clone step
        // This lets you use your custom generated script safely below!
        skipDefaultCheckout()
    }

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins...........'
                    // This is your exact snippet script, with the completed repository URL included
                    checkout scmGit(
                        branches: [[name: '*/main']], 
                        extensions: [], 
                        userRemoteConfigs: [[
                            credentialsId: 'github-token', 
                            url: 'https://github.com'
                        ]]
                    )
                }
            }
        }

        stage('Environment Setup') {
            steps {
                script {
                    echo 'Installing requirements inside Jenkins workspace...'
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
