#! /usr/bin/env python

import sys
import RPi.GPIO as GPIO
import time
import atexit
from threading import Timer as Timer
from multiprocessing.dummy import Pool as ThreadPool

BLUE_LED = 23
YELLOW_LED = 24
RED_LED = 25

LEDS = [BLUE_LED, YELLOW_LED, RED_LED]

class Commands:
    _workerPool = ThreadPool(1)
    _currentState = None
    _stateHello = "HELLO" 
    _stateOk = "OK"
    _stateWarn = "WARN"
    _stateError = "ERROR"
    _stateOff = "OFF"
    _stateProgress = "PROGRESS"
    
    def hello(self):
        self._currentState = self._stateHello
        for i in range(2):
            for led in LEDS:
                GPIO.output(led, GPIO.HIGH)
            time.sleep(0.15)
            for led in LEDS:
                GPIO.output(led, GPIO.LOW)
            time.sleep(0.15)   

    def cmd_ok(self):
        self._currentState = self._stateOk
        self._workerPool.apply_async(self._turnOnOneLed, [BLUE_LED])        

    def cmd_warn(self):
        self._currentState = self._stateWarn
        self._workerPool.apply_async(self._turnOnOneLed, [YELLOW_LED])

    def cmd_error(self):
        self._currentState = self._stateError
        self._workerPool.apply_async(self._turnOnOneLed, [RED_LED])        
 
    def cmd_off(self):
        self._currentState = self._stateOff
        self._workerPool.apply_async(self._turnOnOneLed, [None])
 
    def cmd_progress(self):
        if (self._currentState == self._stateProgress):
            return

        self._currentState = self._stateProgress
        self._workerPool.apply_async(self._spinLeds)        
    
    def destroy(self):
        self.cmd_off()
        self._workerPool.close()
        self._workerPool.join() 

    def _restState(self):
        _inProgress = False        
    
    def _spinLeds(self):
        totalSpinTimeSeconds = 0.5
        stepSleepTime = totalSpinTimeSeconds / ((len(LEDS) - 1) * 2)
        animatePlan = LEDS + LEDS[1:len(LEDS)-1][::-1]
        while(self._currentState == self._stateProgress):
            for led in animatePlan:
                self._turnOnOneLed(led)
                time.sleep(stepSleepTime)

    def _turnOnOneLed(self, toBeTurnedOn):
        for led in LEDS:
            if led == toBeTurnedOn: GPIO.output(led, GPIO.HIGH) 
            else: GPIO.output(led, GPIO.LOW)
        
COMMANDS = Commands()

def setupGpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for led in LEDS:
        GPIO.setup(led, GPIO.OUT)

def processCommand(input):
    command = "cmd_" + input.strip()
    commandHandler = getattr(COMMANDS, command, None)      
    if (callable(commandHandler)):
        commandHandler()

def stdinMode():
    try: 
        while (True):
            line = raw_input()
            processCommand(line)
    except EOFError:
        sys.exit(0)

def interactiveMode():
    print 'type "quit" to exit'
    while (True):
        line = raw_input('command> ')
        if line == 'quit':
            sys.exit(0)
        processCommand(line)

def prepareExit():
    COMMANDS.destroy()   

setupGpio()
atexit.register(prepareExit)
COMMANDS.hello()

if '-i' in sys.argv:
    interactiveMode()
else:
    stdinMode()
