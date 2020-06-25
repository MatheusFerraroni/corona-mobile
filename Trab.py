import numpy as np
import json
import math
import logging

logging.basicConfig(filename='example.log',level=logging.DEBUG, filemode='w')


total_infectados = 0

class CoronaCar:
    def __init__(self, idd):
        self.idd = idd
        self.infected = False
        self.infected_till = -1
        self.can_infect = True

        self.last_update = -1
        self.pos = None

    def update_infos(self, traci, step):
        if self.last_update!=step:
            self.last_update = step
            self.pos = traci.vehicle.getPosition(str(self.idd))

        self.infected = step<self.infected_till

    def is_infected(self):
        return self.infected

    def get_pos(self):
        return self.pos

    def distance_to_car(self, traci, car):
        # x,y = car.get_pos()
        # return traci.vehicle.getDrivingDistance2D(str(self.idd), x, y)

        x1, y1 = self.get_pos()
        x2, y2 = car.get_pos()

        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  

    def remove(self, traci):
        # print("REMOVENDO VEICULO", self.idd)
        traci.vehicle.remove(str(self.idd),3)

    def INFECT(self, traci, till):
        global total_infectados
        if not self.can_infect:
            return
        self.infected = True
        self.infected_till = till
        self.can_infect = False

        traci.vehicle.setColor(str(self.idd), (255,0,0))

        total_infectados += 1




class Trabalho:
    def __init__(self):
        self.veiculos = []

        f = open("./configtrabalho.json","r")
        infos = json.loads(f.read())
        f.close()
        self.isolamento = infos["isolamento"]
        self.chance_infeccao = infos["chance_infeccao"]
        self.tempo_infectado = infos["tempo_infectado"]
        self.distancia_infectar = infos["distancia_infectar"]
        self.random_infected = infos["random_infected"]


    def new_car(self, traci, c):
        if np.random.random()<self.isolamento:
            traci.vehicle.remove(str(c),3)
        else:
            self.veiculos.append(CoronaCar(c))

            if np.random.random()<self.random_infected:
                self.veiculos[-1].INFECT(traci, self.step+self.tempo_infectado)

    def do_work(self, traci, step):
        self.step = step
        cars = traci.vehicle.getIDList()

        for i in range(len(cars)):
            car_id = int(cars[i])

            existe = False
            for j in range(len(self.veiculos)):
                if car_id==self.veiculos[j].idd:
                    existe = True
                    break
            if not existe:
                self.new_car(traci, car_id)

        self.check_infections(traci)




    def check_infections(self, traci):
        for i in range(0,len(self.veiculos),1):
            c = None
            try:
                c = self.veiculos[i]
                c.update_infos(traci, self.step) # atualiza o estado da infeccao e precisa sempre ser executado primeiro para atualizar a posicao
            except Exception as e: # remove que chegaram ao destino
                self.veiculos[i] = None

            if c!=None:
                if not c.is_infected() and not c.can_infect:
                    c.remove(traci)
                    self.veiculos[i] = None



        self.veiculos = [car for car in self.veiculos if car]

        for i in range(0, len(self.veiculos), 1): # percore entre os veiculos checando a distancia
            car1 = self.veiculos[i]
            for j in range(0, len(self.veiculos), 1):
                if i==j:
                    continue
                car2 = self.veiculos[j]

                alvo = None
                if car1.is_infected():
                    if car2.is_infected():
                        continue

                    d = car1.distance_to_car(traci, car2)
                    if d<self.distancia_infectar:
                        if np.random.random()<self.chance_infeccao:
                            car2.INFECT(traci, self.step+self.tempo_infectado)
                elif car2.is_infected():
                    d = car1.distance_to_car(traci, car2)
                    if d<self.distancia_infectar:
                        if np.random.random()<self.chance_infeccao:
                            car1.INFECT(traci, self.step+self.tempo_infectado)



        total_veiculos = len(self.veiculos)
        total_infectado = 0
        for i in range(0, total_veiculos, 1): # percore entre os veiculos checando a distancia
            c = self.veiculos[i]
            if c.is_infected():
                total_infectado+=1


        infos = {}
        infos["step"] = self.step
        infos["veiculos"] = total_veiculos
        infos["infectados"] = total_infectado


        logging.info(json.dumps(infos))