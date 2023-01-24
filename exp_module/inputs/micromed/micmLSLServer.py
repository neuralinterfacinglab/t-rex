"""Python server to stream out Micromed Amplifier data
 from System Evolution via Labstreaming Layer.
"""
__author__ = "Christian Herff"
__date__    = "25.03.2019"

# Builtin
import socketserver # Builtin   

# 3rd party
import numpy as np 
from pylsl import StreamInfo, StreamOutlet

# Local
from micromed import readHeader, convertSI

HEADER = 0
BODY = 1

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for the server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    electrodes = []
    header=[]

    def initLSL(self, header,electrodes):
        """ Initializes the Labstreaming Layer outlet with the Micromed Header information"""
        info = StreamInfo('Micromed', 'EEG', int(self.header['numChan']),int(self.header['sr']), 'float32', 'micm01')
        
        # append some meta-data
        info.desc().append_child_value("manufacturer", "Micromed")
        channels = info.desc().append_child("channels")
        for c in header['channelNames']:
            channels.append_child("channel") \
                .append_child_value("label", c) \
                .append_child_value("unit", "microvolts") \
                .append_child_value("type", "EEG")

        # next make an outlet
        self.outlet = StreamOutlet(info)

    def processData(self,data):
        """ Process one package of trace data and push it to the LSL outlet """
        # Package = 8 bytes
        tracedata = np.frombuffer(data,self.header['dtype'])
        tracedata = tracedata.reshape((int(tracedata.shape[0]/self.header['numChan']), self.header['numChan']))
        tracedata = convertSI(tracedata, self.electrodes).astype('float32')
        # Returns data in microvolts not actual SI
        self.outlet.push_chunk(tracedata)

    def processHeader(self, header, electrodes):
        """ Process one package of trace data and push it to the LSL outlet """
        # Header = 16 bytes
        self.header = header
        self.electrodes = electrodes
        self.initLSL(header,electrodes)
        

    def handle(self):
        # self.request is the TCP socket connected to the client

        package=' '
        while package!=b'':
            package = self.request.recv(14)
            fixCode = package[:4].decode("utf-8"); datType=int.from_bytes(package[4:6],byteorder='little');

            if datType==HEADER:
                size=int.from_bytes(package[6:14],byteorder='little')
                data = data=package[14:]
            elif datType==BODY:
                size=int.from_bytes(package[6:10],byteorder='little')
                data = data=package[10:]

            #print('header reads %s %d %d' %(  fixCode,datType,size))
            if fixCode!='MICM':
                print('Warning: Recieved broken fixCode %s' % fixCode)
                break
                #raise Exception('Unknown TCP package')]
            while len(data)<size:
                package = self.request.recv(min(4096,size-len(data)))
                data = data + package
            
            if datType==HEADER:
                header, electrodes = readHeader(bytearray(data))
                self.processHeader(header,electrodes)
                print('Got a header package of %d bytes' % len(data))
                print('%d channels sampled at %d Hz. Data is %s with %d bytes. ' % (self.header['numChan'],self.header['sr'],  self.header['dtype'],self.header['bytes']))
                #print('Got multiplex of %d' % (self.header['multiplexer']))

            elif datType==BODY:
                self.processData(bytearray(data))
                #print('Got a trace package of %d bytes' % len(data))
               

if __name__ == "__main__":
    HOST, PORT = "localhost", 8000
    #HOST, PORT = "10.99.63.19", 5000
    
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler) # Connect to host and handler object

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print('Running...', flush=True)
    server.serve_forever() # Forevers call the handle() method from handler object on (HOST, PORT)

    # 1) Recieve data from a TCP stream (coming from the micromed machine)
    # 2) Process the data to a format LSL can handle
    # 3) Stream this data out using LSL.StreamOutlet (See initLSL())