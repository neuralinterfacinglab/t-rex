import yaml
import logging
import json

from pathlib import Path

server_logger = logging.getLogger('server')


############# functions for reading and writing on .yaml files #############
def load_data_from_yaml(path_to_file):
    """Loads the data from a .yaml file

    Gets the data from a .yaml file, the user should specify the full path to the file.

    Arguments:
        path_to_file -- full path to the .yaml file to load

    Returns:
        data contained on the .yaml file
    """

    try:
        with open(path_to_file) as file_obj:
            config = yaml.load(file_obj, Loader=yaml.FullLoader)
        return config
    except:
        msg = 'Failed to load config file from: {}.'.format(path_to_file)
        server_logger.error(msg)
        raise Exception(msg)


def save_data_on_yaml(path_to_file, data):
    """Saves the data on the specified .yaml file

    Saves the data object on a .yaml file, the user should specify the full path to the file.

    Arguments:
        path_to_file -- full path to the .yaml file to load
        data -- data to save on the file

    """

    try:
        with open(path_to_file, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
    except:
        msg = 'Failed to load config file from: {}.'.format(path_to_file)
        server_logger.error(msg)
        raise Exception('Failed to save data on file.')


################### function to read from the experiments folder and retrieve the configuration data ###################
def get_exp_list(main_dir):
    """Get a list with the information of each experiment.

    Reads the experiments folder and retrieves the configuration data for each experiment. 
    For each experiment it creates a dictionary with name, description and id.
    The user should specify the full path to the directory where the main module is contained.

    Arguments:
        main_dir -- full path to main directory. The 'experiments' folder should be inside 'exp_module'.

    Returns:
        A list with: 'name', 'description' and 'id' for each of the experiments inside the 'experiments' folder.

        Example:
            [{'name': 'Grasping',
            'description': 'Lorem Ipsum Dolor Sit',
            'id': 'grasping'},
            {'name': 'Sentences',
            'description': 'Lorem Ipsum Dolor Sit',
            'id': 'sentences'}]
    """

    exp_list = []
    exps_dir = Path(main_dir/'exp_module'/'experiments')
    exps_folders = [f for f in exps_dir.iterdir() if f.is_dir()]
    for exp_name in exps_folders:
        exp_config = load_data_from_yaml(Path(exp_name)/'config.yaml')
        exp_data = {
            'name': exp_config.get('name'),
            'description': exp_config.get('description'),
            'id': exp_config.get('id')
        }
        exp_list.append(exp_data)

    return exp_list


################################# functions to get and update participants access data #################################
def get_participants_access_data(main_dir):
    """Get a list with the access information for each participant on record.

    Gets a list of dictionaries that contains for each participant on record, its 'id' and the access to each experiment.
    The user should specify the full path to the directory where the main module is contained.

    Arguments:
        main_dir -- full path to main directory. The 'access.yaml' file should be here.

    Returns:
        A list with: 'participant_id' and 'participant_access' for each of the participants on record.

    """

    access_file = Path(main_dir)/'resources'/'access.yaml'
    access_data = load_data_from_yaml(access_file)

    return access_data


def update_participants_access_file(main_dir, participant_id, participant_access):
    """Updates the .yaml file with the participant's access to the experiments.

    Updates on the 'access.yaml' the participant's access to the experiments. 
    This file must be on the root of the 'main_dir'.

    Arguments:
        main_dir -- full path to main directory. The 'access.yaml' file should be here.
        participant_id -- id of the participant that needs updating.
        participant_access -- the access dictionary that already contains the updated fields.
    """

    # get the list with the access information for each participant on record.
    p_access_data = get_participants_access_data(main_dir)
    p_access_list = p_access_data.get('participants_list')
    # define utility variable to recognize if the participant was already on the list or not
    p_not_found = True

    # if the participant exists update its access with the inputted 'participant_access'
    for p in p_access_list:
        if(p.get('participant_id') == participant_id):
            p['participant_access'] = participant_access
            p_not_found = False
            break

    # if the participant was not found this variable will remain True and we will need to add it to the list
    if(p_not_found):
        p_data = {
            'participant_id': participant_id,
            'participant_access': participant_access
        }
        p_access_list.append(p_data)
    
    p_access_data['participants_list'] = p_access_list
    # get the location of the access file and update the access information
    access_file = Path(main_dir)/'resources'/'access.yaml'
    save_data_on_yaml(access_file, p_access_data)


#################################### functions to get and update the active session ####################################
def get_active_session(main_dir):
    """Get a string with the active session information.

    Gets a string with the active session (ex. 'kh001' or 'khXXX').
    The user should specify the full path to the directory where the main module is contained.

    Arguments:
        main_dir -- full path to main directory. The 'config.yaml' file should be inside the resources folder.

    Returns:
        A string with the 'Participant ID'.
    """
    access_file = Path(main_dir)/'resources'/'access.yaml'
    config_data = load_data_from_yaml(access_file)
    
    return config_data.get('active_session')


def update_active_session(main_dir, active_session):
    """Updates the .yaml file with the active session configuration.

    Updates on the 'config.yaml' the 'active_session' information. This file must be inside './main_dir/resources/'.

    Arguments:
        main_dir -- full path to main directory. The 'config.yaml' file should be inside './main_dir/resources/'.
        active_session -- the active session to update.
    """
    # get the path to the configuration file
    config_file = Path(main_dir)/'resources'/'access.yaml'
    # get the configuration data
    config_data = load_data_from_yaml(config_file)
    # update the active session
    config_data['active_session'] = active_session
    # save the configuration data on the configuration file
    save_data_on_yaml(config_file, config_data)


######################### functions to get the main directory of execution from the config file #########################
def get_main_dir_from_config_file():
    """Get a string with the main directory of execution from the config file.

    Retrieves from the 'config.yaml' file that is inside the 'exp_module', the main directory of execution.

    Returns:
        A string with the path to the main directory of execution.
    """

    config = Path('resources')/'config.yaml'

    for folder in ['.', '..', '../..']:
        path = folder/config

        if path.is_file():
            config_data = load_data_from_yaml(path)

            main_dir = config_data.get('path').get('main')
            if(main_dir == 'default'):
                return Path().absolute()
            else:
                return Path(main_dir)

    msg = 'The main config.yaml file was not found.'
    server_logger.error(msg)
    raise Exception(msg)


def get_active_session_access(main_dir):
    """Get the active session access, the list of exps., the active session, and the access list for all participants.

    Retrieves from the 'config.yaml' and 'access.yaml' files the corresponding active session access, the list of 
    experiments, the active session, and  the access list for all participants.

    Arguments:
        main_dir -- full path to main directory. 
        The 'config.yaml' and 'access.yaml' files should be inside './main_dir/resources/'.

    Returns:
        participant_access -- the access data for the active_session.
            
            Example:
            {'grasping': True, 'sentences': True, 'wordslis': True}
        
        exp_list -- check the :method:`get_exp_list()` function for more info.
        
        active_session -- check the :method:`get_active_session()` function for more info.
        
        p_access_list -- check the :method:`get_participants_access_data()` function for more info.
    """

    # get a list with the config information of each experiment
    exp_list = get_exp_list(main_dir)
    # get a string with the active session information
    active_session = get_active_session(main_dir)
    # get a list with the access information for each participant on record
    p_access_list = get_participants_access_data(main_dir).get('participants_list')

    # Check if ppt_id is in access.yaml, otherwise generate empty one.
    for ppt in p_access_list:
        participant_access = ppt.get('participant_access')
        if ppt['participant_id'] == active_session:
            break
        else:
            participant_access = None

    if not participant_access:
        participant_access =  {
            'participant_access': {exp['id']: False for exp in exp_list}}

    return participant_access, exp_list, active_session, p_access_list


######################### functions to get the password from the config file #########################
def get_pass_from_config_file():
    """Get a string with the password to access the admin panel from the config file.

    Retrieves from the 'config.yaml' file that is inside the 'exp_module', the password to access the admin panel .

    Returns:
        A string with the password to access the admin panel.
    """

    config = Path('resources')/'config.yaml'

    for folder in ['.', '..', '../..']:
        path = folder/config

        if path.is_file():
            config_data = load_data_from_yaml(path)

            password = config_data.get('password')
            return password

    msg = 'The main config.yaml file was not found.'
    server_logger.error(msg)
    raise Exception(msg)


###################### function to get the newest created file from the root of a directory tree ######################
def get_newest_file_from_dir(dir):
    config = load_data_from_yaml(dir/'resources'/'config.yaml')
    paths = config.get('path')
    path_output = Path(paths.get('out'))  # output folder

    Path(path_output).stat().st_mtime

    p = Path(path_output).glob('**/*')
    files = [x for x in p if (x.is_file() and x.suffix == '.xdf')]

    latest = files[0]
    for file in files:
        current = Path(file).stat().st_mtime
        if current > Path(latest).stat().st_mtime:
            latest = file

    return latest


###################### function to obtain and save on file the session access and the exp metadata ######################
def generate_file_with_session_and_exp_metadata(main_dir, output_dir):
    participant_access, exp_list, _, _ = get_active_session_access(main_dir)
    access_and_exp_description_file = 'access.json'

    with open(output_dir/access_and_exp_description_file, 'w') as file:
        # create json object from dictionary
        data = {
            'access': participant_access,
            'experiments_metadata': exp_list
        }
        json_data = json.dumps(data)

        file.write(json_data)
