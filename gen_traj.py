# --------------------------------------------------------------------------
# gen_traj.py
# --------------------------------------------------------------------------
# Author, date  : George Corser, 2015-01-03
# Description   : Generate all points for all trajectories
#                 contained in a GMSF/MMTS trace file
# 
# input file    : GMSF/MMTS trace file of the following form:
#
#                 00000.00 1 1435.34 1539.10 1470.00 1350.00 15.00
# 
#                 00000.00 is trace begin time
#                 1 is the vehicle number
#                 1435.35 is starting x coordinate
#                 1539.10 is starting y coordinate
#                 1470.00 is ending x coordinate
#                 1350.00 is ending y coordinate
#                 15.00 is duration of trace (in seconds)
#
#                 the file is assumed to be sorted by time, vehicle number
#
# processing    : 1. initialize variables
#                 2. open input file
#                 3. loop through lines of input file
#                 4. loop through words in each trace file line
#                    and load them into variables
#                    (now the entire trace file is in RAM)
#                 5. generate intermediate points
#                    and write to output file
#
# program output: gen_traj.out file of the following form:
#
#                 0 1 1435.34 1539.1
#                 1 1 1437.50625 1527.28125
#                 2 1 1439.6725 1515.4625
#                 3 1 1441.83875 1503.64375
#                 4 1 1444.005 1491.825
#                 5 1 1446.17125 1480.00625
#                 6 1 1448.3375 1468.1875
#                 7 1 1450.50375 1456.36875
#                 8 1 1452.67 1444.55
#                 9 1 1454.83625 1432.73125
#                 10 1 1457.0025 1420.9125
#                 11 1 1459.16875 1409.09375
#                 12 1 1461.335 1397.275
#                 13 1 1463.50125 1385.45625
#                 14 1 1465.6675 1373.6375
#                 15 1 1467.83375 1361.81875
#
#                 gen_traj.out should have duration+1 lines
#                 for each line of GMSF/MMTS trace file

import math
import time

# ---------- 1. inititalize variables --------------------------------------
v = 1                # vehicle number (note: there is no vehicle "0")
infile = "city.txt" # gmsf/mmts trace file should be a text file

# code thru "mmts.close()" below is by Patrick D'Errico

times = [] # times in which the states change
cid = []   # car (vehicle) id
curx = []  # starting position on car appearence
cury = []
finx = []  # end position after block
finy = []
elapsed = [] # time steps from start to end

# ---------- 2. open input file --------------------------------------------
print time.ctime(), " ... reading mmts file into variables ... ",
mmts = open(infile, "r")

# ---------- 3. loop through lines in trace file ----------------------------
counter = 7
for line in mmts:

# ---------- 4. loop through words in each trace file line 
#               and load them into variables
  for word in line.split():
        counter = counter + 1
        if counter == 8:
            counter = 1
        if counter == 1:
            stamp = float(word)
            if stamp == 0:
                times.append(0)
            else:
                if stamp > int(stamp): #round up timestamps to keep time consistently
                    times.append((int(stamp)+1))
                else:
                    times.append((int(stamp)))
        if counter == 2:
            cid.append(int(word))           
        if counter == 3:
            curx.append(float(word))
        if counter == 4:
            cury.append(float(word))
        if counter == 5:
            finx.append(float(word))           
        if counter == 6:
            finy.append(float(word))
        if counter == 7:
            stamp = float(word)
            if stamp == 0:
                elapsed.append(0)
            else:
                if stamp > int(stamp): #round up timestamps to keep time consistently
                    elapsed.append((int(stamp)+1))
                else:
                    elapsed.append((int(stamp)))

mmts.close()

print " done.", time.ctime()

# ---------- 7. generate intermediate coordinates
#               and write to output file
print time.ctime(), " ... opening and writing to output file ... ",
outfile = open("gen_traj.out", "w")

for ti in range(len(times)):
      
  if elapsed[ti] == 0:
    print "error: elapsed time is zero"
    print times[ti], cid[ti], curx[ti], cury[ti], finx[ti], finy[ti], elapsed[ti]
    abort = 1/0
  else:
    delta_x = (finx[ti] - curx[ti]) / (elapsed[ti] + 1)
    delta_y = (finy[ti] - cury[ti]) / (elapsed[ti] + 1)
    tt = 0
    cx = curx[ti]
    cy = cury[ti]
    for ei in range(elapsed[ti] + 1):
      s = str(times[ti] + tt)+ " " + str(cid[ti]) + " " \
        + str(curx[ti] + tt*delta_x) + " " + str(cury[ti] + tt*delta_y) + "\n"
      # print s
      outfile.write(s)
      tt += 1
      
outfile.close()
print "done."
