#!/bin/bash
IFS=$'\n\t'

reply=`dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'PlaybackStatus'`
playing=1
#Check if song was playing beforehand
if [[ $reply == *Playing* ]]
then
	playing=0
fi

#Pausing spotify if playing
if [ $playing -eq 0 ]
then
	dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause
fi

#Muting all applications currently playing sound
regex='index: ([0-9]+)'
tmp=$(pacmd list-sink-inputs) 
 
indexes=()

for input in $tmp
do
	#echo $input
	if [[ $input =~ $regex ]]; then
		index="${BASH_REMATCH[1]}"
		pacmd set-sink-input-mute "$index" 1 > /dev/null 2>&1
		indexes+=($index)
	fi
done

#Waiting one sec, playing message, waiting another sec
sleep 1s
mplayer -af volume=10 -user-agent Mozilla "http://translate.google.com/translate_tts?tl=en_us&q=$(echo $* | sed 's#\ #\+#g')" > /dev/null 2>&1 ;
sleep 1s

#Unmuting previously muted
for i in ${indexes[@]}
do
	# Mute with argument 0, false -> unmute
	pacmd set-sink-input-mute "$i" 0 > /dev/null 2>&1
done

#Unpause if playing
if [ $playing -eq 0 ]
then
	dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause
fi
