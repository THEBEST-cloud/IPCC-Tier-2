# Deployment Instructions for Ubuntu 22.04

## Overview

This document provides detailed deployment instructions for the Reservoir GHG Emissions Tool on Ubuntu 22.04.

## System Preparation

### 1. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Docker
```bash
# Install Docker
sudo apt install docker.io -y

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### 3. Install Docker Compose
```bash
# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker-compose --version
```

### 4. Configure Docker Permissions
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes (requires logout/login or newgrp)
newgrp docker

# Verify you can run docker without sudo
docker ps
```

## Application Deployment

### Option 1: Quick Deploy with Script

1. **Navigate to application directory:**
   ```bash
   cd /path/to/reservoir-emissions-tool
   ```

2. **Make startup script executable:**
   ```bash
   chmod +x start.sh
   ```

3. **Run startup script:**
   ```bash
   ./start.sh
   ```

4. **Access application:**
   - Web Interface: http://localhost:8080
   - API Docs: http://localhost:8080/docs

### Option 2: Manual Deployment

1. **Navigate to application directory:**
   ```bash
   cd /path/to/reservoir-emissions-tool
   ```

2. **Create data directory:**
   ```bash
   mkdir -p data
   ```

3. **Build Docker image:**
   ```bash
   docker-compose build
   ```

4. **Start container:**
   ```bash
   docker-compose up -d
   ```

5. **Verify container is running:**
   ```bash
   docker ps
   ```

6. **View logs:**
   ```bash
   docker-compose logs -f
   ```

## Verification

### 1. Test Health Endpoint
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 2. Run API Test Script
```bash
chmod +x test_api.sh
./test_api.sh
```

### 3. Access Web Interface
Open browser and navigate to: http://localhost:8080

## Container Management

### View Container Status
```bash
docker ps
docker-compose ps
```

### View Logs
```bash
# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs for specific time
docker-compose logs --since 30m
```

### Restart Container
```bash
docker-compose restart
```

### Stop Container
```bash
docker-compose stop
```

### Start Stopped Container
```bash
docker-compose start
```

### Stop and Remove Container
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose up --build -d
```

## Resource Management

### Check Resource Usage
```bash
# Disk usage
docker system df

# Container stats
docker stats reservoir-emissions-tool
```

### Clean Up Unused Resources
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup (careful!)
docker system prune -a
```

## Data Management

### Backup Database
```bash
# Stop container
docker-compose stop

# Backup database
cp data/reservoir_emissions.db data/reservoir_emissions.db.backup

# Restart container
docker-compose start
```

### Restore Database
```bash
# Stop container
docker-compose stop

# Restore from backup
cp data/reservoir_emissions.db.backup data/reservoir_emissions.db

# Restart container
docker-compose start
```

### Reset Database
```bash
# Stop container
docker-compose stop

# Remove database
rm data/reservoir_emissions.db

# Restart container (new empty database will be created)
docker-compose start
```

## Network Configuration

### Change Port

The port is currently set to 8080. To change to a different port, edit `docker-compose.yml`:
```yaml
services:
  web:
    ports:
      - "9000:8000"  # Change host port (left side) to desired port
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

Access at the new port: http://localhost:9000

### Firewall Configuration

If using UFW:
```bash
# Allow port 8080
sudo ufw allow 8080/tcp

# Check status
sudo ufw status
```

### Remote Access

To allow remote access (be careful with security!):

1. **Modify docker-compose.yml** - bind to all interfaces:
   ```yaml
   ports:
     - "0.0.0.0:8080:8000"
   ```

2. **Configure firewall:**
   ```bash
   sudo ufw allow 8080/tcp
   ```

3. **Access from remote:**
   ```
   http://<server-ip>:8080
   ```

**Security Warning:** Only expose to trusted networks. Consider using NGINX reverse proxy with HTTPS for production deployments.

## Production Deployment Recommendations

### 1. Use Environment Variables

Create `.env` file:
```env
DATABASE_URL=sqlite:///./data/reservoir_emissions.db
```

### 2. Set Up NGINX Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Set Up Auto-Start on Boot

Docker containers with `restart: unless-stopped` in docker-compose.yml will auto-start.

Verify:
```bash
docker inspect reservoir-emissions-tool | grep RestartPolicy
```

### 5. Set Up Log Rotation

Create `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
docker-compose down
docker-compose up -d
```

### 6. Regular Backups

Add to crontab:
```bash
crontab -e
```

Add line:
```
0 2 * * * cp /path/to/data/reservoir_emissions.db /path/to/backups/reservoir_emissions_$(date +\%Y\%m\%d).db
```

## Monitoring

### Check Application Health
```bash
# Using curl
curl http://localhost:8080/health

# Using watch for continuous monitoring
watch -n 5 'curl -s http://localhost:8080/health | python3 -m json.tool'
```

### Monitor Container
```bash
# Resource usage
docker stats reservoir-emissions-tool

# Process list
docker top reservoir-emissions-tool

# Container details
docker inspect reservoir-emissions-tool
```

## Troubleshooting

### Container Won't Start

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Check port availability:**
   ```bash
   sudo lsof -i :8080
   ```

3. **Check Docker service:**
   ```bash
   sudo systemctl status docker
   ```

4. **Rebuild:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/

# Restart container
docker-compose restart
```

### Database Locked

```bash
# Stop container
docker-compose stop

# Check for processes using database
lsof data/reservoir_emissions.db

# Restart
docker-compose start
```

### Out of Memory

```bash
# Check memory usage
free -h
docker stats

# Add memory limit to docker-compose.yml
services:
  web:
    mem_limit: 1g
```

## Performance Optimization

### 1. Limit Container Resources

Edit `docker-compose.yml`:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

### 2. Use PostgreSQL for Production

Replace SQLite with PostgreSQL for better performance with multiple users:

```yaml
services:
  web:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/reservoir
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 3. Add Redis for Caching

For high-traffic scenarios, add Redis caching layer.

## Security Best Practices

1. **Keep Docker Updated:**
   ```bash
   sudo apt update
   sudo apt upgrade docker.io docker-compose
   ```

2. **Run as Non-Root User:**
   Already configured in Dockerfile

3. **Limit Container Capabilities:**
   Docker security options in docker-compose.yml

4. **Regular Backups:**
   Automate database backups

5. **Monitor Logs:**
   Regularly review application and container logs

6. **Use Secrets Management:**
   For production, use Docker secrets or environment variables

## Maintenance Schedule

### Daily
- Check application health
- Monitor resource usage

### Weekly
- Review logs
- Check for updates
- Backup database

### Monthly
- Clean up old analyses
- Update Docker images
- Security audit

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section
3. Refer to README.md and USER_GUIDE.md
4. Check API documentation at /docs

---

**Deployment Date:** ___________
**Deployed By:** ___________
**Server:** ___________
