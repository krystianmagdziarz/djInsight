# 🔧 Configuration

Complete configuration reference for djinsight settings.

## 📋 Basic Settings

Add these settings to your Django `settings.py`:

```python
# settings.py

# Redis Configuration
DJINSIGHT_REDIS_HOST = 'localhost'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_DB = 0
DJINSIGHT_REDIS_PASSWORD = None
DJINSIGHT_REDIS_TIMEOUT = 5
DJINSIGHT_REDIS_CONNECT_TIMEOUT = 5

# Data Storage
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 7  # 7 days
DJINSIGHT_REDIS_KEY_PREFIX = "djinsight:pageview:"

# Feature Control
DJINSIGHT_ENABLE_TRACKING = True
DJINSIGHT_ADMIN_ONLY = False  # NEW in v0.1.3

# Processing Limits
DJINSIGHT_BATCH_SIZE = 1000
DJINSIGHT_MAX_RETRIES = 3
```

**Celery Schedules:**
```bash
DJINSIGHT_PROCESS_SCHEDULE="10"        # Process views every 10 seconds
DJINSIGHT_SUMMARIES_SCHEDULE="*/10"    # Generate summaries every 10 minutes  
DJINSIGHT_CLEANUP_SCHEDULE="0 1 * * *"   # Cleanup daily at 1:00 AM
```

## 🔒 Access Control Settings

### DJINSIGHT_ADMIN_ONLY

**Default:** `False`  
**Type:** Boolean  
**Added in:** v0.1.3

Controls who can view analytics statistics.

```python
# Allow all users to view statistics (default)
DJINSIGHT_ADMIN_ONLY = False

# Restrict statistics to admin users only  
DJINSIGHT_ADMIN_ONLY = True
```

**When `True`:**
- Only authenticated staff users (`user.is_staff = True`) can view statistics
- Template tags return empty content for non-admin users
- API endpoints require staff permissions
- Non-admin users see "Access denied" messages

**When `False`:**
- All users can view statistics
- No permission checks are performed
- Full backward compatibility

📖 **See also:** [Permission Control Guide](permission-control.md)

## 🗃️ Redis Settings

### DJINSIGHT_REDIS_HOST

**Default:** `'localhost'`  
**Type:** String

Redis server hostname or IP address.

```python
DJINSIGHT_REDIS_HOST = 'localhost'          # Local development
DJINSIGHT_REDIS_HOST = 'redis.example.com'  # Remote server
DJINSIGHT_REDIS_HOST = '10.0.1.100'         # IP address
```

### DJINSIGHT_REDIS_PORT

**Default:** `6379`  
**Type:** Integer

Redis server port number.

```python
DJINSIGHT_REDIS_PORT = 6379    # Default Redis port
DJINSIGHT_REDIS_PORT = 6380    # Custom port
```

### DJINSIGHT_REDIS_DB

**Default:** `0`  
**Type:** Integer (0-15)

Redis database number to use for djinsight data.

```python
DJINSIGHT_REDIS_DB = 0    # Default database
DJINSIGHT_REDIS_DB = 1    # Separate database for analytics
```

### DJINSIGHT_REDIS_PASSWORD

**Default:** `None`  
**Type:** String or None

Redis server password for authentication.

```python
DJINSIGHT_REDIS_PASSWORD = None                 # No authentication
DJINSIGHT_REDIS_PASSWORD = 'your-redis-password'  # With password
```

### DJINSIGHT_REDIS_TIMEOUT

**Default:** `5`  
**Type:** Integer (seconds)

Socket timeout for Redis operations.

```python
DJINSIGHT_REDIS_TIMEOUT = 5    # 5 seconds (default)
DJINSIGHT_REDIS_TIMEOUT = 10   # 10 seconds for slow connections
```

### DJINSIGHT_REDIS_CONNECT_TIMEOUT

**Default:** `5`  
**Type:** Integer (seconds)

Connection timeout for Redis.

```python
DJINSIGHT_REDIS_CONNECT_TIMEOUT = 5    # 5 seconds (default)
DJINSIGHT_REDIS_CONNECT_TIMEOUT = 3    # 3 seconds for fast fail
```

## 💾 Data Storage Settings

### DJINSIGHT_REDIS_EXPIRATION

**Default:** `604800` (7 days)  
**Type:** Integer (seconds)

How long to keep view data in Redis before automatic expiration.

```python
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 7   # 7 days (default)
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 30  # 30 days
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 1   # 1 day for testing
```

⚠️ **Note:** Shorter expiration means less storage usage but potential data loss if Celery workers are down.

### DJINSIGHT_REDIS_KEY_PREFIX

**Default:** `"djinsight:pageview:"`  
**Type:** String

Prefix for all Redis keys used by djinsight.

```python
DJINSIGHT_REDIS_KEY_PREFIX = "djinsight:pageview:"     # Default
DJINSIGHT_REDIS_KEY_PREFIX = "analytics:views:"       # Custom prefix
DJINSIGHT_REDIS_KEY_PREFIX = "mysite:djinsight:"      # Site-specific
```

⚠️ **Warning:** Changing this setting will make existing Redis data inaccessible.

## 🎛️ Feature Control Settings

### DJINSIGHT_ENABLE_TRACKING

**Default:** `True`  
**Type:** Boolean

Master switch to enable/disable all tracking functionality.

```python
DJINSIGHT_ENABLE_TRACKING = True   # Enable tracking (default)
DJINSIGHT_ENABLE_TRACKING = False  # Disable all tracking
```

**When `False`:**
- No JavaScript tracking scripts are generated
- API endpoints return early
- No data is stored in Redis
- Template tags still display existing statistics

## ⚙️ Processing Settings

### DJINSIGHT_BATCH_SIZE

**Default:** `1000`  
**Type:** Integer  
**Environment Variable:** `DJINSIGHT_BATCH_SIZE`

Number of view records to process in each Celery batch.

```python
DJINSIGHT_BATCH_SIZE = 1000    # Default batch size
DJINSIGHT_BATCH_SIZE = 500     # Smaller batches for limited memory
DJINSIGHT_BATCH_SIZE = 2000    # Larger batches for better performance
```

```bash
# Environment variable usage
export DJINSIGHT_BATCH_SIZE=1500
```

### DJINSIGHT_MAX_RECORDS

**Default:** `10000`  
**Type:** Integer  
**Environment Variable:** `DJINSIGHT_MAX_RECORDS`

Maximum number of records to process in a single task run.

```bash
# Environment variable usage
export DJINSIGHT_MAX_RECORDS=20000    # Process more records per run
export DJINSIGHT_MAX_RECORDS=5000     # Process fewer records per run
```

### DJINSIGHT_SUMMARY_DAYS_BACK

**Default:** `1`  
**Type:** Integer  
**Environment Variable:** `DJINSIGHT_SUMMARY_DAYS_BACK`

Number of days back to process when generating daily summaries.

```bash
# Environment variable usage
export DJINSIGHT_SUMMARY_DAYS_BACK=7     # Process last 7 days
export DJINSIGHT_SUMMARY_DAYS_BACK=1     # Process only yesterday (default)
```

### DJINSIGHT_CLEANUP_DAYS_TO_KEEP

**Default:** `90`  
**Type:** Integer  
**Environment Variable:** `DJINSIGHT_CLEANUP_DAYS_TO_KEEP`

Number of days of page view logs to keep before cleanup.

```bash
# Environment variable usage
export DJINSIGHT_CLEANUP_DAYS_TO_KEEP=180  # Keep logs for 6 months
export DJINSIGHT_CLEANUP_DAYS_TO_KEEP=30   # Keep logs for 1 month
```

### DJINSIGHT_MAX_RETRIES

**Default:** `3`  
**Type:** Integer

Maximum number of retry attempts for failed Celery tasks.

```python
DJINSIGHT_MAX_RETRIES = 3    # Default retries
DJINSIGHT_MAX_RETRIES = 5    # More retries for unreliable connections
DJINSIGHT_MAX_RETRIES = 1    # Fewer retries for fast failure
```

## ⏱️ Task Timeout Settings

Configure timeout limits for Celery tasks to prevent hanging tasks and optimize resource usage.

### Processing Task Timeouts

**Task:** `process_page_views_task`

```bash
# Hard timeout - task is killed after this time
export DJINSIGHT_PROCESS_TASK_TIME_LIMIT=1800      # 30 minutes (default)

# Soft timeout - task gets SIGTERM signal
export DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT=1500 # 25 minutes (default)
```

### Summary Generation Timeouts

**Task:** `generate_daily_summaries_task`

```bash
# Hard timeout for summary generation
export DJINSIGHT_SUMMARY_TASK_TIME_LIMIT=900       # 15 minutes (default)

# Soft timeout for summary generation  
export DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT=720  # 12 minutes (default)
```

### Cleanup Task Timeouts

**Task:** `cleanup_old_data_task`

```bash
# Hard timeout for cleanup (longest running task)
export DJINSIGHT_CLEANUP_TASK_TIME_LIMIT=3600      # 60 minutes (default)

# Soft timeout for cleanup
export DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT=3300 # 55 minutes (default)
```

### Timeout Configuration Examples

**Small Application (faster timeouts):**
```bash
# For applications with < 100k page views/day
export DJINSIGHT_PROCESS_TASK_TIME_LIMIT=600       # 10 minutes
export DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT=480  # 8 minutes
export DJINSIGHT_SUMMARY_TASK_TIME_LIMIT=300       # 5 minutes
export DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT=240  # 4 minutes
export DJINSIGHT_CLEANUP_TASK_TIME_LIMIT=1800      # 30 minutes
export DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT=1500 # 25 minutes
```

**Large Application (longer timeouts):**
```bash
# For applications with > 1M page views/day
export DJINSIGHT_PROCESS_TASK_TIME_LIMIT=3600      # 60 minutes
export DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT=3300 # 55 minutes
export DJINSIGHT_SUMMARY_TASK_TIME_LIMIT=1800 # 30 minutes
export DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT=1500 # 25 minutes
export DJINSIGHT_CLEANUP_TASK_TIME_LIMIT=7200      # 2 hours
export DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT=6900 # 1h 55min
```

**Production Kubernetes Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  template:
    spec:
      containers:
      - name: celery-worker
        env:
        # Task parameters
        - name: DJINSIGHT_BATCH_SIZE
          value: "2000"
        - name: DJINSIGHT_MAX_RECORDS
          value: "50000"
        - name: DJINSIGHT_SUMMARY_DAYS_BACK
          value: "3"
        - name: DJINSIGHT_CLEANUP_DAYS_TO_KEEP
          value: "180"
        
        # Timeout configuration
        - name: DJINSIGHT_PROCESS_TASK_TIME_LIMIT
          value: "2400"  # 40 minutes
        - name: DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT
          value: "2100"  # 35 minutes
        - name: DJINSIGHT_SUMMARY_TASK_TIME_LIMIT
          value: "1200"  # 20 minutes
        - name: DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT
          value: "900"   # 15 minutes
        - name: DJINSIGHT_CLEANUP_TASK_TIME_LIMIT
          value: "5400"  # 90 minutes
        - name: DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT
          value: "5100"  # 85 minutes
```

## ⏰ Celery Schedule Settings

djinsight supports configurable task schedules through environment variables. These settings control when background tasks run.

### DJINSIGHT_PROCESS_SCHEDULE

**Default:** `"10"` (every 10 seconds)  
**Type:** String (Environment Variable)  
**Added in:** v0.1.4

Controls how often page views are processed from Redis to database.

```bash
# Environment variable examples
export DJINSIGHT_PROCESS_SCHEDULE="10"        # Every 10 seconds (default)
export DJINSIGHT_PROCESS_SCHEDULE="30"        # Every 30 seconds
export DJINSIGHT_PROCESS_SCHEDULE="*/5"       # Every 5 minutes (cron format)
export DJINSIGHT_PROCESS_SCHEDULE="0 */1 * * *"  # Every hour (full cron)
```

**Supported formats:**
- **Seconds**: `"10"` = every 10 seconds
- **Cron minutes**: `"*/5"` = every 5 minutes  
- **Full cron**: `"0 1 * * *"` = daily at 1:00 AM

### DJINSIGHT_SUMMARIES_SCHEDULE

**Default:** `"*/10"` (every 10 minutes)  
**Type:** String (Environment Variable)  
**Added in:** v0.1.4

Controls how often daily summaries are generated.

```bash
# Environment variable examples
export DJINSIGHT_SUMMARIES_SCHEDULE="*/10"    # Every 10 minutes (default)
export DJINSIGHT_SUMMARIES_SCHEDULE="*/30"    # Every 30 minutes
export DJINSIGHT_SUMMARIES_SCHEDULE="0 */1 * * *"  # Every hour
export DJINSIGHT_SUMMARIES_SCHEDULE="0 0 * * *"    # Daily at midnight
```

### DJINSIGHT_CLEANUP_SCHEDULE

**Default:** `"0 1 * * *"` (daily at 1:00 AM)  
**Type:** String (Environment Variable)  
**Added in:** v0.1.4

Controls when old data cleanup runs.

```bash
# Environment variable examples
export DJINSIGHT_CLEANUP_SCHEDULE="0 1 * * *"     # Daily at 1:00 AM (default)
export DJINSIGHT_CLEANUP_SCHEDULE="0 2 * * 0"     # Weekly on Sunday at 2:00 AM
export DJINSIGHT_CLEANUP_SCHEDULE="0 3 1 * *"     # Monthly on 1st at 3:00 AM
export DJINSIGHT_CLEANUP_SCHEDULE="0 0 * * *"     # Daily at midnight
```

**Cron format explanation:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ day of week (0-6, Sunday=0)
│ │ │ └─── month (1-12)
│ │ └───── day of month (1-31)
│ └─────── hour (0-23)
└───────── minute (0-59)
```

## 🏗️ Environment-Specific Examples

### Development Settings

```python
# settings/development.py

# Use local Redis
DJINSIGHT_REDIS_HOST = 'localhost'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_DB = 1  # Separate from cache

# Short expiration for testing
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24  # 1 day

# Allow all users to see stats
DJINSIGHT_ADMIN_ONLY = False

# Smaller batch sizes for development
DJINSIGHT_BATCH_SIZE = 100
```

```bash
# Environment variables for development
export DJINSIGHT_PROCESS_SCHEDULE="30"      # Every 30 seconds (slower for dev)
export DJINSIGHT_SUMMARIES_SCHEDULE="*/5"   # Every 5 minutes
export DJINSIGHT_CLEANUP_SCHEDULE="0 0 * * *"  # Daily at midnight
```

### Production Settings

```python
# settings/production.py

# Production Redis server
DJINSIGHT_REDIS_HOST = 'redis.yourdomain.com'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

# Longer data retention
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 30  # 30 days

# Restrict to admin users only
DJINSIGHT_ADMIN_ONLY = True

# Optimize for performance
DJINSIGHT_BATCH_SIZE = 2000
DJINSIGHT_REDIS_TIMEOUT = 10
```

```bash
# Environment variables for production
export DJINSIGHT_PROCESS_SCHEDULE="10"       # Every 10 seconds (default)
export DJINSIGHT_SUMMARIES_SCHEDULE="*/10"   # Every 10 minutes (default)
export DJINSIGHT_CLEANUP_SCHEDULE="0 1 * * *"  # Daily at 1:00 AM (default)
```

### Docker/Container Settings

```python
# settings/docker.py

# Use container networking
DJINSIGHT_REDIS_HOST = 'redis'  # Docker service name
DJINSIGHT_REDIS_PORT = 6379

# Environment-based configuration
DJINSIGHT_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
DJINSIGHT_ADMIN_ONLY = os.environ.get('ANALYTICS_ADMIN_ONLY', 'false').lower() == 'true'
```

## 🔧 Advanced Configuration

### Custom Redis Configuration

For advanced Redis setups, you can configure Redis directly:

```python
# settings.py
import redis

# Custom Redis connection pool
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}

# djinsight will use the same connection
DJINSIGHT_REDIS_HOST = '127.0.0.1'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_DB = 1
```

### Celery Integration

Configure Celery for optimal djinsight performance:

```python
# celery.py
from celery import Celery

app = Celery('myproject')

# Optimize for djinsight tasks
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing for djinsight
    task_routes={
        'djinsight.tasks.*': {'queue': 'analytics'},
    },
    
    # Batch processing optimization
    task_always_eager=False,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
```

### Celery Schedule Configuration

Set environment variables to control task schedules:

```bash
# Docker Compose example
environment:
  - DJINSIGHT_PROCESS_SCHEDULE=10          # Every 10 seconds
  - DJINSIGHT_SUMMARIES_SCHEDULE=*/15      # Every 15 minutes  
  - DJINSIGHT_CLEANUP_SCHEDULE=0 2 * * *   # Daily at 2:00 AM

# systemd service example
Environment=DJINSIGHT_PROCESS_SCHEDULE=30
Environment=DJINSIGHT_SUMMARIES_SCHEDULE=0 */1 * * *
Environment=DJINSIGHT_CLEANUP_SCHEDULE=0 1 * * 0

# Kubernetes deployment example
env:
  - name: DJINSIGHT_PROCESS_SCHEDULE
    value: "15"
  - name: DJINSIGHT_SUMMARIES_SCHEDULE  
    value: "*/20"
  - name: DJINSIGHT_CLEANUP_SCHEDULE
    value: "0 3 * * *"
```

## 🔍 Debugging Configuration

### Enable Debug Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'djinsight': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Configuration Testing

Test your configuration:

```python
# Django shell
python manage.py shell

>>> from djinsight.views import redis_client
>>> redis_client.ping()
True

>>> from django.conf import settings
>>> print(f"Admin only: {getattr(settings, 'DJINSIGHT_ADMIN_ONLY', False)}")
>>> print(f"Tracking enabled: {getattr(settings, 'DJINSIGHT_ENABLE_TRACKING', True)}")
```

## 📚 Related Documentation

- [🔒 Permission Control](permission-control.md) - Access control details
- [📦 Installation](installation.md) - Initial setup  
- [⚡ Quick Start](quick-start.md) - Getting started
- [🚄 Performance](performance.md) - Optimization tips 