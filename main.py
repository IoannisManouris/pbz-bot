## ////// MODULES \\\\\\ ##

import discord
from discord import app_commands
from discord.app_commands import Group, command
from discord.ext import commands, tasks
from discord.ext.commands import GroupCog
import random
import os
import json
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

with (ROOT / "settings.json").open(encoding="utf-8") as settings_file:
    settings = json.load(settings_file)

from datetime import datetime
import typing
import requests
from datetime import datetime, timezone
from datetime import timedelta
import time as timeModule
import random
import asyncio

## ////// WEB VARIABLES \\\\\\ ##

Keys = {
    "api_leauge": os.getenv("API_LEAGUE_KEY", ""),
    "roblox": os.getenv("ROBLOX_OPEN_CLOUD_KEY", ""),
    "bloxlink": os.getenv("BLOXLINK_API_KEY", ""),
}
APIs = {
    "dog": "https://dog.ceo/api/breeds/image/random",
    "cat": "https://api.thecatapi.com/v1/images/search",
    "meme": "https://api.apileague.com/retrieve-random-memeKEYWORD_PLACEHOLDER",
    "joke": "https://api.apileague.com/retrieve-random-joke?TAG_PLACEHOLDERexclude-tags=nsfw,dark",
    "dadJoke": "https://icanhazdadjoke.com",
    "riddle": "https://api.apileague.com/retrieve-random-riddle?difficulty=DIFFICULTY_PLACEHOLDER",
    "roblox_ms": "https://apis.roblox.com/messaging-service/v1/universes/UNIVERSE_ID_PLACEHOLDER/topics/TOPIC_PLACEHOLDER",
    "roblox_info": "https://users.roblox.com/v1/users/USER_ID_PLACEHOLDER",
    "roblox_avatar": "https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=USER_ID_PLACEHOLDER&size=420x420&format=Png&isCircular=false",
    "colour": "https://www.thecolorapi.com/id?rgb=RGB_PLACEHOLDER",
    "bloxlinkDtR": f"https://api.blox.link/v4/public/guilds/{settings['guild_id']}/discord-to-roblox/USER_ID_PLACEHOLDER",
    "currency": "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/CURRENCY_PLACEHOLDER.json"
}
Headers = {
    "api_leauge": {"x-api-key": Keys["api_leauge"]},
    "roblox": {"x-api-key": Keys["roblox"], "Content-Type": "application/json"},
    "bloxlink": {"Authorization": Keys["bloxlink"]},
    "dadJoke": {"Accept": "application/json"}
}

## ////// VARIABLES \\\\\\ ##

Coins = {
    "tales": "🪙",
    "heads": "🪙"
}

eightBallResponses = ["Yes, definitely!", "It is certain.", "Without a doubt.", "Yes, absolutely!", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]

StatisticChannels = settings["statistic_channels"]
GameIds = settings["game_ids"]
RoleToggles = settings["role_toggles"]

ErrorDescriptions = {
    "401": {
        "Error": "IAKNA-401",
        "Description": "API key invalid for operation, check authorization key."
    },
    "403": {
        "Error": "AF-403",
        "Description": "Access forbidden."
    },
    "404": {
        "Error": "NF-404",
        "Description": "Not found."
    },
    "500": {
        "Error": "ISE-500",
        "Description": "Internal Server Error"
    },
    "400": {
        "Error": "BR-400",
        "Description": "Request could not be processed."
    },
    "?": {
        "Error": "UE-?",
        "Description": "Unknown Error."
    }
}

TimeUnits = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800
}

currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "SEK", "KRW", "SGD", "NOK", "MXN", "INR", "RUB", "BRL", "ZAR", "TRY", "TWD", "SAR", "DKK", "PLN", "LEV"]

## ////// BOT VARIABLES \\\\\\ ##

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix = "/", intents = intents)

async def configured_guild(interaction):
    return interaction.guild_id == settings["guild_id"]

## ////// FUNCTIONS \\\\\\ ##

def robloxAvatar(user_id):
    response = requests.get(APIs["roblox_avatar"].replace("USER_ID_PLACEHOLDER", str(user_id)))
    if response.status_code == 200:
        image = response.json()["data"][0]["imageUrl"]
        if image:
            return image
    else:
        return ""
    return ""

def robloxInfo(user_id):
    response = requests.get(APIs["roblox_info"].replace("USER_ID_PLACEHOLDER", str(user_id)))
    if response.status_code == 200:
        player_data = response.json()
        return {
            "username": player_data["name"],
            "display": player_data["displayName"],
            "avatar": robloxAvatar(user_id),
            "description": player_data["description"],
            "created": player_data["created"],
            "banned": player_data["isBanned"],
            "verified": player_data["hasVerifiedBadge"]
        }
    else:
        return []

def embed(title, description, footer = "", footer_url = "", image_url = "", thumbnail_url = "", colour_rgb = (0, 0, 0)):
    colour_rgb = discord.Color.from_rgb(colour_rgb[0], colour_rgb[1], colour_rgb[2])

    EmbedMessage = discord.Embed(title = title, description = description, color = colour_rgb)
    EmbedMessage.set_footer(text = footer, icon_url = footer_url)
    EmbedMessage.set_image(url = image_url)
    EmbedMessage.set_thumbnail(url = thumbnail_url)

    return EmbedMessage

def hasRole(user, roleId, guild):
    return (discord.utils.get(guild.roles, id = roleId) in user.roles)

def toSeconds(time):
    return int(time[:-1])*TimeUnits[time[-1].lower()]

async def UpdateStatisticChannels():
    guild = bot.get_guild(settings["guild_id"])
    if guild is None:
        return
    members = guild.member_count
    online = 0
    for member in guild.members:
        if member.status != discord.Status.offline:
            online += 1
    for key, title in (("members", f"👤 Members: {members}"), ("online", f"🟢 Online: {online}")):
        channel = guild.get_channel(StatisticChannels[key])
        if channel and channel.name != title:
            await channel.edit(name=title)

@tasks.loop(minutes=15)
async def statistic_loop():
    await UpdateStatisticChannels()

@bot.event
async def on_ready():
    await bot.tree.sync()
    if not statistic_loop.is_running():
        statistic_loop.start()

@bot.event
async def on_member_join(member):
    if member.guild.id == settings["guild_id"]:
        await UpdateStatisticChannels()

@bot.event
async def on_member_remove(member):
    if member.guild.id == settings["guild_id"]:
        await UpdateStatisticChannels()

## ////// GENERAL COMMANDS \\\\\\ ##

@bot.tree.command(name = "toggle", description = "Add/Remove pings that may or may not interest you.")
@app_commands.check(configured_guild)
@app_commands.describe(role = "The ping role that you'd like to add/remove.")
async def toggle(interaction: discord.Interaction, role: typing.Literal["💸 Giveaways Ping", "🎉 Events Ping", "📢 Community Ping"]):
    roleId = RoleToggles[role]
    roleObject = interaction.guild.get_role(roleId)
    user = interaction.user
    embedResponse = None
    if roleObject in user.roles:
        await user.remove_roles(roleObject)
        embedResponse = embed("Role Removed", f"You've successfully removed {roleObject.mention} from your role list!", colour_rgb = (194, 0, 0))
    else:
        await user.add_roles(roleObject)
        embedResponse = embed("Role Added", f"You've successfully added {roleObject.mention} to your role list!", colour_rgb = (0, 194, 3))
    await interaction.response.send_message(embed = embedResponse)

## ////// BOT COMMANDS \\\\\\ ##

bot_group = Group(name = "bot", description = "Bot related commands.")

@bot_group.command(name = "ping", description = "Get the bot's latency from our servers to discord via ms.")
@app_commands.check(configured_guild)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong {interaction.user.mention}! **({round(bot.latency * 10000, 1)} ms)**")

@bot_group.command(name = "sync", description = "Sync the bot to the latest stats!")
@app_commands.check(configured_guild)
@app_commands.checks.has_permissions(manage_guild=True)
async def sync(interaction: discord.Interaction):
    await UpdateStatisticChannels()
    await bot.tree.sync()
    await interaction.response.send_message(f"☑️ Sync was a success, thank you {interaction.user.mention}!")

bot.tree.add_command(bot_group)

## ////// GAME COMMANDS \\\\\\ ##

game_group = Group(name = "game", description = "Mini game commands!")

@game_group.command(name = "flip", description = "Flip a coin for a random decision!")
async def flip(interaction: discord.Interaction):
    coinEmoji = ""
    coinText = ""
    coinChance = random.randint(1, 2)
    if coinChance == 1:
        coinEmoji = Coins["tales"]
        coinText = "It's tales!"
    elif coinChance == 2:
        coinEmoji = Coins["heads"]
        coinText = "It's heads!"

    await interaction.response.send_message(f"{coinEmoji} {coinText}")

@game_group.command(name = "8ball", description = "Let the magic 8ball answer your question!")
@app_commands.describe(question = "The question that you'd like an answer for.")
async def eightBall(interaction: discord.Interaction, question: str):
    await interaction.response.send_message(f"**{interaction.user.nick}:** *{question}*\n**- 🎱:** {random.choice(eightBallResponses)}")

bot.tree.add_command(game_group)

## ////// FETCH COMMANDS \\\\\\ ##

fetch_group = Group(name = "fetch", description = "Fetch something.")

@fetch_group.command(name = "dog", description = "Find a random dog picture.")
async def dog(interaction: discord.Interaction):
    dog_request = requests.get(APIs["dog"])

    if dog_request.status_code == 200:
        dog_data = dog_request.json()
        if dog_data:
            dog_pic = dog_data["message"]
            await interaction.response.send_message(dog_pic)
        else:
            await interaction.response.send_message(f"❌ There was an error fetching a dog.\n```\nNo dog pictures found.\n```")
    elif dog_request.status_code == 401:
        await interaction.response.send_message("❌ There was an error fetching a dog.\n```\nUnauthorized HTTP 401, check client id.\n```")
    elif dog_request.status_code == 404:
        await interaction.response.send_message("❌ There was an error fetching a dog.\n```\nUnknown HTTP 404, invalid/outdated API.\n```")
    else:
        await interaction.response.send_message(f"❌ There was an error fetching a dog.\n```\nHTTP {dog_request.status_code}\n```")

@fetch_group.command(name = "cat", description = "Fetch a random cat picture.")
async def cat(interaction: discord.Interaction):
    cat_request = requests.get(APIs["cat"])

    if cat_request.status_code == 200:
        cat_data = cat_request.json()
        if cat_data:
            cat_pic = cat_data[0]["url"]
            await interaction.response.send_message(cat_pic)
        else:
            await interaction.response.send_message(f"❌ There was an error fetching a cat.\n```\nNo cat pictures found.\n```")
    elif cat_request.status_code == 401:
        await interaction.response.send_message("❌ There was an error fetching a cat.\n```\nUnauthorized HTTP 401, check client id.\n```")
    elif cat_request.status_code == 404:
        await interaction.response.send_message("❌ There was an error fetching a cat.\n```\nUnknown HTTP 404, invalid/outdated API.\n```")
    else:
        await interaction.response.send_message(f"❌ There was an error fetching a cat.\n```\nHTTP {cat_request.status_code}\n```")

@fetch_group.command(name = "meme", description = "Fetch a random meme.")
@app_commands.describe(keyword = "A keyword representing your meme")
async def meme(interaction: discord.Interaction, keyword: typing.Optional[str]):
    if keyword == None or keyword.replace(" ", "") == "":
        keyword = ""
    else:
        keyword = f"?keywords={keyword.replace(" ", "-")}"

    meme_request = requests.get(APIs["meme"].replace("KEYWORD_PLACEHOLDER", keyword), headers = Headers["api_leauge"])

    embedResponse = None

    if meme_request.status_code == 200:
        meme_data = meme_request.json()
        embedResponse = embed(meme_data["description"], "", image_url = meme_data["url"], footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]", colour_rgb = (57, 255, 20))
    else:
        error = ErrorDescriptions[str(meme_request.status_code)]
        if error == None:
            error = ErrorDescriptions["?"]
        embedResponse = embed(f"HTTP-{str(meme_request.status_code)}", f"There was an error while attempting to fetch a meme:\n```\n{error["Description"]}\n```", footer = f"{error["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))

    await interaction.response.send_message(embed = embedResponse)

@fetch_group.command(name = "joke", description = "Fetch a random joke.")
@app_commands.describe(tag = "A tag representing your joke")
async def joke(interaction: discord.Interaction, tag: typing.Optional[typing.Literal["animal", "clean", "one_liner", "food", "relationship", "sport", "kids", "holiday", "knock_knock", "nerdy", "law", "q_a", "school", "christmas", "analogy", "yo_mama", "blondes", "deep_thoughts", "dad_joke"]]):
    joke_request = None
    if tag == None:
        tag = ""
        joke_request = requests.get(APIs["joke"].replace("TAG_PLACEHOLDER", tag), headers = Headers["api_leauge"])
    elif tag == "dad_joke":
        joke_request = requests.get(APIs["dadJoke"], headers = Headers["dadJoke"])
    else:
        tag = f"include-tags={tag}&"
        joke_request = requests.get(APIs["joke"].replace("TAG_PLACEHOLDER", tag), headers = Headers["api_leauge"])

    if joke_request.status_code == 200:
        joke_data = joke_request.json()
        await interaction.response.send_message(joke_data["joke"].replace("`", "'"))
    else:
        error = ErrorDescriptions[str(joke_request.status_code)]
        if error == None:
            error = ErrorDescriptions["?"]
        embedResponse = embed(f"HTTP-{str(joke_request.status_code)}", f"There was an error while attempting to fetch a joke:\n```\n{error["Description"]}\n```", footer = f"{error["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))
        await interaction.response.send_message(embed = embedResponse)

@fetch_group.command(name = "riddle", description = "Fetch a random riddle.")
@app_commands.describe(difficulty = "The difficulty of your riddle.")
async def riddle(interaction: discord.Interaction, difficulty: typing.Optional[typing.Literal["easy", "medium", "hard"]]):
    if difficulty == None:
        difficulty = random.choice(["easy", "medium", "hard"])

    riddle_request = requests.get(APIs["riddle"].replace("DIFFICULTY_PLACEHOLDER", difficulty), headers = Headers["api_leauge"])

    embedResponse = None

    if riddle_request.status_code == 200:
        colour = None
        if difficulty == "easy":
            colour = (144, 238, 144)
        elif difficulty == "medium":
            colour = (255, 165, 0)
        elif difficulty == "hard":
            colour = (255, 69, 0)
        riddle_data = riddle_request.json()
        embedResponse = embed(f"{difficulty.capitalize()} Riddle!", f"**Riddle:**\n```\n{riddle_data["riddle"]}\n```\n**Answer:** ||{riddle_data["answer"]}||", colour_rgb = colour, footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]")
    else:
        error = ErrorDescriptions[str(riddle_request.status_code)]
        if error == None:
            error = ErrorDescriptions["?"]
        embedResponse = embed(f"HTTP-{str(riddle_request.status_code)}", f"There was an error while attempting to fetch a riddle:\n```\n{error["Description"]}\n```", footer = f"{error["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))

    await interaction.response.send_message(embed = embedResponse)

bot.tree.add_command(fetch_group)

## ////// RANDOM COMMANDS \\\\\\ ##

random_group = Group(name = "random", description = "Get something random.")

@random_group.command(name = "number", description = "Get a random number (0-100 is the default).")
@app_commands.describe(min = "The minimum it can be (0 is default).", max = "The maximum it can be (100 is default).")
async def number(interaction: discord.Interaction, min: typing.Optional[int], max: typing.Optional[int]):
    if not min:
        min = 0
    if not max:
        max = 100
    embedResponse = None
    if min > max:
        embedResponse = embed(title = "Error", description = "There was an error while attempting to get a random number:\n```\nMinimum number cannot be larger than the maximum number.\n```", footer = f"{ErrorDescriptions["400"]["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))
        await interaction.response.send_message(embed = embedResponse)
    else:
        randomNumber = random.randint(min, max)
        await interaction.response.send_message(str(randomNumber))

@random_group.command(name = "colour", description = "Get a random colour.")
async def colour(interaction: discord.Interaction):
    rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    colourResponse = requests.get(APIs["colour"].replace("RGB_PLACEHOLDER", f"{str(rgb[0])}, {str(rgb[1])}, {str(rgb[2])}"))
    embedResponse = None
    if colourResponse.status_code == 200:
        colourData = colourResponse.json()
        if colourData:
            embedResponse = embed(colourData["name"]["value"], f"**RGB:** {colourData["rgb"]["value"]}\n**HEX:** {colourData["hex"]["value"]}\n**HSL:** {colourData["hsl"]["value"]}\n**HSV:** {colourData["hsv"]["value"]}\n**CMYK:** {colourData["cmyk"]["value"]}\n**XYZ:** {colourData["XYZ"]["value"]}\n~~                           ~~\n**[Bare Image]({colourData["image"]["bare"]})**\n**[Named Image]({colourData["image"]["named"]})**\n*The image links are temporary, I'll attempt to turn them into a viewable image from the embed as soon as I find a fix.*", footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]", colour_rgb = rgb)
    elif ErrorDescriptions[str(colourResponse.status_code)]:
        description = ErrorDescriptions[str(colourResponse.status_code)]
        embedResponse = embed(f"HTTP-{str(colourResponse.status_code)}", description = description["Description"], footer = f"{description["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))
    else:
        description = ErrorDescriptions["?"]
        embedResponse = embed(f"HTTP-{str(colourResponse.status_code)}", description = description["Description"], footer = f"{description["Error"]} | {datetime.now().strftime("%d/%m/%Y")}", colour_rgb = (194, 0, 0))
    await interaction.response.send_message(embed = embedResponse)

bot.tree.add_command(random_group)

## ////// ROBLOX COMMANDS \\\\\\ ##

roblox_group = Group(name = "roblox", description = "Manage a roblox account from discord.")

## ////// CASUAL ROBLOX COMMANDS \\\\\\ ##

@roblox_group.command(name = "tax", description = "Find how many robux an amount is with tax.")
@app_commands.check(configured_guild)
@app_commands.describe(robux = "The amount of robux you want the creator to get.")
async def tax(interaction: discord.Interaction, robux: int):
    if robux < 0:
        await interaction.response.send_message("Enter a nonnegative amount.", ephemeral=True)
        return
    taxAmount = (10 * robux + 6) // 7
    taxEmbed = embed("Robux with tax", f"**Requested amount:** {robux} Robux\n**Robux with tax:** {taxAmount} Robux\n~~                                    ~~\n**Creator earnings:** {taxAmount*0.7} Robux\n**Roblox earnings:** {taxAmount*0.3} Robux", colour_rgb = (247, 235, 5), footer = f"{datetime.now().strftime("%d/%m/%Y")} | [dd/mm/yyyy]")
    await interaction.response.send_message(embed = taxEmbed)

@roblox_group.command(name = "devex", description = "Find how many cash you can get with devex.")
@app_commands.check(configured_guild)
@app_commands.describe(robux = "The amount of robux you want to exchange.", currency = "The currency that you'd like the robux to be exchanged for.")
async def devex(interaction: discord.Interaction, robux: int, currency: typing.Optional[typing.Literal[*currencies]]): # type: ignore
    cash = robux*0.0035
    if currency != None and currency != "USD":
        rate_response = requests.get(APIs["currency"].replace("CURRENCY_PLACEHOLDER", "usd"))
        print(rate_response.status_code)
        if rate_response.status_code == 200:
            rate_data = rate_response.json()
            rate_multiplier = rate_data["usd"][currency.lower()]
            if rate_multiplier:
                cash *= rate_multiplier
    else:
        currency = "USD"
    cash = round(cash, 2)
    await interaction.response.send_message(f"{robux} Robux are about {cash} {currency} via the Roblox DevEx Program.")

@roblox_group.command(name = "info", description = "Find information about a user's roblox account.")
@app_commands.check(configured_guild)
@app_commands.describe(user = "The user that you'd like to get info about.")
async def info(interaction: discord.Interaction, user: typing.Optional[discord.User]):
    if user == None:
        user = interaction.user
    robloxId = None
    bloxlinkResponse = requests.get(APIs["bloxlinkDtR"].replace("USER_ID_PLACEHOLDER", str(user.id)), headers = Headers["bloxlink"])
    Footer = None
    Description = None
    EmbedResponse = None
    if bloxlinkResponse.status_code != 200:
        error = ErrorDescriptions[str(bloxlinkResponse.status_code)]
        if not error:
            error = ErrorDescriptions["?"]
        Footer = f"{error["Error"]} | {datetime.now().strftime("%d/%m/%Y")}"
        if bloxlinkResponse.status_code == 404:
            Description = f"The user {user.mention} has not verified with bloxlink."
        else:
            Description = f"An error occured during the info process:\n```\n{error["Description"]}\n```"
    else:
        bloxlinkJSON = bloxlinkResponse.json()
        if bloxlinkJSON["robloxID"]:
            robloxId = bloxlinkJSON["robloxID"]
    if robloxId == None:
        Footer = f"NF-404 | {datetime.now().strftime("%d/%m/%Y")}"
        Description = f"The user {user.mention} has not verified with bloxlink."
        EmbedResponse = embed("Not verified", Description, footer = Footer, colour_rgb = (194, 0, 0))
    else:
        playerInfo = robloxInfo(int(robloxId))
        if not playerInfo or playerInfo == []:
            Footer = f"NF-404 | {datetime.now().strftime("%d/%m/%Y")}"
            Description = f"User's roblox ID is invalid."
            EmbedResponse = embed("Not Found", Description, footer = Footer, colour_rgb = (194, 0, 0))
        else:
            Footer = f"RS-200 | {datetime.now().strftime("%d/%m/%Y")}"
            title = playerInfo["display"]
            if playerInfo["verified"]:
                title = title+" ☑️"
            banned = None
            if playerInfo["banned"]:
                banned = "✅"
            else:
                banned = "❌"
            verified = None
            if playerInfo["verified"]:
                verified = "☑️"
            else:
                verified = "❌"
            created = datetime.strptime(playerInfo["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
            created = created.replace(tzinfo=timezone.utc)
            created = int(created.timestamp())
            EmbedResponse = embed(title, f"**Username:** @{playerInfo["username"]}\n**Description:**\n```\n{playerInfo["description"]}\n```\n**Created at:** <t:{created}> **|** <t:{created}:R>\n**Roblox Banned:** {banned}\n**Roblox Verified:** {verified}", footer = Footer, thumbnail_url = playerInfo["avatar"], colour_rgb = (0, 194, 3))
    await interaction.response.send_message(embed = EmbedResponse)

## ////// MOD ROBLOX COMMANDS \\\\\\ ##

@roblox_group.command(name = "kick", description = "Kick a player.")
@app_commands.check(configured_guild)
@app_commands.describe(game = "The game that the player is located in.", userid = "The roblox user ID of the player that you'd like to kick.", reason = "The reason that you're kicking the player for.")
async def kick(interaction: discord.Interaction, game: typing.Literal["Musical Statues"], userid: int, reason: typing.Optional[str]):
    if not hasRole(interaction.user, settings["game_moderator_role_id"], interaction.guild):
        await interaction.response.send_message("❌ You cannot use this command!", ephemeral = True)
        return
    gameId = str(GameIds[game])
    if reason == None or reason.replace(" ", "") == "":
        reason = "No reason specified."
    kickResponse = requests.post(APIs["roblox_ms"].replace("UNIVERSE_ID_PLACEHOLDER", gameId).replace("TOPIC_PLACEHOLDER", f"Kick_{userid}"), json = {"message": reason}, headers = Headers["roblox"])
    embedResponse = None
    ErrorTitle = "HTTP-"+str(kickResponse.status_code)
    Footer = None
    Description = None
    Thumbnail = ""
    if kickResponse.status_code != 200:
        error = ErrorDescriptions[str(kickResponse.status_code)]
        if not error:
            error = ErrorDescriptions["?"]
        Footer = error["Error"]
        Description = f"An error occured during the kick process:\n```\n{error["Description"]}\n```"
    else:
        playerInfo = robloxInfo(userid)
        if playerInfo == []:
            ErrorTitle = "INVALID USER ID"
            Footer = "IID-404"
            Description = f"There is no player with `{userid}` as their user id."
        else:
            Footer = "RS-200"
            Description = f"**{playerInfo["display"]}** `(@{playerInfo["username"]} | {userid})` has been successfully kicked from `{game}`:\n```\n{reason}\n```"
            Thumbnail = playerInfo["avatar"]
    Footer = Footer+f" | {datetime.now().strftime("%d/%m/%Y")}"
    if kickResponse.status_code == 401:
        embedResponse = embed(title = ErrorTitle, description = Description, footer = Footer, colour_rgb = (194, 0, 0))
    elif kickResponse.status_code == 403:
        embedResponse = embed(title = ErrorTitle, description = Description, footer = Footer, colour_rgb = (194, 0, 0))
    elif kickResponse.status_code == 500:
        embedResponse = embed(title = ErrorTitle, description = Description, footer = Footer, colour_rgb = (194, 0, 0))
    elif kickResponse.status_code == 400:
        embedResponse = embed(title = ErrorTitle, description = Description, footer = Footer, colour_rgb = (194, 0, 0))
    elif kickResponse.status_code == 200:
        embedResponse = embed(title = "Player has been kicked!", description = Description, footer = Footer, colour_rgb = (0, 194, 3), thumbnail_url = Thumbnail)
    else:
        embedResponse = embed(title = ErrorTitle, description = Description, footer = Footer, colour_rgb = (194, 0, 0))
    await interaction.response.send_message(embed = embedResponse)

bot.tree.add_command(roblox_group)

## ////// MUSICAL STATUES COMMANDS \\\\\\ ##

ms_group = Group(name = "ms", description = "Musical Statues commands.")

## ////// MOD COMMANDS \\\\\\ ##

mod_group = Group(name = "mod", description = "Moderation commands.")

@mod_group.command(name = "purge", description = "Clear a text channel's messages.")
@app_commands.check(configured_guild)
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(channel = "The channel that you want to purge.", limit = "The amount of messages that you want to purge.")
async def purge(interaction: discord.Interaction, channel: typing.Optional[discord.TextChannel], limit: int):
    if not channel:
        channel = interaction.channel
    if not channel.permissions_for(interaction.user).manage_messages:
        await interaction.response.send_message("Manage Messages is required in the selected channel.", ephemeral=True)
        return
    if limit >= 200 and not hasRole(interaction.user, settings["large_purge_role_id"], interaction.guild):
        await interaction.response.send_message("❌ Only the owners can purge more than 200 messages!", ephemeral = True)
    else:
        if limit == None: limit = 1024
        await interaction.response.send_message(f"✅ Started the purge for {limit} messages in {channel.mention}!", ephemeral = True)
        deleted = await channel.purge(limit = limit)
        await channel.send(f"✅ Successfully purged {len(deleted)} messages!")

@mod_group.command(name = "kick", description = "Kick a user off the server.")
@app_commands.check(configured_guild)
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(user = "The player that you'd like to kick.", reason = "The reason he'll be kicked for.")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: typing.Optional[str]):
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot moderate someone with the same or a higher role than you!")
    else:
        footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]"
        if reason == None or reason.replace(" ", "") == "":
            reason = "No comments."
        dm_channel = await user.create_dm()
        try:
            DM_Embed = embed("Server Kick", f"You've been kicked from `{interaction.guild.name}`:\n```\n{reason}\n```", footer = footer, colour_rgb = (194, 0, 0), thumbnail_url = (interaction.guild.icon.url if interaction.guild.icon else None))
            await dm_channel.send(embed = DM_Embed)
        except discord.Forbidden:
            print("Could not deliver the moderation notice.")
        await user.kick(reason = f"{reason} [Requested by @{interaction.user.name} | {interaction.user.id}]")
        embedKick = embed("User has been kicked!", f"{user.mention} **(@{user.name} | {user.id})** has been successfully kicked from `{interaction.guild.name}`:\n```\n{reason}\n```", footer = footer, colour_rgb = (0, 194, 3), thumbnail_url = user.display_avatar.url)
        await interaction.response.send_message(embed = embedKick)

@mod_group.command(name = "mute", description = "Mute a user in the server.")
@app_commands.check(configured_guild)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(user = "The user that you'd like to mute.", time = "The time he'll be muted for. (5s, 5m, 5h, 5d, 5w, etc.)", reason = "The reason he'll be muted for.")
async def mute(interaction: discord.Interaction, user: discord.Member, time: str, reason: typing.Optional[str]):
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot moderate someone with the same or a higher role than you!", ephemeral = True)
    else:
        try:
            time = toSeconds(time)
        except Exception:
            await interaction.response.send_message(f"❌ Please provide a valid time, {time} cannot be converted to seconds!", ephemeral = True)
            return
        footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]"
        if reason == None or reason.replace(" ", "") == "":
            reason = "No comments."
        dm_channel = await user.create_dm()
        try:
            DM_Embed = embed("Server Mute", f"You've been muted in `{interaction.guild.name}` and will be unmuted <t:{int(timeModule.time())+time}:R>`:\n```\n{reason}\n```", footer = footer, colour_rgb = (194, 0, 0), thumbnail_url = (interaction.guild.icon.url if interaction.guild.icon else None))
            await dm_channel.send(embed = DM_Embed)
        except discord.Forbidden:
            print("Could not deliver the moderation notice.")
        await user.timeout(timedelta(seconds = time), reason = f"{reason} [Requested by @{interaction.user.name} | {interaction.user.id}]")
        embedMute = embed("User has been muted!", f"{user.mention} **(@{user.name} | {user.id})** has been successfully muted in `{interaction.guild.name}` and will be unmuted <t:{int(timeModule.time())+time}:R>:\n```\n{reason}\n```", footer = footer, colour_rgb = (0, 194, 3), thumbnail_url = user.display_avatar.url)
        await interaction.response.send_message(embed = embedMute)

@mod_group.command(name = "unmute", description = "Unmute a user in the server.")
@app_commands.check(configured_guild)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.describe(user = "The user that you'd like to unmute.")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("This member is outside your role hierarchy.", ephemeral=True)
        return
    footer = f"{datetime.now().strftime("%d/%m/%Y")} [dd/mm/yyyy]"
    dm_channel = await user.create_dm()
    try:
        DM_Embed = embed("Server Unmute", f"You've been unmuted in `{interaction.guild.name}`.", footer = footer, colour_rgb = (0, 194, 3), thumbnail_url = (interaction.guild.icon.url if interaction.guild.icon else None))
        await dm_channel.send(embed = DM_Embed)
    except discord.Forbidden:
        print("Could not deliver the moderation notice.")
    await user.timeout(None)
    embedUnmute = embed("User has been unmuted!", f"{user.mention} **(@{user.name} | {user.id})** has been successfully unmuted in `{interaction.guild.name}`.", footer = footer, colour_rgb = (0, 194, 3), thumbnail_url = user.display_avatar.url)
    await interaction.response.send_message(embed = embedUnmute)

bot.tree.add_command(mod_group)

## ////// RUN PROCESS \\\\\\ ##

if __name__ == "__main__":
    bot.run(os.environ["DISCORD_TOKEN"])
