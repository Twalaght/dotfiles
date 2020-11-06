#!/bin/sh

# Find the current brightness value
current=$(light -G)
current=${current%.*}

# Determine brightness level, defaults to 5, or a value of 10
level=5
if [ "$current" -lt 1 ]; then level=1;
elif [ "$current" -lt 2 ]; then level=2;
elif [ "$current" -le 3 ]; then level=3;
elif [ "$current" -le 5 ]; then level=4;
elif [ "$current" -le 10 ]; then level=5;
elif [ "$current" -le 20 ]; then level=6;
elif [ "$current" -le 40 ]; then level=7;
elif [ "$current" -le 70 ]; then level=8;
elif [ "$current" -le 100 ]; then level=9;
fi

# Increments, decrements, reports, or sets the brightness level
# Exits early if not incrementing or decrementing brightness
if [ "$1" = "+" ]; then level=$((level+1));
elif [ "$1" = "-" ]; then level=$((level-1));
elif [ "$1" = "=" ]; then echo "$level"; exit;
elif [ -n "$1" ]; then light -S "$1"; exit;
fi

# Limits the brightness value if it is out of bounds
if [ "$level" -lt 1 ]; then level=1;
elif [ "$level" -gt 9 ]; then level=9;
fi

# Sets the brightness value based on the given level
case $level in
	1) light -S 0.625;;
	2) light -S 1.25;;
	3) light -S 2.5;;
	4) light -S 5;;
	5) light -S 10;;
	6) light -S 20;;
	7) light -S 40;;
	8) light -S 70;;
	9) light -S 100;;
esac
