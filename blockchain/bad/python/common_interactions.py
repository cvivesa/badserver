# Here is some python to wrap cleos commands to create a user and give permissions to the contract

import shlex, json
import subprocess
from subprocess

####################################################################
#Basic run command function
####################################################################

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))


####################################################################
#Basic User setup with permissions and currency allocation
####################################################################
#Create account command
def crt_act(name, pub_key):
    return run_cmd("cleos create account eosio "+name+" "+pub_key)

def give_timbucks(name, ammount):
    return run_cmd("cleos push action eosio.token transfer '[\"admin\", \""+"name"+"\", \""+str(amount)".00 TBK\", \"Initial Allocation\"]' -p admin@active")

def extend_permissions(name, pub_key):
    return run_cmd("cleos set account permission "+name+" active '{\"threshold\":1,\"keys\":[{\"key\":\""+ pub_key +"\",\"weight\":1}], \"accounts\":[{\"permission\":{\"actor\":\"superfuture\",\"permission\":\"eosio.code\"},\"weight\":1}], \"waits\":[] }' owner -p "+name)

def set_up_user(name, pub_key, ammount):
    crt_act(name, pub_key)
    give_timbucks(name, ammoun)
    extend_permissions(name, pub_key)

####################################################################
# Future Functionality
####################################################################
def create_future(name, buyer, seller, sublot_id, spot_id, start_time, end_time, request_expiration_time, price, future_id):
    return run_cmd("cleos push action superfuture crtfuture '[\""+buyer+"\", \""+seller+"\", \""+str(sublot_id)+"\", \""+str(spot_id)+"\", \""+str(start_time)+"\", \""+str(end_time)+"\", \""+str(request_expiration_time)+"\", \""+str(price)+"\", \""+str(future_id)+"\"]' -p "+name+"@active")


def complete_future(name, buyer, seller, sublot_id, spot_id, start_time, end_time, request_expiration_time, price, future_id):
    return run_cmd("cleos push action superfuture cptfuture '[\""+buyer+"\", \""+seller+"\", \""+str(sublot_id)+"\", \""+str(spot_id)+"\", \""+str(start_time)+"\", \""+str(end_time)+"\", \""+str(request_expiration_time)+"\", \""+str(price)+"\", \""+str(future_id)+"\"]' -p "+name+@active")


def createsublot(name, sublot_id, num_spot, to, transfer_time, return_time):
    return run_cmd("cleos push action superfuture createsublot '[\""+str(sublot_id)+"\", \""+str(num_spot)+"\", \""+to+"\", \""+str(transfer_time)+"\", \""+str(return_time)+"\"]' -p "+name+@active")

####################################################################
# Groups Functionality
####################################################################
def crtgroup(name, title, creator, fee, min_ratio, group_id):
    return run_cmd("cleos push action superfuture crtgroup '[\""+title+"\", \""+creator+"\", \""+str(fee)+"\", \""+str(min_ratio)+"\", \""+str(group_id)+"\"]' -p "+name+@active")


def joingroup(name, user, group_id):
    return run_cmd("cleos push action superfuture joingroup '[\""+user+"\", \""+str(group_id)+"\"]' -p "+name+@active")


def ftrtogrp(name, owner, group_id, future_id):
    return run_cmd("cleos push action superfuture ftrtogrp '[\""+owner+"\", \""+str(group_id)+"\", \""+str(future_id)+"\"]' -p "+name+@active")


def ftrfrmgrp(name, owner, group_id, future_id):
    return run_cmd("cleos push action superfuture frtfrmgrp '[\""+owner+"\", \""+str(group_id)+"\", \""+str(future_id)+"\"]' -p "+name+@active")



####################################################################
# Options Functionality
####################################################################
def create_option(name, buyer, seller, caller, putter, sublot_id, start_time, end_time, contract_expiration_time, request_expiration_time, spot_price, contract_price, collateral):
    return run_cmd("cleos push action superfuture crtoption '[\""+buyer+"\", \""+seller+"\", \""+caller+"\", \""+putter+"\", \""+str(sublot_id)+"\", \""+str(start_time)+"\", \""+str(end_time)+"\", \""+str(contract_expiration_time)+"\", \""+str(request_expiration_time)+"\", \""+str(spot_price+"\", \""+str(contract_price)+"\", \""+str(collateral)+"\"]' -p "+name+@active")


def complete_option(name, buyer, seller, caller, putter, sublot_id, start_time, end_time, contract_expiration_time, request_expiration_time, price, contract_price, collateral, whole_id):
    return run_cmd("cleos push action superfuture cptoption '[\""+buyer+"\", \""+seller+"\", \""+caller+"\", \""+putter+"\", \""+str(sublot_id)+"\", \""+str(start_time)+"\", \""+str(end_time)+"\", \""+str(contract_expiration_time)+"\", \""+str(request_expiration_time)+"\", \""+str(price)+"\", \""+str(contract_price)+"\", \""+str(collateral)+"\", \""+str(whole_id)+"\"]' -p "+name+@active")


def exrcall(name, caller, putter, whole_id):
    return run_cmd("cleos push action superfuture exrcall '[\""+caller+"\", \""+putter+"\", \""+str(whole_id)+"\"]' -p "+name+@active")


def exrput(name, caller, putter, whole_id):
    return run_cmd("cleos push action superfuture exrput '[\""+caller+"\", \""+putter+"\", \""+str(whole_id)+"\"]' -p "+name+@active")


def clmcollat(name, seller, whole_id):
    return run_cmd("cleos push action superfuture clmcollat '[\""+seller+"\", \""+str(whole_id)+"\"]' -p "+name+@active")
