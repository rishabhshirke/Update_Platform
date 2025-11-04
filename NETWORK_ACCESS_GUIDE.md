# Network Access Guide - EOD Report System

## Access the Application from Other Devices

Your EOD Report System is now configured to be accessible from other devices on your network!

---

## 🌐 Server Information

**Server IP Address:** `192.168.0.103`
**Port:** `8000`

---

## 🚀 How to Start the Server

### Step 1: Start Server for Network Access

Instead of the regular `python manage.py runserver`, use:

```bash
cd /home/my/Desktop/Update_Platform
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Important:** Use `0.0.0.0:8000` instead of default to accept connections from other devices!

### Step 2: Verify Server is Running

You should see:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

---

## 📱 How to Access from Other Devices

### From Any Device on the Same Network:

**Option 1: Using IP Address**
```
http://192.168.0.103:8000/
```

**Option 2: Direct URLs**
- **Login**: http://192.168.0.103:8000/accounts/login/
- **Register**: http://192.168.0.103:8000/accounts/register/
- **Admin**: http://192.168.0.103:8000/admin/

### Supported Devices:

✅ **Desktop Computers** (Windows, Mac, Linux)
✅ **Laptops**
✅ **Tablets** (iPad, Android tablets)
✅ **Smartphones** (iPhone, Android phones)
✅ **Any device with a web browser on the same network**

---

## 🔧 Network Requirements

### Same Network:
- All devices must be connected to the **same WiFi network** or LAN
- Example: All connected to "Office WiFi" or same router

### Firewall:
If you can't connect from other devices:

**Linux (Ubuntu/Debian):**
```bash
# Allow port 8000
sudo ufw allow 8000/tcp

# Check firewall status
sudo ufw status
```

**Check if port is listening:**
```bash
netstat -tuln | grep 8000
```

---

## 📋 Step-by-Step Access Instructions

### For Other Employees:

**On Their Device:**

1. **Connect to the same WiFi network** as the server
2. **Open a web browser** (Chrome, Firefox, Safari, etc.)
3. **Type in the address bar:**
   ```
   http://192.168.0.103:8000
   ```
4. **Login** with their credentials
5. **Submit EOD reports** from any device!

### Example Scenario:

```
Server Computer: 192.168.0.103 (Your Desktop)
├── Running: python manage.py runserver 0.0.0.0:8000
│
Employee's Laptop: 192.168.0.105
├── Browser: http://192.168.0.103:8000
├── Login: EMP1 / Emp@1234
└── ✅ Can submit reports!

Employee's Phone: 192.168.0.112
├── Browser: http://192.168.0.103:8000
├── Login: EMP1 / Emp@1234
└── ✅ Can submit reports!

Manager's Tablet: 192.168.0.120
├── Browser: http://192.168.0.103:8000
├── Login: Manager1 / Manager@123
└── ✅ Can review reports!
```

---

## 🔍 Troubleshooting

### Can't Access from Other Devices?

**Check 1: Server Running with 0.0.0.0**
```bash
# Make sure you're using:
python manage.py runserver 0.0.0.0:8000

# NOT just:
python manage.py runserver  # ❌ Won't work from other devices
```

**Check 2: Firewall**
```bash
# Temporarily disable firewall (for testing)
sudo ufw disable

# If it works, then enable and allow port 8000
sudo ufw enable
sudo ufw allow 8000/tcp
```

**Check 3: Same Network**
```bash
# On server computer
ip addr show

# On other device, check it's on same network
# IP should be 192.168.0.XXX
```

**Check 4: Ping Test**
```bash
# From other device, ping the server
ping 192.168.0.103
```

---

## 📱 Mobile-Friendly UI

The application is **fully responsive** and works great on mobile devices:

✅ Touch-friendly buttons
✅ Responsive tables
✅ Mobile-optimized forms
✅ Professional design on all screen sizes

---

## 🔐 Security Notes

### Development Mode (Current Setup):
- Using `0.0.0.0:8000` with `DEBUG=True`
- Suitable for internal network testing
- **DO NOT expose to public internet**

### For Production Deployment:
- Use proper web server (Nginx + Gunicorn)
- Set `DEBUG=False`
- Use HTTPS/SSL certificates
- Restrict `ALLOWED_HOSTS` to specific domains
- Set up proper firewall rules

---

## 💡 Tips

### Keep Server Running:
Use `screen` or `tmux` to keep server running in background:

```bash
# Install screen
sudo apt install screen

# Start screen session
screen -S eod_server

# Run server
cd /home/my/Desktop/Update_Platform
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Detach: Press Ctrl+A then D

# Reattach later:
screen -r eod_server
```

### Check Who's Connected:
```bash
# View server logs to see incoming requests
# You'll see IP addresses of devices accessing the app
```

### Static IP (Recommended):
- Set a static IP for your server computer
- This way the IP won't change after restart
- Configure in your router settings

---

## 📊 Quick Reference

```
┌────────────────────────────────────────────────────┐
│ ACCESS INFORMATION                                  │
├────────────────────────────────────────────────────┤
│ Server IP:    192.168.0.103                        │
│ Port:         8000                                  │
│ URL:          http://192.168.0.103:8000/          │
│                                                     │
│ Start Command:                                      │
│ python manage.py runserver 0.0.0.0:8000           │
│                                                     │
│ Login URLs:                                         │
│ - Employee:   http://192.168.0.103:8000/          │
│ - Manager:    http://192.168.0.103:8000/          │
│ - Admin:      http://192.168.0.103:8000/admin/    │
└────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

**To make the app available right now:**

```bash
cd /home/my/Desktop/Update_Platform
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

Then share this URL with your team:
```
http://192.168.0.103:8000
```

They can access it from any device on the same network! 📱💻🖥️

---

**Ready to go!** The configuration is complete. Just start the server with `0.0.0.0:8000` and share the IP address with your team.
