pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '043671580149'
        AWS_REGION     = 'eu-north-1'  
        ECR_REPO_NAME  = 'mlops-project-1'
        IMAGE_URI      = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}://{ECR_REPO_NAME}"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins...........'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/dp87458/MLOPS-PROJECT-1.git']])
                }
            }
        }

        stage('Setting up our Virtual Environment and installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and installing dependancies...........'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to ECR') {
            steps {
                // Securely binds your AWS secret strings to temporary environment tokens
                withCredentials([
                    string(credentialsId: 'aws-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        echo 'Building and Pushing Docker Image to AWS ECR.............'
                        sh '''
                        # 1. Authenticate Docker directly to your European AWS ECR Registry
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

                        # 2. Build your local Hotel Prediction application container image
                        docker build -t ${IMAGE_URI}:latest .

                        # 3. Push the finalized Docker image live straight to your AWS Cloud repository
                        docker push ${IMAGE_URI}:latest
                        '''
                    }
                }
            }
        }
    }
}