// Mesmo pipeline, agora na DSL declarativa do Jenkins (Groovy).
// Diferenca de arquitetura: o controller do Jenkins agenda o trabalho e um
// agent (aqui, um contêiner Docker) executa cada stage.

pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root:root'
        }
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {
        stage('Preparar ambiente') {
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 src tests'
            }
        }

        stage('Testes') {
            steps {
                // O quality gate e o proprio exit code do pytest:
                // cobertura abaixo de 80% derruba o build.
                sh '''
                    pytest --cov=src --cov-report=xml --cov-fail-under=80 \
                           --junitxml=relatorio-testes.xml
                '''
            }
            post {
                always {
                    junit 'relatorio-testes.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh '''
                    apt-get update && apt-get install -y --no-install-recommends zip
                    mkdir -p dist
                    zip -r "dist/pedidos-${BUILD_NUMBER}.zip" src README.md
                '''
                archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true
            }
        }

        stage('Deploy') {
            when {
                buildingTag()   // so implanta quando o gatilho e uma tag de versao
            }
            steps {
                echo "Implantando ${env.TAG_NAME} no ambiente..."
                echo 'Rollback = reimplantar o artefato da tag anterior.'
            }
        }
    }

    post {
        failure {
            echo 'Pipeline vermelho: o merge fica bloqueado ate a correcao.'
        }
        success {
            echo 'Pipeline verde: artefato pronto para ser liberado.'
        }
    }
}
