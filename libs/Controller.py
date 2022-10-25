import sys

import libs.utils as utils

from libs.Experiment import Experiment


class Controller:
    ''' Handles meta information to run an experiment, such
        as setting pathing and loading config files.
    '''

    def __init__(self, logger) -> None:
        self.logger = logger
        self.main_dir = utils.get_main_dir_from_config_file()
        self.exps = self.get_experiment_dict()
        self.add_sys_paths()
        self.main_config = utils.load_data_from_yaml(self.main_dir/'config.yaml')

    def add_sys_paths(self):
        '''
        Add ./libs and ./exp_module/experiments/ to sys path

        Args
        ----------

        Returns
        ----------
        '''

        for path in [self.main_dir/'libs',
                     self.main_dir/'exp_module'/'experiments']:
            sys.path.insert(0, path)

    def get_experiment_dict(self):
        '''
        Creates a dictionary with paths to all
        experiment folders

        Args
        ----------

        Returns
        ----------
        exp_dict: dict{exp_folder_name: Path()}
        '''

        path = self.main_dir/'exp_module'/'experiments'

        return {exp.name: path/exp for exp in path.iterdir()
                                   if '__' not in exp.name}

    def load(self, name, ppt_id):
        '''
        Creates an Experiment instance and runs it.
        Raises Exception if anything fails

        Args
        ----------
        name: str
            name of experiment
        ppt_id: str
            id of participant, as set in Admin panel

        Returns
        ----------
        e: Experiment() or Exception
            experiment instance or, if failed, an Exception
        '''

        try:
            e = Experiment(name, ppt_id, debug=self.main_config['debug'],
                                         logger=self.logger)
            e.go()
            return e

        except Exception as e:
            self.logger.error(f"Failed running {name}.")
            self.logger.error(f"ERROR {e}.")
            return e


if __name__=='__main__':
    import logging
    c = Controller(logging)
    c.load('grasping', 'test_id_01')
