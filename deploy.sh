#!/bin/bash

# 1️⃣ Navigate to your bot project folder
cd /data/data/com.termux/files/home/x402_peeranky || exit

# 2️⃣ Pull latest changes from GitHub
git pull origin main

# 3️⃣ Optional: Stop any running instance of your Flask bot
pkill -f "python3 app.py"

# 4️⃣ Start the Flask bot in the background
python3 app.py &

# 5️⃣ Optional: Print a message for confirmation
echo "Deployment complete. Flask bot is running with latest updates."
