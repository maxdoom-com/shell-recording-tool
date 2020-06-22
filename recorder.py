#!env/bin/python

import sys, shlex, subprocess, random, tempfile


def exec(cmd, capture_output=True):
    # execute a shell command and maybe return it's captured output
    result = subprocess.run( shlex.split(cmd), capture_output=capture_output )
    if capture_output:
        return result.stdout.decode().split('\n')


def rand(min, max):
    # get a random integer
    return random.randint(min, max)


class Output:
    # the output class encapsulates the video generation and all output operations
    def __init__(self, filename, tmp, framerate=25, prompt="~ > "):
        # init the output
        self._filename = filename
        self._framerate = framerate
        self._prompt = prompt
        self._seq = 0
        self._tmp = tmp
        self._mode = "type"
        self._min_frames = 2
        self._max_frames = 5
        self._nonword_frames = 10
        self._line_frames = 10
        self._window_id = int(exec('xdotool getactivewindow')[0])
        self._command_not_found = "sh: Command not found\n"

    def line(self, s, immediate=False):
        # print a line

        if self._mode == 'splash':
            self._print_line(s, immediate)

        elif self._mode == 'line':
            self._print_line(s, immediate)

        elif self._mode == 'type':
            # in type mode print it char by char
            for c in s:
                self._print_char(c, immediate)

    def clear(self):
        # clear the screen
        exec("clear", False)

    # def exec(self, cmdline, print=True):
    #     # execute a command
    #     if print:
    #         # print a prompt
    #         # print a command
    #         self.prompt()
    #         self.line(cmdline + "\n")
    #     # execute this command, and print the output immediately
    #     exec(cmdline, False)

    def exec(self, cmdline, print=True):
        # execute a command
        if print:
            # print a prompt
            # print a command
            self.prompt()
            self.line(cmdline + "\n")
    
        # execute this command, but print the lines slowly (one by one)
        try:
            output = exec(cmdline, True)
            for line in output:
                self._print_line(line+"\n", True)
        except IndexError:
            self._print_line("### "+cmdline+" ###\n", True)
            self._print_line(self._command_not_found, True)


    def snap(self, count=1):
        # make count snapshots
        for _ in range(count):
            exec(f'xwd -out {self._tmp}/{self._seq:08d}.xwd -id {self._window_id}', False)
            self._seq += 1

    def render_video(self):
        # render the video thru ffmpeg
        exec(f"ffmpeg -y -r {self._framerate} -i {self._tmp}/%08d.xwd -vcodec h264 -tune stillimage -crf 30 {self._filename}.mkv", False)

    def wait(self, seconds):
        # wait some seconds (by making some snapshots)
        self.snap(seconds * self._framerate)

    def _print_char(self, c, immediate=False):
        # print a character

        sys.stdout.write(c)
        sys.stdout.flush()
        if immediate:
            # ... but dont make a snapshot right now
            pass
        else:
            # ... and make some random snapshots to fake natural typing
            if (c >= 'a' and c <= 'z')\
            or (c >= 'A' and c <= 'Z')\
            or (c >= '0' and c <= '9'):
                # ... but only, if it's a letter or digit
                self.snap(rand(self._min_frames, self._max_frames))
            else:
                # ... and not, if it is not...
                self.snap(rand(self._max_frames, self._nonword_frames))


    def _print_line(self, s, immediate=False):
        # print a single line
        sys.stdout.write(s)
        sys.stdout.flush()
        if self._mode == 'splash':
            # in splash mode, we don't make a snap()-shot
            pass
        elif immediate:
            # print the line and make a snapshot, when done
            self.snap()
        else:
            # print the line and make some snapshots
            self.snap(self._line_frames)

    @property
    def framerate(self):
        # get the frame rate
        return self._framerate
    
    @framerate.setter
    def framerate(self, fps):
        # set the frame rate
        self._framerate = fps
    
    def prompt(self):
        # print the prompt
        print("~ > ", end="")
        sys.stdout.flush()
        self.snap()

    @property
    def mode(self):
        # get the printing mode
        return self._mode
    
    @mode.setter
    def mode(self, mode):
        # set the printing mode
        self._mode = mode

    def typing_speed(self, min_frames, max_frames, nonword_frames, line_frames):
        # set the various speeds (defaults are 2 5 10 10)
        self._min_frames = min_frames
        self._max_frames = max_frames
        self._nonword_frames = nonword_frames
        self._line_frames = line_frames


class Interpreter:
    # interpret the input script

    def __init__(self, input, output):
        self._input = input
        self._output = output

    def run(self):
        with open(self._input) as input:
            for line in input:
                self.interpret(line)
        self._output.render_video()

    def interpret(self, line):
        # interprets a single line
        import re

        def split(s):
            # this is an awk like split
            return re.split(r"\s{1,}", s.strip())

        if line.startswith('%'):
            # it's a control command
    
            cmd = split(line)

            if cmd[1] == "splash":
                # % splash -- produce a splash screen
                self._output.mode = 'splash'
            
            elif cmd[1] == "type":
                # % type -- set typing like printing mode
                self._output.mode = 'type'
            
            elif cmd[1] == "line":
                # % line -- set linewise printing mode
                self._output.mode = 'line'
            
            elif cmd[1] == "speed":
                # % speed <int:min_frames> <int:max_frames> <int:nonword_frames> <int:line_frames>
                # -- set various speeds (defaults: 2 5 10 10)
                self._output.typing_speed(int(cmd[2]), int(cmd[3]), int(cmd[4]), int(cmd[5]))
            
            elif cmd[1] == "snap":
                # % snap -- make a single snapshot
                self._output.snap()
            
            elif cmd[1] == "wait":
                # % wait <int:seconds> -- wait for some seconds
                self._output.wait(int(cmd[2]))
            
            elif cmd[1] == "clear":
                # % clear -- clean the screen
                self._output.clear()

            elif cmd[1] == "exec":
                # % exec <string:command> -- execute a command and print the result line by line
                self._output.exec(' '.join(cmd[2:]))

            elif cmd[1] == "framerate":
                # % framerate <int:framerate> -- set the framerate
                self._output.framerate = int(cmd[2])

            elif cmd[1] == "end":
                # % end -- end the script
                return

        elif line.startswith('$'):
            # typed commands with a prompt before it
            # these commands are always entered in typing mode
            self._output.prompt()
            if len(line) == 2:
                self._output.line("\n")
            else:
                self._output.line(line[2:])

        elif line.startswith('>'):
            # output of commands without a prompt, immediately showing up
            if len(line) == 2:
                self._output.line("\n", immediate=True)
            else:
                # self._output.line(line[2:], immediate=True)
                cmd = split(line)
                self._output.exec(' '.join(cmd[1:]))

        else:
            # just print the line
            self._output.line(line)


class Recorder:
    def run(self, input, output):
        """Run the rendering process of a script. ( Try recorder.py run --help )

        This command runs the rendering of a script in the current terminal.
        
        INPUT   the file name of the script to render
        OUTPUT  the file name of the video without extension


        Example of a script
        ==================================================================

        % clear
        % splash
        ###################################################
        # Hello World!                                    #
        ###################################################
        % wait 2
        % type
        $ whoami
        root
        $
        > whoami
        $
        % exec ls
        $
        % wait 3


        Script syntax
        ==================================================================

        - Lines starting with $ are typed in.
        - Lines starting with > are commands that are enetered in type
          mode, executed and output is produced line by line.
        - All lines starting with % are commands:
            % clear ... clear the screen
            % splash ... start printing text without makeing a snapshot
            % type ... start typing as if you were a human
            % line ... start typing line by line
            % snap ... take a snapshow now
            % wait <int:seconds> ... wait some seconds
            % exec <string:command> ... execute a command, output is
                                        printed line by line
            % framerate <int:framerate> ... set the framerate
            % end ... end the program
            % speed min_frames max_frames nonword_frames line_frames
                ... typing speed is randomly chosen between min_... and max_frames
                ... nonword_frames is the amount of frames for non word letters
                ... line_frames is the amount of frames after each typed line


        Required external commands
        ==================================================================

        - xdotool
        - xwd
        - ffmpeg

        """

        with tempfile.TemporaryDirectory() as tmp:
            i = Interpreter(input, Output(output, tmp))
            i.run()


    # def capture(self, output, frametate=25):
    #     """Capture another window and render it. ( Try recorder.py capture --help )
    # 
    #     ***NOT READY***
    # 
    #     1. Click the window you want to record.
    #     2. Press the <PRINT> key to start recording.
    #     3. Press the <PRINT> key again, to stop recording.
    # 
    #     You may repeat steps 2 and 3 as long as you like.
    # 
    #     Recording ends by pressing <CTRL>-<C>.
    #     """
    # 
    #     pass



if __name__ == '__main__':
    from fire import Fire
    Fire(Recorder())
