pipeline {
    agent any

    environment {
        IMAGE_NAME = 'aceest-fitness'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python syntax check') {
            steps {
                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m py_compile app.py tests\\test_app.py'
            }
        }

        stage('Install dependencies and test') {
            steps {
                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
                bat '"C:\\Users\\Nivedhitha\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest -v'
            }
        }

        stage('Build Docker image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Run tests in Docker') {
            steps {
                bat 'docker run --rm %IMAGE_NAME%:%BUILD_NUMBER% python -m pytest -v'
            }
        }
    }

    post {
        always {
            echo 'ACEest Fitness pipeline finished. Check the stage results above.'
        }
    }
}
