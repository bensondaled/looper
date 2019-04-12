## rtaudio testing
import time
import rtaudio as rt
import struct
import numpy as np
import matplotlib.pyplot as pl
pl.ion()

class Player():
    def __init__(self):
        output_device = 'Apple Inc.: Built-in Output'
        output_device_idx = None

        dac = rt.RtAudio()
        n_devices = dac.getDeviceCount()
        for i in range(n_devices):
            info = dac.getDeviceInfo(i)
            #print(info)
            if info['name'] == output_device:
                output_device_idx = i
        
        self.buffer_size = 256

        oParams = {'deviceId': output_device_idx, 'nChannels': 2, 'firstChannel': 0}
        dac.openStream(oParams, {}, 44100, self.buffer_size, self.callback)
        dac.startStream()

        self._idx = 0

        t0 = time.time()
        while True:
            if time.time() - t0 > 2:
                break
        
        try:
            dac.stopStream()
        except:
            pass
        if dac.isStreamOpen():
            dac.closeStream()

    def callback(self, out_buffer, *args):
        for i in range(self.buffer_size):
            samp = np.sin(2*np.pi*440*self._idx/44100)
            struct.pack_into('f', out_buffer, 4*i, samp)
            self._idx += 1

class Recorder():
    def __init__(self):
        input_device = 'Apple Inc.: Built-in Microphone'

        dac = rt.RtAudio()
        input_device_idx = None
        n_devices = dac.getDeviceCount()
        for i in range(n_devices):
            info = dac.getDeviceInfo(i)
            #print(info)
            if info['name'] == input_device:
                input_device_idx = i
        print(input_device_idx)

        self.buffer_size = 512

        oParams = {'deviceId': input_device_idx, 'nChannels': 1, 'firstChannel': 0}
        dac.openStream({}, oParams, 48000, self.buffer_size, self.callback)
        dac.startStream()

        self.data = []

        t0 = time.time()
        while True:
            if time.time() - t0 > 2:
                break
        
        try:
            dac.stopStream()
        except:
            pass
        if dac.isStreamOpen():
            dac.closeStream()

    def callback(self, rw_buffer, r_buffer):
        #rw = rw_buffer[:]
        #r = r_buffer[:]
        
        n_frames = int(len(r_buffer) / 4)
        r = struct.unpack(n_frames*'f', r_buffer)
        self.data.append(r)

if __name__ == '__main__':
    #r = Recorder()
    #d = np.array(r.data, dtype=np.float32)
    #np.save('test', d.ravel())

    p = Player()
##
