# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl
webrepl.start()
gc.collect()

import machine
from machine import Pin, PWM
from time import sleep_ms
from uPy_APDS9960.APDS9960LITE import APDS9960LITE

#Init I2C Buss
#Høyre sensor
i2c  =  machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))               # Node MCU Pin D1:SCL og Node MCU Pin D2:SDA
#Venstre sensor
i2c1 =  machine.I2C(scl=machine.Pin(16), sda=machine.Pin(14))             # Node MCU Pin D0:SCL og Node MCU Pin D5:SDA

#Init sensorVenstre
sensorVenstre=APDS9960LITE(i2c1)                                          # Enable sensor
sensorVenstre.prox.enableSensor()                                         # Enable Light sensor
sensorVenstre.prox.eProximityGain=3                                       # x8 gain
sensorVenstre.prox.eLEDCurrent =6                                         # justerer i forhold til høyde forskjell
sensorVenstre.prox.setInterruptThreshold(high=80,low=0,persistance=7)
sensorVenstre.prox.enableInterrupt(True)                                  # Enable interrupt
sensorVenstre.prox.clearInterrupt()                                       # Clear interrupt

#Init sensorHoyre
sensorHoyre=APDS9960LITE(i2c)                                             # Enable sensor
sensorHoyre.prox.enableSensor()                                           # Enable Light sensor
sensorHoyre.prox.eProximityGain=3                                         # x8 gain
sensorHoyre.prox.eLEDCurrent =6                                           # justerer i forhold til høyde forskjell
sensorHoyre.prox.setInterruptThreshold(high=80,low=0,persistance=7)
sensorHoyre.prox.enableInterrupt(True)                                    # Enable interrupt
sensorHoyre.prox.clearInterrupt()                                         # Clear interrupt

#Setter pinner til motorene
motorVenstreA = PWM(Pin(2, Pin.OUT))                                      # Node MCU Pin D4
motorVenstreB = PWM(Pin(0, Pin.OUT))                                      # Node MCU Pin D3
motorHoyreA   = PWM(Pin(13, Pin.OUT))                                     # Node MCU Pin D7
motorHoyreB   = PWM(Pin(12, Pin.OUT))                                     # Node MCU Pin D6

#Starter med alle mororer avskrudd
motorVenstreA.duty(0)
motorVenstreB.duty(0)
motorHoyreA.duty(0)
motorHoyreB.duty(0)

#tallene viser kraften som motorene bruker. 0 er av og 1023 er max på
motorVenstreHastighetFremover = 80 
motorHoyreHastighetFremover   = 80
motorVenstreHastighetBakover  = 60 
motorHoyreHastighetBakover    = 60
motorVenstreRaskereFremover   = 90
motorHoyreRaskereFremover     = 90
nivåSort                      = 180                                         # Sorthets nivå, testes i koden < 5

# definisjoner/ funksjoner
def kjorTilVenstreMotorFremover():                                        # Venstre motor kjører i gitt hastighet Fremover
    motorVenstreA.duty(motorVenstreHastighetFremover)
    motorVenstreB.duty(0)
    
def kjorTilHoyreMotorFremover():                                          # Høyre motor kjører i gitt hastighet Fremover
    motorHoyreA.duty(motorHoyreHastighetFremover)
    motorHoyreB.duty(0)
    
def kjorTilVenstreMotorBakover():                                         # Venstre motor kjører i gitt hastighet bakover
    motorVenstreA.duty(0)
    motorVenstreB.duty(motorVenstreHastighetBakover)
    motorHoyreA.duty(motorHoyreRaskereFremover)
    sleep_ms(70)

def kjorTilHoyreMotorBakover():                                           # Høyre motor kjører i gitt hastighet bakover
    motorHoyreA.duty(0)
    motorHoyreB.duty(motorHoyreHastighetBakover)
    motorVenstreA.duty(motorVenstreRaskereFremover)
    sleep_ms(70)

def erPaaSvartNivaaVenstre(sesnorLevel):                                  # Nivå på venstre sensor indikerer sort
    rett=True                                                             # Settes til sann
    if(sesnorLevel > nivåSort ):                                          # Sjekker om sensorLevel er høyere eller lavere
        rett=False                                                        # Settes til usann hvis høyere verdi
    return rett                                                           # Returnerer verdien

def erPaaSvartNivaaHoyre(sesnorLevel):                                    # Nivå på høyre sensor indikerer sort
    rett=True                                                             # Settes til sann
    if(sesnorLevel > nivåSort):                                           # Sjekker om sensorLevel er høyere eller lavere
        rett=False                                                        # Settes til usann hvis høyere verdi
    return rett                                                           # Returnerer verdien
    
try :
    sleep_ms(5000)                                                        # Venter ca. 5 sekunder før den starter
    while True:
        #Venstre side
        sleep_ms(50)                                                      # wait for readout to be ready
        venstreSensorlevel=sensorVenstre.prox.proximityLevel              # setter nytt navn for venstre sensor sitt nærhetsnivå
        
        if ( erPaaSvartNivaaVenstre(venstreSensorlevel) ) :               # Sjekker den returnerte verdien fra tidligere
            kjorTilVenstreMotorBakover()                                  # Hvis sann kjører venstre motor bakover
            
        else:
            kjorTilVenstreMotorFremover()                                 # Venstre sensor indikerer ikke svart, og kjører fremover
        
        #Høyre side
        sleep_ms(50)                                                      # wait for readout to be ready
        hoyreSensorlevel=sensorHoyre.prox.proximityLevel                  # Setter nytt navn for høyre sensor sitt nærhetsnivå
        
        if ( erPaaSvartNivaaHoyre(hoyreSensorlevel) ) :                   # Sjekker den returnerte verdien fra tidligere
            kjorTilHoyreMotorBakover()                                    # Hvis sann kjører høyre motor bakover
            
        else:
            kjorTilHoyreMotorFremover()                                   # Høyre sensor indikerer ikke svart, og kjører fremover

#Avslutter programmet med Ctrl + c
except KeyboardInterrupt :
   print("Hade...")
   motorVenstreA.duty(0)
   motorVenstreB.duty(0)
   motorHoyreA.duty(0)
   motorHoyreB.duty(0)
