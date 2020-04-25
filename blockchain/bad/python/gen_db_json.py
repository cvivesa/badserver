#script to generate json for display purposes

import json, random

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(user_pk = 1)
def gen_user(u_id, balance):
    output = "{\"model\": \"parking.eosaccount\", \"pk\": "+str(gen_user.user_pk)+", \"fields\": {\"user\": "+str(u_id)+", \"balance\": \""+str(balance)+".00\", \"minimum_balance\": \"0E-10\"}},"
    gen_user.user_pk += 1;
    return output

@static_vars(spot_pk = 1)
def gen_spot(lot, number):
    output = "{\"model\": \"parking.spot\", \"pk\": "+str(gen_spot.spot_pk)+", \"fields\": {\"lot\": "+str(lot)+", \"number\": " +str(number)+"}}"
    gen_spot.spot_pk += 1
    return output

@static_vars(lot_pk = 1)
def gen_lot(name, lot, num_spot):
    output = "{\"model\": \"parking.lot\", \"pk\": "+str(gen_lot.lot_pk)+", \"fields\": {\"name\": \""+str(name)+"\"}},"
    for i in range(1,num_spot):
        output += gen_spot(lot, i)+","
    #output= output[:-1]
    gen_lot.lot_pk += 1
    return output

@static_vars(future_pk = 1)
def gen_future(buyer, seller, lot, spot, start_time, end_time, request_expiration_time, price):
    output = "{\"model\": \"parking.future\", \"pk\": " + str(gen_future.future_pk) + ", \"fields\": {\"buyer\": "+ str(buyer) \
    + ", \"seller\": " + str(seller) + ", \"lot\": " + str(lot) + ", \"spot\": "+str(spot) \
    +", \"start_time\": \""+start_time+"\", \"end_time\": \"" + end_time \
    +"\", \"request_expiration_time\": \""+request_expiration_time+"\", \"price\": \"" \
    + str(price) +".00\", \"group\": null}},"
    gen_future.future_pk += 1
    return output

def gen_time(month, day):
    day = str(1+day)
    if(len(day)==1):
        day = "0"+day
    month = str(month)
    if(len(month)==1):
        month = "0"+month
    output = "2020-"+str(month)+"-"+str(day)+"T05:56:35Z"
    return output

@static_vars(start_point = [40,40,35,60,90,75,15],m = -0.17)
def gen_price(lot, month, day, length):
    noise = random.uniform(-0.1,0.1)
    daily_price = gen_price.start_point[lot] + gen_price.m*(((month-4)*30)+day) + noise*(gen_price.start_point[lot])
    return int(daily_price*length)

@static_vars(start_point = [40,40,35,60,90,75,15],m = -0.17)
def gen_option_price(lot, month, day):
    noise = random.uniform(-0.25,0.25)
    daily_price = gen_option_price.start_point[lot] + gen_price.m*((month*30)+day) + noise*(gen_option_price.start_point[lot])
    return int(daily_price)

def gen_future_simple(buyer, seller, lot, spot, month, day, length):
    return gen_future(buyer, seller, lot, spot, gen_time(month, day), gen_time(month+((day+length)//29), (day+length)%29), gen_time(month, day), gen_price(lot, month, day, length))

def gen_futures_for_spot(renter, owner, lot, spot, month, day, period):
    output = ""
    output += gen_future_simple(owner,1,lot,spot,month,day,period+1)
    day_offset = 0
    while(day_offset < period):
        max = min(7,period-day_offset)
        day_offset += random.randint(1,4)
        f_len = random.randint(1,max)
        output += gen_future_simple(renter,owner,lot,spot,month+((day+day_offset)//29),(day+day_offset)%29,f_len)
    return output

@static_vars(option_pk = 1)
def gen_option(buyer, seller, lot, spot, start_time, end_time, request_expiration_time, price, fee, collateral, creator):
    out = "{\"model\": \"parking.option\", \"pk\": "+str(gen_option.option_pk)+", \"fields\": {\"buyer\": "+str(buyer)+ \
    ", \"seller\": "+ str(seller) + ", \"lot\": "+str(lot)+", \"spot\": "+str(spot)+", \"start_time\": \""+start_time+ \
    "\", \"end_time\": \""+end_time+"\", \"request_expiration_time\": \"" + request_expiration_time + \
    "\", \"price\": \""+str(price)+".00\", \"group\": null, \"fee\": \""+str(fee)+".00\", \"collateral\": \""+ \
    str(collateral)+".00\", \"creator\": "+str(creator)+"}},"
    gen_option.option_pk += 1
    return out

def gen_option_simple(buyer, seller, lot, spot, month, day):
    return gen_option(buyer, seller, lot, spot, gen_time(month, day), gen_time(month+((day+1)//29), (day+1)%29), gen_time(month, day), \
     gen_option_price(lot, month, day), int(0.2*gen_option_price(lot, month, day)), int(0.5*gen_option_price(lot, month, day)), seller)

def gen_options_for_spot(buyer,seller, lot, spots, month, day, period):
    output = ""
    day_offset = 0
    while(day_offset < period):
        max = min(7,period-day_offset)
        day_offset += random.randint(1,max)
        output += gen_option_simple(buyer,seller,lot,random.randint(1,spots),month+((day+day_offset)//29),(day+day_offset)%29)
        day_offset += 1
    return output


num_users = 7
lots = [["surge1", 1, 5], ["surge2", 2, 5], ["surge3", 3, 5], ["surge4", 4, 5], ["surge5", 5, 5], ["surge6", 6, 5]]

output_str = "["


for i in range(1,num_users+1):
    output_str += gen_user(i, 1000)
    #output_str += ","

#output_str = output_str[:-1]

for lot in lots:
    output_str += gen_lot(lot[0],lot[1],lot[2])
    output_str + ","
#output_str = output_str[:-2]

days = 80

#### Make futures
output_str += gen_futures_for_spot(3,2,1,1,4,23,days)
output_str += gen_futures_for_spot("null",2,1,1,4,23,days)

#### Make futures
output_str += gen_futures_for_spot(3,2,2,1,4,23,days)
output_str += gen_futures_for_spot("null",2,2,1,4,23,days)

#### Make futures
output_str += gen_futures_for_spot(3,2,3,1,4,23,days)
output_str += gen_futures_for_spot("null",2,3,1,4,23,days)

#### Make futures
output_str += gen_futures_for_spot(3,2,4,1,4,23,days)
output_str += gen_futures_for_spot("null",2,4,1,4,23,days)

#### Make futures
output_str += gen_futures_for_spot(3,2,5,1,4,23,days)
output_str += gen_futures_for_spot("null",2,5,1,4,23,days)

#### Make futures
output_str += gen_futures_for_spot(3,2,6,1,4,23,days)
output_str += gen_futures_for_spot("null",2,6,4,4,23,days)

output_str += gen_options_for_spot(3,2,1,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str += gen_options_for_spot(3,2,2,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str += gen_options_for_spot(3,2,3,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str += gen_options_for_spot(3,2,4,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str += gen_options_for_spot(3,2,5,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str += gen_options_for_spot(3,2,6,1,4,26,days)
output_str += gen_options_for_spot("null",2,1,4,4,26,days)

output_str = output_str[:-1]
print(output_str+"]")

#js = json.loads(output_str)
