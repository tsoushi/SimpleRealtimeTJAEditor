import XInput
from pynput import keyboard
from pygame import mixer
mixer.init()
import time

class XinputHandler(XInput.EventHandler):
    def __init__(self, keyMan):
        super().__init__(0, 1, 2, 3)
        self.keyMan = keyMan

    def process_button_event(self, event):
        if event.type == XInput.EVENT_BUTTON_PRESSED:
            if event.button_id in [1,2,4,8, 4096, 8192, 16384, 32768]:
                self.keyMan.ckey = '1'
            if event.button_id in [256, 512]:
                self.keyMan.ckey = '2'

class KeyMan:
    def __init__(self):
        self.ckey = ''
        keyboard.Listener(on_press=self.press).start()
        handler = XinputHandler(self)
        thread = XInput.GamepadThread()
        thread.add_event_handler(handler)
    
    def reset(self):
        self.ckey = '0'

    def press(self, key: keyboard.HotKey):
        try:
            if key.char in 'jf':
                self.ckey = '1'
            elif key.char in 'kd':
                self.ckey = '2'
            elif key.char in 'q':
                self.ckey = 'q'
        except AttributeError:
            pass

class Waiter:
    def __init__(self):
        self.lastTime = None

    def init(self):
        self.lastTime = time.time()

    def wait(self, sec):
        nextTime = self.lastTime + sec
        sleepTime = nextTime - time.time()
        if sleepTime > 0:
            time.sleep(nextTime - time.time())
        self.lastTime = nextTime
        
key = KeyMan()


beep1 = mixer.Sound('beep1')
beep2 = mixer.Sound('beep2')

#
# エディター
#
def editor(beats, secPerBeat, length, soundSpan, lag):

    if secPerBeat/2-lag < 0 or secPerBeat/2+lag < 0:
        print('lag値が大きすぎます')
        return
    sheet = []

    input('(press enter key to start)')
    key.reset()

    waiter = Waiter()
    waiter.init()
    for _ in range(length):
        line = ''
        beep1.play()
        waiter.wait(secPerBeat/2+lag)
        line += key.ckey
        key.reset()
        waiter.wait(secPerBeat/2-lag)
        for i in range(beats-1):
            if (i+1) % soundSpan == 0:
                beep2.play()
            waiter.wait(secPerBeat/2+lag)
            line += key.ckey
            key.reset()
            waiter.wait(secPerBeat/2-lag)
        
        print(line)
        sheet.append(line)
    
    return sheet


def editor_ex(bpm: int, base: int, beats: int, length: int, soundSpan: int=1, lag=0):
    # base : 基本の拍数
    # beats : 1小節内の拍数
    # length : 小節数
    # soundSpan : 音を鳴らす頻度
    # lag : 入力の遅延補正

    secPerMeasure = (60/bpm) * base
    secPerBeat = secPerMeasure / beats

    return editor(beats, secPerBeat, length, soundSpan, lag)


