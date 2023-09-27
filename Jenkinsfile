pipeline {
    agent any

    stages {
        stage('PRE-BUILD') {
            steps {
                script {
                    echo "Pre-Build Stage"
                    echo preBuildContent
                }
            }
        }

        stage('BUILD') {
            steps {
                echo "Hello World"
            }
        }

        stage('POST-BUILD') {
            steps {
                script {
                    echo "Post-Build Stage"
                    echo postBuildContent
                }
            }
        }

        stage('PRE-DEPLOY') {
            steps {
                script {
                    echo "Pre-Deploy Stage"
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
                    echo postDeployContent
                }
            }
        }
    }
}
