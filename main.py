###########################################################
## Bot that shows my love and affection for Omori Stonks ##
###########################################################

# Imports #
from discord.ext import commands
import discord
import requests
import random
import json
import os
import warnings
import time
import asyncio

from yahoo_fin import stock_info

import jsonwriter

###############
## Constants ##
###############
# Feel free to change these values to your liking #

APITOKENS = {

}

TOKEN = '' # Your bot's token
PREFIX = "$" # Prefix for commands for the bot

###############

# Bot #

bot = commands.Bot(command_prefix=PREFIX)

#Basic Stuff :)#
bot.remove_command("help")
warnings.filterwarnings("ignore", category=DeprecationWarning)

##################################################################
## --------------------- Helper Functions --------------------- ##
##################################################################

def marketOpen(): #Returns if market status in better grammar
    status = stock_info.get_market_status()
    if status == "OPEN":
        return "Open"
    elif status == "PRE":
        return "Pre-Market"
    elif status == "CLOSED":
        return "Closed"
    else:
        return "Post-Market"

#Examples: regularMarketChange, regularMarketDayLow, regularMarketDayHigh, gmtOffSetMilliseconds
def getStockAttributes(stock, atts): #returns sorted list of stock attributes passed
    acronym = stock.upper()
    raw = stock_info.get_quote_data(acronym)
    retList = []
    #print(raw)
    for i in atts:
        if i in raw:
            retList.append(raw[i])
        else:
            retList.append(None)
    return retList

################################
def checkServer(id): #Returns True if server exists
    if jsonwriter.serverExists(id):
        return True
    else:
        jsonwriter.initServer(id)
        return False
def checkUser(id, servID): #Returns True if user exists
    checkServer(servID)
    if jsonwriter.userExists(id, servID):
        return True
    else:
        jsonwriter.initUser(id, servID)
        return False
#################################

def getInventoryPrice(inv): #Returns total price of inventory
    total = 0
    for i in inv:
        total += stock_info.get_live_price(i["stock"]) * float(i["amount"])
    return total

##################################################################

##############
## Commands ##
##############

cmds_desc = {
    "help": {"desc": "Returns a list of valid commands",
             "aliases": ["cmds"]},
    "getprice": {"desc": "Returns the current price of a stock",
             "aliases": ["gp", "price"],
             "args": ["<stock name>"],
             "args_desc": ["Abbrivation or Name of Stock/Company"]},
    "inventory": {"desc": "Returns a list of stocks in your inventory",
             "aliases": ["inv", "i"],
             "args": ["<stocks or crypto>"],
             "args_desc": ["View stocks or cryptocurrencies (default: all)"]},
    "leaderboard": {"desc": "Returns a list of top valued players",
             "aliases": ["lb", "top"],
             "args": ["<flag>"],
             "args_desc": ["Learn more about flags with $help flags"]},
    "buy": {"desc": "Buys a stock",
             "aliases": ["b"],
             "args": ["<stock name>", "<amount>"],
             "args_desc": ["Abbrivation or Name of Stock/Company", "Amount of stocks to buy"]},
    "sell": {"desc": "Sells a stock",
             "aliases": ["s"],
             "args": ["<stock name>", "<amount>"],
             "args_desc": ["Abbrivation or Name of Stock/Company", "Amount of stocks to sell (can be 'all')"]},
}

@bot.command(name="help", aliases=cmds_desc["help"]["aliases"])
async def help(ctx):
    embed = discord.Embed(title="Omor-Bot Commands", description="Refer to this embed for info about commands!", color=0x8093F1)
    for i in cmds_desc.keys(): #Repeats for each command
        desc = "*"+cmds_desc[i]["desc"]+"*"

        if "aliases" in cmds_desc[i]:
            desc+= "\nAlt Commands: *"+" ".join(cmds_desc[i]["aliases"])+"*"


        if "args" in cmds_desc[i]:
            if "args_desc" in cmds_desc[i]:
                desc+= "\nArgument Descriptions:"
                for o in range(len(cmds_desc[i]["args"])):
                    desc+= "\n    *"+cmds_desc[i]["args"][o]+"*: "+cmds_desc[i]["args_desc"][o]

            embed.add_field(name="**"+PREFIX+i+" "+" ".join(cmds_desc[i]["args"])+"**:", value=desc, inline=False)
        else:
            embed.add_field(name="**"+PREFIX+i+"**:", value=desc, inline=False)

    embed.set_image(url="https://c.tenor.com/P8YGOH-QPMAAAAAd/omori-sunny-omori.gif")
    embed.set_footer(text="Stock-Game | Made by Gameknight#9101")
    await ctx.send(embed=embed)

@bot.command(name="getprice", aliases=cmds_desc["getprice"]["aliases"])
async def getprice(ctx, *, name):
    acronym = name.upper()
    price = stock_info.get_live_price(acronym)
    if price == None or price == 0:
        await ctx.send("Stock not found!")
        return
    else:
        price = round(price, 2)
    stats = getStockAttributes(acronym, ["regularMarketChange", "displayName", "marketCap"])
    color = [0xFF4141, "📉"]
    if float(stats[0]) > 0:
        color = [0x41FF5F, "📈"]
        stats[0] = "+"+str(round(float(stats[0]), 2))
    else:
        color = [0xFF4141, "📉"]
        stats[0] = str(round(float(stats[0]), 2))


    embed = discord.Embed(title=color[1]+" Price of "+str(stats[1])+" ("+acronym+") "+color[1], description="The market is: **"+marketOpen()+"**", color=color[0])
    embed.add_field(name="**Price: "+str(price)+" USD**", value="Day Change: *"+str(stats[0])+" USD*\nMarket Cap: "+str(stats[2]), inline=False)
    embed.set_footer(text="Stock-Game | Made by Gameknight#9101")
    embed.set_image(url="https://cdn.discordapp.com/attachments/742080383306432578/1009253356788797490/omori0.gif")
    await ctx.send(embed=embed)

@bot.command(name="inventory", aliases=cmds_desc["inventory"]["aliases"])
async def inventory(ctx, *t):
    checkUser(ctx.author.id, ctx.guild.id)
    user = jsonwriter.getUser(ctx.author.id, ctx.guild.id)
    if t == "Crypto":
        await ctx.send("Crypto not yet implemented!")
        return
    elif t == "Stocks":
        await ctx.send("Stocks not yet implemented!")
        return
    config = jsonwriter.getConfig(ctx.guild.id)
    embed = discord.Embed(title=ctx.author.display_name+"'s Inventory", description="Balance: **"+user["cash"]+" "+config[1]+"**\n**Total Inventory Value: "+str(getInventoryPrice(user["stocks"])+float(user["cash"]))+" "+config[1]+"**", color=0x8093F1)
    if len(user["stocks"]) == 0:
        embed.add_field(name="Empty :(", value="*Your inventory is empty right now!!! Use '$buy <stock name>' to buy some stocks!*", inline=False)
    else:
        embed.add_field(name="**|Stocks|**", value="*Sorted by Value*", inline=False)
        stocksTemp = []
        for acronym, amount in user["stocks"]:
            #[0. acronym, 1. amount, 2. price, 3. name]#
            stocksTemp.append([acronym, amount, float(amount)*stock_info.get_live_price(acronym), getStockAttributes(acronym, ["displayName"])[0]])

        def sortMethod(x):
            return x[2]
        stocksTemp.sort(key=sortMethod, reverse=True)

        for stock in stocksTemp:
            embed.add_field(name="**"+stock[3]+" ("+stock[0]+")**", value="Amount: "+str(stock[1])+" | Price: "+str(stock[2])+" "+config[1], inline=False)
    embed.set_footer(text="Stock-Game | Made by Gameknight#9101")
    await ctx.send(embed=embed)

@bot.command(name="leaderboard", aliases=cmds_desc["leaderboard"]["aliases"])
async def leaderboard(ctx, *t):
    users = jsonwriter.getServer(ctx.guild.id)["users"]

    lis = []
    for id, val in users.items():
        user = None
        try:
            user = await bot.fetch_user(int(id))
        except:
            user = bot.get_user(int(id))
        if user == None:
            continue
        lis.append([user, getInventoryPrice(val["stocks"])+float(val["cash"])])

    def sort_by_value(e):
        return e[1]

    sorted(lis, key=sort_by_value, reverse=True)

    config = jsonwriter.getConfig(ctx.guild.id)
    embed = discord.Embed(title="Leaderboard", description="*Top players in '"+ctx.guild.name+"'!*", color=0x8093F1)
    iteration = 1
    for i in lis:
        if iteration == 1:
            embed.add_field(name="**1: 👑"+i[0].display_name+"**", value="**Balance: "+str(i[1])+" "+config[1]+"**", inline=True)
        elif iteration == 2:
            embed.add_field(name="*2: 🥇"+i[0].display_name+"*", value="*Balance: "+str(i[1])+" "+config[1]+"*", inline=True)
        elif iteration == 3:
            embed.add_field(name="*3: 🥇"+i[0].display_name+"*", value="*Balance: "+str(i[1])+" "+config[1]+"*", inline=True)
        else:
            embed.add_field(name="*"+str(iteration)+": "+i[0].display_name, value="Balance: "+str(i[1])+" "+config[1], inline=True)
        iteration+=1
        if iteration == 101:
            embed.add_field(name="*...*", value="*...*", inline=True)
            break

    embed.set_footer(text="Stock-Game | Made by Gameknight#9101")
    await ctx.send(embed=embed)

@bot.command(name="buy", aliases=cmds_desc["buy"]["aliases"])
async def buy(ctx, *args):
    checkUser(ctx.author.id, ctx.guild.id)
    info = jsonwriter.getUser(ctx.author.id, ctx.guild.id)
    if len(args) < 2:
        await ctx.send("Please specify a stock to buy and how many!")
        return
    config = jsonwriter.getConfig(ctx.guild.id)
    acronym = args[0].upper()
    pps = stock_info.get_live_price(acronym)
    stocknum = float(args[1])
    atts = getStockAttributes(acronym, ["displayName"])
    embed1 = discord.Embed(title="**Buy Stock "+atts[0]+" ("+acronym+")?**", description="*Are you sure you want to buy '"+str(stocknum)+"' "+atts[0]+" stocks for "+str(stocknum*pps)+" "+config[1]+"?*", color=0x8093F1)
    embed1.add_field(name="**Remaining Balance After Transaction:**", value="*"+str(float(info["cash"])-(stocknum*pps))+" "+config[1]+"*", inline=False)
    embed1.set_footer(text="*React with ✅ to confirm or ❌ to cancel*")
    message = await ctx.send(embed=embed1)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    try: #Waiting for confirmation reaction (check or X)
        reaction, user = await bot.wait_for("reaction_add", timeout=30, check=lambda reaction, user: (reaction.emoji == '✅' or reaction.emoji == '❌') and user == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("Transaction cancelled!")
        return

    if reaction.emoji == '❌':
        await ctx.send("Transaction cancelled!")
        return
    elif reaction.emoji == '✅':
        ret = jsonwriter.buyStock(ctx.author.id, ctx.guild.id, acronym, stocknum, pps)
        if ret != True:
            await ctx.send("ERROR: "+ret+"\n*(You were not charged)*")
            return
        embed = discord.Embed(title="**Successfully bought "+atts[0]+" ("+acronym+")!**", description="*You have bought "+str(stocknum)+" "+atts[0]+" stocks for "+str(stocknum*pps)+" "+config[1]+"!*", color=0x8093F1)
        embed.set_footer(text="Stock-Game | Made by Gameknight#9101")
        embed.add_field(name="**Remaining Balance: **", value="*"+str(float(info["cash"])-(stocknum*pps))+" "+config[1]+"*", inline=False)
        await ctx.send(embed=embed)
#####################################

bot.run(TOKEN)