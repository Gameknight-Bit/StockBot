## Module that writes and interacts with JSON files ##
## Specifically for Discord Bot Users :) ##

import json
import datetime
import uuid

## Transactions ##
class Transaction:
    def __init__(self, userid, servID, stock, amount, pps, type):
        self.type = type or "BUY" #SELL or BUY
        self.userID = userid or 0
        self.servID = servID or 0
        self.stock = stock or ""
        self.amount = amount or 0
        self.pps = pps or 0
        self.UUID = str(uuid.uuid4().hex)
        self.date = datetime.datetime.now().strftime("%d/%m/%Y | %H:%M:%S")

    def __str__(self):
        return "Type: "+ self.type + ", UserID: " + self.userID + ", ServerID: " + self.servID + ", Stock: " + self.stock + ", Amount: " + str(self.amount) + ", PPS: " + str(self.pps) + ", Date: " + self.date + ", UUID: " + self.UUID

    def todict(self):
        return {"type": self.type ,"userId": self.id, "serverId": self.servID, "stock": self.stock, "amount": self.amount, "pps": self.pps, "date": self.date, "UUID": self.UUID}

    def fromdict(self, dict):
        self.userID = dict["userId"]
        self.servID = dict["serverId"]
        self.stock = dict["stock"]
        self.amount = dict["amount"]
        self.pps = dict["pps"]
        self.date = dict["date"]
        self.UUID = dict["UUID"]

#Returns dict or None if user not found#
def getServer(id): #Returns data for server and clients
    with open("datastore/serverdata.json", "r+") as f:
        data = json.load(f)
        if str(id) in data:
            return data[str(id)]
        else:
            print("ERROR: Server " + str(id) + " not found")
            return None

#Returns True if server exists#
def serverExists(id): #Returns True if server exists
    data = getServer(id)
    if data is not None:
        return True
    else:
        return False

#Gets Server Config#
def getConfig(id): #Returns config for server
    if not serverExists(id):
        return None
    else:
        data = getServer(id)
        return [data["startingCash"], data["currency"], data["competitions"]]

#Returns dict or None if user not found#
def getUser(id, servID): #Returns data for user with id
    data = getServer(servID)
    if str(id) in data["users"]:
        return data["users"][str(id)]
    else:
        return None

#Returns True if user exists#
def userExists(id, servID): #Returns True if user exists
    data = getServer(servID)
    if serverExists(servID) and str(id) in data["users"]:
        return True
    else:
        return False

#Returns True if Successful#
def initServer(id): #Initializes server data
    if serverExists(id):
        return False
    with open("datastore/serverdata.json", "r+") as f:
        data = json.load(f)
        data[str(id)] = {
            "users": {},
            "startingCash": "100000",
            "currency": "USD",
            "competitions": "False",
            "history": {},
        }
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        return True

#Returns True if Successful#
# d = {"startingCash": val, "currency": val, "competitions": val} #
def updateServer(id, d): #updates server data with dict d (use sparingly)
    if not serverExists(id):
        return False
    with open("datastore/serverdata.json", "r+") as f:
        data = json.load(f)
        data[str(id)] = {
            "users": data[str(id)],
            "startingCash": d["startingCash"] or "100000",
            "currency": d["currency"] or "USD",
            "competitions": d["competitions"] or "False",
            "history": data[str(id)]["history"],
        }
        f.seek(0)
        json.dump(data, f)
        f.truncate()
        return True

#Returns None#
def initUser(id, servID):
    with open("datastore/serverdata.json", "r+") as f:
        data = json.load(f)
        data[str(servID)]["users"][str(id)] = {
            "stocks": {},
            "cash": data[str(servID)]["startingCash"],
            "currency": data[str(servID)]["currency"],
            "transactions": [],
            "history": {},
        }
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

#Returns True if Successful#
def updateUser(id, servID, d): #updates user data with dict d (use sparingly)
    if not userExists(id, servID):
        if not serverExists(servID):
            return False
        initUser(id, servID)

    with open("datastore/serverdata.json", "r+") as f:
        data = json.load(f)
        data[str(servID)]["users"][str(id)] = d
        f.seek(0)
        json.dump(data, f)
        f.truncate()
        return True

##########################
## STOCK TRADING SYSTEM ##
##########################

#Returns True if Successful# (error message if not)
def buyStock(id, servID, stock, amount, pps): #buys stock
    if not userExists(id, servID):
        if not serverExists(servID):
            return False
        initUser(id, servID)

    #with open("datastore/serverdata.json", "r+") as f:
    data = getUser(id, servID)#json.load(f)
    #userdata = data[str(servID)]["users"][str(id)]

    '''if float(data[str(servID)]["users"][str(id)]["cash"]) < amount * pps:
        return "Insufficient Funds"
    if stock in data[str(servID)]["users"][str(id)]["stocks"]:
        data[str(servID)]["users"][str(id)]["stocks"][stock] = str(amount+float(userdata["stocks"][stock]))
    else:
        data[str(servID)]["users"][str(id)]["stocks"][stock] = str(amount)

    data[str(servID)]["users"][str(id)]["cash"] = str(float(userdata["cash"])-(amount * pps)) 
    data[str(servID)]["users"][str(id)]["transactions"].append(Transaction(id, servID, stock, amount, pps, "BUY").todict())
        
    updateUser(id, servID, data[str(servID)]["users"][str(id)])'''
    if float(data["cash"]) < amount * pps:
        return "Insufficient Funds"
    if stock in data["stocks"]:
        data["stocks"][stock] = str(amount+float(data["stocks"][stock]))
    else:
        data["stocks"][stock] = str(amount)

    data["cash"] = str(float(data["cash"])-(amount * pps)) 
    data["transactions"].append(Transaction(id, servID, stock, amount, pps, "BUY").todict())
        
    updateUser(id, servID, data)
    #f.seek(0)
    #json.dump(data, f)
    #f.truncate()
    return True

#Returns True if Successful# (error message if not)
def sellStock(id, servID, stock, amount, pps): #sells stock
    if not userExists(id, servID):
        if not serverExists(servID):
            return False
        initUser(id, servID)

    data = getUser(id, servID)#json.load(f)
    userdata = data[str(servID)]["users"][str(id)]

    if stock not in data[str(servID)]["users"][str(id)]["stocks"]:
        return stock+" stock not found"

    if userdata["stocks"][stock] < amount:
        return "Not enough stocks to sell "+str(amount)

    if stock in data[str(servID)]["users"][str(id)]["stocks"]:
        data[str(servID)]["users"][str(id)]["stocks"][stock] = str(amount-float(userdata["stocks"][stock]))
        if data[str(servID)]["users"][str(id)]["stocks"][stock] == 0:
            del data[str(servID)]["users"][str(id)]["stocks"][stock]

    data[str(servID)]["users"][str(id)]["cash"] = str(float(userdata["cash"])+(amount * pps)) 
    data[str(servID)]["users"][str(id)]["transactions"].append(Transaction(id, servID, stock, amount, pps, "SELL").todict())
        
    updateUser(id, servID, data[str(servID)]["users"][str(id)])

    return True

#Returns 

##########
## DOCS ##
##########

