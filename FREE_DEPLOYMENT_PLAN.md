# 100% FREE Deployment Plan - EOD Report System on AWS

**Goal:** Deploy Django application with PostgreSQL on AWS Free Tier with **$0 monthly cost** for 12 months.

**Strategy:** Use single EC2 instance for both web server AND database to stay completely free.

---

## 📋 Table of Contents

1. [Deployment Strategy](#deployment-strategy)
2. [Cost Analysis](#cost-analysis)
3. [Architecture Overview](#architecture-overview)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Step-by-Step Deployment](#step-by-step-deployment)
6. [Automated Deployment Script](#automated-deployment-script)
7. [Post-Deployment Tasks](#post-deployment-tasks)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment Strategy

### Why NOT Use RDS?

| Option | Cost | Why? |
|--------|------|------|
| **RDS db.t2.micro** | FREE for 12 months | ✅ Managed, but stops being free after trial |
| **PostgreSQL on EC2** | FREE forever (within EC2 hours) | ✅ Use same EC2 instance = no extra cost |

**Our Choice:** **PostgreSQL on EC2 Instance**
- Uses same 750 EC2 hours
- No separate RDS charges after 12 months
- Full control over database
- Single server = simpler architecture

---

## 💰 Cost Analysis

### What We'll Use:

| Resource | Specification | Free Tier Limit | Usage | Cost |
|----------|--------------|----------------|-------|------|
| **EC2 Instance** | t2.micro (1 vCPU, 1GB RAM) | 750 hours/month | 720 hours | **$0** |
| **EBS Storage** | 30 GB SSD | 30 GB/month | 30 GB | **$0** |
| **PostgreSQL** | On EC2 (not RDS) | Included in EC2 | - | **$0** |
| **Elastic IP** | 1 static IP | 1 IP (when attached) | 1 IP | **$0** |
| **Data Transfer** | Outbound | 15 GB/month | ~2-5 GB | **$0** |
| **Nginx/Gunicorn** | On EC2 | Included | - | **$0** |

### Monthly Cost Breakdown:

```
EC2 t2.micro:        $0.00  (Free Tier: 750 hrs)
EBS 30GB:            $0.00  (Free Tier: 30GB)
Elastic IP:          $0.00  (attached to running instance)
Data Transfer:       $0.00  (under 15GB)
PostgreSQL:          $0.00  (on EC2, no RDS)
-------------------------------------------
TOTAL:               $0.00/month ✅
```

**Duration:** 12 months FREE
**After Free Tier:** ~$8-10/month (just EC2 + EBS)

---

## 🏗️ Architecture Overview

### Single-Server Architecture (Cost Optimized):

```
┌─────────────────────────────────────────────────────────┐
│                    Internet                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AWS EC2 t2.micro Instance                  │
│              Ubuntu 20.04 (1GB RAM, 1 vCPU)            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Port 80/443: Nginx (Reverse Proxy + Static)   │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     ▼                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Port 8000: Gunicorn (WSGI Server)              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     ▼                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Django Application (eod_project)               │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     ▼                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Port 5432: PostgreSQL Database (Local)         │   │
│  │  - Database: eod_reports                        │   │
│  │  - User: eod_user                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Cron Jobs (Email Automation)                   │   │
│  │  - 6:00 PM IST: Send EOD reminders              │   │
│  │  - 6:30 PM IST: Send manager notifications      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Storage: 30 GB EBS (SSD)                              │
└─────────────────────────────────────────────────────────┘
```

### Traffic Flow:

```
User Request
    ↓
Nginx:80 (receives request)
    ↓
Gunicorn:8000 (processes Django)
    ↓
Django Application (business logic)
    ↓
PostgreSQL:5432 (data storage)
    ↓
Response back to user
```

---

## ✅ Pre-Deployment Checklist

### On Your Local Machine:

- [x] AWS CLI installed and configured
- [x] AWS account with Free Tier available
- [x] GitHub repository ready: `https://github.com/rishabhshirke/Update_Platform`
- [x] Project works locally with PostgreSQL
- [ ] Domain name (optional - can use EC2 IP)

### AWS Account Requirements:

- [x] Valid AWS account (account: 964680330236)
- [x] Credit card on file (for verification only)
- [x] IAM user with permissions (user: Mahesh)
- [x] Region selected: ap-south-1 (Mumbai)
- [ ] Billing alerts set up ($1 threshold)

### Required Information:

```bash
# Save these for later:
AWS Region: ap-south-1
EC2 Instance Type: t2.micro
AMI: Ubuntu 20.04 LTS
Storage: 30 GB gp3
PostgreSQL Version: 14
Python Version: 3.8
```

---

## 🚀 Step-by-Step Deployment

### Phase 1: Create EC2 Key Pair

**Purpose:** SSH access to your server

```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name eod-reports-key \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/eod-reports-key.pem

# Set permissions
chmod 400 ~/.ssh/eod-reports-key.pem

# Verify
ls -l ~/.ssh/eod-reports-key.pem
```

✅ **Success:** Key saved to `~/.ssh/eod-reports-key.pem`

---

### Phase 2: Create Security Group

**Purpose:** Firewall rules for your server

```bash
# Create security group
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name eod-reports-sg \
    --description "Security group for EOD Reports application" \
    --query 'GroupId' \
    --output text)

echo "Security Group ID: $SECURITY_GROUP_ID"

# Add SSH rule (from your IP only)
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr $MY_IP/32

# Add HTTP rule (from anywhere)
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Add HTTPS rule (from anywhere)
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Verify rules
aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --query 'SecurityGroups[0].IpPermissions'
```

✅ **Success:** Security group created with SSH, HTTP, HTTPS access

---

### Phase 3: Launch EC2 Instance

**Purpose:** Create your free web server

```bash
# Get latest Ubuntu 20.04 AMI ID
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

echo "AMI ID: $AMI_ID"

# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t2.micro \
    --key-name eod-reports-key \
    --security-group-ids $SECURITY_GROUP_ID \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=eod-reports-server}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Instance launched successfully!"
echo "Public IP: $PUBLIC_IP"
echo "SSH Command: ssh -i ~/.ssh/eod-reports-key.pem ubuntu@$PUBLIC_IP"
```

✅ **Success:** EC2 instance running with public IP

---

### Phase 4: Allocate Elastic IP (Optional but Recommended)

**Purpose:** Get a permanent IP address (free when attached)

```bash
# Allocate Elastic IP
ALLOCATION_ID=$(aws ec2 allocate-address \
    --domain vpc \
    --query 'AllocationId' \
    --output text)

# Associate with instance
aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID

# Get the Elastic IP
ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --query 'Addresses[0].PublicIp' \
    --output text)

echo "✅ Elastic IP allocated: $ELASTIC_IP"
echo "This IP will persist even if you stop/start the instance"
```

---

### Phase 5: Connect and Configure Server

**Purpose:** Install all necessary software

```bash
# SSH into server
ssh -i ~/.ssh/eod-reports-key.pem ubuntu@$PUBLIC_IP
```

**Once connected, run these commands:**

#### 5.1 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

#### 5.2 Install Python and Dependencies

```bash
# Install Python 3.8 and pip
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip

# Install build tools
sudo apt install -y build-essential libssl-dev libffi-dev

# Install Git
sudo apt install -y git

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Install Nginx
sudo apt install -y nginx

# Verify installations
python3.8 --version
psql --version
nginx -v
git --version
```

#### 5.3 Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE eod_reports;
CREATE USER eod_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE eod_user SET client_encoding TO 'utf8';
ALTER ROLE eod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE eod_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE eod_reports TO eod_user;
\q

# Test connection
psql -U eod_user -d eod_reports -h localhost
# Enter password when prompted
# Type \q to exit
```

#### 5.4 Create Application User

```bash
# Create user for running the app
sudo useradd -m -s /bin/bash eodapp
sudo usermod -aG sudo eodapp

# Switch to eodapp user
sudo su - eodapp
```

#### 5.5 Clone Repository

```bash
cd /home/eodapp
git clone https://github.com/rishabhshirke/Update_Platform.git
cd Update_Platform
```

#### 5.6 Create Virtual Environment

```bash
python3.8 -m venv venv
source venv/bin/activate
```

#### 5.7 Install Python Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

#### 5.8 Create Production Environment File

```bash
nano .env
```

**Add this content (update values):**

```bash
# Django Settings
SECRET_KEY=generate-a-new-secure-key-here-use-django-command
DEBUG=False
ALLOWED_HOSTS=YOUR_ELASTIC_IP,yourdomain.com

# Database (Local PostgreSQL)
DB_NAME=eod_reports
DB_USER=eod_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=shirkerishabh10@gmail.com
EMAIL_HOST_PASSWORD=ealqdszzdmkxiacr
DEFAULT_FROM_EMAIL=EOD Reports <shirkerishabh10@gmail.com>
```

**Generate SECRET_KEY:**

```bash
python3.8 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

#### 5.9 Run Migrations

```bash
cd /home/eodapp/Update_Platform
source venv/bin/activate
python manage.py migrate
```

#### 5.10 Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts
```

#### 5.11 Collect Static Files

```bash
python manage.py collectstatic --no-input
```

#### 5.12 Test Application

```bash
python manage.py runserver 0.0.0.0:8000
```

Open browser: `http://YOUR_ELASTIC_IP:8000`

**If works:** ✅ Press `Ctrl+C` to stop

---

### Phase 6: Configure Gunicorn Service

**Purpose:** Run Django as a service

```bash
# Exit eodapp user back to ubuntu
exit
```

#### 6.1 Create Gunicorn Socket

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

**Content:**

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

#### 6.2 Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Content:**

```ini
[Unit]
Description=gunicorn daemon for EOD Reports
Requires=gunicorn.socket
After=network.target

[Service]
User=eodapp
Group=www-data
WorkingDirectory=/home/eodapp/Update_Platform
EnvironmentFile=/home/eodapp/Update_Platform/.env
ExecStart=/home/eodapp/Update_Platform/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          eod_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 6.3 Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Test
sudo systemctl status gunicorn.socket
curl --unix-socket /run/gunicorn.sock localhost
```

---

### Phase 7: Configure Nginx

**Purpose:** Web server and reverse proxy

```bash
sudo nano /etc/nginx/sites-available/eod_reports
```

**Content:**

```nginx
server {
    listen 80;
    server_name YOUR_ELASTIC_IP;

    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias /home/eodapp/Update_Platform/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/eodapp/Update_Platform/media/;
        expires 30d;
    }

    # Django application
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/eod_reports /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Set Permissions

```bash
sudo usermod -aG eodapp www-data
sudo chmod 755 /home/eodapp
sudo chmod 755 /home/eodapp/Update_Platform
sudo chmod -R 755 /home/eodapp/Update_Platform/staticfiles
sudo chmod -R 755 /home/eodapp/Update_Platform/media
```

---

### Phase 8: Set Up Cron Jobs

**Purpose:** Automated email reminders

```bash
sudo su - eodapp
crontab -e
```

**Add these lines:**

```cron
# Send EOD reminders at 6:00 PM IST (12:30 UTC)
30 12 * * 1-5 cd /home/eodapp/Update_Platform && /home/eodapp/Update_Platform/venv/bin/python manage.py send_eod_reminders >> /home/eodapp/cron.log 2>&1

# Send manager notifications at 6:30 PM IST (13:00 UTC)
0 13 * * 1-5 cd /home/eodapp/Update_Platform && /home/eodapp/Update_Platform/venv/bin/python manage.py send_manager_notifications >> /home/eodapp/cron.log 2>&1
```

---

### Phase 9: Configure Firewall (UFW)

**Purpose:** Additional security layer

```bash
# Exit to ubuntu user
exit

# Install UFW (if not installed)
sudo apt install ufw

# Allow SSH (IMPORTANT - do first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

### Phase 10: Final Testing

```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status postgresql
```

**Test in browser:** `http://YOUR_ELASTIC_IP`

✅ **You should see your EOD Reports application!**

---

## 🤖 Automated Deployment Script

I'll create a script that automates everything:

```bash
#!/bin/bash
# save as: deploy_aws_free.sh

set -e  # Exit on error

echo "🚀 Starting FREE AWS Deployment for EOD Reports..."

# Variables
KEY_NAME="eod-reports-key"
SG_NAME="eod-reports-sg"
INSTANCE_NAME="eod-reports-server"
REGION="ap-south-1"

# Phase 1: Create Key Pair
echo "📝 Creating EC2 key pair..."
aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/${KEY_NAME}.pem
chmod 400 ~/.ssh/${KEY_NAME}.pem
echo "✅ Key pair created: ~/.ssh/${KEY_NAME}.pem"

# Phase 2: Create Security Group
echo "🔒 Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SG_NAME \
    --description "Security group for EOD Reports" \
    --query 'GroupId' \
    --output text)
echo "✅ Security Group ID: $SECURITY_GROUP_ID"

# Add rules
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 22 --cidr $MY_IP/32
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 443 --cidr 0.0.0.0/0
echo "✅ Security rules added"

# Phase 3: Launch EC2 Instance
echo "🖥️  Launching EC2 instance..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance ID: $INSTANCE_ID"
echo "⏳ Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Phase 4: Allocate Elastic IP
echo "🌐 Allocating Elastic IP..."
ALLOCATION_ID=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $ALLOCATION_ID
ELASTIC_IP=$(aws ec2 describe-addresses --allocation-ids $ALLOCATION_ID --query 'Addresses[0].PublicIp' --output text)
echo "✅ Elastic IP: $ELASTIC_IP"

# Save details
cat > deployment_info.txt <<EOF
Deployment Information
======================
Instance ID: $INSTANCE_ID
Security Group ID: $SECURITY_GROUP_ID
Elastic IP: $ELASTIC_IP
SSH Key: ~/.ssh/${KEY_NAME}.pem

SSH Command:
ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$ELASTIC_IP

Application URL:
http://$ELASTIC_IP
EOF

echo ""
echo "✅ ✅ ✅  AWS Infrastructure Created Successfully! ✅ ✅ ✅"
echo ""
cat deployment_info.txt
echo ""
echo "📋 Next Steps:"
echo "1. SSH into server: ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$ELASTIC_IP"
echo "2. Follow manual setup steps in FREE_DEPLOYMENT_PLAN.md"
echo ""
```

**Usage:**

```bash
chmod +x deploy_aws_free.sh
./deploy_aws_free.sh
```

---

## 📊 Post-Deployment Tasks

### 1. Set Up Billing Alerts

```bash
# Go to AWS Console
# Billing → Budgets → Create budget
# Set: $1/month alert threshold
```

### 2. Configure Database Backups

```bash
# Create backup script
sudo nano /home/eodapp/backup.sh
```

**Content:**

```bash
#!/bin/bash
BACKUP_DIR="/home/eodapp/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Django backup
cd /home/eodapp/Update_Platform
source venv/bin/activate
python manage.py dumpdata > $BACKUP_DIR/django_backup_$DATE.json

# PostgreSQL backup
pg_dump -U eod_user -h localhost eod_reports > $BACKUP_DIR/postgres_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Make executable and add to cron:**

```bash
chmod +x /home/eodapp/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/eodapp/backup.sh >> /home/eodapp/backup.log 2>&1
```

### 3. Monitor Resource Usage

```bash
# Install htop
sudo apt install htop

# Check resources
htop
df -h
free -h
```

### 4. Update Application

```bash
cd /home/eodapp/Update_Platform
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
```

---

## 📈 Monitoring & Maintenance

### Daily Checks

```bash
# Check services status
sudo systemctl status nginx gunicorn postgresql

# Check disk space
df -h

# Check memory
free -h

# Check application logs
sudo journalctl -u gunicorn -n 50
```

### Weekly Tasks

- Check billing dashboard
- Review application logs
- Test email functionality
- Verify backups exist

### Monthly Tasks

- Update system packages: `sudo apt update && sudo apt upgrade`
- Review free tier usage
- Clean old logs: `sudo journalctl --vacuum-time=30d`

---

## 🆘 Troubleshooting

### Issue: Can't SSH to instance

```bash
# Check security group allows your IP
aws ec2 describe-security-groups --group-ids $SECURITY_GROUP_ID

# Update SSH rule with current IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 22 --cidr $MY_IP/32
```

### Issue: 502 Bad Gateway

```bash
# Check Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Issue: Database connection error

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
sudo -u eodapp psql -U eod_user -d eod_reports -h localhost

# Check .env file
cat /home/eodapp/Update_Platform/.env
```

---

## 💰 Cost Tracking Commands

```bash
# Check instance running time
aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].LaunchTime'

# Check instance state
aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].State.Name'
```

---

## ✅ Deployment Checklist

- [ ] EC2 t2.micro instance launched
- [ ] Elastic IP allocated and associated
- [ ] Security group configured (SSH, HTTP, HTTPS)
- [ ] PostgreSQL installed and configured on EC2
- [ ] Django application cloned and configured
- [ ] Gunicorn service running
- [ ] Nginx configured and serving traffic
- [ ] Static files collected and serving
- [ ] Cron jobs configured for emails
- [ ] Firewall (UFW) enabled
- [ ] Database backups scheduled
- [ ] Billing alerts set up
- [ ] Application accessible via Elastic IP
- [ ] Admin panel working
- [ ] Email sending functional
- [ ] All tests passing

---

## 🎉 Success Metrics

Your deployment is successful when:

✅ Application accessible at: `http://YOUR_ELASTIC_IP`
✅ Admin panel works: `http://YOUR_ELASTIC_IP/admin`
✅ Employees can login and submit reports
✅ Managers can review reports
✅ Emails are sending (test with dry-run)
✅ Monthly cost: **$0.00**

---

## 📞 Quick Commands Reference

```bash
# SSH to server
ssh -i ~/.ssh/eod-reports-key.pem ubuntu@YOUR_ELASTIC_IP

# Restart services
sudo systemctl restart gunicorn nginx postgresql

# View logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log

# Update application
cd /home/eodapp/Update_Platform
git pull && sudo systemctl restart gunicorn

# Check costs (AWS Console only)
# Billing Dashboard → Cost Explorer
```

---

## 🎯 Expected Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| AWS Infrastructure Setup | 10 minutes | Automated |
| Server Configuration | 20 minutes | Manual |
| Application Deployment | 15 minutes | Manual |
| Testing & Verification | 10 minutes | Manual |
| **Total** | **~55 minutes** | |

---

## 🚀 Ready to Deploy?

**Run this command to start:**

```bash
cd /home/my/Desktop/Update_Platform
./deploy_aws_free.sh
```

**Then follow the on-screen instructions!**

---

**Questions or issues?** Check the troubleshooting section or AWS documentation.

**Good luck with your FREE deployment!** 🎉💰
