# builtin
import json
from shutil import ExecError
import yaml
import os

# 3th party
from flask import request, jsonify, render_template
import pathlib

# local
from flaskr import *
from libs.Controller import Controller
import libs.utils as utils


################################################################################################################
######## API ROUTES ################ API ROUTES ################ API ROUTES ################ API ROUTES ########
################################################################################################################

@app.route("/define_user_and_access", methods=['POST', 'GET'])
def define_user_and_access():
    """Route that defines the user_id and to which experiments the user can access."""

    # get the updated data from the UI
    data = request.get_data()
    data = json.loads(data.decode("UTF-8"))
    # get participant id from the updated data
    participant_id = data.get('participant')
    # get participant access from the updated data
    participant_access = {}
    for exp in data.get('exp_list'):
        participant_access[exp.get('id')] = exp.get('checked')

    # update the access file with the new access for this participant
    utils.update_participants_access_file(MAIN_DIR, participant_id, participant_access)

    # update the active session
    utils.update_active_session(MAIN_DIR, participant_id)

    return '/admin_panel'


@app.route("/check_password", methods=['GET'])
def check_password():
    """Route that checks if the password is correct to give access to the admin view.
        The password is configured on the main config.yaml file."""
    pwrd = request.args.get('pass')
    if(pwrd == PASSWORD):
        return 'True'
    else:
        return 'False'


@app.route("/exp_went_well", methods=['GET'])
def exp_went_well():
    """Route that created the 'feedback.exp' file getting the user feedback."""
    
    latest = utils.get_newest_file_from_dir(MAIN_DIR)
    feedback_file = 'feedback.txt'
    with open(latest.parent/feedback_file, 'w') as file:
        file.write('User indicated GOOD')

    utils.generate_file_with_session_and_exp_metadata(MAIN_DIR, latest.parent)

    return 'experiment went WELL, thanks for the feedback'


@app.route("/exp_went_bad", methods=['GET'])
def exp_went_bad():
    """Route that created the 'feedback.exp' file getting the user feedback."""
    
    latest = utils.get_newest_file_from_dir(MAIN_DIR)
    feedback_file = 'feedback.txt'
    with open(latest.parent/feedback_file, 'w') as file:
        file.write('User indicated BAD')
    
    utils.generate_file_with_session_and_exp_metadata(MAIN_DIR, latest.parent)
    
    return 'experiment went BAD, thanks for the feedback'


@app.route("/start_exp", methods=['GET'])
def start_exp():
    """Route that runs the experiment's init sequence."""
    experiment_to_start = request.args.get('experiment_to_start')
    # get the participant id from the config file
    ppt_id = utils.get_active_session(MAIN_DIR)
    
    server_logger.info(f'For participant: {ppt_id}, starting experiment: {experiment_to_start}.')

    c = Controller(server_logger)
    status = c.load(experiment_to_start, ppt_id)

    # if there was an error during the execution then stay in the Home view and set the error message
    if(isinstance(status, Exception)):
        return str(status), 500
    else:
        return '/experiment_end'


@app.route('/load_exp_grid', methods=['GET'])
def load_exp_grid():

    # get the access for the active session, the full list of experiments and the active session
    participant_access, exp_list, _, _ = utils.get_active_session_access(MAIN_DIR)

    # get a list that contains only the experiment that this used has access to      
    only_exps_with_access_list = []
    for exp in exp_list:
        p_access_to_exp = participant_access.get(exp.get('id'))
        if(p_access_to_exp is not None and p_access_to_exp):
            exp['action'] = 'start_exp(\''+ exp.get('id')+ '\');'
            only_exps_with_access_list.append(exp)

    return json.dumps({'experiments': only_exps_with_access_list})
