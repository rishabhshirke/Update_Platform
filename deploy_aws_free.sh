#!/bin/bash
# AWS Free Tier Deployment Script for EOD Reports System
# This script automates the AWS infrastructure setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   AWS Free Tier Deployment - EOD Reports System     ║${NC}"
echo -e "${GREEN}║   100% FREE for 12 Months                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration Variables
KEY_NAME="eod-reports-key"
SG_NAME="eod-reports-sg"
INSTANCE_NAME="eod-reports-server"
REGION="ap-south-1"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}🔍 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run: aws configure${NC}"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
AWS_USER=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)
echo -e "${GREEN}✅ Authenticated as: $AWS_USER (Account: $AWS_ACCOUNT)${NC}"
echo ""

# Phase 1: Create EC2 Key Pair
echo -e "${YELLOW}📝 Phase 1/4: Creating EC2 key pair...${NC}"
if [ -f ~/.ssh/${KEY_NAME}.pem ]; then
    echo -e "${YELLOW}⚠️  Key pair already exists at ~/.ssh/${KEY_NAME}.pem${NC}"
    read -p "Do you want to delete and recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm ~/.ssh/${KEY_NAME}.pem
        aws ec2 delete-key-pair --key-name $KEY_NAME 2>/dev/null || true
    else
        echo -e "${GREEN}✅ Using existing key pair${NC}"
    fi
fi

if [ ! -f ~/.ssh/${KEY_NAME}.pem ]; then
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ~/.ssh/${KEY_NAME}.pem
    chmod 400 ~/.ssh/${KEY_NAME}.pem
    echo -e "${GREEN}✅ Key pair created: ~/.ssh/${KEY_NAME}.pem${NC}"
else
    echo -e "${GREEN}✅ Using existing key pair: ~/.ssh/${KEY_NAME}.pem${NC}"
fi
echo ""

# Phase 2: Create Security Group
echo -e "${YELLOW}🔒 Phase 2/4: Creating security group...${NC}"

# Check if security group exists
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "$SECURITY_GROUP_ID" == "None" ]; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for EOD Reports application" \
        --query 'GroupId' \
        --output text)
    echo -e "${GREEN}✅ Security Group created: $SECURITY_GROUP_ID${NC}"

    # Add rules
    echo -e "${YELLOW}🔓 Adding security rules...${NC}"
    MY_IP=$(curl -s https://checkip.amazonaws.com)

    # SSH rule (from your IP only)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 22 --cidr $MY_IP/32 \
        --output text
    echo -e "${GREEN}  ✅ SSH (22) from $MY_IP${NC}"

    # HTTP rule
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --output text
    echo -e "${GREEN}  ✅ HTTP (80) from anywhere${NC}"

    # HTTPS rule
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 443 --cidr 0.0.0.0/0 \
        --output text
    echo -e "${GREEN}  ✅ HTTPS (443) from anywhere${NC}"
else
    echo -e "${GREEN}✅ Using existing security group: $SECURITY_GROUP_ID${NC}"
fi
echo ""

# Phase 3: Launch EC2 Instance
echo -e "${YELLOW}🖥️  Phase 3/4: Launching EC2 t2.micro instance...${NC}"

# Check if instance already exists
EXISTING_INSTANCE=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running,pending,stopped" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text 2>/dev/null || echo "None")

if [ "$EXISTING_INSTANCE" != "None" ]; then
    echo -e "${YELLOW}⚠️  Instance already exists: $EXISTING_INSTANCE${NC}"
    read -p "Do you want to terminate it and create a new one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  Terminating existing instance...${NC}"
        aws ec2 terminate-instances --instance-ids $EXISTING_INSTANCE
        aws ec2 wait instance-terminated --instance-ids $EXISTING_INSTANCE
        echo -e "${GREEN}✅ Instance terminated${NC}"
    else
        INSTANCE_ID=$EXISTING_INSTANCE
        echo -e "${GREEN}✅ Using existing instance: $INSTANCE_ID${NC}"
    fi
fi

if [ -z "$INSTANCE_ID" ]; then
    # Get latest Ubuntu 20.04 AMI
    echo -e "${YELLOW}🔍 Finding latest Ubuntu 20.04 AMI...${NC}"
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
        --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
        --output text)
    echo -e "${GREEN}✅ AMI ID: $AMI_ID${NC}"

    # Launch instance
    echo -e "${YELLOW}🚀 Launching instance...${NC}"
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type t2.micro \
        --key-name $KEY_NAME \
        --security-group-ids $SECURITY_GROUP_ID \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)

    echo -e "${GREEN}✅ Instance ID: $INSTANCE_ID${NC}"
    echo -e "${YELLOW}⏳ Waiting for instance to start (this may take 1-2 minutes)...${NC}"
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo -e "${GREEN}✅ Instance is running!${NC}"
fi

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)
echo -e "${GREEN}📍 Public IP: $PUBLIC_IP${NC}"
echo ""

# Phase 4: Allocate Elastic IP
echo -e "${YELLOW}🌐 Phase 4/4: Allocating Elastic IP...${NC}"

# Check if instance already has an Elastic IP
EXISTING_EIP=$(aws ec2 describe-addresses \
    --filters "Name=instance-id,Values=$INSTANCE_ID" \
    --query 'Addresses[0].PublicIp' \
    --output text 2>/dev/null || echo "None")

if [ "$EXISTING_EIP" != "None" ]; then
    ELASTIC_IP=$EXISTING_EIP
    echo -e "${GREEN}✅ Instance already has Elastic IP: $ELASTIC_IP${NC}"
else
    # Allocate new Elastic IP
    ALLOCATION_ID=$(aws ec2 allocate-address \
        --domain vpc \
        --query 'AllocationId' \
        --output text)

    # Associate with instance
    aws ec2 associate-address \
        --instance-id $INSTANCE_ID \
        --allocation-id $ALLOCATION_ID \
        --output text

    ELASTIC_IP=$(aws ec2 describe-addresses \
        --allocation-ids $ALLOCATION_ID \
        --query 'Addresses[0].PublicIp' \
        --output text)

    echo -e "${GREEN}✅ Elastic IP allocated: $ELASTIC_IP${NC}"
    echo -e "${GREEN}💡 This IP will persist even if you stop/start the instance${NC}"
fi
echo ""

# Save deployment information
DEPLOYMENT_FILE="deployment_info.txt"
cat > $DEPLOYMENT_FILE <<EOF
╔══════════════════════════════════════════════════════╗
║        AWS Deployment Information                    ║
╚══════════════════════════════════════════════════════╝

📋 AWS Resources
─────────────────────────────────────────────────────
Instance ID:        $INSTANCE_ID
Security Group:     $SECURITY_GROUP_ID
Elastic IP:         $ELASTIC_IP
Region:             $REGION
Instance Type:      t2.micro (Free Tier)
Storage:            30 GB gp3 (Free Tier)
SSH Key:            ~/.ssh/${KEY_NAME}.pem

🔗 Access Information
─────────────────────────────────────────────────────
Application URL:    http://$ELASTIC_IP
Admin Panel:        http://$ELASTIC_IP/admin

🔐 SSH Access
─────────────────────────────────────────────────────
Command:
ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$ELASTIC_IP

💰 Cost Information
─────────────────────────────────────────────────────
Current Monthly Cost:  \$0.00 (Free Tier)
Free Tier Duration:    12 months from signup
After Free Tier:       ~\$8-10/month

📝 Next Steps
─────────────────────────────────────────────────────
1. Wait 2-3 minutes for instance to fully initialize
2. SSH into the server:
   ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$ELASTIC_IP

3. Follow the setup steps in FREE_DEPLOYMENT_PLAN.md:
   - Install PostgreSQL, Python, Nginx
   - Clone repository
   - Configure application
   - Set up Gunicorn and Nginx
   - Configure cron jobs

4. Access your application at:
   http://$ELASTIC_IP

📚 Documentation
─────────────────────────────────────────────────────
Full deployment guide: FREE_DEPLOYMENT_PLAN.md
Repository: https://github.com/rishabhshirke/Update_Platform

⚠️  Important Reminders
─────────────────────────────────────────────────────
✓ Set up billing alerts in AWS Console (recommend \$1/month)
✓ Keep your SSH key secure: ~/.ssh/${KEY_NAME}.pem
✓ Run instance 24/7 to stay within 750 hours/month free tier
✓ If you stop the instance, Elastic IP remains free (when associated)
✓ Monitor your Free Tier usage in AWS Billing Dashboard

Deployment completed at: $(date)
EOF

# Display summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ AWS Infrastructure Setup Complete! ✅           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
cat $DEPLOYMENT_FILE
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Deployment info saved to: $DEPLOYMENT_FILE${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}🎯 Quick Start:${NC}"
echo -e "${YELLOW}1. SSH to server:${NC} ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$ELASTIC_IP"
echo -e "${YELLOW}2. Follow FREE_DEPLOYMENT_PLAN.md for complete setup${NC}"
echo ""
echo -e "${GREEN}🎉 Happy Deploying! 🚀${NC}"
