#!/bin/sh

compton &
openrazer-daemon &
#synclient PalmDetect=1 &
#synclient PalmMinWidth=1 &
#nvidia-settings --load-config-only &
/home/michael/.bin/configure_x

feh --bg-scale /home/michael/.wallpaper.png &
stalonetray -p --dockapp-mode &
redshift-gtk &
pulseaudio &
cbatticon &
#mate-volume-control-applet &

#thunar --daemon &
#xfce4-volumed &
(sleep 0.5 && tdc -w 110 -f "%x %H:%M") &

#(sleep 1 && rm -rf ~/.mozilla/firefox/*/{Cache,places.sqlite,places.sqlite-journal,urlclassifier3.sqlite,urlclassifierkey3.txt,XPC.mfasl,XUL.mfasl} ) &

[ `/usr/bin/cksum '/home/michael/.bin/vault' | /usr/bin/cut -d ' ' -f 1` -eq '639895823' ] || /usr/bin/zenity --info --text='ALERT: vault cksum changed'
#xbacklight -set 55 &
