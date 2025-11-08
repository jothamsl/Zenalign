# Docker Setup for Senalign

This guide explains how Senalign uses Docker for MongoDB.

## Why Docker?

✅ **No installation needed** - MongoDB runs in a container  
✅ **Consistent environment** - Works the same on all systems  
✅ **Easy cleanup** - Remove containers without affecting your system  
✅ **Isolated data** - MongoDB data stays in Docker volumes  

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Local Machine              │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Senalign   │───▶│   MongoDB    │  │
│  │   (Python)   │    │   (Docker)   │  │
│  │  Port 8000   │    │  Port 27017  │  │
│  └──────────────┘    └──────────────┘  │
│         ▲                    │          │
│         │                    ▼          │
│    Your Browser      Docker Volume      │
│   (localhost:8000)   (Persistent Data)  │
└─────────────────────────────────────────┘
```

## docker-compose.yml Explained

```yaml
services:
  mongodb:
    image: mongo:7.0           # Official MongoDB 7.0 image
    container_name: senalign-mongodb
    restart: unless-stopped    # Auto-restart on crashes
    ports:
      - "27017:27017"         # Map container port to host
    environment:
      MONGO_INITDB_DATABASE: senalign  # Create this DB on startup
    volumes:
      - mongodb_data:/data/db          # Persist data
      - mongodb_config:/data/configdb  # Persist config
    healthcheck:                       # Check if MongoDB is ready
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/senalign --quiet
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mongodb_data:
    driver: local              # Store data on local disk
  mongodb_config:
    driver: local
```

## Common Docker Commands

### Start MongoDB
```bash
docker compose up -d mongodb
# -d = detached mode (runs in background)
```

### Check Status
```bash
docker compose ps
# Shows running containers

docker compose logs mongodb
# View MongoDB logs

docker compose logs -f mongodb
# Follow logs in real-time (Ctrl+C to exit)
```

### Stop MongoDB
```bash
docker compose down
# Stops and removes container (data persists in volumes)
```

### Remove Everything (including data)
```bash
docker compose down -v
# -v = remove volumes (deletes all data!)
# ⚠️  Use with caution
```

### Restart MongoDB
```bash
docker compose restart mongodb
```

## Data Persistence

MongoDB data is stored in Docker volumes:
- **mongodb_data** - Database files
- **mongodb_config** - Configuration files

These persist even when you stop the container.

### View Volume Location
```bash
docker volume inspect senalign_mongodb_data
```

### Backup Data
```bash
# Export data
docker exec senalign-mongodb mongodump --out /tmp/backup
docker cp senalign-mongodb:/tmp/backup ./mongodb_backup

# Restore data
docker cp ./mongodb_backup senalign-mongodb:/tmp/restore
docker exec senalign-mongodb mongorestore /tmp/restore
```

## Connecting to MongoDB

### From Senalign (Python)
```python
# In .env file:
MONGODB_URI=mongodb://localhost:27017/senalign

# The app connects automatically
from app.services.db import init_db
client = init_db()
```

### From MongoDB Shell
```bash
# Install mongosh on your system, then:
mongosh "mongodb://localhost:27017/senalign"
```

### From MongoDB Compass (GUI)
1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect to: `mongodb://localhost:27017/senalign`

## Troubleshooting

### "Cannot connect to Docker daemon"
**Problem:** Docker Desktop is not running  
**Solution:** Start Docker Desktop application

### "Port 27017 already in use"
**Problem:** Another MongoDB instance is using the port  
**Solution:**
```bash
# Option 1: Stop the other MongoDB
lsof -i :27017
kill <PID>

# Option 2: Use a different port
# Edit docker-compose.yml:
ports:
  - "27018:27017"
# Update .env:
MONGODB_URI=mongodb://localhost:27018/senalign
```

### "Container keeps restarting"
**Problem:** MongoDB is crashing  
**Solution:**
```bash
# Check logs
docker compose logs mongodb

# Common issues:
# - Insufficient disk space
# - Corrupted data (try: docker compose down -v)
# - Port conflict
```

### "Connection timeout"
**Problem:** MongoDB hasn't fully started  
**Solution:**
```bash
# Wait 10-15 seconds after starting
docker compose up -d mongodb
sleep 10
python test_mongodb.py
```

## Alternative: MongoDB Atlas (Cloud)

If you prefer cloud MongoDB instead of Docker:

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string (looks like: `mongodb+srv://...`)
4. Update `.env`:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/senalign
   ```
5. No Docker needed!

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

---

**Questions?** Check the main README.md or QUICKSTART.md
