# Here is some python to wrap cleos commands to create a user and give permissions to the contract

import shlex, json
import subprocess
from eospy.cleos import Cleos

####################################################################
# Set the url
####################################################################
ce = Cleos(url='http://localhost:8888')

####################################################################
#Basic run command function
####################################################################

def push_action(arguments, payload, pkey):
    #Converting payload to binary
    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
    #Inserting payload binary form as "data" field in original payload
    payload['data'] = data['binargs']
    #final transaction formed
    trx = {"actions": [payload]}
    import datetime as dt
    trx['expiration'] = str(
        (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
    # key = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    key = eospy.keys.EOSKey('5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')
    resp = ce.push_transaction(trx, key, broadcast=True)
    return resp


####################################################################
#Basic User setup with permissions and currency allocation
####################################################################
#Create account command
def crt_act(name, priv_key):
    resp = ce.create_account('eosio', priv_key, name, 'EOS5YMv2UBcuiExv1C8fZjjnE4evofRdBh5Nrt8TYz44G7KC5tZNq', \
    'EOS5YMv2UBcuiExv1C8fZjjnE4evofRdBh5Nrt8TYz44G7KC5tZNq', stake_net='1.0000 EOS', stake_cpu='1.0000 EOS', \
    ramkb=8, permission='active {\"threshold\":1,\"keys\":[{\"key\":\""+ priv_key +"\",\"weight\":1}], \"accounts\":[{\"permission\":{\"actor\":\"superfuture\",\"permission\":\"eosio.code\"},\"weight\":1}], \"waits\":[] }', transfer=False, broadcast=True)
    return resp


def give_timbucks(name, ammount):
    arguments = {
        "from": "admin",
        "to": str(name),
        "quantity": str(amount)+".00 TBK",
        "memo": "Initial Allocation"
    }
    payload = {
        "account": "eosio.token",
        "name": "transfer",
        "authorization": [{
        "actor": "admin",
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, admin_key)


def set_up_user(name, priv_key, ammount):
    crt_act(name, priv_key)
    give_timbucks(name, ammount)

####################################################################
# Future Functionality
####################################################################
def create_future(name, buyer, seller, sublot_id, spot_id, start_time, end_time, request_expiration_time, price, future_id, priv_key):
    arguments = {
        "buyer": buyer,
        "seller": seller,
        "sublot_id": sublot_id,
        "spot_id": spot_id,
        "start_time": start_time,
        "end_time": end_time,
        "request_expiration_time": request_expiration_time,
        "price": str(price)+".00 TBK",
        "future_id": future_id
    }
    payload = {
        "account": "superfuture",
        "name": "crtfuture",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)

def complete_future(name, buyer, seller, sublot_id, spot_id, start_time, end_time, request_expiration_time, price, future_id, priv_key):
    arguments = {
        "buyer": buyer,
        "seller": seller,
        "sublot_id": sublot_id,
        "spot_id": spot_id,
        "start_time": start_time,
        "end_time": end_time,
        "request_expiration_time": request_expiration_time,
        "price": str(price)+".00 TBK",
        "future_id": future_id
    }
    payload = {
        "account": "superfuture",
        "name": "cptfuture",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)

####################################################################
# Groups Functionality
####################################################################
def crtgroup(name, title, creator, fee, min_ratio, group_id, priv_key):
    arguments = {
        "title": title,
        "creator": creator,
        "spot_id": spot_id,
        "min_ratio": min_ratio,
        "fee": str(fee)+".00 TBK",
        "group_id": group_id
    }
    payload = {
        "account": "superfuture",
        "name": "crtgroup",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)


def joingroup(name, user, group_id, priv_key):
    arguments = {
        "user": user,
        "group_id": group_id
    }
    payload = {
        "account": "superfuture",
        "name": "joingroup",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)


def ftrtogrp(name, owner, group_id, future_id, priv_key):
    arguments = {
        "owner": owner,
        "future_id": future_id,
        "group_id": group_id
    }
    payload = {
        "account": "superfuture",
        "name": "ftrtogrp",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)


def ftrfrmgrp(name, owner, group_id, future_id, priv_key):
    arguments = {
        "owner": owner,
        "future_id": future_id,
        "group_id": group_id
    }
    payload = {
        "account": "superfuture",
        "name": "ftrfrmgrp",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)



####################################################################
# Options Functionality
####################################################################
def create_option(name, buyer, seller, caller, putter, sublot_id, start_time, end_time, contract_expiration_time, request_expiration_time, spot_price, contract_price, collateral, priv_key):
    arguments = {
        "buyer": buyer,
        "seller": seller,
        "caller": caller,
        "putter": putter,
        "sublot_id": sublot_id,
        "start_time": start_time,
        "end_time": end_time,
        "contract_expiration_time": contract_expiration_time,
        "request_expiration_time": request_expiration_time,
        "spot_price": str(spot_price)+".00 TBK",
        "contract_price": str(contract_price)+".00 TBK",
        "collateral": str(collateral)+".00 TBK",
    }
    payload = {
        "account": "superfuture",
        "name": "crtoption",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)

def complete_option(name, buyer, seller, caller, putter, sublot_id, start_time, end_time, contract_expiration_time, request_expiration_time, price, contract_price, collateral, whole_id, priv_key):
    arguments = {
        "buyer": buyer,
        "seller": seller,
        "caller": caller,
        "putter": putter,
        "sublot_id": sublot_id,
        "start_time": start_time,
        "end_time": end_time,
        "contract_expiration_time": contract_expiration_time,
        "request_expiration_time": request_expiration_time,
        "spot_price": str(spot_price)+".00 TBK",
        "contract_price": str(contract_price)+".00 TBK",
        "collateral": str(collateral)+".00 TBK",
        "whole_id": whole_id
    }
    payload = {
        "account": "superfuture",
        "name": "crtoption",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)

def exrcall(name, caller, putter, whole_id, priv_key):
    arguments = {
        "caller": caller,
        "putter": putter,
        "whole_id": whole_id
    }
    payload = {
        "account": "superfuture",
        "name": "exrcall",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)


def exrput(name, caller, putter, whole_id):
    arguments = {
        "caller": caller,
        "putter": putter,
        "whole_id": whole_id
    }
    payload = {
        "account": "superfuture",
        "name": "exrput",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)


def clmcollat(name, seller, whole_id):
    arguments = {
        "seller": seller,
        "whole_id": whole_id
    }
    payload = {
        "account": "superfuture",
        "name": "clmcollat",
        "authorization": [{
        "actor": name,
        "permission": "active",
        }],
    }
    return push_action(arguments, payload, priv_key)
