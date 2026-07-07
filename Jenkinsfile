pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '043671580149'
        AWS_REGION     = 'eu-north-1'  
        ECR_REPO_NAME  = 'mlops-project-1'
        IMAGE_URI      = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}://${ECR_REPO_NAME}"
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
                    # FIX: Force delete any old, broken corrupted venv folder first!
                    rm -rf venv ${VENV_DIR}

                    python3 -m venv ${VENV_DIR}
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
                        sh """
                        # 1. Automatically check and install AWS CLI system-wide if it was wiped out
                        if ! command -v aws &> /dev/null; then
                            echo "AWS CLI not found. Installing now..."
                            apt-get update && apt-get install -y curl unzip
                            curl "https://amazonaws.com" -o "awscliv2.zip"
                            unzip -q awscliv2.zip
                            ./aws/install --update
                            rm -rf awscliv2.zip aws/
                        fi
                        # 1. Direct login using clean endpoints
                        aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 043671580149.dkr.ecr.eu-north-1.amazonaws.com

                        # 2. Hardcoded tag to completely eliminate any environment string errors
                        docker build -t 043671580149.dkr.ecr.eu-north-1.amazonaws.com/mlops-project-1:latest .

                        # 3. Push it live to your Stockholm repository
                        docker push 043671580149.dkr.ecr.eu-north-1.amazonaws.com/mlops-project-1:latest
                        """
                    }
                }
            }
        }
    }
}