from __future__ import print_function
import ctypes
import time
import pydirectinput
import mido
from future.types.newbytes import unicode

import util
import tkinter
import sys
import os
from threading import Thread
from pynput.keyboard import Listener, Key
from tkinter import filedialog

pydirectinput.PAUSE = 0
keys = util.mapping


class Play(Thread):
    Exit = False
    go = False
    speed = 1.0

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        while not self.Exit:
            root = tkinter.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename()

            try:
                mid = mido.MidiFile(filepath)
            except:
                print("file error")
                os._exit(0)

            messages = []
            node_type = ['note_on', 'note_off']
            for i, track in enumerate(mid.tracks):
                print(f'Track {i}')
                for msg in track:
                    info = msg.dict()
                    if info['type'] in node_type:
                        if info['type'] == 'note_on':
                            messages.append(info)

            speed = str(input("Input play speed(x) (default: 1.0)"))
            if speed == "":
                self.speed = float(1.0)
            else:
                self.speed = float(speed)

            shift = 0
            while shift == 0:
                auto_tune = input("Turn on automatic transposition ? (0/1) (default: 0)")
                if auto_tune == "1":
                    shift, score = util.get_shift_best_match(messages)
                    print("Transposition: ", shift)
                    print("Hit: ", f'{score:.2%}')
                    break
                elif auto_tune == "0" or auto_tune == "":
                    shift = 0
                    break

            print()
            print("Please press \"Space\" to start playback")
            print()
            print("Please press \"Tab\" to stop playback")
            print()
            print("Please press \"Shift\" to stop playback and reselect the file")
            print()
            print("Press ↑ to speed up 0.1x")
            print()
            print("Press ↓ to speed down 0.1x")
            print()

            while True:
                if self.go:
                    break

            start_time = time.time()
            input_time = 0.0
            for msg in mid:
                if not self.go:
                    break

                input_time += msg.time / self.speed

                playback_time = time.time() - start_time
                duration_to_next_event = input_time - playback_time

                if duration_to_next_event > 0.0:
                    time.sleep(duration_to_next_event)

                if msg.type == 'note_on' and msg.note + shift in keys:
                    pydirectinput.press(keys[msg.note + shift])
            print("Play ends")
            self.go = False


def main():
    playing = Play()
    playing.start()

    def onRelease(key):
        if key == Key.space:
            playing.go = True
        elif key == Key.shift:
            playing.go = False
        elif key == Key.up:
            playing.speed += 0.1
            print("Playback speed is", f'{playing.speed:.1f}')
            print()
        elif key == Key.down:
            playing.speed -= 0.1
            print("Playback speed is", f'{playing.speed:.1f}')
            print()
        elif key == Key.tab:
            playing.go = False
            playing.Exit = True
            sys.exit(0)

    with Listener(
            on_press=(),
            on_release=onRelease
    ) as listener:
        listener.join()


if __name__ == '__main__':
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


