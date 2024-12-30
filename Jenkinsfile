pipeline {
    agent any
    environment {
        GIT_URL = 'https://github.com/MuhammadIshaqSkd/chair-be'
        BRANCH = 'development'
        CREDENTIALS_ID = '338'
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
                    echo "Stopping existing sdfsdf.."
                    echo "Building new images..."
                    echo "Starting containers..."
                }
            }
        }
        // Optional: If you want to archive something, specify file patterns here

    }
}
