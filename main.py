from __future__ import division
import os
import sys
import subprocess
import signal
import socket
import threading
import time
from optparse import OptionParser


import Trab


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME not defined")
import traci





class UnusedPortLock:
    lock = threading.Lock()

    def __init__(self):
        self.acquired = False

    def __enter__(self):
        self.acquire()

    def __exit__(self):
        self.release()

    def acquire(self):
        if not self.acquired:
            UnusedPortLock.lock.acquire()
            self.acquired = True

    def release(self):
        if self.acquired:
            UnusedPortLock.lock.release()
            self.acquired = False

def find_unused_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.bind(('127.0.0.1', 0))
    sock.listen(socket.SOMAXCONN)
    ipaddr, port = sock.getsockname()
    sock.close()
    
    return port

def terminate_sumo(sumo):
    if sumo.returncode == None:
        os.kill(sumo.pid, signal.SIGILL)
        time.sleep(0.5)
        if sumo.returncode == None:
            os.kill(sumo.pid, signal.SIGKILL)
            time.sleep(1)
            if sumo.returncode == None:
                time.sleep(10)





def run(network, begin, end, interval):

    step = 1

    controlador = Trab.Trabalho()

    while step == 1 or traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()          

        vehicles = traci.simulation.getEndingTeleportIDList()
        for vehicle in vehicles:
            traci.vehicle.remove(vehicle, reason=4)



        controlador.do_work(traci, step) # magic is here

        step += 1
    
    time.sleep(10)
    print("Simulation finished")
    traci.close()
    sys.stdout.flush()
    time.sleep(10)
        
def start_simulation(sumo, scenario, network, begin, end, interval, output):
    unused_port_lock = UnusedPortLock()
    unused_port_lock.__enter__()
    remote_port = find_unused_port()

    sumo = subprocess.Popen([sumo, "-c", scenario, "--tripinfo-output", output, "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    unused_port_lock.release()


    try:
        traci.init(remote_port)
        run(network, begin, end, interval)
    except Exception as e:
        print(e)
        raise
    finally:
        print("Terminating SUMO")  
        terminate_sumo(sumo)
        unused_port_lock.__exit__()
        
def main():

    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command", default="sumo-gui", help="The command used to run SUMO [default: %default]", metavar="COMMAND")
    parser.add_option("-s", "--scenario", dest="scenario", default="conf.sumocfg", help="A SUMO configuration file [default: %default]", metavar="FILE")
    parser.add_option("-n", "--network", dest="network", default="wuhan.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")    
    parser.add_option("-b", "--begin", dest="begin", type="int", default=0, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
    parser.add_option("-e", "--end", dest="end", type="int", default=600, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
    parser.add_option("-i", "--interval", dest="interval", type="int", default=1, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
    parser.add_option("-o", "--output", dest="output", default="output.xml", help="The XML file at which the output must be written [default: %default]", metavar="FILE")


    (options, args) = parser.parse_args()
    

        
    start_simulation(options.command, options.scenario, options.network, options.begin, options.end, options.interval, options.output)





if __name__ == "__main__":
    main()