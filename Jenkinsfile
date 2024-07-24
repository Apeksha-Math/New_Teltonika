pipeline {
    agent any

    environment {
        // Define the Docker image name and tag to be used throughout the pipeline
        DOCKER_IMAGE = 'pydoc:latest'
    }

    stages {
        stage('Checkout') {
            steps {
                // Clone the repository from the specified branch and URL
                git branch: 'socket_pgm', url: 'https://github.com/Apeksha-Math/New_Teltonika.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image using the Dockerfile in the repository
                    def customImage = docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests inside a Docker container created from the built image
                    def customImage = docker.image(DOCKER_IMAGE)
                    customImage.inside {
                        echo "Start running tests"
                        // Uncomment the next line to actually run tests using pytest
                        // bat 'pytest tests/'
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push the Docker image to a Docker registry using the specified credentials
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-credentials-id') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Deploy the Docker container to a remote server using SSH
                    sshagent(['ssh-credentials-id']) {
                        bat '''
                        @echo off
                        ssh user@yourserver "docker pull %DOCKER_IMAGE% && docker run -d --name your-container-name -p 80:80 %DOCKER_IMAGE%"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            // Send an email notification with the build results
            mail to: 'you@example.com',
                 subject: "Pipeline: ${currentBuild.fullDisplayName}",
                 body: "Build ${currentBuild.result}: ${currentBuild.fullDisplayName} \n See details at: ${env.BUILD_URL}"
        }
    }
}
