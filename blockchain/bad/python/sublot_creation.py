#Admin creates a bunch of sublots

# Here is some python to do the contract set up
import shlex, json
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

def crt_sublot(sublot_id, num_spots, start_time, end_time):
    run_cmd("cleos push action superfuture createsublot '[\""+sublot_id+"\",\""+num_spots+"\",\"admin\",\""+start_time+"\",\""+end_time+"\"]' -p admin@active")

def crt_lot(sublot_arr): #sub_lot_arr is an array of arrays
    for sublot in sublot_arr:
        crt_sublot(sublot[0],sublot[1],sublot[2],sublot[3])

lots = [
    [],
    [],
    ]
