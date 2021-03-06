from random import randrange, random
import sys
from time import sleep
import globals


class Rocket:

    ################################################
    # O CONSTRUTOR DA CLASSE NÃO PODE SER ALTERADO #
    ################################################
    def __init__(self, type):
        self.id = randrange(1000)
        self.name = type
        if(self.name == 'LION'):
            self.fuel_cargo = 0
            self.uranium_cargo = 0
            

    def nuke(self, planet): # Permitida a alteração
        planet_damage = self.damage()
        planet_lock = globals.get_planet_lock(planet.name)

        # escolhendo aleatoriamente qual polo será atacado
        # e adquirindo o mutex do polo para que nao sejam atingidos ao mesmo tempo
        # e destruam o planeta
        north_or_south_pole = random()
        if(north_or_south_pole < 0.51):
            globals.get_north_pole_lock(planet.name).acquire()
            print(f"[EXPLOSION] - The {self.name} ROCKET reached the planet {planet.name} on North Pole")
        else:
            globals.get_south_pole_lock(planet.name).acquire()
            print(f"[EXPLOSION] - The {self.name} ROCKET reached the planet {planet.name} on South Pole")
        
        #mutex do planeta para atingir com a bomba e diminuir o terraform
        planet_lock.acquire()
        planet.nuke_detected(planet_damage)
        planet_lock.release()

        if(north_or_south_pole < 0.51):
            globals.get_north_pole_lock(planet.name).release()
        else:
            globals.get_south_pole_lock(planet.name).release()

    
    def voyage(self, planet): # Permitida a alteração (com ressalvas)
        
        bases_ref = globals.get_bases_ref()
        
        #comportamento do foguete LION é diferente pois ele
        #nao ataca, apenas leva recursos
        if self.name == 'LION':
            moon_base = bases_ref['moon']

            failure =  self.do_we_have_a_problem()

            #Se nao falhou na viagem, preenche os recursos da lua
            if(not failure):
                globals.get_moon_resources_mutex().acquire()
                moon_base.uranium += 75
                moon_base.fuel += 120
                globals.get_moon_resources_mutex().release()
            else:
                #se der falha, solicita um novo foguete
                globals.get_moon_needs_resources_mutex().acquire()
                globals.set_moon_needs_resources(True)
                globals.get_moon_needs_resources_mutex().release()
        else:
            # Essa chamada de código (do_we_have_a_problem e simulation_time_voyage) não pode ser retirada.
            # Você pode inserir código antes ou depois dela e deve
            # usar essa função.
            self.simulation_time_voyage(planet)
            if len(globals.get_not_terraformed_planets()) > 0:
                failure =  self.do_we_have_a_problem()
                #Se nao falhou na viagem, atinge o planeta destino
                if(not failure):
                    self.nuke(planet)



    ####################################################
    #                   ATENÇÃO                        # 
    #     AS FUNÇÕES ABAIXO NÃO PODEM SER ALTERADAS    #
    ###################################################
    def simulation_time_voyage(self, planet):
        if planet.name == 'MARS':
            sleep(2) # Marte tem uma distância aproximada de dois anos do planeta Terra.
        else:
            sleep(5) # IO, Europa e Ganimedes tem uma distância aproximada de cinco anos do planeta Terra.

    def do_we_have_a_problem(self):
        if(random() < 0.15):
            if(random() < 0.51):
                self.general_failure()
                return True
            else:
                self.meteor_collision()
                return True
        return False
            
    def general_failure(self):
        print(f"[GENERAL FAILURE] - {self.name} ROCKET id: {self.id}")
    
    def meteor_collision(self):
        print(f"[METEOR COLLISION] - {self.name} ROCKET id: {self.id}")

    def successfull_launch(self, base):
        if random() <= 0.1:
            print(f"[LAUNCH FAILED] - {self.name} ROCKET id:{self.id} on {base.name}")
            return False
        return True
    
    def damage(self):
        return random()

    def launch(self, base, planet):
        if(self.successfull_launch(base)):
            print(f"[{self.name} - {self.id}] launched.")
            self.voyage(planet)        
