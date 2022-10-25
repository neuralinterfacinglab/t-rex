import numpy as np

def readHeader(fid):
    info={}
    fid.seek(175)
    headerType=np.fromfile(fid,dtype=np.uint8,count=0)#int.from_bytes(fid.read(1),byteorder='big')
    if headerType!=4:
        raise Exception('Invalid header!')
    fid.seek(138)
    info['dataStartOffset'] = np.fromfile(fid,dtype=np.uint32,count=1)[0]
    info['numChan'], info['multiplexer'], info['rateMin'], info['bytes']= np.fromfile(fid,dtype=np.uint16,count=4)
    datTypes={1:np.uint8,2:np.uint16,4:np.uint32}
    info['dtype']=datTypes[info['bytes']]
    fid.seek(400+8)
    info['triggerArea'], info['triggerAreaLength']= np.fromfile(fid,dtype=np.uint32,count=2)
    fid.seek(0,2)
    eof = fid.tell()
    info['fileLength'] = eof-info['dataStartOffset']
    elec = getElectrodeInfo(fid,0,info['numChan'])
    info['sr'] = elec['rate_coef'] * info['rateMin']
    channelSR=[]
    channelNames=[]
    refs=[]
    electrodes=[]
    for c in range(info['numChan']):
        elec=getElectrodeInfo(fid,c,info['numChan'])
        channelNames.append(elec['pos_input'])
        refs.append(elec['neg_input'])
        channelSR.append(elec['rate_coef']* info['rateMin'])
        electrodes.append(elec)
    info['channelSR']=channelSR
    info['channelNames'] = channelNames
    info['References'] = refs
    return info,electrodes

def convertSI(data, electrodes):
    if len(electrodes)!=data.shape[1]:
        raise Exception('Electrode descriptions do not match data shape')
    #Scale data to SI units
    for chan in range(data.shape[1]):
        cElec=electrodes[chan]
        data[:,chan] = - ((data[:,chan] - cElec['logical_ground'] ) / (cElec['logical_max'] - cElec['logical_min']+1)) * (cElec['physical_max'] - cElec['physical_min'])
        if type(cElec['measurement_unit'])!=str:
            data[:,chan] = data[:,chan] * cElec['measurement_unit']
    return data
    
    
def getElectrodeInfo(fid,c,numChannels):
    electrode={}
    fid.seek(192+8)
    electrodeArea = np.fromfile(fid,dtype=np.uint32,count=1)[0]
    fid.seek(176+8)
    codeArea = np.fromfile(fid,dtype=np.uint32,count=1)[0]
    fid.seek(codeArea)
    code=np.fromfile(fid,dtype=np.uint16,count=numChannels)
    electrode['chanRecord'] = code[c]
    fid.seek(electrodeArea+code[c]*128+2)
    electrode['pos_input'] = ''.join([chr(char) for char in np.fromfile(fid,dtype=np.uint8,count=6) if char!=0])
    electrode['neg_input'] = ''.join([chr(char) for char in np.fromfile(fid,dtype=np.uint8,count=6) if char!=0])
    electrode['logical_min'], electrode['logical_max'],electrode['logical_ground'],electrode['physical_min'],electrode['physical_max'] = np.fromfile(fid,dtype=np.int32,count=5)
    unit = np.fromfile(fid,dtype=np.int16,count=1)[0]
    measurement_units={-1:1e-9,0:1e-6,1:1e-3,2:1,100:'percent',101:'bpm',102:'Adim'}
    electrode['measurement_unit']= measurement_units[unit]
    fid.seek(8,1)
    electrode['rate_coef']=np.fromfile(fid,dtype=np.uint16,count=1)[0]
    return electrode


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fileName = r'C:\data\tcp.TRC'
    with open(fileName,'rb') as fid:
        info, electrodes = readHeader(fid)
        # Read & prep trigger area data
        print(info['triggerArea'],info['dataStartOffset'])
        fid.seek(info['triggerArea'])
        trigger=np.ones((2,int(info['triggerAreaLength']/6)))
        for i in range(int(info['triggerAreaLength']/6)):
            trigger[0,i]=np.fromfile(fid,dtype=np.uint32,count=1)[0]
            trigger[1,i]=np.fromfile(fid,dtype=np.int16,count=1)[0]
            if trigger[0,i]>info['fileLength']/info['numChan']/info['bytes']:
                trigger=trigger[:,:i]
                break

        # Load Data
        fid.seek(info['dataStartOffset'])
        tracedata = np.fromfile(fid,info['dtype'])
        tracedata = tracedata.reshape((int(tracedata.shape[0]/info['numChan']),info['numChan']))
        tracedata = tracedata.astype('float')
        tracedata = convertSI(tracedata, electrodes)
        plt.plot(tracedata[:,0])
        plt.show()
        