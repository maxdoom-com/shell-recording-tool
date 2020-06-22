This tool runs the rendering of a script in the current terminal.
( Try ./recorder.py run --help )


Installation
==================================================================

```sh
python3 -m venv env
env/bin/pip install -r requirements.txt
```

[![Installation tutorial on youtube](https://img.youtube.com/vi/kXG2_LJ7ttQ/0.jpg)](https://www.youtube.com/watch?v=kXG2_LJ7ttQ)


Required external commands
==================================================================

- xdotool
- xwd
- ffmpeg


Running
==================================================================

env/bin/python3 recorder.py input.script output

INPUT   the file name of the script to render
OUTPUT  the file name of the video without extension (will create OUTPUT.mkv)


Example of a script
==================================================================

```
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
```


Script syntax
==================================================================

- Lines starting with $ are typed in.
- Lines starting with > are commands that are enetered in type
  mode, executed and output is produced line by line.
- All lines starting with % are commands:
    - % clear ... clear the screen
    - % splash ... start printing text without makeing a snapshot
    - % type ... start typing as if you were a human
    - % line ... start typing line by line
    - % snap ... take a snapshow now
    - % wait <int:seconds> ... wait some seconds
    - % exec <string:command> ... execute a command, output is
                                  printed line by line
    - % framerate <int:framerate> ... set the framerate
    - % end ... end the program
    - % speed min_frames max_frames nonword_frames line_frames
        - ... typing speed is randomly chosen between min_... and max_frames
        - ... nonword_frames is the amount of frames for non word letters
        - ... line_frames is the amount of frames after each typed line



Adding sound
========================================================================

```sh
ffmpeg -i your-video.mkv -i your-sound.wav -c:v copy -c:a aac -shortest your-video-with-sound.mkv
```


