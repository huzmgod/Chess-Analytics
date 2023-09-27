pipeline {
    agent any

    stages {
        
        stage('BUILD') {
            steps {
                echo "Hello World"
            }
        }

        stage('POST-BUILD') {
            steps {
                script {
                    echo "Post-Build Stage"
                    def postBuildContent = "secPostBuild()"
                    echo postBuildContent
                }
            }
        }

        stage('PRE-DEPLOY') {
            steps {
                script {
                    echo "Pre-Deploy Stage"
                    def preDeployContent = "secPreDeploy()"
                    echo preDeployContent
                }
            }
        }

        stage('DEPLOY') {
            steps {
                echo "Deploying..."
            }
        }

        stage('POST-DEPLOY') {
            steps {
                script {
                    echo "Post-Deploy Stage"
                    def postDeployContent = "secPostDeploy()"
                    echo postDeployContent
                }
            }
        }
    }
}
