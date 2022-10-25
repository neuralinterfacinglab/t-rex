# builtin
from sys import excepthook
import yaml
import os

# 3th party
from flask import render_template

# local
from flaskr import *

import libs.utils as utils


####################################################################################################################
########### VIEWS ###################### VIEWS ###################### VIEWS ###################### VIEWS ###########
####################################################################################################################

@app.route("/")
@app.route("/home")
def home():
    """View that contains the list of all the experiments."""

    server_logger.info("User accessed 'Experimental menu'")
    # TODO Move the grid logic from the JavaScript to here
    return render_template('index.html', title='Experimental menu')


@app.route("/admin_login")
def admin_login():
    """View that asks for the admin password to access the admin window."""    
    
    server_logger.info("User accessed 'Login'")
    return render_template('admin_login.html', title='Login')


@app.route("/admin_panel")
def admin_panel():
    """View that handles the configuration of the user_id and its permits."""    
    
    server_logger.info("User accessed 'Admin Panel'")

    # get the access for the active session, the full list of experiments and the active session
    participant_access, exp_list, active_session, _ = utils.get_active_session_access(MAIN_DIR)

    # iterate through the exp_list to define what is the participant's access for each of the experiments
    # if the exp_id is not found for this participant then by default the participant will not have access to it
    for exp in exp_list:
        exp_id = exp.get('id')
        if(participant_access.get(exp_id) is not None):
            exp['checked'] = participant_access.get(exp_id)
        else:
            exp['checked'] = False
            participant_access[exp_id] = False

    # Just in case that there are new experiments added to the 'experiments' folder we always update the .yaml
    # file with the participants access to the experiments
    utils.update_participants_access_file(MAIN_DIR, active_session, participant_access)

    return render_template('admin_panel.html', title='Admin Panel', exp_list=exp_list, participant=active_session)


@app.route("/experiment_start")
def experiment_start():
    """View that:   if everything went well, displays the "Experiment is running" message
                    if some error happened, displays the error and the possible solution.
    """

    server_logger.info("User accessed 'Start experiment'")
    return render_template('experiment_start.html', title='Start experiment')


@app.route("/experiment_end")
def experiment_end():
    """View that:   displays two buttons to check if everything went well with the experiment
                    afterwards, it asks if the user want to repeat the experiment or go to the Home screen.
    """

    server_logger.info("User accessed 'End experiment'")
    return render_template('experiment_end.html', title='End experiment')
