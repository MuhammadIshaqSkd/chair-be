pipeline {
    agent any
    environment {
        GIT_URL = 'https://github.com/MuhammadIshaqSkd/chair-be'
        BRANCH = 'development'
        CREDENTIALS_ID = '338'
        PROJECT_DIR = '/var/jenkins_home/chair-be'
    }
    stages {
         stage('Checkout') {
            steps {
                dir("${PROJECT_DIR}") {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: "${BRANCH}"]],
                        userRemoteConfigs: [[url: "${GIT_URL}", credentialsId: "${CREDENTIALS_ID}"]]
                    ])
                }
            }
        }
        stage('Run Docker Commands') {
            steps {
                script {
                    echo "Stopping existing containers.."
                    echo "Building new images..."
                    echo "Starting containers..."
                }
            }
        }
        // Optional: If you want to archive something, specify file patterns here

    }
}
