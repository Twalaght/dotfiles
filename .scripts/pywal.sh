#!/bin/sh
# Wrapper for easy generation of themes, plus saving, loading, and resetting

# Ensures we have only one given argument
if [ "$#" != 1 ]; then
	echo 'usage: pywal [-s "save"] [-l "load"] [-r "reset"] [path/to/image]'
	exit
fi

if [ "$1" = -s ]; then
	# Saves the current colour scheme
	cp ~/.cache/wal/sequences ~/.cache/wal/sequencesBup
elif [ "$1" = -l ]; then
	# Loads a saved colour scheme
	cp ~/.cache/wal/sequencesBup ~/.cache/wal/sequences
elif [ "$1" = -r ]; then
	# Resets the colour scheme
	:> ~/.cache/wal/sequences
else
	# Generates the colour scheme from the given image
	wal --vte -i "$1"
fi
