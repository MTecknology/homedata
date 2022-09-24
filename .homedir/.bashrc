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

export TH_SRC='https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/current/amd64/iso-cd/firmware-11.5.0-amd64-netinst.iso' TH_CKSUM='2fde00391688f569d2df4ac655f9bda32f6522635514a28de7ef10e684c752af296c4e4eadca7a2afba487780ef559a61051131e7f6e758d7792fa87660b57b8'
