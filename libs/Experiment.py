import subprocess
from logging import captureWarnings, exception
from time import perf_counter as time

from pylsl import StreamInfo, StreamOutlet
from pylsl import resolve_streams
from pylsl import resolve_byprop
from pylsl import ContinuousResolver

import libs.utils as utils
from libs.Recorder import Recorder
from libs.Trigger import Trigger


class  Experiment:
    ''' Handles start, record and stopping of all LabStreamingLayer
        streams and devices required for a single experiment. '''

    def __init__(self, name, ppt_id, debug=False, 
                                     logger=None) -> None:
        self.name = name
        self.ppt_id = ppt_id
        self.experiment_dir = None
        self.config = self.load_config(name)
        self.logger = logger
        
        self.input_ids = []  # IDs of LSL streams to record

        self.rec = None
        self.trig = None

        self.process = None

        self.debug = debug
        if self.debug:
            self.setup_debugging()
        
        self.cr = ContinuousResolver()  # Unreliable if only checked once

    def setup_debugging(self):
        ''' Changes eeg stream to an empty stream with
            stream_id = DBG01 and name = debug for 
            easy debugging

        Args
        ----------

        Returns
        ----------
        '''

        msg = '''WARNING: Debugging mode = on | Setting up empty stream with source_id = DBG01.
              No stream will be recorded.'''
        self.logger.warning(msg)
        
        source_id = 'DBG01'
        self.input_ids = [source_id]

        info = StreamInfo(name='debug', source_id=source_id)
        self.outlet_debug = StreamOutlet(info)

    def load_config(self, name):
        ''' Loads config of a single experiment.

        Args
        ----------
        name: str
            name of experiment folder

        Returns
        ----------
        config: dict
            dictionary of the config.yml in ./experiments/name
        '''

        main_dir = utils.get_main_dir_from_config_file()

        self.experiment_dir = main_dir/'exp_module'/'experiments'/name
        config_file_path = self.experiment_dir/'config.yaml'

        return utils.load_data_from_yaml(config_file_path)

    def get_devices_list(self):
        ''' Loads the list of devices from config
            and converts to the correct format

        Args
        ----------

        Returns
        ----------
        devices: list[str]
            List of strings for streams to search for
        '''

        devices = self.config.get('device_inputs', 'missing_header')

        if devices == 'missing_header':
            msg = "No header named device_input defined in experiment config."
            self.logger.error(msg)
            raise Exception(msg)
        
        if devices == None:
            msg = "No list provided under device_inputs in experiment config."
            self.logger.error(msg)
            raise Exception(msg)

        if not isinstance(devices, list):
            devices = [devices]

        devices = [str(d) for d in devices]

        return devices

    def get_device_input_source_ids(self):
        ''' Add all devices (listed under config/device_inputs) that input data to LabStreamingLayer to
            to the list of streams to record.
                - Checks for source_id, name and type.
                - Assumes that all devices listed are already initialized.
                  i.e. it will only check once
            Raises error if:
                - device_inputs is not defined a key in exp/config.yaml
                - No streams are present
                - Not all streams are matched

        Args
        ----------

        Returns
        ----------
        '''

        missing_streams = []

        has_attr = lambda d, s: [d==s.source_id().lower(),
                                 d==s.name().lower(),
                                 d==s.type().lower()]

        if self.debug:
            return

        devices = self.get_devices_list()
        current_streams = resolve_streams()

        if not current_streams:
            msg = f"Cant find any devices. No streams available. Listed devices: {devices}"
            self.logger.error(msg)
            raise Exception(msg)

        for device in devices:

            for stream in current_streams: 

                has_match = has_attr(device.lower(), stream)

                if any(has_match):

                    if stream.source_id() in self.input_ids:
                        msg = f'Stream <id: {stream.source_id()}, name: {stream.name()}, type: {stream.type()}> already in list to record. Skipping... Listed stream ids: {self.input_ids}'
                        self.logger.warning(msg)

                    self.input_ids += [stream.source_id()]
                    break

            if not any(has_match):
                missing_streams += [device]

        if missing_streams:
            msg = f'No stream exists with source_id, name or type for devices: {[f"<{d}>" for d in missing_streams]}'
            self.logger.error(msg)
            raise Exception(msg)

    def setup_recorder(self):
        ''' Initialized Recorder instance, add streams
            to record, and creates an output path

        Args
        ----------

        Returns
        ----------
        '''

        self.rec = Recorder(self.logger)
        self.rec.add_streams_by_id(self.input_ids)
        self.rec.set_output_path(self.ppt_id, self.name)

    def setup_trigger(self):
        ''' Initialized Trigger instance and setup 
            LSL stream.

        Args
        ----------

        Returns
        ----------
        '''

        self.trig = Trigger(self.config['trigger'], logger=self.logger)

        if self.trig.is_active:
            self.trig.connect_to_port()
            self.trig.setup_lsl()

    def setup(self):
        ''' Calls all separate components to setup

        Args
        ----------

        Returns
        ----------
        '''

        self.get_device_input_source_ids()
        self.setup_recorder()
        self.setup_trigger()

    def experiment_is_running(self):
        ''' Checks if and experiment process is
            currently running

        Args
        ----------

        Returns
        ----------
        ok: Bool
        '''

        if isinstance(self.process, subprocess.Popen):
            status = self.process.poll()
            if not status:
                return True

        return False

    def run_start_command(self):
        ''' Runs a non-blocking command as listed in exp/config.yaml.

        Args
        ----------

        Returns
        ---------- 
        p: Popen instance
           instance of the process of <command>
        '''

        command = self.config['command']
        try:
            p = subprocess.Popen(command, shell=True)
        except Exception as err:
            self.logger.error(f'''Command: <{command}> cannot be executed, did you supply the correct executable?\n\tFull error: {err}''')
            raise err

        if p.returncode == 1:
            msg = f'The subprocess raised the following error: {p.stderr}'
            self.logger.error(msg)
            raise Exception(msg)

        return p

    def start(self):
        ''' Starts the experiment UI and looks for the stream on a timeout. 
            The UI should generate a markerstream and should be recorded.
            Therefore, the recorder only starts recording once this UI
            stream is found and included, meaning that data will only 
            be recorded from that point onward! If the actual experiment 
            starts running before the recorder has included the stream,
            data up to this point will NOT be recorded. A 'press button
            when ready' screen in the experiment is recommended.

            Length of timeout is set seperately per experiment in
            exp/config.yaml

        Args
        ----------

        Returns
        ----------
        '''
        
        # Start Experiment UI as subprocess
        self.process = self.run_start_command()
        
        ts = time()
        while True:
            # NOTE: resolve_byprop has a timeout argument builtin, but the 
            #       self.cr: ContinuousRecorder is much quicker: 0.500000s vs 0.000000s.
            #       Be aware than in the continuous resolver can be unreliable if checked
            #       once for streams. It doesnt return all streams every time. 
            streams = [stream for stream in self.cr.results() if stream.source_id()==self.config['exp_outlet']]

            if streams:
                break

            if time() - ts >= self.config['timeout']:
                msg = f"Cannot find experiment stream with source_id: {self.config['exp_outlet']} \t[ Timeout={self.config['timeout']}s ]"
                self.logger.error(msg)
                raise TimeoutError(msg)

            if not self.experiment_is_running():
                msg = f"Command <{self.config['command']}> has not executed successfully."
                self.logger.error(msg)
                raise Exception(msg)

        self.rec.add_streams_by_id([streams[0].source_id()])
        self.rec.start()

        # Send trigger once recording has started
        if self.trig.is_active:
            self.trig.send()

    def stop(self):
        ''' Stops and closes all running components

        Args
        ----------

        Returns
        ----------
        '''

        if self.trig.is_active:
            self.trig.send()
            self.trig.close()

        self.logger.info(f'Experiment <{self.name}> finished , stopping recorder...')
        self.rec.stop()

    def go(self):
        ''' Main entry point for running experiments.

        Args
        ----------

        Returns
        ----------
        '''

        self.setup()

        # Run experiment
        self.start()

        # Wait until experiment finished
        self.process.wait()

        self.stop()