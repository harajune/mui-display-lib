
# mui touch panel event class
# -*- coding: utf-8 -*-

import sys
import asyncio
from evdev import InputDevice, categorize, ecodes, list_devices, KeyEvent


EV_SYN = 0x00   # event type sync
SYN_REPORT = 0  # event code sync report

EV_KEY = 0x01       # event type key (touch down or up or hold)
BTN_TOUCH = 0x14a   # event code touch
VALUE_UP = 0        # evnet value up
VALUE_DOWN = 1      # event value down
VALUE_MOVE = 2      # event value move

EV_ABS = 0x03   # event type Axis postion report
ABS_X = 0x00    # event code Axis X
ABS_Y = 0x01    # event code Axis Y


class MotionEvent(object):
    """
    Touch event class

    Attributes
    -----------
    timestamp :  float
        timestamp

    action : int
        touch action type. VALUE_UP or VALUE_DOWN or VALUE_MOVE

    x : int
        touch x position

    y : int
        touch y position
    """

    def __init__(self):
        self._timestamp = 0
        self._action = VALUE_UP
        self._x = 0
        self._y = 0

    def __str__(self):
        msg = '--- MotionEvent at {:f}, action {:d}, x {:d}, y {:d} ---'
        return msg.format(self.timestamp, self.action, self.x, self.y)

    def copy(self, e: 'MotionEvent'):
        self._timestamp = e.timestamp
        self._action = e.action
        self._x = e.x
        self._y = e.y
        

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def action(self):
        return self._action

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @timestamp.setter
    def timestamp(self, t):
        self._timestamp = t

    @action.setter
    def action(self, action):
        self._action = action

    @x.setter
    def x(self, x):
        self._x = x

    @y.setter
    def y(self, y):
        self._y = y
        

class InputEventListener(object):
    """
    Interface definition class for a callback to be invoked when a touch event will occur.
    If you want to receive touch event, please override onInputEvent method.
    """

    def onInputEvent(self, e:MotionEvent):
        """
        touch event callback

        Parameters
        -----------
        e : MotionEvent
        """
        raise NotImplementedError


class InputHandler(object):
    """
    InputHandler is handling touch event.

    Examples
    --------
    from mui_ui import InputHandler, InputEventListener

    class App(InputEventListener):
        def __init__(self):
            # create input event handler
            self._input = InputHandler(self)

        def mainLoop(self):
            # start capture touch event
            self._input.startEventLoop()

        def onInputEvent(self, e: MotionEvnet):
            # handling motion event. for instance, pass to UI(dispatchTouchEvent())


    # start application
    app = App()
    app.mainLoop()

    See Also
    --------
    InputEventListener
    MotionEvent
    """

    def __init__(self, listener:InputEventListener, target_device='Atmel maXTouch Touchscreen'):
        """
        Parameters
        ------------
        listener : InputEventListener
            callback

        target_device : str
            touch device name(DO NOT NEED CHANGE)
        """
        self.motionEvent = None
        self.inputEventListener = listener

        # get mui touch panel
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if device.name == target_device:
                print(device)
                self.device = device
    
    def startEventLoop(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.eventLoop())

    async def eventLoop(self):
        changeKey = False
        async for ev in self.device.async_read_loop():
            #print(ev)

            # handle input event
            if self.motionEvent == None:
                self.motionEvent = MotionEvent()

            if ev.type == EV_SYN:
                # last data sing for multi part touch events.
                if changeKey == False:
                    self.motionEvent.action = VALUE_MOVE
                self.motionEvent.timestamp = ev.timestamp()
                self.handleInputEvent(self.motionEvent)
                changeKey = False
                
            if (ev.type == EV_ABS and ev.code == ABS_X):
                self.motionEvent.x = (ev.value // 2)

            if (ev.type == EV_ABS and ev.code == ABS_Y):
                self.motionEvent.y = (ev.value // 20)

            if (ev.type == EV_KEY):
                self.motionEvent.action = ev.value
                changeKey = True

    def handleInputEvent(self, e:MotionEvent):
        self.inputEventListener.onInputEvent(e)



# for test
class TestInputEventListener(InputEventListener):
    def __init__(self):
        super().__init__()

    def onInputEvent(self, e:MotionEvent):
        print(e)

if __name__ == '__main__':
    try:
        listener = TestInputEventListener()
        input = InputHandler(listener)
        input.startEventLoop()
    except (KeyboardInterrupt, EOFError):
        pass
    sys.exit(0)


