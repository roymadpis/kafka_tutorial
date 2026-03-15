pipeline {
    agent any

    environment {
        // Ensuring docker-compose uses the current build ID for uniqueness
        COMPOSE_PROJECT_NAME = "build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Up') {
            steps {
                echo 'Starting services with Docker Compose...'
                // --build ensures your packet-app is re-compiled
                // -d runs it in the background
                sh 'docker compose up -d --build'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Waiting for Kafka to be ready...'
                // Small sleep or a script to wait for port 9092
                sleep 15 
            }
        }

        stage('Verify Pipeline') {
            steps {
                echo 'Running integration tests or logs check...'
                // Example: check if your packet-app is actually running
                sh 'docker compose ps'
                sh 'docker compose logs packet-app'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up containers...'
            // -v removes volumes so Kafka data doesn't persist between builds
            // sh 'docker-compose down -v'
        }
        success {
            echo 'Build and Deployment successful!'
        }
        failure {
            echo 'Build failed. Check the logs above.'
        }
    }
}