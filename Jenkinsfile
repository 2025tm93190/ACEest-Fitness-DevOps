
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        IMAGE_NAME = 'aceest-fitness:latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                bat 'dir'
                bat '\"%PYTHON%\" -m py_compile app.py'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '\"%PYTHON%\" -m pip install -r requirements.txt'
            }
        }

        stage('Run Pytest') {
            steps {
                bat '\"%PYTHON%\" -m pytest tests -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Test Inside Docker') {
            steps {
                bat 'docker run --rm %IMAGE_NAME% python -m pytest tests -v'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed and the Docker image was built.'
        }
        failure {
            echo 'FAILED: Check the stage logs above to find the error.'
        }
    }
}
