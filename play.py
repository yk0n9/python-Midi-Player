import time
import pydirectinput
import mido
import util
import tkinter
from tkinter import filedialog

pydirectinput.PAUSE=0
keys = {24: 'z', 26: 'x', 28: 'c', 29: 'v', 31: 'b', 33: 'n', 35: 'm',
        36: 'z', 38: 'x', 40: 'c', 41: 'v', 43: 'b', 45: 'n', 47: 'm',
        48: 'z', 50: 'x', 52: 'c', 53: 'v', 55: 'b', 57: 'n', 59: 'm',
        60: 'a', 62: 's', 64: 'd', 65: 'f', 67: 'g', 69: 'h', 71: 'j',
        72: 'q', 74: 'w', 76: 'e', 77: 'r', 79: 't', 81: 'y', 83: 'u',
        84: 'q', 86: 'w', 88: 'e', 89: 'r', 91: 't', 93: 'y', 95: 'u'}

root = tkinter.Tk()
root.withdraw()
filepath = filedialog.askopenfilename()

speed = str(input("Input play speed(x) (default: 1.0)"))
if speed == "":
    speed = float(1)
else:
    speed = float(speed)

class MyMidiFile(mido.MidiFile):
    
    def play(self, meta_messages=False, speed=1):
        start_time = time.time()
        input_time = 0.0

        for msg in self:
            input_time += msg.time / speed

            playback_time = time.time() - start_time
            duration_to_next_event = input_time - playback_time

            if duration_to_next_event > 0.0:
                time.sleep(duration_to_next_event)

            if isinstance(msg, mido.MetaMessage) and not meta_messages:
                continue
            else:
                yield msg

try:
    mid = MyMidiFile(filepath)
except:
    print("The file error")
    quit()

tracks = []
type = ['note_on','note_off']
for i,track in enumerate(mid.tracks):
    print(f'Track {i}')
    for msg in track:
        info = msg.dict()
        if (info['type'] in type):
            if info['type'] == 'note_on':
                tracks.append(info)

shift = 0
while shift == 0:
    auto_tune = input("Turn on automatic transposition ? (0/1) (default: 0)")
    if auto_tune == "1":
        shift, score = util.get_shift_best_match(tracks)
        print("Transposition: ", shift)
        print("Hit: ", f'{score:.2%}')
        break
    elif auto_tune == "0" or auto_tune == "":
        shift = 0
        break

sleep_time = str(input("Sleep time(s) (default: 2)"))
if sleep_time == "":
    sleep_time = int(2)
else:
    sleep_time = int(sleep_time)
print("Play will be start in " + str(sleep_time) + " seconds")
time.sleep(sleep_time)

for msg in mid.play(speed=speed):
    if msg.type == 'note_on':
        if msg.note+shift in keys:
            pydirectinput.press(keys[msg.note+shift])

print("Play ends")
