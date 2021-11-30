import XInput
from pynput import keyboard
from pygame import mixer
mixer.init()
import time

import threading

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
    
    def process_trigger_event(self, event):
        pass

    def process_stick_event(self, event):
        pass


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
        except (AttributeError, TypeError):
            pass

class Waiter:
    def __init__(self):
        self.lastTime = None

    def init(self, sec=0):
        self.lastTime = time.time() + sec

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
def editor(beats, secPerBeat, length, soundSpan, lag, music=None, musicLoc=0, beep=True):

    sheet = []
    if music:
        musicObj = mixer.Sound(music)

    input('(press enter key to start)')

    if music:
        musicObj.play()
        time.sleep(musicLoc)
    key.reset()

    waiter_sound = Waiter()
    waiter_key = Waiter()
    waiter_sound.init()

    waiter_key.init(lag)
    def soundf(waiter):
        for _ in range(length):
            line = ''
            if beep:
                beep1.play()
            waiter.wait(secPerBeat/2)
            line += key.ckey
            waiter.wait(secPerBeat/2)
            for i in range(beats-1):
                if beep:
                    if (i+1) % soundSpan == 0:
                        beep2.play()
                waiter.wait(secPerBeat/2)
                line += key.ckey
                waiter.wait(secPerBeat/2)
            if 'q' in line:
                return
            
    def keyf(waiter, sheet):
        for _ in range(length):
            line = ''
            waiter.wait(secPerBeat/2)
            line += key.ckey
            key.reset()
            waiter.wait(secPerBeat/2)
            for i in range(beats-1):
                waiter.wait(secPerBeat/2)
                line += key.ckey
                key.reset()
                waiter.wait(secPerBeat/2)
            if 'q' in line:
                return
            print(line)
            sheet.append(line)

    threading.Thread(target=soundf, args=(waiter_sound,), daemon=True).start()
    th = threading.Thread(target=keyf, args=(waiter_key, sheet), daemon=True)
    th.start()
    th.join()
    
    return sheet


def editor_ex(bpm: int, base: int, beats: int, length: int, soundSpan: int=1, lag=0, music=None, musicLoc=0, beep=True):
    # base : 基本の拍数
    # beats : 1小節内の拍数
    # length : 小節数
    # soundSpan : 何拍毎に音を鳴らすか
    # lag : 入力の遅延補正(入力判定を遅らせる。0以上の値)

    secPerMeasure = (60/bpm) * base
    secPerBeat = secPerMeasure / beats

    return editor(beats, secPerBeat, length, soundSpan, lag, music, musicLoc, beep)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('bpm', type=float)
    parser.add_argument('--base', '-bs', default=4, type=int, help='基本の拍数')
    parser.add_argument('--beats', '-bt', default=4, type=int, help='1小節内の拍数')
    parser.add_argument('--length', '-l', default=40, type=int, help='1小節内の拍数')
    parser.add_argument('--soundSpan', '-ss', default=1, type=int, help='何小節毎に音を鳴らすか')
    parser.add_argument('--lag', '-lag', default=0, type=float, help='入力の遅延補正(入力判定を遅らせる。0以上の値)')
    parser.add_argument('--music', '-m', type=str, help='音楽ファイル')
    parser.add_argument('--musicLoc', '-ml', default=0, type=float, help='音楽の開始地点(秒数)')
    parser.add_argument('--beep', default=True, type=lambda i:bool(int(i)), help='メトロノーム音を鳴らすか(0 or 1)')
    parser.add_argument('--out', '-o', type=str, help='譜面ファイルの出力先')
    args = parser.parse_args()

    sheet = editor_ex(args.bpm, args.base, args.beats, args.length, args.soundSpan, args.lag, args.music, args.musicLoc, args.beep)

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sheet))
    else:
        print()
        print('='*30)
        print()
        print('\n'.join(sheet))
