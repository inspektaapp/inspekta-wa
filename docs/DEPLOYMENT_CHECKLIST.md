# Production Deployment Checklist

## ✅ **Build & Deployment Validation Status**

### **🎯 Current Status: DEVELOPMENT READY**
- ✅ **96.2% validation success** (25/26 checks passed)
- ✅ All core dependencies installed and working
- ✅ FastAPI application imports and starts successfully
- ✅ All health check endpoints responding (200 OK)
- ✅ Logging system configured and operational
- ✅ Docker configuration created and ready
- ⚠️ **Production readiness: FALSE** (expected - in development mode)

---

## **📋 Pre-Production Checklist**

### **1. Environment Configuration**
- [ ] **Replace development SECRET_KEY** with 64-character secure key
- [ ] **Configure WhatsApp Business API credentials:**
  - [ ] `WHATSAPP_TOKEN` - Permanent access token
  - [ ] `WHATSAPP_PHONE_ID` - Phone number ID
  - [ ] `WHATSAPP_VERIFY_TOKEN` - Custom webhook verification token
  - [ ] `WHATSAPP_APP_SECRET` - App secret for signature verification
- [ ] **Configure Inspector API integration:**
  - [ ] `INSPECTOR_API_BASE_URL` - Production API URL
  - [ ] `INSPECTOR_API_KEY` - Production API key
- [ ] **Set up production database:**
  - [ ] `DATABASE_URL` - PostgreSQL connection string
  - [ ] Run database migrations: `alembic upgrade head`
- [ ] **Configure Redis for production:**
  - [ ] `REDIS_URL` - Production Redis instance
  - [ ] `CELERY_BROKER_URL` - Redis broker URL
- [ ] **Set up email service:**
  - [ ] `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
  - [ ] `FROM_EMAIL` - Verified sender email
- [ ] **Disable debug mode:**
  - [ ] `DEBUG=False`
  - [ ] `DEVELOPMENT_MODE=False`

### **2. Security Hardening**
- [ ] **SSL/TLS certificates** installed and configured
- [ ] **Firewall rules** configured (allow only necessary ports)
- [ ] **Rate limiting** configured for production traffic
- [ ] **Webhook signature verification** enabled
- [ ] **CORS settings** restricted to production domains
- [ ] **Security headers** configured (HSTS, CSP, etc.)
- [ ] **Secret management** - no secrets in code/config files

### **3. Infrastructure Setup**
- [ ] **Production server** provisioned and configured
- [ ] **Load balancer** configured (if needed)
- [ ] **Reverse proxy** (Nginx/Apache) configured
- [ ] **Process manager** (systemd/supervisor) configured
- [ ] **Auto-restart** on failure configured
- [ ] **Log rotation** configured
- [ ] **Backup strategy** implemented

### **4. Monitoring & Alerting**
- [ ] **Health check monitoring** configured
- [ ] **Application metrics** collection setup
- [ ] **Log aggregation** configured
- [ ] **Error tracking** (Sentry/equivalent) configured
- [ ] **Uptime monitoring** configured
- [ ] **Alert notifications** configured (email/Slack/SMS)
- [ ] **Performance monitoring** configured

### **5. Testing & Validation**
- [ ] **End-to-end testing** in staging environment
- [ ] **WhatsApp webhook** tested with Meta verification
- [ ] **Load testing** completed
- [ ] **Disaster recovery** tested
- [ ] **Backup restoration** tested
- [ ] **Monitoring alerts** tested

---

## **🚀 Deployment Commands**

### **Option 1: Docker Deployment**
```bash
# 1. Build production image
docker build -t inspector-whatsapp-bot:latest .

# 2. Run with production environment
docker run -d \
  --name inspector-whatsapp-bot \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env.production \
  -v ./logs:/app/logs \
  inspector-whatsapp-bot:latest

# 3. Check health
curl http://localhost:8000/api/v1/health/ready
```

### **Option 2: Direct Deployment**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set production environment
export ENVIRONMENT=production

# 3. Run database migrations
alembic upgrade head

# 4. Start application
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 5. Start background workers
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

### **Option 3: Docker Compose**
```bash
# 1. Configure production environment
cp .env.example .env.production
# Edit .env.production with production values

# 2. Deploy with compose
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/api/v1/health/detailed
```

---

## **🔍 Validation Commands**

### **Pre-Deployment Validation**
```bash
# Run comprehensive validation
python3 validate_deployment.py

# Check production readiness
curl http://localhost:8000/api/v1/health/detailed | jq '.configuration.production_ready'

# Test all endpoints
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/ready
curl http://localhost:8000/api/v1/health/live
```

### **WhatsApp Webhook Setup**
```bash
# 1. Configure webhook URL (replace with your domain)
curl -X POST "https://graph.facebook.com/v18.0/{phone-number-id}/webhooks" \
  -H "Authorization: Bearer {access-token}" \
  -H "Content-Type: application/json" \
  -d '{
    "webhooks_url": "https://your-domain.com/api/v1/webhook",
    "verify_token": "your_verify_token"
  }'

# 2. Subscribe to webhook fields
curl -X POST "https://graph.facebook.com/v18.0/{app-id}/subscriptions" \
  -H "Authorization: Bearer {access-token}" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "callback_url": "https://your-domain.com/api/v1/webhook",
    "verify_token": "your_verify_token",
    "fields": ["messages"]
  }'
```

### **Post-Deployment Verification**
```bash
# 1. Health checks
curl https://your-domain.com/api/v1/health/detailed

# 2. Test webhook endpoint
curl https://your-domain.com/api/v1/webhook?hub.mode=subscribe&hub.challenge=123&hub.verify_token=your_token

# 3. Check logs
tail -f logs/app.log
tail -f logs/whatsapp.log
tail -f logs/errors.log

# 4. Monitor processes
ps aux | grep uvicorn
ps aux | grep celery
```

---

## **📊 Performance Benchmarks**

### **Expected Performance Metrics**
- **Response Time:** Health endpoints < 100ms
- **Webhook Processing:** < 500ms per message
- **Concurrent Users:** 100+ simultaneous WhatsApp users
- **Message Throughput:** 1000+ messages/hour
- **Uptime:** 99.9%

### **Resource Requirements**
- **Minimum:** 1 CPU, 1GB RAM, 10GB storage
- **Recommended:** 2 CPU, 2GB RAM, 20GB storage
- **High Load:** 4 CPU, 4GB RAM, 50GB storage

---

## **🚨 Emergency Procedures**

### **Rollback Plan**
```bash
# 1. Stop current deployment
docker stop inspector-whatsapp-bot

# 2. Start previous version
docker run -d --name inspector-whatsapp-bot-backup [previous-image]

# 3. Update DNS/load balancer if needed
# 4. Investigate and fix issues
```

### **Quick Debugging**
```bash
# Check application status
curl http://localhost:8000/api/v1/health/detailed

# Check logs for errors
grep -i error logs/app.log
grep -i error logs/errors.log

# Check system resources
docker stats inspector-whatsapp-bot
htop

# Test webhook connectivity
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

---

## **✅ Sign-off Checklist**

Before going live, ensure all stakeholders have signed off:

- [ ] **Development Team** - Code review and testing complete
- [ ] **DevOps Team** - Infrastructure and monitoring ready
- [ ] **Security Team** - Security review and penetration testing complete
- [ ] **Business Team** - User acceptance testing complete
- [ ] **Support Team** - Documentation and runbooks ready

---

## **📞 Support Contacts**

- **Technical Issues:** [Your support team]
- **WhatsApp API Issues:** Meta Business Support
- **Inspector API Issues:** [Inspector platform support]
- **Infrastructure Issues:** [DevOps team]

---

**Last Updated:** 2025-09-20
**Version:** 1.0.0
**Deployment Status:** ✅ Ready for Production Setup