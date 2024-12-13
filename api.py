from fastapi import *
import uvicorn
import sqlite3
from contextlib import asynccontextmanager
import os


class StorageBase():
    def __init__(self):
        self.conn = sqlite3.connect('base.db')
        self.cur = self.conn.cursor()
    
    async def addAccount(self, phone, api_id, api_hash, twofa, channelID):
        try:
            self.conn.execute("INSERT INTO accs VALUES (?, ?, ?, ?, ?)", (api_id, api_hash, phone, twofa, channelID))
            self.conn.commit()
            return True
        except Exception as e:return e
    async def getAccounts(self):
        try:return self.conn.execute('SELECT * FROM accs').fetchall()
        except Exception as e:return e
    async def delAccount(self, phone):
        try:
            self.conn.execute('DELETE FROM accs WHERE phone = ?', (phone, ))
            self.conn.commit()
            return True
        except Exception as e:return e
    
    async def addText(self, notif, phone):
        try:
            self.conn.execute("INSERT INTO texts VALUES (?, ?)", (notif, phone))
            self.conn.commit()
            return True
        except Exception as e:return e
    async def delText(self, notif, phone):
        try:
            self.conn.execute("DELETE FROM texts WHERE example = ? AND phone = ?", (notif, phone))
            self.conn.commit()
            return True
        except Exception as e:return e   
    async def getTexts(self, phone):
        try:return self.conn.execute('SELECT * FROM texts WHERE phone = ?', (phone,)).fetchall()
        except Exception as e:return e
    
    async def addInterval(self, inter, phone):
        try:
            self.conn.execute("INSERT INTO interval VALUES (?, ?)", (inter, phone))
            self.conn.commit()
            return True
        except Exception as e:return e
    async def delIntervals(self, phone):
        try:
            self.conn.execute("DELETE FROM interval WHERE phone = ?", (phone,))
            self.conn.commit()
            return True
        except Exception as e:return e   
    async def getInterval(self, phone):
        try:return self.conn.execute('SELECT * FROM interval WHERE phone = ?', (phone,)).fetchall()
        except Exception as e:return e
        
    async def newChannel(self, phone, newchannel):
        try:
            self.conn.execute("UPDATE accs SET channel = ? WHERE phone = ?", (newchannel, phone))
            self.conn.commit()
            return True
        except Exception as e:return e

@asynccontextmanager
async def overfunk(app:FastAPI):
    yield

app = FastAPI(lifespan=overfunk)        
base = StorageBase()
        
        
@app.post("/addAcc")
async def addingTG(phone, api_id, api_hash, twofa, channelID, defaultInterval):
    print(phone, api_id, api_hash, twofa, channelID)
    await base.addInterval(defaultInterval, phone)
    return await base.addAccount(phone, api_id, api_hash, twofa, channelID)

@app.post("/editChannel")
async def editChannel(phone, newChannel:str):
    return await base.newChannel(phone, newChannel)

@app.get("/Accs")
async def getTgs():return await base.getAccounts()

@app.post("/delAcc")
async def deleteAcc(phone):
    try:os.remove(f"./sess/{phone}.session")
    except:pass
    return await base.delAccount(phone)

@app.get("/texts")
async def getTexts(phone):return await base.getTexts(phone)

@app.post('/addText')
async def addTextx(notif, phone):return await base.addText(notif, phone)

@app.post("/delText")
async def delTxt(notif, phone):return await base.delText(notif, phone)

@app.get("/interval")
async def getInterval(phone):return (await base.getInterval(phone))

@app.post("/addInter")
async def addIntervale(inter:str, phone):
    print(inter)
    if all([x.isdigit() for x in inter.split("-")]):
        await base.delIntervals(phone)
        return await base.addInterval(inter, phone)
    return False

@app.post("/delInter")
async def delInterval(phone):return await base.delIntervals(phone)
    
    
    
       



if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8855, reload=True)