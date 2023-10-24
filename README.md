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

The easiest way to run the docker image

1. Clone the repository and cd to the directory
   ```
   git clone https://github.com/StarshinePony/Derpy-Bot && cd Derpy-Bot
   ```

1. Build the Dockerfile
   ```
   docker build -t derpybot .
   ```

2. Run the Docker image
   ```
   docker run -d --restart always derpybot
   ```
