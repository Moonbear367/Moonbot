MoonBot, 
Made by Moonbear367
 
A self-hosted server alert bot that primerly uses discord DM's for delivary.
Combatable with both linux and windows due to being written in python 3.14 
It uses 'uv' for enviroment and package managemnt

linux workflow:
- Download and place the files inside a new user-account for enviroment separation
- Onces downloaded move to bots home directory and type: "uv sync"
- Before running the bot go through the config & pyproject .tomls to customise bot
- After editing use: "uv run moonbot" to start 

If you want to use systemctl to manage the bot, theres a ".servise" file inclueded,
place it inside: /etc/systemed/systems/ and use "moonbot.service" to interact with it


