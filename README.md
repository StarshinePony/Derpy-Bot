# Derpy Bot
 Discord Bot with own warn system, economical system inbuilt music features and more!



 SETUP:
1. Clone the repo on your device
2. Create a .env file and add these lines of information:


    discord_token = "YOUR BOT TOKEN"

   
    authserver = YOUR MAIN SERVER ID

   
    developerid = YOUR USER ID
   
4. optionally deploy the repo to your server
5. if you want to run it on your home device run the command: pip install -r requirements.txt
6. start the bot with python main.py
7. Have fun!... And praise Derps


# Deploying on a Linux Server (Ubuntu)

The easiest way to deploy this bot on a linux server with a self updating feature is creatig a cron job and Github.

1. Pull your own or this respostory using ```git clone https://github.com/StarshinePony/Derpy-Bot/```
2. cd to the cloned directory using ```cd Derpy-Bot```
3. Make sure to follow step 2 from Setup.
4. Ignore the .env file ```git rm --cached .env```
5. Create a systemd job using ```sudo nano /etc/systemd/system/derpybot.service```
6. place the following text in the file. Replace <username> with your linux user
```
[Unit]
Description=Derpy-Bot systemd Job

[Service]
User=<username>
WorkingDirectory=/home/<username>/mxx/Derpy-Bot/
ExecStartPre=git pull
ExecStart=/usr/local/bin/python3.10 /home/runner2/mxx/Derpy-Bot/main.py
Restart=always
[Install]
WantedBy=multi-user.target
```
7. save the file using ^s and exit using ^x, start the service and enable the service: ```sudo systemctl start derpybot && sudo systemctl enable derpybot```
8. open crontab: ```sudo crontab -e```
9. paste the following text on a new line at the bottom: ```0 0 * * * sudo systemctl restart derpybot```
10. Save and exit again using ^s ^x
11. Done! Your bot now updates and restarts every day at 0:00

(script coming soon)
