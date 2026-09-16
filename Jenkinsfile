pipeline {
  agent any

  options {
    disableConcurrentBuilds()
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '12'))
  }

  triggers {
    cron('TZ=Asia/Shanghai\nH 3 * * 0')
  }

  parameters {
    string(name: 'CLEAN_ROOT', defaultValue: '/Users/artechphy/Documents', description: 'Directory tree to scan')
    string(name: 'INACTIVE_DAYS', defaultValue: '30', description: 'Minimum inactive age in days')
    choice(name: 'CLEAN_MODE', choices: ['apply', 'audit'], description: 'apply deletes; audit only reports')
  }

  environment {
    PYTHONDONTWRITEBYTECODE = '1'
  }

  stages {
    stage('Verify cleaner') {
      steps {
        sh 'python3 -m unittest discover -s tests -v'
      }
    }

    stage('Clean inactive node_modules') {
      steps {
        sh '''
          set -eu
          python3 src/node_modules_cleaner.py \
            --root "$CLEAN_ROOT" \
            --days "$INACTIVE_DAYS" \
            --mode "$CLEAN_MODE" \
            --exclude-file config/excludes.txt \
            --report-dir reports/runtime
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/runtime/*.json', allowEmptyArchive: true
    }
  }
}
