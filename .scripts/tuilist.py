#!/usr/bin/python3

import curses
import json
import os
import re
from pathlib import Path

# Check a playlist json file exists
json_path = Path(Path.home() / ".config" / "playlist.json")
if not json_path.exists():
    # Creates an example config if no config is found
    print(f"Playlist data not found at {json_path}, an example one has been created")
    example = {"folders": ["FLAC", "MP3 No Parity"], "playlists": ["Max Atk", "Running", \
            "Chillin", "Singing"], "songs": {}}

    # Write the new config to disk
    json_file = open(json_path, "w")
    json.dump(example, json_file, indent = 4)
    json_file.close()
    quit()

# Load the main music path from an environmental variable
music_path = Path(os.environ["MUSIC_PATH"])

# Load the playlist information json file
json_file = open(json_path, "r")
json_data = json.load(json_file)
json_file.close()

# Walk through each of the watch folders specified by the json
songs = []
for i in range(len(json_data["folders"])):
    folder = Path(music_path / json_data["folders"][i])
    for path, subdir, files in os.walk(folder):
        for file in files:
            # Ignore any files that are not audio
            if os.path.splitext(file)[1] not in [".flac", ".FLAC", ".mp3", ".MP3"]:
                    continue

            # Check if the song already exists in the json
            entry = list(os.path.splitext(file)[:2])
            if entry[0] not in json_data["songs"]:
                # Get the path of each song
                entry.append(path)

                # Add a -1 entry for each playlist we have
                entry.append([-1] * len(json_data["playlists"]))

                # Append all this information to the array
                songs.append(entry)

# Sort the songs we currently have
songs.sort()

# Add songs to the list that were read in the database
for i in json_data["songs"].keys():
    songs.append([i, json_data["songs"][i][0], json_data["songs"][i][1], json_data["songs"][i][2]])

# Print the interactive playlist menu
def menu(main, height, width, selected, start):
    main.clear()

    # Print the horizontal borders
    main.addstr(0, 0, "╔═[Song title]" + "═" * (width - 15) + "╗")
    main.addstr(height - 1, 0, "╚" + "═" * (width - 2))

    # Display playlist titles above their respective check boxes
    offset = width - 10 * (len(json_data["playlists"]) + 1)
    main.addstr(0, offset - 2, "[Playlists]")
    for i in range(len(json_data["playlists"])):
        main.addstr(0, offset + 10 * (i + 1), "[" + json_data["playlists"][i] + "]")

    for i in range(height - 2):
        # Draw vertical borders
        main.addstr(i + 1, 0, "║")
        main.addstr(i + 1, width - 1, "║")

        # Truncate the song title if required
        title = songs[i + start][0]
        if len(title) > offset + 8:
            title = title[:int(offset + 5)] + "..."

        # If a given song is selected, highlight it
        if i + start == selected:
            main.attron(curses.color_pair(1))
            main.addstr(i + 1, 1, title)
            main.attroff(curses.color_pair(1))
        else:
            main.addstr(i + 1, 1, title)

        # Draw each of the playlist check boxes
        for j in range(len(json_data["playlists"])):
            display = "[  ---  ]"
            if songs[start + i][3][j] == 0:
                display = "[       ]"
            elif songs[start + i][3][j] == 1:
                display = "[  ***  ]"

            main.addstr(i + 1, offset + 10 * (j + 1), display)

    main.refresh()

# Write changes to the json playlist file
def write_out(json_data):
    # Clear the existing json entry, and make a copy of sorted songs to insert
    json_data["songs"] = {}
    s_songs = songs.copy()
    s_songs.sort()

    # Add songs to the list from the database
    for i in range(len(s_songs)):
        # Ignore reading songs with no playlist data
        if s_songs[i][3] == [-1] * len(json_data["playlists"]):
            continue

        # Create a dictionary entry for songs with valid playlist data
        json_data["songs"][s_songs[i][0]] = s_songs[i][1], s_songs[i][2], s_songs[i][3]

    # Open the json file and write the changes to it
    json_file = open(json_path, "w")
    json.dump(json_data, json_file, indent = 4)
    json_file.close()


# Export playlists from database
def export(json_data):
    # Write to the database before exporting
    write_out(json_data)

    # For every playlist, check if each song is in it
    for i in range(len(json_data["playlists"])):
        playlist = []

        for key in json_data["songs"].keys():
            song = json_data["songs"][key]

            if song[2][i] == 1:
                # Create a string such that formatting is correct for an m3u
                entry = re.sub("^.*Music", "/storage/emulated/0/Music", song[1])
                playlist.append(entry + "/" + key + song[0])

        # Output playlists to the current working directory
        title = json_data["playlists"][i] + ".m3u"
        outpath = Path(Path.cwd() / title)
        with open(outpath, "w") as out:
                out.write("\n".join(playlist))


# Define the programs main loop to be run with curses
def main(main):
    # Turn off cursor blinking
    curses.curs_set(0)

    # Set the colour scheme for selected song
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Get the height and width of the terminal
    term_h, term_w = main.getmaxyx()

    # Set the height to terminal height, or song list if smaller
    size = len(songs) + 2
    if size > term_h:
        size = term_h

    # Specify the starting and current selected rows
    start = 0
    selected = 0

    # Print the menu initially
    menu(main, size, term_w, selected, 0)

    while True:
        # Get the users key presses
        key = main.getch()

        # Change the selected line with the arrow or vim keys
        if key in [curses.KEY_UP, 75, 107] and selected > 0:
            selected -= 1
        elif key in [curses.KEY_DOWN, 74, 106] and selected < len(songs) - 1:
            selected += 1

        # Modify playlist selection by the number keys, up to 9
        elif key in range(49, 49 + len(json_data["playlists"])):
            if songs[selected][3][key - 49] == 1:
                songs[selected][3][key - 49] = 0
            else:
                songs[selected][3][key - 49] = 1

            # If a new song, zero it if a selection is made
            for i in range(len(songs[selected][3])):
                if songs[selected][3][i] == -1:
                    songs[selected][3][i] = 0

        # If 0 is pressed, add the song to the database, but not to any playlists
        elif key == 48:
            songs[selected][3] = [0] * len(json_data["playlists"])

        # If Q or q is pressed, quit
        elif key in [81, 113]:
            quit()

        # If W or w is pressed, write to the json file
        elif key in [87, 119]:
            write_out(json_data)
            main.addstr(size - 1, 2, "[Written out to json file]")
            continue

        # If E or e is pressed, quit
        elif key in [69, 101]:
            export(json_data)
            main.addstr(size - 1, 2, "[Exported playlists to files]")
            continue

        # Push the start line up or down as needed
        if selected < start:
            start -= 1
        elif selected - size >= start - 2:
            start += 1

        # Refresh the menu
        menu(main, size, term_w, selected, start)

# Run the main program loop with curses
curses.wrapper(main)
