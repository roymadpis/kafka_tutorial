pipeline {
    agent any

    environment {
        // We use a fixed name inhere to ensure that the same contaniers are reused across stages,
        // and we can easily access them from the host machine.
        COMPOSE_PROJECT_NAME = "kafka-tutorial-stack"
        APP_TAG = "v${env.BUILD_NUMBER}" 
    }

    stages {
        stage('Checkout-grab-code') {
            steps {
                // Go to the repository I defined in the project settings, and download the code into this workspace
                checkout scm
            }
        }
        stage('Cleanup Previous Run') {
            steps {
                echo 'Removing any old containers from previous builds...'
                // 'down' stops and removes containers/networks. 
                // We add || true so it doesn't fail if nothing exists yet.
                sh 'docker compose down -v || true'
                sh "APP_TAG=${env.APP_TAG} docker compose up -d --build"
            }
        }


        stage('Build & docker Up') {
            steps {
                // This will build the Docker image for the driver and start both the Kafka and driver containers.
                // This tells Docker to look for a file named docker-compose.yaml in the current directory.
                // It readss the instructions and starts creating the "Desired State" (i.e., making sure Kafka and the App we are running).
                echo 'Starting services...'
                echo "Deploying version ${env.APP_TAG} to fixed containers..."
                sh "APP_TAG=${env.APP_TAG} docker compose up -d --build"
            }
        }

        stage('Health Check') {
            steps {
                // This is a simple health check to ensure that Kafka is up and running before we proceed.
                echo 'Waiting for Kafka...'
                sleep 15 
            }
        }

        stage('Verify') {
            steps {
                // This is just to verify that the containers are up and running.
                // We should see both the Kafka and driver containers in the output.
                sh 'docker compose ps'
                sh 'docker compose logs --tail=10 app' // Show the last 10 lines of the driver logs to verify it's running and connecting to Kafka.
            }
        }
    }

    post {
        success {
            echo "Successfully deployed! Access Kafka at localhost:9092"
        }
        failure {
            echo 'Build failed. Cleaning up failed attempt...'
            sh 'docker compose down -v'
        }
    }
}