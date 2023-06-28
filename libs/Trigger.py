from time import sleep
from serial import Serial
from serial.tools import list_ports

from pylsl import StreamInfo, StreamOutlet

from libs.utils import get_main_dir_from_config_file
from libs.utils import load_data_from_yaml

STREAM_INFO = ('TriggerSequence', 'Markers', 1, 0, 'string', 'triggersync')

class Trigger():


    def __init__(self, is_active: bool, logger=False):
        self.port = None
        self.outlet = None
        self.is_active = is_active
        self.logger = logger
        
        self.serial_com_name = None
        self.sequence = []

        self.load_config()

    def load_config(self):
        ''' Loads trigger info in main config

        Args
        ----------

        Returns
        ----------
        '''

        main_dir = get_main_dir_from_config_file()
        config = load_data_from_yaml(main_dir/'resources'/'config.yaml')
        
        if not 'trigger' in config:
            msg = 'No trigger header defined in main config.'
            self.logger.error(msg)
            raise KeyError(msg)

        try:
            self.serial_com_name = config['trigger']['serial_com_name']
            self.sequence = config['trigger']['sequence']

        except Exception as e:
            msg = 'Failed parsing trigger info from main config. Make sure to have the following form:\ntrigger:\n  serial_com_name: str\n  sequence: list[binary int]'
            self.logger.error(msg)
            raise e
        
    def connect_to_port(self):
        ''' Connects to port based on name as 
            listed in main config.

        Args
        ----------

        Returns
        ----------
        '''

        if not self.port:
            port_info = self.get_port_by_attr('description', self.serial_com_name)
        
        self.port = Serial(port_info.device)
        self.port.timeout=1
        self.port.setDTR(False)
        
        if not self.port.is_open:
            self.port.open()

        if self.logger:
            self.logger.info(f'Connected to trigger device: {port_info.device}')


    def get_port_by_attr(self, attr, value):
        ''' Search for port based on key value pairs

        Args
        ----------
        attr: str
            COM port instance attribute name
        value: any
            value to match of COM port attribute

        Returns
        ----------
        port: Port instance
            matched port
        '''

        ports = list_ports.comports()
        port = [p for p in ports if value in getattr(p, attr)]
        
        if not port:
            msg = f'No ports exist with {attr} = {value}'
            self.logger.error(msg)
            raise AttributeError(msg)
        elif len(port) > 1:
            self.logger.warning(f'Multiple ports found, using port: {port[0].description}') 
        
        return port[0]

    def setup_lsl(self, info=STREAM_INFO):
        ''' setup stream to send trigger sequence to

        Args
        ----------
        info = tuple(str, str, int, int, str, str)
            tuple with args required to StreamInfo object

        Returns
        ----------
        '''

        info = StreamInfo(*info)
        self.outlet = StreamOutlet(info)
        
        if self.logger:
            self.logger.info(f'Successful setup TriggerLSL stream: {info}')

    def send(self, seq=[], fs=10):
        ''' Send a sequence to trigger and to
            LSL stream outlet

        Args
        ----------
        seq = []: list[int[binary], ...]
            binary sequence to send
        fs = 10:  int
            frequency to send each sequence element in Hz

        Returns
        ----------
        '''
        if not self.port:
            msg = 'Port not connected. Did you run Trigger.connect_to_port()?'
            self.logger.error(msg)
            raise ConnectionError(msg)

        if not self.outlet:
            msg = 'LSL stream not setup. Did you run Trigger.setup_lsl()?'
            self.logger.error(msg)
            raise ConnectionError(msg)

        if not seq:
            seq = self.sequence

        # seq = bytearray(seq)
        if self.logger: 
            self.logger.info('Sending trigger sequence | Start')

        self.outlet.push_sample([f'Sending trigger sequence: {seq}'])

        for i, bit in enumerate(seq):
            try:
                self.port.write(bytes([bit]))
                self.outlet.push_sample([f'{i}-{bit}'])
            finally:
                # self.port.write(b'0')
                self.port.write(bytes([0]))

            sleep(1/fs)

        self.outlet.push_sample([f'Finished sending sequence: {seq}'])

        if self.logger: 
            self.logger.info('Sending trigger sequence | End')
    
    def close(self):
        ''' Closes port

        Args
        ----------

        Returns
        ----------
        '''
        if self.port.is_open:
            self.port.close()

        if self.logger:
            self.logger.info(f'Closed port')


def go():
    ''' Main entry point to setup, run and
        close a trigger

        Args
        ----------

        Returns
        ----------
        '''
    import logging
    t = Trigger(is_active=True, logger=logging)
    t.connect_to_port()
    t.setup_lsl()
    t.send(fs=5)
    t.close()


if __name__=='__main__':
    go()