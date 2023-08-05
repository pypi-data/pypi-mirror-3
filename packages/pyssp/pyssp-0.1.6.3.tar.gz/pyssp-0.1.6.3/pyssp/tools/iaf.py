#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy as sp
import sys
import wave
import tempfile
from pyssp.util import read_signal,get_frame,add_signal,compute_avgpowerspectrum,write_signal
from pyssp.voice_enhancement import SupectralSubtruction,MMSE_STSA,JointMap,MMSE_LogSTSA
from pyssp.noise_estimation import MinimumStatistics
from pyssp.vad.ltsd import LTSD
import optparse

def vad(vas,signal,winsize,window):
    out=sp.zeros(len(signal),sp.float32)
    for va in vas:
        for i in range(va[0],va[1]+2):
            add_signal(out,get_frame(signal, winsize, i)*window,winsize,i)
    return out

def noise_reduction(signal,params,winsize,window,ss,ntime):
    out=sp.zeros(len(signal),sp.float32)
    nf = len(signal)/(winsize/2) - 1

    ms = MinimumStatistics(winsize,window,params[2])
    NP_lambda = compute_avgpowerspectrum(signal[0:winsize*int(params[2] /float(winsize)/(1000.0/ntime))],winsize,window)
    ms.init_noise_profile(NP_lambda)
    forward_enoise=[None]*nf
    for no in xrange(nf):
        frame = get_frame(signal, winsize, no)
        forward_enoise[no]=ms.compute(frame,no)
        
    ms2 = MinimumStatistics(winsize,window,params[2])        
    NP_lambda2 = compute_avgpowerspectrum(signal[len(signal)-winsize*int(params[2] /float(winsize)/(1000.0/ntime)):],winsize,window)
    ms2.init_noise_profile(NP_lambda2)
    backward_enoise=[None]*nf
    for no in reversed(range(nf)):
        frame = get_frame(signal, winsize, no)
        backward_enoise[no]=ms2.compute(frame,no)
        
    for no in xrange(nf):
        frame = get_frame(signal, winsize, no)
        n_pow = (forward_enoise[no]+backward_enoise[no])/2.0
        res = ss.compute_by_noise_pow(frame,n_pow)
        add_signal(out, res,  winsize, no)
    return out

def write(param,signal):
    st = tempfile.TemporaryFile()
    wf=wave.open(st,'wb')
    wf.setparams(params)
    s=sp.int16(signal*32767.0).tostring()
    wf.writeframes(s)
    st.seek(0)
    print st.read()

def read(fname,winsize):
    if fname =="-":
        wf=wave.open(sys.stdin,'rb')
        n=wf.getnframes()
        str=wf.readframes(n)
        params = ((wf.getnchannels(), wf.getsampwidth(),
                   wf.getframerate(), wf.getnframes(),
                   wf.getcomptype(), wf.getcompname()))
        siglen=((int )(len(str)/2/winsize) + 1) * winsize
        signal=sp.zeros(siglen, sp.float32)
        signal[0:len(str)/2] = sp.float32(sp.fromstring(str,sp.int16))/32767.0
        return signal,params
    else:
        return read_signal(fname,winsize)


if __name__=="__main__":
    parser = optparse.OptionParser(usage="%prog [-m METHOD] [-w WINSIZE] [- s NOISETIME(ms)] [-t LTSD_THREASHOLD] INPUTFILE OUTPUTFILE\n method 0 : SupectralSubtruction\n        1 : MMSE_STSA\n        2 : MMSE_LogSTSA\n        3 : JointMap\n if INPUTFILE is \"-\", read wave data from stdin")

    parser.add_option("-w", type="int", dest="winsize", default=1024)
    parser.add_option("-m", type="int", dest="method", default=0)
    parser.add_option("-s", type="int", dest="ntime", default=300)
    parser.add_option("-t", type="int", dest="th", default=25)
    (options, args) = parser.parse_args()

    if len(args)!=2:
        parser.print_help()
        exit(2)

    fname = args[0]
    oname = args[1]
    signal, params = read(fname,options.winsize)

    window = sp.hanning(options.winsize)
    import os.path
    
    root,ext = os.path.splitext(args[0])
    if options.method==0:
        ss = SupectralSubtruction(options.winsize,window)
    elif options.method==1:
        ss = MMSE_STSA(options.winsize,window)
    elif options.method==2:
        ss = MMSE_LogSTSA(options.winsize,window,alpha=0.99)
    elif options.method==3:
        ss = JointMap(options.winsize,window,alpha=0.99)

    if params[0]==1:
        n_signal = noise_reduction(signal,params,options.winsize,window,ss,options.ntime)
        ltsd = LTSD(options.winsize,window,5,lambda0=options.th)
        res,ltsds =  ltsd.compute_with_noise(n_signal,n_signal[0:options.winsize*int(params[2] /float(options.winsize)/(1000.0/options.ntime))])#maybe 300ms
        write_signal(oname,params, vad(res,n_signal,options.winsize,window))
        for x in res:
            print ",".join([str(i) for i in x])
    elif params[0]==2:
        write(params, signal,oname)
