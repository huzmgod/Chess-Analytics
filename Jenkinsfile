pipeline {
    agent any

    stages {
        
        stage('BUILD') {
            steps {
                echo "Hello World"
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
