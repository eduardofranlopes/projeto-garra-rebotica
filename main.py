#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait

# Initialize the EV3 Brick
ev3 = EV3Brick()

# Define a porta que o motor da garra está conectado.
motor_garra = Motor(Port.A)

# Define a porta que o motor do braço está conectado.
# Configura o motor que gira o braço. Valores positivos fazem o braço subir.
# Valores positivos fazem o braço subir.
# Direçao definida como COUNTERCLOCKWISE para garantir que o braço gire no sentido anti-horário.
motor_braco = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])

#Define a porta que o motor da base está conectado.
#Configura o motor que gira a base.
#Valores positivos fazem a base girar se afastando do fim de curso.
#Direção definida como COUNTERCLOCKWISE para garantir que a base gire no sentido anti-horário se afastando do sensor de toque.
motor_base = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

# Limitado a velocidade máxima de 60 e aceleraçao max de 120 para os motores do braço e da base tenham movimentos suaves e controlados.
motor_braco.control.limits(speed=60, acceleration=120)
motor_base.control.limits(speed=60, acceleration=120)

# Define a porta que sera usada pelo sensor de toque(fim de curso).
fim_de_curso = TouchSensor(Port.S1)

# Define a porta que o sensor de cor está conectado.
sensor_braco = ColorSensor(Port.S3)

#Calibraçao do Robot Arm.

# Rotina de "Homing" para o braço.
# Inicializa o braço. Primeiro ele deve descer por um segundo.
# Depois ele sobe lentamente (15 graus por segundo) até que o sensor de cor detecte a parte branca.
# Entáo o motor é resetado para o ponto definido como zero.
# O motor estaciona nesse ponto para que o braço não se mova.
motor_braco.run_time(-30, 1000)
motor_braco.run(15)
while sensor_braco.reflection() < 32:
    wait(10)
motor_braco.reset_angle(0)
motor_braco.hold()

# Rotina de "Homing" para a base.
# O motor da base gira em sentido horário até tocar o sensor de fim de curso.
# Ao encostar o sistema define como ponto zero a posição atual do motor da base.
# Ele permanece estacionado nessa posiçao.
motor_base.run(-60)
while not fim_de_curso.pressed():
    wait(10)
motor_base.reset_angle(0)
motor_base.hold()


# # Rotina de "Homing" para a garra.
# Inicializar a garra. Primeiro gira o motor até que a garra esteja fechada.
# O motor é controlado para que ele para quando atingir a força máxima (stall(50%)).
# Depois gira o motor por 90 graus para abrir a garra.
# O motor define o ponto atual como zero
# O motor a partir desse ponto definido abre a garra em -90 graus
# Essa configuração é feita para que a garra sempre comece na mesma posiçao, ecitando que ela force as engrenagens ou gire mais que o espaço fisico permite.
motor_garra.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
motor_garra.reset_angle(0)
motor_garra.run_target(200, -90)


def pegar_objeto(posicao):
    # Essa função faz a base do robô girar até a posição indicada.
    # Lá, ela abaixa o cotovelo, fecha a garra e levanta o 
    # cotovelo de novo pra pegar o objeto.

    # Gira até a posição de coleta.
    motor_base.run_target(60, posicao)

    # Abaixa o braço.
    motor_braco.run_target(60, -40)

    # Fecha a garra pra prender a pilha de rodas.
    motor_garra.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)

    # Levanta o braço pra erguer a pilha de rodas.
    motor_braco.run_target(60, 0)


def soltar_objeto(posicao):
    # Essa função faz a base girar até a posição indicada.
    # Lá, ela abaixa o cotovelo e abre a garra pra soltar o objeto.
    # Depois, levanta o braço de novo.

    # Gira até o lugar de entrega.
    motor_base.run_target(60, posicao)
    
    # Abaixa o braço pra colocar a pilha de rodas no chão.
    motor_braco.run_target(60, -40)
    
    # Abre a garra pra soltar as rodas.
    motor_garra.run_target(200, -90)
    
    # Levanta o braço.
    motor_braco.run_target(60, 0)

# Toca três bipes para avisar que a calibração acabou.
for i in range(3):
    ev3.speaker.beep()
    wait(100)

# Define os três pontos de destino para pegar e mover as pilhas de rodas.
ESQUERDA = 160
MEIO = 100
DIREITA = 40

# Esta é a parte principal do programa. É um loop que roda sem parar.
#
# Primeiro, o robô move o objeto da esquerda para o meio.
# Segundo, o robô move o objeto da direita para a esquerda.
# Por fim, o robô move o objeto que agora está no meio para a direita.
#
# No fim das contas, as pilhas da esquerda e da direita trocaram de lugar.
# Aí o loop recomeça e faz tudo de novo, repetidamente.
while True:
    # Move uma pilha de rodas da esquerda para o meio.
    pegar_objeto(ESQUERDA)
    soltar_objeto(MEIO)

    # Move uma pilha de rodas da direita para a esquerda.
    pegar_objeto(DIREITA)
    soltar_objeto(ESQUERDA)

    # Move uma pilha de rodas do meio para a direita.
    pegar_objeto(MEIO)
    soltar_objeto(DIREITA)