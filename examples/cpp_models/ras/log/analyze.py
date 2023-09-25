import matplotlib.pyplot as plt
import json
import sys
import numpy as np
import seaborn as sns
import pandas as pd
import re

#### single data visualization ####
#### travel distance vs (speed, risk_prob, action) ####
#if len(sys.argv) == 2:
#
#    with open(sys.argv[1], "r") as f:
#        data = json.load(f)
#
#    travel_dist = []
#    ego_vel = []
#    for frame in data:
#        travel_dist.append(frame.get("lane_position"))
#        ego_vel.append(frame.get("speed"))
#
#    fig, ax = plt.subplots(3, 1, tight_layout=True)
#    ax[0].plot(travel_dist, ego_vel, ".", linestyle="-")
#    ax[0].set_xlim(0, 500)
#    ax[0].set_ylabel("vehicle speed [m/s]")
#    ax[1].set_xlim(0, 500)
#    ax[1].set_ylabel("risk probs")
#    ax[2].set_xlim(0, 500)
#    ax[2].set_ylabel("intervention request")
#    ax[2].set_xlabel("travel distance [m]")
#
#    risk_ids = [] 
#    color_map = plt.get_cmap("Set3")
#    risk_num = len(data[0].get("risks"))
#
#    for risk in data[0].get("risks"):
#        risk_ids.append(risk.get("id"))
#
#    prev_ego_pose = 0.0
#    for i in range(0, len(risk_ids)):
#        id = risk_ids[i]
#        risk_prob = []
#        risk_pose = []
#        clossing_frame = 0
#
#        for frame_num in range(0, len(data)):
#            for risk in data[frame_num].get("risks"):
#
#                if id != risk.get("id"): continue
#
#                risk_prob.append(risk.get("prob")) 
#                position = risk.get("lane_position") if id[0] != "-" else 500.0 - risk.get("lane_position")
#                risk_pose.append(position)
#
#                if prev_ego_pose < position <= data[frame_num].get("lane_position"):
#                    clossing_frame = frame_num
#
#            prev_ego_pose = data[frame_num].get("lane_position")
#
#        ax[1].plot(risk_pose, risk_prob, linestyle="-", color=color_map(i/len(risk_ids)))
#        ax[1].plot(risk_pose[0], risk_prob[0]+0.01, marker="$S$", markersize=5, color=color_map(i/len(risk_ids)))
#        ax[1].plot(risk_pose[clossing_frame], risk_prob[clossing_frame]+0.01, "x", markersize=5, color=color_map(i/len(risk_ids)))
#        ax[1].plot(risk_pose[-1], risk_prob[-1]+0.01, marker="$G$", markersize=5, color=color_map(i/len(risk_ids)))
#
#
#    last_request_target = ""
#    request_position = []
#    hight = 1
#    for frame in data:
#        print(request_position, last_request_target, frame.get("action_target"))
#
#        if frame.get("action") == "REQUEST" \
#           and (len(request_position)==0 or frame.get("action_target") == last_request_target):
#                request_position.append(frame.get("lane_position"))
#                last_request_target = frame.get("action_target")
#        elif len(request_position) > 0:
#            ax[2].plot(request_position, [hight]*len(request_position), marker=".", linestyle="-", color=color_map(risk_ids.index(last_request_target)/len(risk_ids)))
#            request_position = []
#            last_request_target = ""
#            hight += 1
#
#
#    plt.show()

if len(sys.argv) == 2:

    with open(sys.argv[1], "r") as f:
        data = json.load(f)

    fig, ax = plt.subplots(2, 1, tight_layout=True)
    ax2 = ax[0].twinx()

    elapse_time_list = []
    elapse_time = 0.0
    ego_vel = []
    for frame in data:
        elapse_time_list.append(elapse_time)
        elapse_time += 2.0
        ego_vel.append(frame.get("speed"))
    
    ax[0].plot(elapse_time_list, ego_vel, ".", linestyle="-")

    risk_ids = [] 
    risk_num = len(data[0].get("risks"))
    for risk in data[0].get("risks"):
        risk_ids.append(risk.get("id"))
    color_map = plt.get_cmap("Set3")


    reserved_time_list = []
    for i in range(0, len(risk_ids)):
        id = risk_ids[i]
        elapsed_time = 0.0
        is_crossed = False
        last_prob = None
        crossing_time = 0
        

        for frame in data:
            elapsed_time += 2.0
            for risk in frame.get("risks"):

                if id != risk.get("id"): continue

                last_prob = risk.get("prob")
                position = risk.get("lane_position") if id[0] != "-" else 500.0 - risk.get("lane_position")
                if crossing_time == 0 and position <= frame.get("lane_position"):
                    print(f"crossed with {risk.get('id')} at {elapsed_time}")
                    is_crossed = True

                    crossing_time = elapsed_time
                    while True:
                        if crossing_time in reserved_time_list: 
                            crossing_time += 1.0
                        else:
                            break
                    crossing_prob = risk.get("prob")
                    if crossing_prob == 0.0: crossing_prob += 0.01 

                    ax2.bar(crossing_time, crossing_prob, color=color_map(i/len(risk_ids)))
                    reserved_time_list.append(crossing_time)
                    continue



        if not is_crossed:
            crossing_time = elapsed_time
            while True:
                if crossing_time in reserved_time_list: 
                    crossing_time += 1.0
                else:
                    break
            ax2.bar(crossing_time, last_prob, color=color_map(i/len(risk_ids)))


    last_action_target = None
    buf_prob = []
    buf_time = []
    elapsed_time = 0.0
    for frame in data:
        elapsed_time += 2.0

        target = frame.get("action_target")
        if frame.get("action") in ["NO_ACTION", "RECOG"] or last_action_target != target:
            for risk in frame.get("risks"):
                if last_action_target != risk.get("id"): continue
                buf_prob.append(risk.get("prob"))
                buf_time.append(elapsed_time)


            if last_action_target != None:
                ax[1].plot(buf_time, buf_prob, linestyle="-", marker=".", color=color_map(risk_ids.index(last_action_target)/len(risk_ids)))

            if frame.get("action") in ["NO_ACTION", "RECOG"]:
                last_action_target = None
            else:
                last_action_target = target
            buf_prob = []
            buf_time = []
            continue

        for risk in frame.get("risks"):
            if target != risk.get("id"): continue
            print(f"requested to {target} at {elapsed_time}")
            buf_prob.append(risk.get("prob"))
            buf_time.append(elapsed_time)
            last_action_target = target

    ax[0].set_xlim(0, elapsed_time)
    ax[0].set_ylabel("vehicle speed [m/s]")
    ax[1].set_xlim(0, elapsed_time)
    ax[1].set_ylabel("risk probs")
    ax2.set_ylabel("intervention request")
    ax2.set_xlabel("travel distance [m]")

    plt.show()

elif len(sys.argv) > 2:

    df = pd.DataFrame(columns = ["policy", "risk_num", "travel_time", "total_fuel_consumption", "mean_fuel_consumption", "dev_accel", "mean_speed", "risk_omission", "risk_omission_num", "ambiguity_omission", "ambiguity_omission_num", "request_time"])
    fig, ax = plt.subplots(1, 1, tight_layout=True)

    for file in sys.argv[1:]:
        with open(file, "r") as f:
            data = json.load(f)

        policy = re.findall("([A-Z]*)\d", file)[0]
        risk_num = float(re.findall("([\d.]*)_", file)[0]) * 2 * 500
        travel_time = 0.0
        fuel_consumption = [] 
        accel = []
        speed = []
        risk_omission = 0.0 
        risk_omission_num = 0
        ambiguity_omission = 0.0 
        ambiguity_omission_num = 0
        request_time = 0.0

        last_ego_position = 0.0
        for frame in data:
            travel_time += 2.0
            speed.append(frame.get("speed"))
            accel.append(frame.get("accel"))
            fuel_consumption.append(frame.get("fuel_consumption"))
            
            if frame.get("action") == "REQUEST":
                request_time += 2.0

            if frame.get("risks") is None:
                print(f"skipped {file} because of no obstacle spawned")
                continue

            for risk in frame.get("risks"):
                position = risk.get("lane_position") if risk.get("id")[0] != "-" else 500.0 - risk.get("lane_position")
                if last_ego_position < position <= frame.get("lane_position"):

                    ambiguity_omission += 0.5 - abs(0.5 - risk.get("prob"))
                    if 0.0 < risk.get("prob") < 1.0:
                        ambiguity_omission_num += 1

                    if speed[-1] > 2.8:
                        risk_omission += risk.get("prob") 
                        risk_omission_num += 1


            last_ego_position = frame.get("lane_position") 

        total_fuel_consumption = sum(fuel_consumption)
        mean_fuel_consumption = sum(fuel_consumption)/len(fuel_consumption)
        mean_speed = sum(speed)/len(speed)

        dev_accel = 0.0
        mean_accel = sum(accel)/len(accel)
        for a in accel:
            dev_accel += (a - mean_accel) ** 2
        dev_accel = dev_accel / len(accel)

        buf_df = pd.DataFrame([[policy, risk_num, travel_time, total_fuel_consumption, mean_fuel_consumption, dev_accel, mean_speed, risk_omission, risk_omission_num, ambiguity_omission, ambiguity_omission_num, request_time]], columns=df.columns)
        df = pd.concat([df, buf_df], ignore_index=True)


    print(df["policy"])
    sns.lineplot(data=df, x="risk_num", y="travel_time", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="total_fuel_consumption", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="mean_fuel_consumption", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="dev_accel", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="mean_speed", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="risk_omission", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="risk_omission_num", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="ambiguity_omission", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="ambiguity_omission_num", hue="policy", markers=True)
    plt.show()
    sns.lineplot(data=df, x="risk_num", y="request_time", hue="policy", markers=True)
    plt.show()
