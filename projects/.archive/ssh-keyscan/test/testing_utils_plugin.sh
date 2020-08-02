#!/usr/bin/env bash

PLUGIN_POSITIONAL=()

function show_plugin_help {
	echo '  No options'
}

function parse_plugin_command_line {
	export PLUGIN_POSITIONAL="$@"
}

function plugin_cleanup {
	:
}

function plugin_name {
	echo 'ssh-keyscan'
}
