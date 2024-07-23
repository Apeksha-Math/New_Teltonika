pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Clone the repository
                git branch: 'socket_pgm', url: 'https://github.com/Apeksha-Math/New_Teltonika.git'               
            }
        }

        stage('Build') {
            steps {
                // Install dependencies, e.g., for Python (assuming pip is in PATH)
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                // Print a message
                bat 'echo "Running unit tests..."'
                // Run your unit tests
                // bat 'pytest tests/'
            }
        }

       stage('Deploy') { 
            steps {
                echo 'Starting the Deploy Stage'
                echo 'Deploy Stage completed successfully'
            }
        }
    }
    post {
        always {
            echo "Pipeline: ${currentBuild.fullDisplayName}"
            echo "Build ${currentBuild.result}"
            echo "${env.BUILD_URL}"
        }
    }

}
