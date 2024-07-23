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
                // Deploy to your server, e.g., using SCP or SSH equivalent on Windows
                bat '''
                robocopy . \\yourserver\path\to\deploy\ /E
                ssh user@yourserver "sc stop your-socket-service && sc start your-socket-service"
                '''
            }
        }
    }

    post {
        always {
            // Cleanup actions, notifications, etc.
            mail to: 'you@example.com',
                 subject: "Pipeline: ${currentBuild.fullDisplayName}",
                 body: "Build ${currentBuild.result} \n ${env.BUILD_URL}"
        }
    }
}
