
module.exports = {
  apps: [
    {
      name: 'jobfinder-api',
      script: 'uvicorn',
      args: 'api.main:app --host 0.0.0.0 --port 8000 --workers 4',
      interpreter: 'python',
      env_file: '.env.production',
      error_file: './logs/api-error.log',
      out_file: './logs/api-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'jobfinder-celery',
      script: 'celery',
      args: '-A api.app.celery_app worker --loglevel=info --concurrency=4',
      interpreter: 'python',
      env_file: '.env.production',
      error_file: './logs/celery-error.log',
      out_file: './logs/celery-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'jobfinder-frontend',
      script: 'npm',
      args: 'run start',
      cwd: './frontend',
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 5000
      }
    }
  ]
};
