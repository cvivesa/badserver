#Admin creates a bunch of sublots

# Here is some python to do the contract set up
import shlex, json
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

def crt_sublot(sublot_id, num_spots, start_time, end_time):
    run_cmd("cleos push action superfuture createsublot '[\""+sublot_id+"\",\""+num_spots+"\",\"admin\",\""+start_time+"\",\""+end_time+"\"]' -p admin@active")

def crt_lot(sublot_arr, start_time, end_time): #sub_lot_arr is an array of arrays
    for sublot in sublot_arr:
        crt_sublot(sublot[0],sublot[1],)

lots = [[1,5],[2,5],[3,5],[4,5],[5,5],[6,5]]

start_time = 1587777605

end_time = 1687777605

for lot in lots:
    crt_lot(lot, start_time, end_time)
