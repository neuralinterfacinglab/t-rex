"""Module to interpret Micromed header and data"""
__author__  = "Christian Herff"
__date__    = "25.03.2019"
import numpy as np

def convertSI(data, electrodes):
    if len(electrodes)!=data.shape[1]:
        raise Exception('Electrode descriptions do not match data shape')
    #Scale data to SI units
    siData = np.zeros(data.shape)
    data = data.astype('int')
    for chan in range(data.shape[1]):
        cElec=electrodes[chan]
        # Should there be a minus here?
        siData[:,chan] = ((data[:,chan] - cElec['logical_ground'] ) / (cElec['logical_max'] - cElec['logical_min']+1)) * (cElec['physical_max'] - cElec['physical_min'])
        #if type(cElec['measurement_unit'])!=str:
        #    siData[:,chan] = siData[:,chan] * cElec['measurement_unit']
    return siData

def getElectrodeInfo(bArr,c,numChannels):
    electrode={}
    #bArr.seek(192+8)
    electrodeArea = np.frombuffer(bArr,dtype=np.uint32,count=1,offset=200)[0]
    #bArr.seek(176+8)
    codeArea = np.frombuffer(bArr,dtype=np.uint32,count=1,offset=184)[0]
    #bArr.seek(codeArea)
    code=np.frombuffer(bArr,dtype=np.uint16,count=numChannels,offset=codeArea)
    electrode['chanRecord'] = code[c]
    #bArr.seek(electrodeArea+code[c]*128+2)
    offS = electrodeArea+code[c]*128+2
    electrode['pos_input'] = ''.join([chr(char) for char in np.frombuffer(bArr,dtype=np.uint8,count=6,offset=offS) if char!=0])
    electrode['neg_input'] = ''.join([chr(char) for char in np.frombuffer(bArr,dtype=np.uint8,count=6, offset=offS+6) if char!=0])
    electrode['logical_min'], electrode['logical_max'],electrode['logical_ground'],electrode['physical_min'],electrode['physical_max'] = np.frombuffer(bArr,dtype=np.int32,count=5,offset=offS+12)
    unit = np.frombuffer(bArr,dtype=np.int16,count=1,offset=offS+32)[0]
    measurement_units={-1:1e-9,0:1e-6,1:1e-3,2:1,100:'percent',101:'bpm',102:'Adim'}
    electrode['measurement_unit']= measurement_units[unit]
    #bArr.seek(8,1)
    electrode['rate_coef']=np.frombuffer(bArr,dtype=np.uint16,count=1,offset=offS+34+8)[0]
    return electrode

def readHeader(bArr):
    info={}
    #bArr.seek(175)
    headerType=np.frombuffer(bArr,dtype=np.uint8,count=0,offset=175)#int.from_bytes(bArr.read(1),byteorder='big')
    if headerType!=4:
        raise Exception('Invalid header!')
    #bArr.seek(138)
    info['dataStartOffset'] = np.frombuffer(bArr,dtype=np.uint32,count=1,offset=138)[0]
    info['numChan'], info['multiplexer'], info['rateMin'], info['bytes']= np.frombuffer(bArr,dtype=np.uint16,count=4,offset=138+4)
    datTypes={1:np.uint8,2:np.uint16,4:np.uint32}
    info['dtype']=datTypes[info['bytes']]
    #bArr.seek(400+8)
    info['triggerArea'], info['triggerAreaLength']= np.frombuffer(bArr,dtype=np.uint32,count=2,offset=408)
    #bArr.seek(0,2)
    #eof = bArr.tell()
    #info['fileLength'] = eof-info['dataStartOffset']
    elec = getElectrodeInfo(bArr,0,info['numChan'])
    info['sr'] = elec['rate_coef'] * info['rateMin']
    channelSR=[]
    channelNames=[]
    refs=[]
    electrodes=[]
    for c in range(info['numChan']):
        elec=getElectrodeInfo(bArr,c,info['numChan'])
        channelNames.append(elec['pos_input'])
        refs.append(elec['neg_input'])
        channelSR.append(elec['rate_coef']* info['rateMin'])
        electrodes.append(elec)
    info['channelSR']=channelSR
    info['channelNames'] = channelNames
    info['References'] = refs
    return info,electrodes