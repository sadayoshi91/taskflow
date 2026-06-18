# Example environment variables for running TaskFlow on Windows PowerShell.
# Adjust values to match the local PostgreSQL and Redis installation.

$env:DJANGO_SECRET_KEY = "change-me-for-local-demo"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"

$env:POSTGRES_DB = "taskflow"
$env:POSTGRES_USER = "taskflow"
$env:POSTGRES_PASSWORD = "taskflow"
$env:POSTGRES_HOST = "127.0.0.1"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_CONN_MAX_AGE = "60"
$env:POSTGRES_CONNECT_TIMEOUT = "10"

$env:REDIS_CACHE_URL = "redis://127.0.0.1:6379/1"
$env:CELERY_BROKER_URL = "redis://127.0.0.1:6379/2"
$env:CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/3"

$env:PROJECT_LIST_CACHE_TIMEOUT = "300"
$env:ACTIVE_TASK_LIST_CACHE_TIMEOUT = "300"