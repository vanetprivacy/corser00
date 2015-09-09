# --------------------------------------------------------------------------
# Filename      : calc_kda_smz.py
# --------------------------------------------------------------------------
# Author        : George Corser
# Date          : 2015-01-03
# Language Ver. : Python 2.7
#
# INSTRUCTIONS  : Change the values of USER-DEFINED VARIABLES in section 0
#                 See also: COPYRIGHT NOTICE, below
#
# Description   : Calculate k (anonymity set size), d_bar (average distance),
#                 and anon_duration (anonymity duration)
#                 for SMZ (simple mix zone) privacy model
#
#                 This program is part of a series of steps to analyze vehicle
#                 network (VANET) privacy protocols using mobility models from 
#                 GMSF/MMTS vehicle trace files. To use this program,
# 
#                 a. download 3 mmts.dat files, City, Urban, and Rural,
#                    from gmsf.sourceforge.net
#                 b. rename the .dat files to city.txt, urban.txt, rural.txt
#                 c. run gen_traj.py against each file to generate a fully
#                    enumerated trajectory file, gen_traj.out
#                 d. rename the .out files to city.uns, urban.uns, rural.uns
#                 e. sort the files by time, vehicle using unix sort command:
#                    sort -k1n -k2n rural.uns > rural.srt
#                    (files should be named city.srt, urban.srt, rural.srt)
#                 f. run this program to create a file calc_kda_smz.sta,
#                    described in the "program output" section below
# 
# Input file    : a sorted, fully enumerated trajectory file (.srt) of the form
#
#                 0 1 1435.34 1539.1
# 
#                 0       is the current time
#                 1       is the vehicle number
#                 1435.34 is starting x coordinate of vehicle 1 at time 0
#                 1539.10 is starting y coordinate of vehicle 1 at time 0
#
#                 the file is assumed to be sorted by time, vehicle number
#                 "fully enumerated" means it is not a trace file, but rather
#                 a complete set of (x, y, t) positions
#
# Processing    : 1. initialize variables
#                 2. open input file
#                 3. loop through lines of input file
#                 4. loop through words in each line of input file
#                    and load them into variables
#                    (now the entire input file is in RAM)
#                 5. initialize variables for gathering statistics
#                 6. loop through all time slices, vehicles
#                    and calculate k, d_bar and anon_time for each vehicle
#                    as it exits the region
#                    (now all statistical data are in RAM)
#                 7. write statistics to .sta file
#                    and print summary results
#
# Output file   : calc_kda_smz.sta statistics file
#                 see section 7 for explanation of output file
#
# Output print  : see end of section 7 for explanation
#
# Running time  : on pentium i5 it ran ~5.5 hours...
#                 from Thu Jan 08 03:41:08 2015
#                 to   Thu Jan 08 09:07:04 2015
#
#                 city  ~ 15 minutes per parameter set, 3 sets, ~ 45 mins
#                 urban ~  3 minutes per parameter set, 3 sets, ~  9 mins
#                 rural <  1 minute  per parameter set, 3 sets, ~  3 mins
#
# --------------------------------------------------------------------------
#
#  COPYRIGHT NOTICE
#
#  Copyright (c) 2015, George Corser. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  1. Redistributions of source code must retain this copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holders nor the names of
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS `AS IS'
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS
#  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, LOSS OF USE, DATA,
#  OR PROFITS) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
#  THE POSSIBILITY OF SUCH DAMAGE.
#
#  @author George Corser <george@corser.com>
# 
# --------------------------------------------------------------------------

import math
import time

def smz_stats (smz_duration, smz_radius, smz_x, smz_y, infile):
   
  # ---------- 1. initialize variables --------------------------------------

  v = 1                  # vehicle number (note: there is no vehicle "0")
  # infile = "rural.srt" # should be city.srt, urban.srt, or rural.srt
  outfile = "calc_kda_smz.sta"
  SIM_TIME = 2000        # this is total simulation time of city, urban, rural
                         # files from gmsf.sourceforge.net

  # ----- USER-DEFINED VARIABLES -----
  # change these in ===== main ===== section at bottom of this code
  # vary the parameters below to test the effectiveness of smz privacy protocol
  # smz_duration = 50    # suggest 25, 50, 75 seconds
  # smz_radius   = 50    # suggest 50, 100, 150 meters
  # smz_x        = 2290  # city:  390, urban: 1430, rural: 2290
  # smz_y        =  800  # city: 1710, urban: 2490, rural:  800

  # speed of cars is around 20 m/s, width of region is 3000 m,
  # so a car could possibly traverse the region in 3000/20 = 150 seconds

  # the arrays below contain hundreds of thousands of elements, len(times)

  times = [] # time
  cid   = [] # vehicle id
  curx  = [] # x position at time
  cury  = [] # y position at time

  # ---------- 2. open input file --------------------------------------------

  srt = open(infile, "r")

  # ---------- 3. loop through lines of input file ---------------------------

  counter = 4
  for line in srt:

  # ---------- 4. loop through words in each line of input file  
  #               and load them into variables

    for word in line.split():
          counter = counter + 1
          if counter == 5:
              counter = 1
          if counter == 1:
              times.append(int(word))
          if counter == 2:
              cid.append(int(word))           
          if counter == 3:
              curx.append(float(word))
          if counter == 4:
              cury.append(float(word))

  srt.close()

  # ---------- (now the entire input file is in RAM) -------------------------

  # ---------- 5. initialize variables for gathering statistics --------------

  # the arrays below contain < 10000 elements, the number of vehicles: max(cid)

  smz_grp = []       # smz_grp[cid[i]] is smz to which vehicle cid[i] belongs
                     # smz's occur every ( SIM_TIME / smz_duration ) seconds
  k = []             # anonymity set size when cid[i] leaves region
  d_bar = []         # average distance between cid[i] and other active vehicles
                     # in same smz as cid[i] when cid[i] leaves region
  anon_duration = [] # length of time vehicle was anonymous
  anon_begin = []    # begin time of anonymity for vehicle, cid[i]
  vehx = []          # current x position of vehicle
  vehy = []          # current y position of vehicle
  veh_begin_x = []   # first x position of vehicle
  veh_begin_y = []   # first y position of vehicle
  veh_end_x = []     # last x position of vehicle
  veh_end_y = []     # last y position of vehicle
  smz_entry_time = []# time vehicle entered smz
  smz_exit_time = [] # time vehicle exited smz
  region_exit_time = [] # time vehicle exited the region
  veh_exit_flag = [] # indicates vehicle has exited the region

  # regarding veh_exit_flag[] array...
  # sometimes a vehicle might linger for more than one time period near
  # the boundary of the region. we flag the first instance of an exit 
  # to prevent double-counting exits 

  # initialize all the arrays declared above

  for i in range(min(cid),max(cid)+2):
  # note: index of array = v where v is vehicle number
  # note: there is no vehicle 0
    smz_grp.append(-1) # initialize all vehicles to belong to no group
    k.append(-1)       # -1 means k has not been set (real k is at least 1)
    d_bar.append(0)
    anon_duration.append(0) # duration of anonymity while in region
    anon_begin.append(-1)   # time when vehicle enters smz
    vehx.append(-1)         # most recent x position of vehicle
    vehy.append(-1)
    veh_begin_x.append(-1) # coord where vehicle appears (usu. edge of region)
    veh_begin_y.append(-1)
    veh_end_x.append(-1) # coord where vehicle disappears (usu. edge of region)
    veh_end_y.append(-1)
    smz_entry_time.append(-1)
    smz_exit_time.append(-1)
    region_exit_time.append(-1)
    veh_exit_flag.append(0)

  smz_total = 0 # this is the total number of vehicles that entered the smz,
                # used to cross-check other values, like smz_count array,
                # and to determine how many vehciles entered smz
                # but did not exit the region
  smz_count = []# the number of vehicles currently in each smz
  
  for i in range(0, SIM_TIME/smz_duration + 2):
    smz_count.append(0) # initialize counters to zero

  # ---------- 6. loop through all time slices, vehicles
  #               and calculate k, d_bar and anon_time for each vehicle
  #               as it exits the region

  # smz_grp[i]... is the batch of cars that are mixed in the current
  # window of time. For example, if smz_duration is 50-seconds then the cars
  # in range of the smz's (x,y) coordinates in the first 50-seconds 
  # are assigned smz_grp zero (0).

  last_smz_grp = -1
  # ----- loop through entire set of times, cid, curx, cury arrays
  for i in range (len(times)):
    v = cid[i]
    cur_smz_grp = times[i] / smz_duration # set current smz_grp (truncates)
    vehx[v] = curx[i] # most recent x position of vehicle
    vehy[v] = cury[i] # most recent y position of vehicle
    if veh_begin_x[v] != -1:
      veh_begin_x[v] = curx[i]
      veh_begin_y[v] = cury[i]
    veh_end_x[v] = curx[i]
    veh_end_y[v] = cury[i]

    # ----- check if vehicle is entering smz
    
    # if vehicle within range of (smz_x,smz_y) and no smz_grp assigned
    if smz_radius > math.sqrt((float(curx[i]) - smz_x) ** 2 \
      + (float(cury[i]) - smz_y) ** 2) and smz_grp[v] < 0 :
      smz_grp[v] = cur_smz_grp # set current vehicle's smz_grp
      smz_count[cur_smz_grp] += 1   # increment current smz_grp
      anon_begin[v] = times[i] # set start time of anon period for vehicle
      smz_total +=1
      smz_entry_time[v] = times[i]
      smz_exit_time[v] = (cur_smz_grp + 1) * smz_duration
      
    # cars end trajectory when they hit the edge of region (0 or 3000) 
    # that's when we collect the statisics k, d_bar and anon_duration (kda)
    # vehicles usually originate at edge of region at beginning of trajectory 
    # but values get overwritten (unless the vehicle terminates inside region)

    # ----- check if vehicle is exiting region

    # check if vehicle is exiting region is within 20 m of edge
    # vehicles move at about 20 m/s (~45 mph),
    # program uses 1 sec time intervals,
    # therefore often a vehicle is near region boundary for > 1 sec
    
    edge_threshold = 20 
    if curx[i] < 0 + edge_threshold \
      or curx[i] > 3000 - edge_threshold \
      or cury[i] < 0 + edge_threshold \
      or cury[i] > 3000 - edge_threshold:
      
      # compute stats only if v was assigned a group
      # and not exited already
      if smz_grp[v] > -1 and veh_exit_flag[v] == 0: 
        veh_exit_flag[v] = 1
        region_exit_time[v] = times[i]
        
        # ----- compute k -----
        
        k[v] = smz_count[smz_grp[v]] # should be same as d_count+1
        smz_count[smz_grp[v]] -= 1   # decrement vehicle's smz_grp
          
        # ----- compute d_bar -----
        
        d_sum = 0                              # compute d_bar
        d_count = 0                            # d_count == k - 1
        # loop through all vehicles... if vehicle was anonymized...
        # and vehicle is active... and vehicle is not current vehicle...
        # and vehicle is in same smz_grp as current vehicle
        for j in range(min(cid),max(cid)+1):   
          if smz_grp[j] > -1 and vehx[j] > -1  and v != j \
            and smz_grp[j] == smz_grp[v] :               
            # sum distances from current vehicle (the one exiting the region)
            # to each of the other vehicles in its group 
            d_sum = d_sum + math.sqrt( (float(curx[i]) - vehx[j]) ** 2 \
              + (float(cury[i]) - vehy[j]) ** 2 ) # increment d_sum
            d_count += 1                          # increment d_count
        if d_sum > 0 and k[v] > 0:
          d_bar[v] = float(d_sum) / k[v]    # d_bar for vehicle set here
          d_bar[v] = float(d_sum) / (d_count + 1) # d_bar for vehicle set here
                                                      # d_count == k - 1
          k[v] = d_count + 1
          if d_bar[v] > 3000:
            print v
        
        # ----- compute anon_duration -----
        
        if region_exit_time[v] > smz_exit_time[v]:
          anon_duration[v] = region_exit_time[v] - smz_exit_time[v]
        else:
          anon_duration[v] = 0

        # ----- deactivate vehicle -----
        
        vehx[v] = -2
        vehy[v] = -2

  # ---------- (now all statistical data are in RAM) -------------------------

  # ---------- 7. write statistics to .sta file and print summary results ----

  k_sum = 0
  d_sum = 0
  a_sum = 0
  k_sum_indiv = 0
  d_sum_indiv = 0
  a_sum_indiv = 0
  counter = 0
  counter_indiv = 0

  sta = open(outfile, "w")    
  for v in range(min(cid),max(cid)+1):
    # if smz_grp[v] == 0: # uncomment to write just one smz
      s  = str(v) # vehicle id
      if k[v] < 1:
        k[v] = 1
      s += " " + str(k[v]) # anonymity set size
      s += " " + str(d_bar[v]) # avg dist of decoys at end of i' trajectory
      s += " " + str(anon_duration[v]) # length of time possible for anon LBS
      s += " " + str(smz_exit_time[v])
      s += " " + str(region_exit_time[v])
      s += " " + str(veh_end_x[v])
      s += " " + str(veh_end_y[v])
      s += " " + str(smz_grp[v])
      k_sum += k[v]
      d_sum += d_bar[v]
      a_sum += anon_duration[v]
      if k[v] > 1:
        k_sum_indiv += k[v]
        d_sum_indiv += d_bar[v]
        a_sum_indiv += anon_duration[v]
        counter_indiv += 1
      counter += 1
      sta.write(s + "\n")
  counter_indiv = smz_total
  sta.close()

  # count how many vehicles are active in smz_group at program termination
  count_total = 0
  for i in range(len(smz_count)):
    if smz_count[i] > 0:
        count_total += smz_count[i]

  # print "parms:" mobility model, smz_duration, smz_radius,
  # " - tot-sys-kda: ", avg_k, avg_d, avg_a, total vehicles (counter),
  # " - anon-only-kda: ", avg_k, avg_d, avg_a, anon vehicles (counter_indiv),
  # number of anonymized vehicles that never exited region (count_total)
  
  print ("parms:", infile, smz_duration, smz_radius, " - tot-sys-kda:", \
    float(k_sum) / counter, float(d_sum) / counter, float(a_sum) / counter, \
    counter, " - anon-only-kda:", float(k_sum_indiv) / counter_indiv, \
    float(d_sum_indiv) / counter_indiv, float(a_sum_indiv) / counter_indiv, \
    counter_indiv, count_total)


# ========== 0. main =======================================================

print (time.ctime()) # beginning of program

# SIM_TIME is 2000 seconds so smz_duration of  25 means 80   smz's
# SIM_TIME is 2000 seconds so smz_duration of  50 means 40   smz's
# SIM_TIME is 2000 seconds so smz_duration of  75 means 26.7 smz's
# SIM_TIME is 2000 seconds so smz_duration of 100 means 20   smz's

# SIM_WIDTH is 3000 meters so smz_radius of  50 is 1.6%
# SIM_WIDTH is 3000 meters so smz_radius of 100 is 3.3%
# SIM_WIDTH is 3000 meters so smz_radius of 150 is 5.0%

# rural

sx = 2290
sy = 800
inf = "rural.srt"

for smz_duration in range(25, 125, 25): # [25, 50, 75]
  for smz_radius in range(50, 200, 50): # [50, 100, 150]
    smz_stats(smz_duration, smz_radius, sx, sy, inf)

# urban

sx = 1430
sy = 2490
inf = "urban.srt"

for smz_duration in range(25, 125, 25): # [25, 50, 75]
  for smz_radius in range(50, 200, 50): # [50, 100, 150]
    smz_stats(smz_duration, smz_radius, sx, sy, inf)

# city

sx = 390
sy = 1710
inf = "city.srt"

for smz_duration in range(25, 125, 25): # [25, 50, 75]
  for smz_radius in range(50, 200, 50): # [50, 100, 150]
    smz_stats(smz_duration, smz_radius, sx, sy, inf)

print (time.ctime()) # ===== end of program =====
