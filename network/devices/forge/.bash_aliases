alias dput-ssh='dput ssh.upload.debian.org'
alias lintian-check='lintian -EviIL +pedantic' # file.changes
alias pbuilder-dist='echo NO #'

# Fantastic!
alias git-view='git log --all --graph --decorate --oneline --simplify-by-decoration'

# apt-get intsall ffmpeg libav-tools libaom-dev libaom0 ;; ffprobe
# for i in plexmediaserver sonarr radarr; do servite "$i" stop; done
# movie=
# minifi movie:
#  ffmpeg -i "orig/$movie" -hwaccel -vcodec libx264 -crf 24 "$movie"
#  ffmpeg -i "orig/$movie" -c:v libaom-av1 -crf 30 -b:v 0 -strict experimental "$movie"

alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

ssh() {
  if [[ "$2" == "" ]]; then
    command ssh "$1" -Xt screen -aAdr -RR work bash
  else
    command ssh $@
  fi
}

shrink_pdf() {
  input="$1"
  output='output.pdf'
  [[ "$2" == '' ]] || output="$2"
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$output" "$input"
}

# Debian Dev
alias lintian-check='lintian -EviIL +pedantic' # file.changes
alias build-unstable='rm -f debian/files; gbp buildpackage --git-pbuilder --git-dist=unstable --git-arch=amd64'
alias pbuilder-dist='echo NO #'
build() {
	# example: build stable 32
	dist="$1"; shift
	arch="$2"; shift
	[[ "$arch" == '32' ]] && arch='i386'
	[[ "$arch" == '64' ]] && arch='amd64'
	rm -f debian/files
	gbp buildpackage --git-pbuilder \
		--git-dist="$dist" \
		--git-arch="$arch" "$@"
}
update_builders() {
	for arch in i386 amd64; do
		for suite in experimental unstable stable; do
			sudo cowbuilder --update --override-config \
				--basepath="/var/cache/pbuilder/base-$suite-$arch.cow" \
				--distribution="$suite" \
				--architecture "$arch"
		done
	done
}
