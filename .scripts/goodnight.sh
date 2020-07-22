#!/bin/bash
# Displays a message when shut down

# Stores all the shutdown messages
array[0]="It's been fun"
array[1]="Until next time"
array[2]="Go get 'em tiger"
array[3]="Make it so"
array[4]="See you on the other side"
array[5]="Exhibit no restraint"
array[6]="Rip and tear"
array[7]="Have just the greatest day"
array[8]="Avenge me"
array[9]="Stay safe"
array[10]="Situation normal"
array[11]="PROTOCOL <3"
array[12]="Fly, you fool"
array[13]="Never surrender"
array[14]="See you Space Cowboy"
array[15]="End of the line"
array[16]="A leaf on the wind"
array[17]="You are who you choose to be"
array[18]="Finish the fight"
array[19]="Change da world, my final message. Goodbye"
array[20]="Protocol 3: Protect the pilot"
array[21]="Tell 'em to make it count"
array[22]="Any way the wind blows..."
array[23]="You'll find me chasing the sun"
array[24]="It'll all be okay"
array[25]="We can be heroes, just for one day"
array[26]="You and I are gonna live forever"
array[27]="Slide away"
array[28]="I wanna be the hunter not the hunted, I wanna be the killer not the prey"
array[29]="The dance of life, the hunter and the agile prey"
array[30]="We never lost control"
array[31]="Don't wait or play to indecision!"
array[32]="Hit 'em right between the eyes"
array[33]="We're gonna take over!"
array[34]="I just wanna cause a little entropy"
array[35]="How do we sleep while our beds are burning?"
array[36]="Three, two, one, let's jam!"
array[37]="We'll all float on okay"
array[38]="Hello, goodbye, I'll see you in hell!"
array[39]="Here I am, stuck in the middle with you"

# Function to print center text
print_center() {
	cols=$(tput cols) 
	printf "\n%*s\n" $(((${#1}+cols)/2)) "$1"
}

# Displays the appropriate opening message
clear
if [ "$1" = -r ]; then
	print_center "[ RESTARTING ]"
else
	print_center "[ SHUTTING DOWN ]"
fi

# Picks a random quote to send
index=$((RANDOM%${#array[@]}))

# Displays a message from the array, on a delay
sleep 1
print_center "${array[$index]}"
sleep 3

# Shuts down or restarts appropriately
if [ "$1" = -r ]; then
	shutdown now -r
else
	shutdown now
fi
