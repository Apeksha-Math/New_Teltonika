pipeline {
    agent any

    stages {
        stage('Checkout') {
            agent {
                label 'mdvr'
            }
            steps {
                git branch: 'socket_pgm', url: 'https://github.com/Apeksha-Math/New_Teltonika.git'
            }
        }

        stage('Build Approval') {
            steps {
                script {
                    try {
                        // Approval for Build stage
                        timeout(time: 5, unit: 'MINUTES') {
                            emailext body: emailBodyBuild,
                                     subject: 'Build Approval Required',
                                     to: recipientEmailBuild,
                                     mimeType: 'text/html'

                            def buildApproval = input message: 'Waiting for build approval',
                                                  ok: 'Proceed',
                                                  submitter: 'build-approver',
                                                  parameters: [
                                                      string(defaultValue: '', description: 'Have you thoroughly reviewed the changes incorporated in this build?', name: 'reviewChanges'),
                                                      string(defaultValue: '', description: 'Are you confident that all modifications align with the project\'s coding standards and best practices?', name: 'codingStandards'),
                                                      string(defaultValue: '', description: 'Does the completed build adhere to the specified project requirements and objectives?', name: 'adhereToRequirements')
                                                  ]

                            // Store parameters
                            reviewChangesValue = buildApproval['reviewChanges']
                            codingStandardsValue = buildApproval['codingStandards']
                            adhereToRequirementsValue = buildApproval['adhereToRequirements']

                            // Log user's responses
                            echo "Build Approval Responses: ${buildApproval}"
                        }
                    } catch (err) {
                        currentBuild.result = 'FAILURE'
                        echo "An error occurred during the build approval stage: ${err}"
                        error "Build approval stage encountered an error. Build will not proceed."
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            agent {
                label 'mdvr'
            }
            steps {
                // Build Docker image
                bat 'docker build -t 6458d2549bcb/pydoc:1 .'

                // Push Docker image to Docker Hub registry
                withCredentials([usernamePassword(credentialsId: '377e98fd-7ba5-4b8f-a3a2-405f82ade900', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    bat 'docker login -u %DOCKER_USERNAME% -p %DOCKER_PASSWORD%'
                    bat 'docker push 6458d2549bcb/pydoc:1'
                }
            }
        }

        stage('Deployment Approval') {
            steps {
                script {
                    try {
                        // Approval for Deploy stage
                        timeout(time: 5, unit: 'MINUTES') {
                            emailext body: emailBodyDeploy,
                                     subject: 'Deployment Approval Required',
                                     to: recipientEmailDeploy,
                                     mimeType: 'text/html'

                            def deployApproval = input message: 'Waiting for deployment approval',
                                                    ok: 'Proceed',
                                                    submitter: 'deploy-approver',
                                                    parameters: [
                                                        string(defaultValue: '', description: 'Have you thoroughly reviewed the changes incorporated in this deployment?', name: 'reviewChanges'),
                                                        string(defaultValue: '', description: 'Are you confident that all modifications align with the project\'s coding standards and best practices?', name: 'codingStandards'),
                                                        string(defaultValue: '', description: 'Does the completed deployment adhere to the specified project requirements and objectives?', name: 'adhereToRequirements')
                                                    ]

                            // Store parameters
                            deployReviewChangesValue = deployApproval['reviewChanges']
                            deployCodingStandardsValue = deployApproval['codingStandards']
                            deployAdhereToRequirementsValue = deployApproval['adhereToRequirements']

                            // Log user's responses
                            echo "Deploy Approval Responses: ${deployApproval}"
                        }
                    } catch (err) {
                        currentBuild.result = 'FAILURE'
                        echo "An error occurred during the deployment approval stage: ${err}"
                        error "Deployment approval stage encountered an error. Deployment will not proceed."
                    }
                }
            }
        }

        stage('Deploy to Kubernetes Staging') {
            agent {
                label 'mdvr'
            }
            steps {
                // Apply Kubernetes manifests to staging environment
                bat 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
