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
                // Install dependencies, e.g., for Python
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                // Run your unit tests
                sh 'pytest tests/'
            }
        }

        stage('Deploy') {
            steps {
                // Deploy to your server, e.g., using SCP or SSH
                sh '''
                scp -r * user@yourserver:/path/to/deploy/
                ssh user@yourserver 'systemctl restart your-socket-service'
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
