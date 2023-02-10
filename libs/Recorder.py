import os
import sys
import datetime as dt
from subprocess import PIPE, Popen, check_output

from pathlib import Path

from pylsl import ContinuousResolver

import libs.utils as utils



class LabRecorderCLI():
    '''Process based interface for LabRecorder

    Written by Robert Guggenberger
    see: https://gist.github.com/agricolab/47d3126d9f150b6584d6ec8c7bc791e7
        
    Example::

        cmd = 'C:\\tools\\lsl\\LabRecorder\\LabRecorderCLI.exe'
        filename = os.path.join(os.path.expanduser('~'), 'Desktop\\untitled.xdf')                
        streams = "type='EEG' type='Markers'"
        streams = "type='dfg'"
        lr = LabRecorderCLI(cmd)
        lr.start_recording(filename, streams)
        print('Start recording')
        time.sleep(5)
        print('Stop recording')    
        lr.stop_recording() 
    '''

    def __init__(self, cmd) -> None:
        if not os.path.exists(cmd):
            raise FileNotFoundError
        self.cmd = cmd

    def start_recording(self, filename:str, streams:str) -> None:

        self.process = Popen([str(self.cmd), str(filename)] + streams,
                             stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)

        peek =  self.process.stdout.peek()
        if b'matched no stream' in peek:
            raise ConnectionError(peek.decode().strip())

    def stop_recording(self) -> None:
        if hasattr(self, 'process'):       
            o, e = self.process.communicate(b'\n')
            if self.process.poll() != 0:
                raise ConnectionError(o + e)  

class Recorder():
    ''' Handles everything related to setup, start and
        stop of LabRecorder
    '''

    def __init__(self, logger=None) -> None:
        self.path_main = utils.get_main_dir_from_config_file()
        self.config = self.load_config(self.path_main)
        self.logger = logger

        paths = self.config.get('path')

        self.path_recorder =   self.select_recorder()  # Path(paths.get('exe'))
        self.path_output =     Path(paths.get('out'))  # .xdf output file
        self.output_filename = Path('test.xdf')
        self.output_folder =   None
        
        self.CLI = LabRecorderCLI(self.path_main/self.path_recorder)
        self.resolver = ContinuousResolver()

        self.ids = []


    def load_config(self, main_dir):
        ''' Loads main config 

        Args
        ----------
        main_dir: Path instance
            Path to top level directory of T-Rex

        Returns
        ----------
        config: dict
            dict with all config info
        '''

        return utils.load_data_from_yaml(main_dir/'resources'/'config.yaml')
    
    def select_recorder(self):
        ''' Adds multiple stream_ids to the list
            to record.

        Args
        ----------

        Returns
        ----------
        labrecorderCLI_path: Path
            path to the OS compatible labrecorderCLI.
        '''

        path = Path('./libs/labrecorder/')
        
        platform = sys.platform() if callable(sys.platform) else sys.platform
        platform = platform.lower()

        if platform in ['win32', 'win64', 'windows']:

            return  path/Path('./windows/LabRecorderCLI.exe')


        if platform == 'darwin':

            processor = check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).lower()

            if 'm1' in processor:
                return path/Path('./macos/LabRecorderCLI_m1')

            elif 'm2' in processor:
                return path/Path('./macos/LabRecorderCLI_m2')

        raise FileNotFoundError('Cannot find path to LabRecorderCLI')

    def set_output_path(self, ppt_id: str, name: str) -> None:
        '''  Creates the output structure for output
             files
             # TODO: save used config

        Args
        ----------
        ppt_id: str
            id of participant, as set in admin panel.
        name: str
            name of experiment that is being ran

        Returns
        ----------
        '''

        today = dt.datetime.today()
        date = today.strftime('%Y_%m_%d')
        time = today.strftime('%H_%M_%S')

        self.output_folder = Path('{}/{}/{}/{}/{}_{}'.format(
            self.path_main,
            self.path_output,
            ppt_id,
            date,
            name, time))
        
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.generate_outputfile(ppt_id, name)

        self.full_output_path = self.output_folder/self.output_filename

    def generate_outputfile(self, ppt_id, name):
        ''' Generate filename and makes sure files
            are not overwritten

        Args
        ----------
        ppt_id: str
            id of participant, as set in admin panel.
        name: str
            name of experiment that is being ran

        Returns
        ----------
        '''

        i = 1
        filename = f'{ppt_id}_{name}_{i}.xdf'
        output_dir = self.path_main/self.path_output
        output_file = output_dir/filename
        while output_file.exists():
            i += 1
            filename = f'{ppt_id}_{name}_{i}.xdf'
            output_file = output_dir/filename
        self.output_filename = filename

    def add_streams_by_id(self, ids: list) -> None:
        ''' Adds multiple stream_ids to the list
            to record.

        Args
        ----------
        ids: list
            list of LSL stream_ids 

        Returns
        ----------
        '''
        self.ids += list(zip(['source_id']*len(ids), ids))


    def run_checks(self):
        if not (self.path_main/self.path_recorder).exists():
            msg = 'Path to recorder does not exist. (main config)'
            self.logger.error(msg)
            raise NameError(msg)

    def start(self):
        ''' Checks if everything is ready to record and
            runs the CLI if so.

        Args
        ----------

        Returns
        ----------
        '''

        self.run_checks()

        search_args =  [f"{arg}='{id_}'" for arg, id_ in self.ids]
        self.logger.info(f'Recording streams: {search_args}')

        self.CLI.start_recording(filename=self.full_output_path,
                                 streams=search_args)
        self.logger.info(f'Started recording to {self.output_filename}')

    def stop(self):
        ''' Wraps up after recording

        Args
        ----------

        Returns
        ----------
        '''
        self.CLI.stop_recording()
        self.logger.info('Stopped recording')


if __name__=='__main__':
    ids = ['RDS01', 'gms01']
    ids = ['DBG01']

    r = Recorder()
    r.include_streams_by_id(ids)
    r.start()
