#[ -z "$PS1" ] && return
HISTCONTROL=ignoredups:ignorespace
shopt -s histappend
HISTSIZE=100000
HISTFILESIZE=200000
shopt -s checkwinsize
PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
[[ -f ~/.bash_aliases ]] && . ~/.bash_aliases
declare -x PATH="$PATH:$HOME/.bin"
declare -x PATH="$PATH:/usr/local/sbin"

export EMAIL='Michael Lustfield <michael@lustfield.net>'
export DEBEMAIL='michael@lustfield.net'
export DEBFULLNAME='Michael Lustfield'
export DEBSIGN_KEYID='765AD085'

export TH_SRC='https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current/amd64/iso-cd/firmware-11.3.0-amd64-netinst.iso' TH_CKSUM='eba7ce7823681a610f9f23d6468976517ed92b6b90acec4ac55df62b0a090050bba0145ef5c07f544b92569cd10e9572f4e9f7c3415b3323abffa51cd7c5d4f4'
