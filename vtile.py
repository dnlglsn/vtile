"""
An easy way to tile windows, specifying the location, number of rows, and
number of columns.

Throughout the script, these variables are used as defined:
    location: [row, column] position from top to bottom and left to right
    rows: the number of total rows
    columns: the number of total columns
    padding: a [N, E, S, W] padding of pixels around the edge of the screen
    border: a [width, height] size of window decorations, based on your current
            window theme.
    margin: a number of empty pixels surrounding each window

References:
https://askubuntu.com/questions/682027/arrange-windows-by-script
https://unix.stackexchange.com/questions/14159/how-do-i-find-the-window-dimensions-and-position-accurately-including-decoration
"""

import argparse
import subprocess


def call(command):
    return subprocess.check_output(command, shell=True).decode().strip()


def get_active_window():
    """ Get the ID of the active window. """
    return call('xdotool getactivewindow')


def get_screen_size():
    """ Return an integer list (width, height) of the current screen. """
    cmd = "xdpyinfo | awk '/dimensions:/ { print $2; exit }'"
    return map(int, call(cmd).split('x'))


def get_border():
    cmd = "xprop _NET_FRAME_EXTENTS -id %s | cut -d '=' -f 2 | tr -d ' '"
    return list(map(int, call(cmd % get_active_window()).split(',')))


def get_new_size(columns, rows, padding):
    """ Get the new size of a window for resizing and moving purposes. """
    screenW, screenH = get_screen_size()
    left, right, top, bottom = get_border()
    width = (screenW - sum(padding[1::2])) // columns - left - right
    height = (screenH - sum(padding[0::2])) // rows - top - bottom
    return width, height


def get_current_pos():
    """ The (x, y) in pixels of the current window, without the border. """
    cmd = "xdotool getwindowgeometry %s | awk '/Position:/ { print $2; exit }'"
    return list(map(int, call(cmd % get_active_window()).split(',')))


def get_current_size():
    """ The (w, h) in pixels of the current window, without the border. """
    cmd = "xdotool getwindowgeometry %s | awk '/Geometry:/ { print $2; exit }'"
    return list(map(int, call(cmd % get_active_window()).split('x')))


def resize(window, width, height):
    """ Resize a window to (width, height) pixels. """
    call('xdotool windowsize %s %i %i' % (window, width, height))


def move(window, r, c):
    """ Move a window to an (x, y) pixel position. """
    call('xdotool windowmove %s %i %i' % (window, c, r))


def main(location, rows, columns, padding, margin):
    """ Resize and move the window. """

    window = get_active_window()
    width, height = get_new_size(columns, rows, padding)

    resize(window, width - margin * 2, height - margin * 2)

    left, right, top, bottom = get_border()

    r = location[0] * (height + top + bottom) + padding[0] + margin
    c = location[1] * (width + left + right) + padding[3] + margin

    move(window, r, c)


def _move_to_row(padding, margin, row):
    """ Move the window down, setting the number of rows to 2. """

    window = get_active_window()

    _, screenH = get_screen_size()
    left, right, top, bottom = get_border()
    height = (screenH - sum(padding[0::2])) // 2 - top - bottom
    width, _ = get_current_size()
    c, _ = get_current_pos()

    resize(window, width, height - margin * 2)

    r = row * (height + top + bottom) + padding[0] + margin

    move(window, r, c - left - right)


def move_up(padding, margin):
    _move_to_row(padding, margin, 0)


def move_down(padding, margin):
    _move_to_row(padding, margin, 1)


if __name__ == '__main__':

    defaultLocation = [0, 0]
    defaultColumns = 3
    defaultRows = 1
    defaultPadding = [10, 10, 10, 50]
    defaultMargin = 10

    parser = argparse.ArgumentParser(description='Vertically tile windows.')

    parser.add_argument('-l', '--location', type=int, nargs=len(defaultLocation),
                        default=defaultLocation,
                        help=('The [row, column] to move the window to. The '
                              'default is %s.' % str(defaultLocation)))

    parser.add_argument('-c', '--columns', type=int, default=defaultColumns,
                        help=('The number of columns on the screen. The '
                              'default is %i' % defaultColumns))

    parser.add_argument('-r', '--rows', type=int, default=defaultRows,
                        help=('The number of rows on the screen. The '
                              'default is %i' % defaultRows))

    parser.add_argument('-p', '--padding', type=int, nargs=len(defaultPadding),
                        default=defaultPadding,
                        help=('The number of pixels around the edge of the '
                              'screen (N, E, S, W) to ignore. The default '
                              'is %s' % str(defaultPadding)))

    parser.add_argument('-m', '--margin', type=int, default=defaultMargin,
                        help=('The number of empty pixels surrounding each '
                              'window. Default is %s.' % str(defaultMargin)))

    parser.add_argument('-u', '--up', action='store_true',
                        help=('Move a window to the top row setting the number'
                              ' of rows to 2'))

    parser.add_argument('-d', '--down', action='store_true',
                        help=('Move a window to the bottom row setting the'
                              ' number of rows to 2'))

    # Parse the arguments
    args, leftovers = parser.parse_known_args()

    # Do everything twice because terminal windows are dumb.

    # First check if we are just moving it up or down
    if args.up:
        move_up(args.padding, args.margin)
        move_up(args.padding, args.margin)
    elif args.down:
        move_down(args.padding, args.margin)
        move_down(args.padding, args.margin)
    # If not, call as normal
    else:
        # Resize and move the window
        main(args.location, args.rows, args.columns, args.padding, args.margin)
        main(args.location, args.rows, args.columns, args.padding, args.margin)
