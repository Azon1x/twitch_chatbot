import json
from twitchio.ext import commands
import requests
import os

os.startfile("YOUR TOKEN_FILE.url")
input = input("Vložte token:")
token = str(input)

with open("{oauth_token.txt}", "r") as t:
    bot_token = t.read().strip()
    
bot_nickname = "BOT NICK"
user_points = {}

# Load saved points data from file if it exists
try:
    with open("YOUR POINTS_FILE.txt", "r") as f:
        user_points = json.load(f)
except FileNotFoundError:
    exit()

clientid = "YOUR CLIENT_ID"
clientsecret = "YOUR CLIENT_SECRET"

try:
    url = "https://id.twitch.tv/oauth2/token"
    querystring = {"client_id":clientid,"client_secret":clientsecret,"grant_type":"authorization_code","redirect_uri":"http://localhost","code":{token}}
    headers = {"cookie": "twitch.lohp.countryCode=CZ; server_session_id={YOUR SERVER_SESSION_ID}; unique_id={YOUR UNIQUE_ID}; unique_id_durable={YOUR UNIQUE_ID}; twitch.lohp.countryCode=CZ"}
    response = requests.request("POST", url, headers=headers, params=querystring).text
    access_token = json.loads(response)['access_token']
except:
    print("Nesprávný token")

oauth_token = access_token

channel_name = 'YOUR CHANNEL ID'
headers = {
    'Client-ID': clientid,
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/json',
    'User-Agent': {bot_nickname}
}

# New bot instance
bot = commands.Bot(
    token=bot_token,
    nick=bot_nickname,
    prefix='!',
    initial_channels=['YOUR CHANNEL NAME']
)

print("YOUR BOT NAME is running!")

@bot.command(name="hello")
async def hello_command(ctx):
    try:
        args = ctx.message.content.split(" ")
        user = args[1].lstrip("@").lower()
        
        await ctx.send(f"Hello, {user}!")
    
    except:
        await ctx.reply(f"Hello, {ctx.author.name}!")

@bot.command(name="addpoints")
async def addpoints_command(ctx):
    try:
        # Check if the user has permission to add points
        if "broadcaster" not in ctx.author.badges and "moderator" not in ctx.author.badges:
            await ctx.send("Sorry, you don't have permission to use this command.")

        else:
            # Get the user and amount of points to add
            args = ctx.message.content.split(" ")
            user = args[1].lstrip("@").lower()
            points = int(args[2])
            
            # Check if the points provided is a positive number
            if points <= 0:
                await ctx.send("Error: The points argument must be a positive number.")
                return
            
            # Update the point counter dictionary
            if user in user_points:
                user_points[user] += points
            else:
                user_points[user] = points

            # Write the updated points data to file
            with open("{YOUR POINTS_FILE.txt}", "w") as f:
                json.dump(user_points, f)

            # Send a message confirming the points were added
            await ctx.send(f"{points} points added to {user}'s total.")

    except (IndexError, AttributeError):
        await ctx.send("Error: Invalid command syntax. Usage: !addpoints <username> <amount>")
    except:
        await ctx.reply("Something went wrong, try again later.")

@bot.command(name="removepoints")
async def removepoints_command(ctx):
    try:
        # Check if the user has permission to remove points
        if "broadcaster" not in ctx.author.badges and "moderator" not in ctx.author.badges:
            await ctx.send("Sorry, you don't have permission to use this command.")

        else:
            # Get the user and amount of points to remove
            args = ctx.message.content.split(" ")
            user = args[1].lstrip("@").lower()
            points = int(args[2])
            
            # Check if the points provided is a positive number
            if points <= 0:
                await ctx.send("Error: The points argument must be a positive number.")
                return
            
            # Check if the user has enough points to remove
            if user in user_points and user_points[user] >= points:
                user_points[user] -= points
            else:
                await ctx.send(f"Error: {user} doesn't have enough points to remove.")
                return

            # Write the updated points data to file
            with open("{YOUR POINTS_FILE.txt}", "w") as f:
                json.dump(user_points, f)

            # Send a message confirming the points were removed
            await ctx.send(f"{points} points removed from {user}'s total.")

    except (IndexError, AttributeError):
        await ctx.send("Error: Invalid command syntax. Usage: !removepoints <username> <amount>")
    except:
        await ctx.reply("Something went wrong, try again later.")

@bot.command(name="points")
async def points_command(ctx):
    try:
        args = ctx.message.content.split(" ")
        user = args[1].lstrip("@").lower()
        points = user_points.get(user, 0)

        await ctx.send(f"{user} has {points} points.")

    except:
        # Get the user's current points
        user = ctx.author.name
        points = user_points.get(user, 0)
        
        # Send a message with the user's points
        await ctx.send(f"{user} has {points} points.")

@bot.command(name="clip")
async def clip_command(ctx): 
    try: 
        # Create a clip for the current live stream
        clip_url = "https://api.twitch.tv/helix/clips"
        params = {
            "broadcaster_id": {channel_name},
            "has_delay": False
        }
        response = requests.post(clip_url, headers=headers, params=params)
        data = json.loads(response.text)
        clip_url = data["data"][0]["edit_url"]
        clean_clip_url = clip_url[:-5]

        # Send a message to the chat with the link to the created clip
        await ctx.send(f"Check out the new clip! {clean_clip_url}")
    except:
        await ctx.reply("Something went wrong, try again later.")

@bot.command(name='settitle')
async def change_title(ctx, *, new_title: str):
    try:
        if "broadcaster" not in ctx.author.badges and "moderator" not in ctx.author.badges:
            await ctx.send("Sorry, you don't have permission to use this command.")
        else:    
            url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_name}'
            data = {'title': new_title}
            response = requests.patch(url, headers=headers, json=data)
            
            # check the response status code to ensure the request was successful
            if response.status_code == 200 or response.status_code == 204:
                await ctx.send(f'Successfully changed stream title to "{new_title}"')
            else:
                await ctx.send(f'Failed to change stream title: {response.status_code}')
    except:
        await ctx.reply("Something went wrong, try again later.")

@bot.command(name='setgame')
async def set_game(ctx, *, game_name: str):
    try:
        if "broadcaster" not in ctx.author.badges and "moderator" not in ctx.author.badges:
                await ctx.send("Sorry, you don't have permission to use this command.")
        else:
            params = {
                'query': game_name,
            }
            response = requests.get('https://api.twitch.tv/helix/search/categories', headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    game_id = data['data'][0]['id']
                    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_name}&game_id={game_id}'
                    response = requests.patch(url, headers=headers)
                    if response.status_code == 200 or response.status_code == 204:
                        await ctx.send(f'Successfully changed stream game to "{game_name}"')
                    else:
                        await ctx.send(f'Failed to change stream game: {response.status_code}')
                else:
                    await ctx.send(f'Could not find game with name "{game_name}"')
            else:
                await ctx.send(f'Failed to search for game: {response.status_code}')
    except:
        await ctx.reply("Something went wrong, try again later.")


bot.run()

