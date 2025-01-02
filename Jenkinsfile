pipeline {
    agent any
    environment {
        GIT_URL = 'https://github.com/MuhammadIshaqSkd/chair-be'
        BRANCH = 'development'
        CREDENTIALS_ID = '3388'
    }
    stages {
        stage('Checkout') {
            steps {
                git(
                    branch: "${BRANCH}",
                    url: "${GIT_URL}",
                    credentialsId: "${CREDENTIALS_ID}"
                )
            }
        }

        stage('Run Docker Commands') {
            steps {
                script {
                   echo "Stopping existing containers.."
                    sh 'docker-compose -f docker-compose-dev.yaml down'
                    echo "Building new images..."
                    sh 'docker-compose -f docker-compose-dev.yaml build'
                    echo "Starting containers..."
                    sh 'docker-compose -f docker-compose-dev.yaml up -d'
                }
            }
        }
        // Optional: If you want to archive something, specify file patterns here

    }
}
