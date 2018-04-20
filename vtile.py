"""
An easy way to tile windows vertically, specifying the number of columns.

Throughout the script, these variables are used as defined:
    position: column number from left to right
    columns: the number of total columns
    margin: a [N, E, S, W] margin of pixels around the edge of the screen
    border: a [width, height] size of window decorations, based on your current
            window theme.
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
    return map(int, call('xdotool getdisplaygeometry').split())


def get_new_size(columns, margin, border):
    """ Get the new size of a window for resizing and moving purposes. """
    screenWidth, screenHeight = get_screen_size()
    width = (screenWidth - sum(margin[1::2])) // columns - border[0]
    height = screenHeight - sum(margin[0::2]) - border[1]
    return width, height


def resize(window, width, height):
    """ Resize a window to (width, height) pixels. """
    call('xdotool windowsize %s %i %i' % (window, width, height))


def move(window, x, y):
    """ Move a window to an (x, y) pixel position. """
    call('xdotool windowmove %s %i %i' % (window, x, y))


def main(position, columns, margin, border):
    """ Resize and move the window. """

    window = get_active_window()
    width, height = get_new_size(columns, margin, border)

    resize(window, width, height)

    x = position * (width + border[0]) + margin[3]
    y = margin[0]

    move(window, x, y)


if __name__ == '__main__':

    defaultPosition = 0
    defaultColumns = 3
    defaultMargin = [0, 0, 0, 40]
    defaultBorder = [10, 31]

    parser = argparse.ArgumentParser(description='Vertically tile windows.')

    parser.add_argument('-p', '--position', type=int, default=defaultPosition,
                        help=('The column number to move the window to. The '
                              'default is %i.' % defaultPosition))

    parser.add_argument('-c', '--columns', type=int, default=defaultColumns,
                        help=('The number of columns on the screen. The '
                              'default is %i' % defaultColumns))

    parser.add_argument('-m', '--margin', type=int, nargs=len(defaultMargin),
                        default=defaultMargin,
                        help=('The number of pixels around the edge of the '
                              'screen (N, E, S, W) to ignore. The default '
                              'is %s' % str(defaultMargin)))

    parser.add_argument('-b', '--border', type=int, nargs=len(defaultBorder),
                        default=defaultBorder,
                        help=('The number of pixels on each window (Width, '
                              'Height) for theme decoration. The default is '
                              '%s' % str(defaultBorder)))

    # Parse the arguments
    args = parser.parse_args()

    # Resize and move the window
    main(args.position, args.columns, args.margin, args.border)
