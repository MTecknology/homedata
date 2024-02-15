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
