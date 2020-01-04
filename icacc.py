from __future__ import absolute_import
from __future__ import print_function

from collections import defaultdict

import os
import sys
import optparse
import random

# car setting
CarMaxSpeed = "15.0"

# class decleration
class Car:

    MaxLengthToControl = 180

    route_type_to_lane = {}
    route_type_to_lane["route_WE"] = 1
    route_type_to_lane["route_WN"] = 2
    route_type_to_lane["route_WS"] = 0
    route_type_to_lane["route_EW"] = 1
    route_type_to_lane["route_EN"] = 0
    route_type_to_lane["route_ES"] = 2
    route_type_to_lane["route_NE"] = 2
    route_type_to_lane["route_NW"] = 0
    route_type_to_lane["route_NS"] = 1
    route_type_to_lane["route_SE"] = 0
    route_type_to_lane["route_SN"] = 1
    route_type_to_lane["route_SW"] = 2

    def __init__(self, route_type, VehId):
        self.route_type = route_type
        self.VehId = VehId
        self.count = self.MaxLengthToControl * 10 / 15 

    def new_to_road(self):
        traci.vehicle.add(self.VehId, self.route_type, typeID="VehicleA", departSpeed=CarMaxSpeed, departLane=self.route_type_to_lane[self.route_type])
        traci.vehicle.setSpeedMode(self.VehId, 0)

    def step(self):
        self.count = self.count - 1
        traci.vehicle.setSpeed(self.VehId, float(CarMaxSpeed))
        traci.vehicle.setSpeedMode(self.VehId, 0)
        if self.count <= 0:
            return True
        else:
            return False

class RoadController:
    def __init__(self):
        self.waiting_dispatch = defaultdict(list)
        self.on_road_car = []

    def dispatch_car_from_waiting(self, step):
        cars = self.waiting_dispatch[step]
        for car in cars:
            car.new_to_road()
            self.on_road_car.append(car)

    def assigned_car(self, step_to_roll_out, car):
        self.waiting_dispatch[step_to_roll_out].append(car)

    def step(self):
        for car in self.on_road_car:
            if car.step():
                self.on_road_car.remove(car)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

# simulation setting
SimulationStepLength = 0.05
SimulationPeriod = 1800
SimulationEnding = 2000
SimulationDuration = SimulationEnding/SimulationStepLength
print("Duration of Simulation(steps): " + str(SimulationDuration))

def generate_routefile():
    random.seed(42)  # make tests reproducible
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>""", file = routes)
        # vehicle configuration of simulation
        print("""
        <vType id="VehicleA" accel="3.5" decel="5.0" sigma="0" length="5" maxSpeed="{}" speedFactor="1.0" minGap="0.0"
        guiShape="passenger" speedDev="0" tau="0.1"/>
        """.format(CarMaxSpeed), file=routes)
        #speedFactor="1.0"   speedDev="0"
        # route configuration of simulation
        print("""
        <route id="route_WE" edges="L1 L2 L11 L12" />
        <route id="route_WN" edges="L1 L2 L15 L16" />
        <route id="route_WS" edges="L1 L2 L7 L8" />
        <route id="route_EW" edges="L9 L10 L3 L4" />
        <route id="route_EN" edges="L9 L10 L15 L16" />
        <route id="route_ES" edges="L9 L10 L7 L8" />
        <route id="route_NE" edges="L13 L14 L11 L12" />
        <route id="route_NW" edges="L13 L14 L3 L4" />
        <route id="route_NS" edges="L13 L14 L7 L8" />
        <route id="route_SE" edges="L5 L6 L11 L12" />
        <route id="route_SN" edges="L5 L6 L15 L16" />
        <route id="route_SW" edges="L5 L6 L3 L4" />
        """, file=routes)
        print("</routes>", file=routes)

def generate_car(road_control, step):
    if random.uniform(0,1) < 0.6:
        road_control.assigned_car(step, Car("route_WE", "WE_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_WN", "WN_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_WS", "WS_{}".format(step)))
    if random.uniform(0,1) < 0.6:
        road_control.assigned_car(step, Car("route_EW", "EW_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_EN", "EN_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_ES", "ES_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_NE", "NE_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_NW", "NW_{}".format(step)))
    if random.uniform(0,1) < 0.6:
        road_control.assigned_car(step, Car("route_NS", "NS_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_SE", "SE_{}".format(step)))
    if random.uniform(0,1) < 0.6:
        road_control.assigned_car(step, Car("route_SN", "SN_{}".format(step)))
    if random.uniform(0,1) < 0.2:
        road_control.assigned_car(step, Car("route_SW", "SW_{}".format(step)))

def run():
    """execute the TraCI control loop"""
    random.seed(42)
    step = 0
    road_control = RoadController()
    while step < 1000:
        if step % 10 == 0:
            generate_car(road_control, step)
        road_control.dispatch_car_from_waiting(step)
        road_control.step()
        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                        default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                            "--tripinfo-output", "tripinfo.xml"])
    run()

# N = SimulationPeriod  # number of time steps
# # demand per second from different directions (probabilities)
# pWE = 1. / 10   # vehicles from west lane
# pWN = 1. / 12
# pWS = 1. / 30
# pEW = 1. / 12   # vehicles from east lane
# pEN = 1. / 16
# pES = 1. / 25
# pNE = 1. / 14   # vehicles from north lane
# pNW = 1. / 16
# pNS = 1. / 18
# pSE = 1. / 12   # vehicles from south lane
# pSN = 1. / 16
# pSW = 1. / 20
# generate vehicles randomly
# vehNr = 0
# for i in range(N):
#     # vehicles dirving from west
#     if random.uniform(0, 1) < pWE:
#         print('    <vehicle id="vWE_%i" type="VehicleA" route="route_WE" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pWN:
#         print('    <vehicle id="vWN_%i" type="VehicleA" route="route_WN" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pWS:
#         print('    <vehicle id="vWS_%i" type="VehicleA" route="route_WS" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1

#     # vehicles dirving from east
#     if random.uniform(0, 1) < pEW:
#         print('    <vehicle id="vEW_%i" type="VehicleA" route="route_EW" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pEN:
#         print('    <vehicle id="vEN_%i" type="VehicleA" route="route_EN" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pES:
#         print('    <vehicle id="vES_%i" type="VehicleA" route="route_ES" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1

#     # vehicles dirving from south
#     if random.uniform(0, 1) < pSE:
#         print('    <vehicle id="vSE_%i" type="VehicleA" route="route_SE" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pSN:
#         print('    <vehicle id="vSN_%i" type="VehicleA" route="route_SN" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pSW:
#         print('    <vehicle id="vSW_%i" type="VehicleA" route="route_SW" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1

#     # vehicles dirving from north
#     if random.uniform(0, 1) < pNE:
#         print('    <vehicle id="vNE_%i" type="VehicleA" route="route_NE" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pNS:
#         print('    <vehicle id="vNS_%i" type="VehicleA" route="route_NS" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1
#     if random.uniform(0, 1) < pNW:
#         print('    <vehicle id="vNW_%i" type="VehicleA" route="route_NW" depart="%i" />' % (
#             vehNr, i), file=routes)
#         vehNr += 1

# traci.vehicle.add("newVeh", "route_WN", typeID="VehicleA", departSpeed="15.0", departLane="2")
# traci.vehicle.setSpeedMode("newVeh", 0)
# traci.vehicle.setSpeed("newVeh", 10.0)
# traci.vehicle.setSpeedMode("newVeh", 0)