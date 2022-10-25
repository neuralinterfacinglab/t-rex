# T-REX (sTandalone Recording eXperience)

We present the sTandalone Recording eXperience **T-REX**, an open-source, OS-independent, user-friendly, scalable, and customizable web interface used for recording (neuroscientific) experiments. Under the hood, T-REX handles data synchronization from multiple-streams, ensures all data streams are recorded and saved to the user-specified location. By taking care of the overhead, the researcher can spent all its time on actually recording experiments.

## Table of contents

- <a href="#Project_Description">Project description</a>
- <a href="#materials-software-and-technologies">Materials</a>
- <a href="#how-to-install-and-run-the-project">Installation</a>
- <a href="#how-to-use-the-project">Use cases</a>


<!-- For a full description please see the [accompanying preprint here](): -->



<!-- that handles the setup and recording (neuroscientific) experiments.
 T-REX signficantly reduces time by handling the overhead of setting up, and the start and stop of experiments, increasing the time the research can spent on recording.
 recording experiments and synchronization of multiple datastreams
 the execution of experiments, continuous recording, and synchronization of neural data from hospitalized neurosurgical patients. We provide researchers with a solution that can significantly increase time spent on recording instead of on the setup with its possible errors. -->

## Project Description

**T-Rex** acts as the middle man handling the experimental overhead for the researcher (<a href="#figure_components">Figure 1</a>). When using **T-Rex**, the researcher can select an experiment by simply pressing a button on the main menu screen (<a href="#figure_windows">Figure 2</a> A). When an experiment is selected, **T-Rex** checks the availability of all required input devices for the selected experiment and establishes a connection. For example, a movement-tracking experiment requires input from a hand-tracking device and the amplifier measuring the participants' neural activity. **T-Rex** will search for and connect to these devices. **T-Rex** will also start the experiment user interface (UI) that instructs the participant on what task to perform. It starts recording all data streams and saves them to a folder specified by the researcher. The synchronized data is saved inside this folder using the `.xdf` file format. Lastly, the UI prompts the participant on how the experiment went and returns to the *Home* screen, where the next experiment can be selected. The only action the researcher has to perform is to start the required device data stream(s) and select the experiment in the *Home* screen.

<figure>
    <img src="README_images/components.jpg"
         alt="Components of T-Rex"
         width="400"
         id='figure_components'>
    <figcaption>Figures 1: The use of T-Rex imposes no limitations on the researchers' inputs, outputs, behavior, or frameworks for creating the experiments. (A) Represents a set of possible inputs. (B) T-Rex sits in the middle handling the logic that connects the inputs and the outputs. The three main software components of the system are also illustrated (Web interface, Controller, and User configuration). (C) Depicts a set of possible outputs. It is worth emphasizing that the inputs and outputs are not limited to those represented.</figcaption>
</figure>

### Materials, software, and technologies

The web interface (including the *Home* screen with experiment selection, see <a href="#figure_windows">Figure 2</a> A-D) is built using [Bootstrap5](https://getbootstrap.com/docs/5.1/getting-started/introduction/) for the front-end and the Python package [Flask](https://flask.palletsprojects.com/en/2.1.x/) for the back-end.

The Controller, handling set up, start and stop of the experiments, is built in `Python 3.9+` and requires a few dependencies found in `requirements.txt` in the repository. Data synchronization is implemented using Lab Streaming Layer.

**T-Rex** is compatible with Windows, macOS, and Linux. As **T-Rex** is lightweight and primarily active before and after experiments, the hardware requirements are determined mainly by the recording of the experiment in Lab Streaming Layer, instead of **T-Rex**.

### Web interface

The Web interface includes four windows: *Home*, *Experiment Feedback*, *Admin Login*, and *Admin Configuration* (<a href="#figure_windows">Figure 2</a>).

The *Home* window (<a href="#figure_windows">Figure 2</a> A) displays all the experiments in a grid. Experiments' cards' are shown on that grid with a title, description, and start button. When the button is pressed, the *Controller* executes a command that starts the selected experiment. The command is defined by the researcher and specified in the experiment's configuration file. During the experiment, the web interface is on stand-by awaiting the completion of the experiment.

After completion, the participant is redirected to the *Experiment Feedback* window where the question *"How did the experiment go?"* is prompted (<a href="#figure_windows">Figure 2</a> B). The participants are required to select a feedback option to continue. This allows the researcher to save a brief experiment evaluation to assess data quality in later analysis. In potential future applications, the participant might perform the experiments by themselves. Then this feedback is useful to flag the researcher to be aware of a potential loss in data quality during later analysis. The feedback is stored under the file name `feedback.txt` in the same folder as the most recent `.xdf` file (that contains the data recorded from the experiment).

The Admin Configuration provides the researcher with a closed environment where the participant identifier and a selection of all available experiments can be chosen. To access the Admin Configuration, the researcher must first log in using the password that is configured in the main configuration file (<a href="#figure_windows">Figure 2</a> C). When logged in, the researcher can see the configuration of the active experimental session, composed of an alphanumeric participant identifier and their access to experiments. A list of all the experiments included in the platform is visible from this window, but only those with checked marks are visible to the participant. The changes on this window are only applied after pressing the **"Save"** button at the end of the page.

<figure>
    <img src="README_images/web.jpg"
         alt="Visible windows in T-REX"
         id='figure_windows'>
    <figcaption>Figure 2: Screenshots of the main four windows in the Web interface. (A) The Home window contains all the experiments accessible to the user, shown in a grid configuration. (B) The Experiment Feedback window allows for obtaining feedback from the participants about their experience with the experiment. It is achieved through the green ("All good") and the red ("Not so good") button. The participants can only continue after pressing one of these buttons. (C) The Admin Login window allows access to the administration panel by entering the password. (D) The Admin Configuration window, where the administrator can create new participants and modify their access to experiments.</figcaption>
</figure>


## How to Install and Run the Project

Prerequisites:

- `Python 3.9 (or higher)`
- `Git`

We recommend running T-REX in a virtual environment. See [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for installation and usage. Any other virtual environment manager should work as well.
For using `git` see [this guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

After you setup a virtual env with `python 3.9+` and `git`, clone the repository in your specified folder and install all dependencies in your virtual environment. If using miniconda or similar you can do so by running these commands:
```batch
git clone https://github.com/neuralinterfacinglab/continuous-recording
git checkout development
cd continuous-recording
conda create --name trex python=3.9
conda activate trex
pip install -r requirements.txt
start run.bat
```

T-Rex is now ready to go. Try out one of our included example experiments!
You can start one of the experiments from the web interface that just opened to test that everything is working correctly. The current environment is configured as development, so a testing stream named `DBG01` will start automatically, allowing you to try the system. Important: if want to start recording real experiments, turn debug mode of!

## How to Use the Project

### Example experiments

We have included three different example experiments to provide a more practical view of how to use **T-Rex**. The examples can also serve as a quick start for researchers to create new experiments or adapt the ones included.



<figure>
    <img src="README_images/use_case_experiments.jpg"
         alt="Visible windows in T-REX"
         id='fig_usecase'>
    <figcaption>Figure 3:  User interfaces for the three Use cases experiments included. (A) Grasping, simple text-based experiment built using the Python package Tkinter. (B) Grasping Web experiment, re-implementation of the Grasping experiment as a Single Page Application (SPA) to allow its execution on any device with access to a web browser. (C) 3D hand tracking experiment, the hand tracking is performed using the LeapMotion controller, and the experiment is implemented in Python using the package Tkinter.</figcaption>
</figure>

#### Case 1: Simple experiment in Python

This experiment is a simple text-based instruction for a grasping task (<a href="#fig_usecase">Figure 3</a> A). The participant is prompted by text in a [Python tkinter](https://docs.python.org/3/library/tkinter.html) window to continuously open and close either their left or right hand. The experiment requires neural data as the input device and generates a StreamOutlet to send markers that inform about the start and end of the experiment and of the trials. The neural data is acquired from a stream with `name=Micromed`, `type=EEG`, `source\_id=micm01`. These values are all set by the user. As **T-Rex** will search for all three options (name, type or source_id), only one needs to be provided. Therefore, the option under `device_inputs` in `grasping\config.yaml` is set to `eeg` (case-insensitive). Next, the Marker StreamOutlet that the experiment itself will generate has `source\_id=emuidw22`. When the `Experiment` class runs the experiment command (`command` field in `grasping\config.yaml`) it will search for this streams. Therefore, the `exp_outlet` field is set to `emuidw22`. Finally, since the grasping experiment is Python-based, the `command` should use Python to call the script with the command: `python .\exp_module\experiments\grasping\grasping.py`.

When these options are set, the experiment is ready to go and can be started by pressing the start button on the *Home* window. The Tk window opens and waits for the spacebar to be pressed. Once pressed, the experiment starts and is locked on the topmost position upon completion. When the experiment is finished and closed (i.e., the command call ends and returns to the Experiment class), the **Experiment** instance stops the recording and saves the data.

#### Case 2: Simple experiment in a WebUI

From the Web Interface, participants and researchers can access the main functionalities of **T-Rex**, allowing the potential execution of the system on a headless server, different from the interface that interacts with the participants. The system that runs **T-Rex** could create a local network that serves the experiments to different devices (tablets, laptops, smartphones), removing the need for an active internet connection which could render the execution unsafe.

To illustrate this paradigm, we created the grasping web experiment, which mimics the behavior of the "grasping" experiment but in a web format (<a href="#fig_usecase">Figure 3</a> B). Given that this experiment consists of a Single Page Application (SPA), it can be wholly executed on any device with access to a web browser, like laptops, tablets, and smartphones. The grasping web experiment also illustrates options other than a Tk window for experimenting.

For constructing the experiment, we used HTML, CSS (using Bootstrap5 for the responsiveness and other visual aspects), and JavaScript for the behavior. The device input is the same as in the Tk implementation as well as the StreamOutlet containing the markers, thus, the `device_inputs` and `exp_outlet` are the same. The difference is in the command executed to start the experiment. In this case, `start .\exp_module\experiments\graspingWeb\index.html|` is used.

Once the experiment is started on the *Home* window, the **Experiment** instance opens another tab on the browser displaying the "grasping_web" experiment. The experiment starts when the participant presses the green "Start" button. When the experiment is finished, the participant or researcher is prompted to press a red button to close the experiment. The GraspingWeb command call is finished at button-press and returns to the **Experiment** instance, stopping the recording and saving the data.

#### Case 3: Multiple devices

Lastly, we included a 3D hand-tracking experiment, where the goal is to hold the cursor (a black circle) on the target (a red circle). The cursor can be moved in 3d, where the third dimension controls the size of the circle (<a href="#fig_usecase">Figure 3</a> C). In this case, the hand tracking is done by the [LeapMotion controller](https://www.ultraleap.com/product/leap-motion-controller/). We have provided a `.exe` that reads the data from the tracker and sends it to an LSL StreamOutlet with `name=LeapLSL`, `type=Coordinates`, `source\_id=LEAPLSL01`. In addition to the hand-tracking information, we also need neural activity, for which we use the same StreamOutlet as described in case 2. Lastly, the experiment is implemented in a Python Tk window and generates a marker Stream similar to the streams described in the previous use case with `Source\_id=BUBBLE01`. Thus, to set up the configuration for this experiment, we set command to `python .\exp_module\experiments\Bubbles\bubbles.py`, `exp_outlet` to `BUBBLE01` and device_inputs to `LEAPLSL01` (the tracking information stream) and `eeg` (the neural data stream). To run the experiment, the researcher should start the device stream before the experiment is started in the *Home* screen. (i.e. run the `.exe` first).

### Adding new experiments

The following steps describe how to add a new experiment from scratch to **T-Rex**:

1. Create the experiment folder inside the directory `./exp_module/experiments/`.
2. Create the experiment configuration file (`config.yaml`) inside the new folder.
3. Adjust the fields to the specific experiment.

After completing these initial steps, the experiment should be visible from the Admin Configuration panel. The researcher can set the experiment as "visible" from the admin panel by selecting its corresponding check mark. If configured as "visible", it should appear on the *Home* window, and it can be executed by clicking on its respective button.

It is worth mentioning that some parameters might need to be revised when porting an already-configured version of **T-Rex** to a different OS. For example, the parameter `command`, when used on Windows to start a python experiment, the definition is the following:

```python
command: python .\exp_module\experiments\example\example_experiment.py
```

However, when used on Unix or Unix-like systems, the definition changes to the following:

```python
command: python ./exp_module/experiments/example/example_experiment.py
```

The difference comes because `"/"` is the path separator on Unix and Unix-like systems, and Microsoft uses `"\"`.

There might be other scenarios where the parameter `command` might differ between OS, so we recommend revising each experiment configuration file when porting the platform to a different OS.

Even so, incorporating new experiments into `T-Rex` is seamless. Several experiments can be quickly integrated into the platform with just a few easy steps.

## Credits and article link
The collaborators of this project are:
[Joaquín Amigó-Vega](https://neuralinterfacinglab.github.io/people/joaquin_amigo/index.html), [Maarten C. Ottenhoff](https://neuralinterfacinglab.github.io/people/Maarten_Ottenhoff/index.html), [Maxime Verwoert](https://neuralinterfacinglab.github.io/people/maxime_verwoert/index.html), [Pieter Kubben](https://neuralinterfacinglab.github.io/people/pieter_kubben/index.html), and [Christian Herff](https://neuralinterfacinglab.github.io/people/christian_herff/index.html).

We want to thank also the members of the [Neural Interfacing Lab](https://neuralinterfacinglab.github.io/).
