import aiohttp
from flask import Flask, request, jsonify
import os
import base64

DEBUG = (os.getenv('BALWGT_DEBUG', 'TRUE') == "TRUE")
HOST = os.getenv('BALWGT_HOST', "127.0.0.1")
DATA_PATH = os.getenv('BALWGT_DATA_PATH', "./data")
ACCESS_PATH = os.path.join(DATA_PATH, "access.txt")

app = Flask(__name__)

@app.route('/setup', methods=['POST'])
async def setup():
    setup_token = request.json['setup_token']
    await init_from_setup(setup_token)
    return ('',200)

@app.route('/accounts', methods=['GET'])
async def accounts():
    
    accounts = await get_simple_accounts()

    return jsonify({"accounts": accounts})


#optional comma delimted account_ids query parameter for filtering
@app.route('/net_balance', methods=['GET'])
async def net_balance():
    
    account_ids = request.args.get('account_ids')
    
    accounts = await get_accounts()
    
    if account_ids:
        account_ids = account_ids.split(',')
        accounts = [a for a in accounts if a['id'] in account_ids]

    balance = sum([float(a["balance"]) for a in accounts])
    balance = round(balance, 2)
    balance = str(balance)
    print("balance", balance)
    if balance[0] == '-':
        balance = "-$"+balance[1:]
    else:
        balance = "$"+balance
    return jsonify({"balance": balance})

async def access_from_setup(setup_token):
    claim_url = base64.b64decode(setup_token).decode('utf-8')
    async with aiohttp.ClientSession() as session:
       async with session.post(claim_url) as response:
            access_url = await response.text()
            return access_url

def save_access(access_url):
    with open(ACCESS_PATH, "w") as f:
        f.write(access_url)
        

def load_access():
    with open(ACCESS_PATH, "r") as f:
        return f.read()

async def init_from_setup(setup_token):
    access_url = await access_from_setup(setup_token)
    save_access(access_url)

async def get_accounts():
    access_url = load_access()

    async with aiohttp.ClientSession() as session:
        async with session.get(access_url+"/accounts") as response:
            data = await response.json()
    
    accounts = data["accounts"]
    return accounts

async def get_simple_accounts():
    accounts = await get_accounts()
    return [{
        "name": account["name"],
        "id": account["id"]
    } for account in accounts]
    

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST)