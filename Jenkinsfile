pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Rajesh-210/travels-python.git'
            }
        }

        stage('Check Required Tools') {
            steps {
                sh "docker --version"
                sh "python3 --version || true"
                sh "pip3 --version || true"
            }
        }

        stage('Navigate & List Files') {
            steps {
                sh """
                    echo "Listing project files..."
                    ls -la
                """
            }
        }

        stage('Docker Build Image') {
            steps {
                sh """
                    echo "Building Docker image for travels-python..."
                    docker build -t travels-python-image .
                """
            }
        }

        stage('Docker Run Container') {
            steps {
                sh """
                    echo "Stopping existing container if running..."
                    docker rm -f travels-python-container || true

                    echo "Starting new container..."
                    docker run -d --name travels-python-container -p 5000:5000 travels-python-image
                """
            }
        }

    }
}
