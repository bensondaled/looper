##
from soup.getch import Getch
import rtmidi

class GetchInterface():
    def __init__(self, output_port_name='getch'):
        self.output_port_name = output_port_name
        self.exit_key = 'q'
        self.channel = 10
        self.velocity = 120
        
        # setup midi output
        self.out = rtmidi.RtMidiOut()
        self.out.openVirtualPort(self.output_port_name)

        self.key_mappings = {
                                'c': 5,
                                'r': 4,
                                't': 42,
                                'a': 36,
                                's': 37,
                                'd': 38,
                                'f': 39,
                                'g': 40,
                                'h': 41,
                                'j': 42,
                                'k': 43,
                                'l': 44,
                            }

        self.getch = Getch()

    def is_note(self, key):
        return key in self.key_mappings.keys()

    def play_note(self, key):
        note = self.key_mappings[key]
        msg_on = rtmidi.MidiMessage().noteOn(self.channel, note, self.velocity)
        msg_off = rtmidi.MidiMessage().noteOff(self.channel, note)
        self.out.sendMessage(msg_on)
        self.out.sendMessage(msg_off)

    def run(self):
        while True:
            key = self.getch()

            if self.is_note(key):
                self.play_note(key)

            elif key == self.exit_key:
                break

##
if __name__ == '__main__':
    gi = GetchInterface()
    gi.run()

##
