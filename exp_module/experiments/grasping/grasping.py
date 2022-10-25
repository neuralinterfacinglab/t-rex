import tkinter as  tk
from pylsl import StreamInfo, StreamOutlet
import csv, random


EXP_END = 'End of experiment'
EXP_PRESS_TO_START = 'Press <spacebar> to begin'

class singleWordsGui:
    numTrials = 5
    durationWords= 3
    durationCross= 0 

    def __init__(self, master, words):
        self.root = master
        self.words = words

        #Layout
        self.width = self.root.winfo_screenwidth() * 2 / 3
        self.height =self.root.winfo_screenheight() * 2 / 3
        self.root.geometry('%dx%d+0+0' % (self.width, self.height))
        self.root.title("Single Words")
        #Initialize LSL
        info = StreamInfo('SingleWordsMarkerStream', 'Markers', 1, 0, 'string', 'emuidw22')
        # next make an outlet
        self.outlet = StreamOutlet(info)

        self.label = tk.Label(font=('Helvetica bold', 22)) #, background='gray'
        self.lblVar = tk.StringVar()
        self.label.configure(textvariable=self.lblVar)
        self.lblVar.set(EXP_PRESS_TO_START)
        self.label.pack(expand=1)
        

        self.root.bind('<space>', self.run)

    def run(self, event):
        self.root.unbind('<space>')
        self.outlet.push_sample(['experimentStarted'])
        self.root.after(0, self.trial)


    def trial(self):
        self.label.pack(expand=1)
        self.root.update_idletasks()
        if len(self.words)==0 or self.numTrials==0:
            self.root.after(0,self.end)
        else:
            self.numTrials= self.numTrials-1
            word = self.words.pop(0)
            self.outlet.push_sample(['start;' +  word])
            self.lblVar.set(word)
            self.root.update_idletasks()
            self.root.after(self.durationWords * 1000)
            self.outlet.push_sample(['end;' +  word])
            self.root.after(self.durationCross * 1000, self.trial)
            self.root.update_idletasks()

    def end(self):
        self.outlet.push_sample(['experimentEnded'])
        self.lblVar.set(EXP_END)
        self.root.update_idletasks()


def getWords(filename):
    with open(filename, newline='') as file:
        words = [line.rstrip('\n') for line in file]
    return words

def genWords(words, times, filename):
    words_to_write = words * times
    with open(filename, 'w') as f:
        for word in words_to_write:
            f.write(word + '\n')

def start():
    filename = 'exp_module\\experiments\\grasping\\wordsOpenClose.txt'
    genWords(['Open', 'Close'], 2, filename)
    words = getWords(filename)
    root = tk.Tk()
    my_gui = singleWordsGui(root,words)
    root.wm_attributes("-topmost", True)
    root.mainloop()

if __name__=='__main__':
    start()