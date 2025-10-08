pipeline {
  agent any

  environment {
    APP_HOST     = 'ec2-18.168.11.31.compute-1.amazonaws.com'
    APP_SSH      = "app@${APP_HOST}"
    APP_DIR      = "/opt/calculator-app"
    VENV_DIR     = "${APP_DIR}/venv"
    SSH_CRED     = "app-ssh-key"
  }

  triggers {
    githubPush()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git --version'
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          python3 --version
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
        '''
      }
    }

    stage('Install deps & Lint/Test') {
      steps {
        sh '''
          . .venv/bin/activate
          pip install -r requirements.txt
          pip install flake8 pytest
          flake8 .
          pytest -q
        '''
      }
    }

    stage('Package') {
      steps {
        sh 'tar czf build.tgz --exclude .venv --exclude __pycache__ --exclude .git *'
        archiveArtifacts artifacts: 'build.tgz', fingerprint: true
      }
    }

    stage('Deploy to EC2') {
      steps {
        sshagent(credentials: [env.SSH_CRED]) {
          sh '''
            set -e
            RSYNC_RSH="ssh -o StrictHostKeyChecking=no"
            # Ensure target dir exists and owned by app
            ssh -o StrictHostKeyChecking=no ${APP_SSH} 'sudo mkdir -p '"${APP_DIR}"' && sudo chown -R app:app '"${APP_DIR}"''

            # Sync source code (delete removed files)
            rsync -az --delete -e "$RSYNC_RSH" ./ ${APP_SSH}:${APP_DIR}/

            # Create venv if missing, install deps, restart service
            ssh -o StrictHostKeyChecking=no ${APP_SSH} "bash -lc '
              set -e
              cd ${APP_DIR}
              [ -d ${VENV_DIR} ] || python3 -m venv ${VENV_DIR}
              . ${VENV_DIR}/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              sudo systemctl daemon-reload
              sudo systemctl restart calculator
              systemctl --no-pager -l status calculator || true
            '"
          '''
        }
      }
    }
  }

  post {
    success {
      echo 'Deploy succeeded.'
    }
    failure {
      echo 'Build or deploy failed.'
    }
  }
}
