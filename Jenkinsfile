pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies'

                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install --upgrade pip'

                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Build and Syntax Check') {
            steps {
                echo 'Checking Python syntax'

                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m compileall -q app.py'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running Pytest test cases'

                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest -v
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image'

                bat 'docker build -t aceest-fitness .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All pipeline stages completed successfully!'
        }

        failure {
            echo 'FAILURE: A pipeline stage failed. Check Console Output for details.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}