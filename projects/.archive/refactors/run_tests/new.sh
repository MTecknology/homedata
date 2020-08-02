#!/usr/bin/env bash
##
# Wrapper script for running integration tests and working with kitchen.
##


##
# Main / Main Operations
##

# Primary entry point for script execution
main() {
	check_packages || die 'Package requisites not met.'
	case "$OPERATION" in
		test) main_test || die 'Some (or all) tests failed.';;
		clean) main_clean || die 'Issue encountered while cleaning up test artifacts.';;
		update) main_update || die 'Issue encountered while updating vagrant boxes.';;
	esac
}

# Update vagrant boxes
main_update() {
	local err=0
	msg "Pruning old Vagrant boxes, updating boxes and exiting."
	vagrant box prune || die 'Issue encountered pruning vagrant boxes.'
	if [[ "$TARGET" == '' ]]; then
		msg 'Updating all boxes.'
		boxes=("$(vagrant box outdated --global | awk -F"'" '/outdated/ { print $2 }')")
		if [[ "${boxes[0]}" != '' ]]; then
			for box in "${boxes[@]}"; do
				vagrant box update --box "$box" || err=1
			done
		fi
	else
		msg 'Updating specified box.'
		vagrant box update --box "$TARGET" || err=1
	fi

	return $err
}

# Clean up test artifacts
main_clean() {
	cleanup || return 1
	return 0
}

# Run integration tests and clean up
main_test() {
	local err=0
	cleanup

	log "PARAMETERS: ${PARAMS[*]}"
	log "PLUGIN ARGS: ${PLUGIN_ARGS[*]}"

	msg 'Testing: start'
	for machine in $(kitchen list -b "$TARGET"); do
		msg "Running tests on: $machine"
		[[ "$KEEPLOGS" ]] && lf="&>'$LOGFILE.$machine'"
		if eval kitchen test "$machine" $lf; then
			log "PASSED: $machine"
		else
			log "FAILED: $machine"
			err=1
		fi
	done
	msg 'Testing: end'


	printf '#- Results: start\n%s\n#- Results: end\n' "$(< "$LOGFILE")"

	if [[ "$KEEPLOGS" ]]; then
		msg "Test logs retained at $LOGFILE and $LOGFILE.{machine}."
	else
		rm "$LOGFILE"*
	fi

	[[ "$CLEANUP" ]] && cleanup

	return $err
}

# Clean up test machines and artifacts
cleanup() {
	local err=0
	msg 'Running clean up tasks.'

	[[ "$HAS_PLUGIN" ]] && plugin_cleanup
	kitchen destroy "$TARGET" &>/dev/null || err=1

	IFS=' ' read -r -a machines <<< "$(kitchen list -b "$TARGET")"
	IFS=$'\n' read -r -a boxes <<< "$(vagrant global-status | grep "$PWD")"

	for machine in "${machines[@]}"; do
		local nl=()
		for box in "${boxes[@]}"; do
			vid="$(awk -v tgt="$machine" '/tgt/ {print $1}' <<<"$box")"
			if [[ "$vid" ]]; then
				vagrant destroy --force "$vid" &> /dev/null || err=1
			else
				nl+=("$box")
			fi
		done
		boxes=("${nl[@]}")
	done

	return $err
}


##
# Helper Functions
##

# Parse options passed to script and load into environment
load_opts() {
	PARAMS=("$@")

	# Defaults
	LOGFILE="/tmp/run_tests.${$}.log"
	OPERATION='test'
	PLUGIN_ARGS=()
	unset HAS_PLUGIN
	unset KEEPLOGS
	unset CLEANUP
	unset TARGET
	unset QUIET


	local OPTIND OPTARG opt
	while getopts ':xukceqdh-:' opt; do
		case "$opt" in
			x) OPERATION='clean';;
			u) OPERATION='update';;
			k) KEEPLOGS='y';;
			c) CLEANUP='y';;
			e) export USE_EMERGE='TRUE';;
			q) QUIET='y';;
			d) set -x;;
			h) show_usage; exit 0;;
			-)
				case "$OPTARG" in
					clean)	OPERATION='clean';;
					update) OPERATION='update';;
					keeplogs) KEEPLOGS='y';;
					cleanup) CLEANUP='y';;
					emerge) export USE_EMERGE='TRUE';;
					quiet) QUIET='y';;
					debug) set -x;;
					help) show_usage; exit 0;;
					# legacy opts
					use-emerge) export USE_EMERGE='TRUE';;
					with-cleanup) CLEANUP='y';;
					*)
						PLUGIN_ARGS+=("--$OPTARG")
						n="${PARAMS[$((OPTIND-1))]}"
						if [[
						    ! "$n" =~ '-' &&
						    ! "$OPTARG" =~ '='
						    ]]; then
							PLUGIN_ARGS+=("$n")
							let 'OPTIND += 1'
						fi
						;;
				esac
				;;
		esac
	done
	TARGET="${PARAMS[$((OPTIND-1))]}"

	if [[ -e "$PWD/test/testing_utils_plugin.sh" ]]; then
		. "$PWD/test/testing_utils_plugin.sh"
		parse_plugin_command_line ${PLUGIN_ARGS[@]}
		HAS_PLUGIN='y'
	fi
}

# Print usage/help information
show_usage() {
	cat <<-EOF
	$0 [options] <target>

	Positional Options:
	  <target>		Restrict execution to instances matching <target> (default: all available)

	Execution Options:
	  <none>		Run integration tests
	  -u	--update	Update vagrant boxes
	  -x	--clean		Clean up test artifacts and exit
	  -h	--help		Show this usage text and exit.

	Runtime Options:
	  -d	--debug		Enable shell debug
	  -q	--quiet		Don't print informational messages

	Test Options:
	  -e	--emerge	Use $Client's Emerge repositories
	  -c	--cleanup	Clean up machines after testing (default: keep failed)
	  -k	--keeplogs	Write logs to per-test files (default: stdout)
	EOF

	if [[ "$HAS_PLUGIN" ]]; then
		printf '\n%s\n' "Options for test plugin:"
		show_plugin_help
	fi

	cat <<-EOF

	Examples:

	    Run all available tests on all supported distros:
	        run_tests.sh

	    Run tests, removing all machines after testng:
	        run_tests.sh -c

	    Run tests on Ubuntu machines:
	        run_tests.sh ubuntu

	    Clean up images from testing; no testing:
	        run_tests.sh -x

	    Typical usage:
	        run_tests.sh -eck ubuntu-1604
	EOF
}

# Verify required packages are installed
check_packages() {
	local err=0
	for pkg in 'kitchen' 'vagrant' 'VBoxManage'; do
		if ! command -v "$pkg" >/dev/null; then
			printf 'Not found in path: %s\n' "$pkg"
			err=1
		fi
	done
	return $err
}

# Write message to log file
log() {
	[[ "$LOGFILE" && "$*" ]] | return 1
	printf '%s\n' "$*" >> "$LOGFILE"
}

# Print a message (if tty/non-quiet)
msg() {
	[[ -t 1 ]] || return 0
	[[ "$QUIET" ]] || printf 'INFO: %s\n' "$*"
}

# Print a message and exit
die() {
	[[ "$*" ]] && printf '*** %s ***\n' "$*"
	exit 2
}


##
# Script Kickoff
##

load_opts "$@"
main
