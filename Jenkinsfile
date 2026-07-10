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
                    # 1. PERMANENT FIX: Automatically install Python3 system-wide if missing
                    if ! command -v python3 &> /dev/null; then
                        echo "Python3 not found inside container. Installing now..."
                        apt-get update && apt-get install -y python3 python3-venv
                    fi
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
                        . venv/bin/activate
                        pip install --no-cache-dir --break-system-packages awscli

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
        stage('Deploy to AWS ECS') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        echo 'Deploying Hotel App Container Live to AWS ECS Fargate.............'
                        sh """
                        # 1. Instruct AWS to create a clean, free-tier container cluster space
                        aws ecs create-cluster --cluster-name mlops-project-1-cluster --region eu-north-1

                        # 2. Register your exact ECR container image configuration blueprint
                        aws ecs register-task-definition \
                            --family mlops-project-1-task \
                            --network-mode awsvpc \
                            --requires-compatibilities FARGATE \
                            --cpu "256" \
                            --memory "512" \
                            --execution-role-arn "arn:aws:iam::043671580149:role/ecsTaskExecutionRole" \
                            --container-definitions '[{
                                "name": "mlops-project-1",
                                "image": "043671580149.dkr.ecr.eu-north-1.amazonaws.com/mlops-project-1:latest",
                                "portMappings": [{
                                    "containerPort": 8080,
                                    "hostPort": 8080
                                }]
                            }]' \
                            --region eu-north-1
                        """
                    }
                }
            }
        }
    }
}