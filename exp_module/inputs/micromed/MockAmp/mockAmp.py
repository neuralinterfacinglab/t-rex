"""
Script to mimick the behaviour of System Evolution in streaming out data.
"""
__author__ = "Christian Herff"
__date__    = "25.03.2019"

import socket
import time

from readTRCFile import getElectrodeInfo,readHeader
# fileName = 'EEG_18.TRC'
fileName = 'EEG_496790.TRC'
filePath = '../data/'
fileName = '%s%s' % (filePath, fileName)
#fileName = 'C:/data/EEG_496790.TRC'
HOST, PORT = "localhost", 8000

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    fid = open(fileName,'rb')
except:
    try:
        # new_path = '../Micromed/data/EEG_18.TRC'
        new_path = '../Micromed/data/EEG_496790.TRC'
        fid = open(new_path, 'rb')
    except:
        print("can't find TRC at {}".format(new_path))

info, electrodes = readHeader(fid)
try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    #sock.sendall(bytes(data + "\n", "utf-8"))
    fid.seek(0)
    headerSize = info['triggerArea']
    packetHeader=bytes('MICM',"utf-8") + (0).to_bytes(2,byteorder='little') +  int(headerSize).to_bytes(8, byteorder='little')
    header = fid.read(headerSize)
    sock.sendall(packetHeader + header)
    #sock.sendall(header)
    # sock.sendall(fid.read(headerSize)) # info['triggerArea']
    print('Header sent')
    #Continuous mode
    # block mode is  (int(info['numChan']) * int(info['bytes']) * numSamples)
    numSamples=int(info['sr']/16)
    packetHeader = bytes('MICM',"utf-8") + (1).to_bytes(2,byteorder='little') + (  (int(info['numChan']) * int(info['bytes']) * numSamples)).to_bytes(4, byteorder='little')
    fid.seek(info['dataStartOffset'])
    buff=fid.read(info['bytes'] * info['numChan'] * numSamples)
    sock.sendall(packetHeader + buff)
    buff=fid.read(info['bytes'] * info['numChan'] * numSamples)
    print('Started MockAmp.')
    while buff!='':
        time.sleep(1/8) # TODO: Change back to 1/16
        sock.sendall(packetHeader + buff)
        buff=fid.read(info['bytes'] * info['numChan']* numSamples)
        if len(buff)<numSamples*info['bytes']*info['numChan']:
            break
        print('.', end='', flush=True)
    print('Done')
    # Receive data from the server and shut down
    #received = str(sock.recv(1024), "utf-8")
finally:
    sock.close()


fid.close()