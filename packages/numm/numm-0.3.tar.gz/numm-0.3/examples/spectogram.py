import numpy as np
idx = 0
recent_audio = np.zeros(4096, np.int16)
recent_video = np.zeros((240,320,3), np.uint8)
freq_bins = np.exp2(np.linspace(np.log2(27000),np.log2(27),240))

def get_freq(fourier, frequency):
    freqs = np.fft.fftfreq(len(fourier), 1/44100.0)
    nearest = (abs(freqs - frequency)).argmin()
    return abs(fourier[nearest])

def video_out(a):
    global idx
    fourier=np.fft.fft(recent_audio)
    values =np.array([get_freq(fourier,X) for X in freq_bins])
    recent_video[:,idx,1] = (values/10000).clip(0,255)
    idx = (idx + 1) % a.shape[1]
    a[:] = np.roll(recent_video, -idx, axis=1)

def audio_in(a):
    recent_audio[:] = np.roll(recent_audio, -len(a))
    recent_audio[:len(a)] = a.mean(axis=1)
