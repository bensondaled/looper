##
import time
import rtmidi

class Looper():
    def __init__(self,
                 controller_name='MPK Mini Mk II'
                 ):

        # settings
        self.rec_toggle_note = 4
        self.channel_toggle_note = 5
        self.controller_name = controller_name
        self.output_port_name = 'test_port'
        self.max_channel = 16

        # setup midi input
        self.inn = rtmidi.RtMidiIn()
        self.port_names = [self.inn.getPortName(i) for i in \
                range(self.inn.getPortCount())]
        self.input_port_idx = self.port_names.index(self.controller_name)
        self.inn.openPort(self.input_port_idx)

        # setup midi output
        self.out = rtmidi.RtMidiOut()
        self.out.openVirtualPort(self.output_port_name)

        # runtime
        self.recording = False
        self._channel = 1
        self.playback_t0 = time.time()
        self.recording_t0 = time.time()
        self.loop_duration = None
        self.buffers = []
        self.buffer_idxs = []

    def is_rec_toggle(self, note, on_only=False):
        is_note = note.getNoteNumber()==self.rec_toggle_note
        is_on_or_off = note.isNoteOnOrOff()
        is_on = note.isNoteOn()
        if on_only:
            return is_note and is_on
        else:
            return is_note and is_on_or_off
    
    def is_channel_toggle(self, note, on_only=False):
        is_note = note.getNoteNumber()==self.channel_toggle_note
        is_on_or_off = note.isNoteOnOrOff()
        is_on = note.isNoteOn()
        if on_only:
            return is_note and is_on
        else:
            return is_note and is_on_or_off

    def refresh_playback(self):
        if self.loop_duration is not None and self.playback_dt > self.loop_duration:
            self.playback_t0 = time.time()
            self.playback_dt = 0
            self.buffer_idxs = [0 for _ in self.buffer_idxs]

    def toggle_recording(self):
        self.recording = not self.recording
        print(f'Recording: {self.recording}')

        # if toggle caused us to start recording
        if self.recording:
            self.recording_t0 = time.time()
            self.recording_dt = 0
        
            # add a new buffer for this recording
            self.buffers.append([])
            self.buffer_idxs.append(0)

        # if toggle caused us to stop recording
        elif not self.recording:

            if self.loop_duration is None:
                # this was the end of the first loop, store the duration
                self.loop_duration = self.recording_dt
                self.playback_t0 = time.time()
                self.playback_dt = 0

    def toggle_channel(self):
        self._channel += 1
        if self._channel > self.max_channel:
            self._channel = 1
        print(f'Now on channel {self._channel}')

    def process_message(self, msg):
        msg.setChannel(self._channel)
        return msg

    def update_buffer(self, msg):
        if self.recording and not self.is_rec_toggle(msg):
            self.buffers[-1].append([self.recording_dt, msg])

    def playback(self):

        # run through all buffers (one per recording made)
        for idx, buf in enumerate(self.buffers):
            
            # skip the most recent buffer if we're still recording into it
            if self.recording and idx == len(self.buffers) - 1:
                break

            # retrieve all notes in this buffer that should be played now
            while True:
                candidate_idx = self.buffer_idxs[idx]

                if candidate_idx >= len(buf):
                    break # already finished all notes in this buffer for this loop

                candidate_time, candidate_msg = buf[candidate_idx]

                if self.playback_dt >= candidate_time:
                    # the time has come for the next note
                    self.out.sendMessage(candidate_msg)
                    self.buffer_idxs[idx] += 1
                else:
                    # the time is not yet here for the next note, maybe next time
                    break

    def run(self):
        
        # main loop
        while True:

            # compute elapsed time
            self.playback_dt = time.time() - self.playback_t0
            self.recording_dt = time.time() - self.recording_t0

            # if at end of playback loop, start from beginning
            self.refresh_playback()

            # playback any recorded messages from the buffer
            self.playback()

            # query for incoming message
            msg = self.inn.getMessage(1)
            
            # process received message
            if msg is not None:

                msg = self.process_message(msg)

                # process toggle for recording
                if self.is_rec_toggle(msg, on_only=True):
                    self.toggle_recording()
                
                # process toggle for channel
                if self.is_channel_toggle(msg, on_only=True):
                    self.toggle_channel()
                
                # otherwise always play out the received note
                else:
                    self.out.sendMessage(msg)

                # if in recording mode, add note to the buffer
                self.update_buffer(msg)

    def end(self):
        self.out.closePort()
        self.inn.closePort()

##
if __name__ == '__main__':
    looper = Looper()
    looper.run()

##
