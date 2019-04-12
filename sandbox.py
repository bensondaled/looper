
## test setups
'''
controller_name = 'MPK Mini Mk II'
output_port_name = 'test_port'
channel = 10
velocity = 120

notes = {   'h': 42,
            'k': 36,
            's': 38
        }

# setup input
inn = rtmidi.RtMidiIn()
port_names = [inn.getPortName(i) for i in range(inn.getPortCount())]
port_idx = port_names.index(controller_name)
inn.openPort(port_idx)

# setup output
out = rtmidi.RtMidiOut()
out.openVirtualPort(output_port_name)
'''

## midi controller loop

while True:
    msg = inn.getMessage(1)
    if msg is not None:
        #print(msg)
        out.sendMessage(msg)

## computer keyboard loop

def send_note(note):
    msg_on = rtmidi.MidiMessage().noteOn(channel, note, velocity)
    msg_off = rtmidi.MidiMessage().noteOff(channel, note)
    out.sendMessage(msg_on)
    out.sendMessage(msg_off)

getch = Getch()
while True:
    key = getch()
    note = notes.get(key, None)
    if note:
        print(key)
        send_note(note)


