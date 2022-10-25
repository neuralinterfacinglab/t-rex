import pygame as pyg
import numpy as np
from pylsl import StreamInlet, StreamOutlet, StreamInfo, resolve_byprop
from time import perf_counter


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LSL_LEAP_SOURCE_ID = "LEAPLSL01"

# Boundaries from LEAP coordinate system [determined by hand]
LEAP_MAX_X = 300  # [-300, 300]
LEAP_MAX_Y = 150  # [100, 400]
LEAP_MAX_Z = 200  # [-200, 200]

PYGAME_MIN_RADIUS = 0  # Will be offset by +10
PYGAME_MAX_RADIUS = 100
HALF_RADIUS = 50

n_targets = 5

class game():

    def __init__(self, x, y):
        self.size_x = x
        self.size_y = y
        self.screen = None
        self.half_x = x * 0.5
        self.half_y = y * 0.5

        # UI objects
        self.text = None
        self.text_rect = None
        self.cursor_obj = None
        self.cursor_color = BLACK
        self.target_obj = None
        
        # Flags
        self.waiting_for_go = True
        self.is_running = True
        self.target_reached = True

        # Experiment
        self.cursor = [self.half_x, self.half_y, HALF_RADIUS]
        self.current_target = []
        self.targets = []
        self.timer = 0
        self.trial_num = -1

        # LSL
        self.inlet = None
        self.outlet = None

        pyg.init()
        
        self.setup_screen(x, y)


    def setup_screen(self, x, y):
        self.screen = self.set_screen_size(x, y)
        pyg.display.set_caption('Bubbles')

    def set_screen_size(self, x=None, y=None):
        x = self.size_x if not x else x
        y = self.size_y if not y else y

        return pyg.display.set_mode((x, y))

    def draw_text(self, text):
        font = pyg.font.Font(None, 36)
        self.text = font.render(text, True, (0, 0, 0))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.size_x // 2, self.size_y // 2)

    def set_targets(self, n):
        '''
        Creates n targets to draw on screen
        Each '3D' target is represented as 2D coordinate and a radius.
        '''

        # TODO: Update to constants
        margin = .05  # % from borders
        x = np.random.randint(0+self.size_x*margin , self.size_x-self.size_x*margin, n)
        y = np.random.randint(0+self.size_y*margin , self.size_y-self.size_x*margin, n)
        radii = np.random.randint(10, 110, n)  # TODO: 10 = middle (0 in leapspace), 1 = furthest to screen, 20 = closest to screen. Will be trial and error
        self.targets = np.vstack((x, y, radii)).T

    def create_leap_inlet(self, timeout=10):
        streams = resolve_byprop('source_id', LSL_LEAP_SOURCE_ID)
        self.inlet = StreamInlet(streams[0])

    def create_outlet(self):
        info = StreamInfo('Bubble', 'Markers', 1, 0, 'string', 'BUBBLE01')
        self.outlet = StreamOutlet(info)

    def send_metadata(self):
        # TODO: Coordinate system
        
        pass

    def create_new_target(self):
        self.current_target = self.targets[0, :]
        self.targets = np.delete(self.targets, 0, axis=0)
        self.target_reached = False
        self.trial_num += 1
        self.outlet.push_sample([f'{self.trial_num};new_target;{self.current_target}'])

    def draw_target(self):
        self.target_obj = pyg.draw.circle(
                            self.screen,
                            color=RED,
                            center=self.current_target[0:2],
                            radius=self.current_target[2])

    def draw_cursor(self):
        self.cursor_obj = pyg.draw.circle(
                                self.screen,
                                color = self.cursor_color,
                                center = self.cursor[0:2],
                                radius = self.cursor[2])

    def change_cursor_coordinate_system(self, x, y, z):
        '''
        pos = position in LEAP coordinates
        '''

        # direction * (v - leap_offset) / leap_scale * pygame_scale + pygame_offset
        x = x / LEAP_MAX_X * self.half_x + self.half_x
        y = -(y-250) / LEAP_MAX_Y * self.half_y + self.half_y
        z = z / LEAP_MAX_Z * HALF_RADIUS + HALF_RADIUS + 10
        
        return [x, y, z]

    def update_cursor_position(self):
        chunk = self.inlet.pull_chunk()
        if chunk[0]:
            pos = chunk[0][-1][7:10]
            self.cursor = np.array(self.change_cursor_coordinate_system(x=pos[0], y=pos[1], z=pos[2]))

    def cursor_on_target(self):
        return all([
            np.linalg.norm(self.cursor[0:2] - self.current_target[0:2]) < 15,  # Close enough XY
            abs(self.cursor[2] - self.current_target[2]) < 5 ])                # Close enough Z (different because scale)
        
    def check_target_acquired(self):
        if self.timer:
            if perf_counter() - self.timer > 1:
                self.target_reached = True
                self.reset_cursor()
                self.outlet.push_sample([f'{self.trial_num};target_reached;{self.current_target}'])
        else:
            self.cursor_color = GREEN
            self.timer = perf_counter()

    def reset_cursor(self):
        self.cursor_color = BLACK

    def reset_timer(self):
        self.timer = None

    def setup(self):
        '''
        1. Draw Press space to continue      
        2. Wait for keypress
        3. If pressed:
            Start mainloop    
        '''

        self.create_leap_inlet()
        self.create_outlet()
        self.set_targets(n_targets)
        self.draw_text('Press space to continue.')
        self.send_metadata()

    def wait_for_go(self):
        while self.waiting_for_go:
            self.screen.fill(WHITE)
            self.screen.blit(self.text, self.text_rect)

            for event in pyg.event.get():
                if event.type == pyg.KEYUP and event.key == pyg.K_SPACE:
                    # self.waiting_for_go = False
                    return

                if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()

            pyg.display.update()

    def run_experiment(self):
        
        self.outlet.push_sample(['experiment_started'])

        while self.is_running:
            
            if self.target_reached:
                self.create_new_target()
                if self.targets.size < 1:
                    break
            
            self.update_cursor_position()

            # Draw
            self.screen.fill(WHITE)

            self.draw_target()
            self.draw_cursor()

            if self.cursor_on_target():
                self.check_target_acquired()
            else:
                self.reset_cursor()
                self.reset_timer()

            # Check for events
            for event in pyg.event.get():
                # print(event)
                if event.type == pyg.KEYUP and event.key == pyg.K_SPACE:
                    # Debug
                    # self.waiting_for_go = False
                    self.target_reached = True

                if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()

            pyg.display.update()

    def finish(self):
        self.draw_text('Experiment Finished!')
        self.outlet.push_sample(['experiment_finished'])
        while True:
            self.screen.fill(WHITE)
            self.screen.blit(self.text, self.text_rect)

            for event in pyg.event.get():
                if event.type == pyg.KEYUP and event.key == pyg.K_SPACE:
                    # self.waiting_for_go = False
                    return

                if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()

            pyg.display.update()

    def run(self):
        self.setup()
        self.wait_for_go()
        self.run_experiment()
        self.finish()

def go():
    g = game(1600, 900)
    g.run()
    

if __name__=='__main__':
    go()

    print('Done')