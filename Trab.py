import numpy as np
import json
import math
# import logging
# import logging.handlers


total_infectados = 0
total_criado = 0

class CoronaCar:
    def __init__(self, idd):
        global total_criado
        self.idd = idd
        self.infected = False
        self.infected_till = -1
        self.can_infect = True

        self.last_update = -1
        self.pos = None

        self.tentativas_infect = []

        total_criado+=1

        self.start_contagious = float('infinity')

        self.contacts = 0

    def update_infos(self, traci, step):
        if self.last_update!=step:
            self.last_update = step
            self.pos = traci.vehicle.getPosition(str(self.idd))

        status = step>self.start_contagious and step<self.infected_till

        if self.infected and status==False:
            traci.vehicle.setColor(str(self.idd), (0,0,255))

        self.infected = status

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
        traci.vehicle.remove(str(self.idd),3)

    def INFECT(self, step, traci, till):
        global total_infectados
        if not self.can_infect:
            return

        self.start_contagious = step+1
        self.infected = False
        self.infected_till = till+1
        self.can_infect = False

        traci.vehicle.setColor(str(self.idd), (255,0,0))

        total_infectados += 1
        # print("FUI INFECTADO", self.idd)

    def checa_delay_infect(self, step, carid):


        ret = True
        for i in range(len(self.tentativas_infect)):
            if self.tentativas_infect[i]["step"]+300<step:
                self.tentativas_infect[i] = None
            elif self.tentativas_infect[i]["car"]==carid:
                ret = False
                break


        self.tentativas_infect = [car for car in self.tentativas_infect if car]

        return ret



    def add_tentativa(self, step, carid):
        self.tentativas_infect.append({"step":step, "car":carid})
        # print(self.idd, self.tentativas_infect)


class Trabalho:

    def __init__(self, config_file):
        global total_infectados, total_criado
        total_infectados = 0
        total_criado = 0
        self.veiculos = []

        config_path = './configurations/pandemic_a/{0}'.format(config_file)
        f = open(config_path, "r")
        infos = json.loads(f.read())
        f.close()


        log_path = './log_output/{0}'.format(infos["nome"])

        self.file_log = open(log_path,"w")


        self.isolamento = infos["isolamento"]
        self.chance_infeccao = infos["chance_infeccao"]
        self.tempo_infectado = infos["tempo_infectado"]
        self.distancia_infectar = infos["distancia_infectar"]
        self.random_infected = infos["random_infected"]

        print(self)

    def __str__(self):
        r = {}
        r["isolamento"] = self.isolamento
        r["chance_infeccao"] = self.chance_infeccao
        r["tempo_infectado"] = self.tempo_infectado
        r["distancia_infectar"] = self.distancia_infectar
        r["random_infected"] = self.random_infected
        return json.dumps(r)

    def stop(self):
        self.file_log.close()



    def new_car(self, traci, c):
        if np.random.random()<self.isolamento:
            traci.vehicle.remove(str(c),3)
        else:
            self.veiculos.append(CoronaCar(c))

            if np.random.random()<self.random_infected:
            # if total_criado==40:
                # print("INFECTANDO LAST")
                self.veiculos[-1].INFECT(self.step, traci, self.step+self.tempo_infectado)

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




        self.veiculos = [car for car in self.veiculos if car]



        for i in range(0, len(self.veiculos), 1): # percore entre os veiculos checando a distancia
            car1 = self.veiculos[i]
            for j in range(0, len(self.veiculos), 1):
                car2 = self.veiculos[j]

                if i==j:
                    continue

                d = car1.distance_to_car(traci, car2)
                if d<self.distancia_infectar:

                    can_go = car1.checa_delay_infect(self.step,car2.idd) and car2.checa_delay_infect(self.step,car1.idd)
                    if can_go:

                        power = np.random.random()
                        if car1.is_infected():
                            if not car2.is_infected():
                                # print("DISTANCIA TESTE", car1.idd, car2.idd, d)
                                # print("POW",power)

                                car1.add_tentativa(self.step,car2.idd)
                                car2.add_tentativa(self.step,car1.idd)
                                if power<self.chance_infeccao:
                                    car2.INFECT(self.step, traci, self.step+self.tempo_infectado)

                        # elif car2.is_infected():
                        #     car1.add_tentativa(self.step,car2.idd)
                        #     car2.add_tentativa(self.step,car1.idd)
                        #     if power<self.chance_infeccao:
                        #         car1.INFECT(traci, self.step+self.tempo_infectado)



        total_veiculos = len(self.veiculos)
        atual_total_infectado = 0
        for i in range(0, total_veiculos, 1): # percore entre os veiculos checando a distancia
            c = self.veiculos[i]
            if c.is_infected():
                atual_total_infectado+=1


        infos = {}
        infos["step"] = self.step
        infos["atual_veiculos"] = total_veiculos
        infos["atual_infectados"] = atual_total_infectado
        infos["total_infectados"] = total_infectados
        infos["total_criado"] = total_criado



        self.doLog(infos)

    def doLog(self, infos):
        self.file_log.write(json.dumps(infos)+"\n")
