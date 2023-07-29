# Faehre 73 BOT
The ferry 73 connects Landungsbrücken and Ernst-August-Schleuse.
At times the ferry doesnt go bc.
- the tide is too high (sometimes announced last minute) and the ferry will terminate instead at Argentinienbrücke
- HADAG announces other reasons for disruption of services

This script checks the predicted tide levels provided by 
   > "copyright_note": "©Bundesamt für Seeschifffahrt und Hydrographie (BSH). Das BSH übernimmt für die angegebenen Informationen keine Gewähr. Beobachtungen:©Generaldirektion Wasserstraßen und Schifffahrt",

and sends an alarm to a telegram group if the tide is forecasted to be too high.

Also forwards all HADAG tweets concerning line 73.

## How to run
Create .env file , set your 
- BEARER_TOKEN_TWITTER
- CHAT_ID_TELEGRAM
- BOT_TOKEN_TELEGRAM

run main.py

### How to create a bot and add it to a telegram group?
0 - Create Group without the bot

1 - Create bot: Look for "Botfather" in your contacts. Make a new bot by sending "/newbot" to him.
Choose a name etc.

2- Add the bot to the group.
Go to the group, click on group name, click on Add members, in the searchbox search for your bot like this: @my_bot, select your bot and click add.

3- Send a dummy message to the bot.
You can use this example: /my_id @my_bot
(I tried a few messages, not all the messages work. The example above works fine. Maybe the message should start with /)

4- Go to following url: https://api.telegram.org/botXXX:YYYY/getUpdates
replace XXX:YYYY with your bot token

5- Look for "chat":{"id":-zzzzzzzzzz,
-zzzzzzzzzz is your chat id (with the negative sign).

6- Testing: You can test sending a message to the group with a curl:

curl -X POST "https://api.telegram.org/botXXX:YYYY/sendMessage" -d "chat_id=-zzzzzzzzzz&text=my sample text"

If you miss step 2, there would be no update for the group you are looking for. Also if there are multiple groups, you can look for the group name in the response ("title":"group_name").