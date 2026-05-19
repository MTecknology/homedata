#!/usr/bin/env bash

KITCHEN=$(which kitchen)
VAGRANT=$(which vagrant)
VBOX=$(which VBoxManage)

function run_tests_cleanup_vms {
  vm_ids=""

  for machine in $($KITCHEN list -b "$1"); do
    vm_ids="$vm_ids $(vagrant global-status | grep $PWD | grep $machine | cut -f 1 -d ' ')"
  done
  $KITCHEN destroy "$1" > /dev/null

  # We then run destroy over any stray VMs
  # That is, VMs that might have failed during create, so were not destroyed
  # by kitchen destroy
  for vm_id in $vm_ids; do
    vagrant destroy --force $vm_id > /dev/null 2>&1
  done
}

if [ -z $KITCHEN ]; then
  echo "Cannot find kitchen binary. Please install to run tests."
  echo "The easiest way to do this is probably by installing ChefDK."
  echo "See the testing-utils README for more information."
  exit 1
fi

if [ -z $VAGRANT ]; then
  echo "Cannot find Vagrant binary. Please install to run tests."
  echo "See the testing-utils README for more information."
  exit 1
fi

if [ -z $VBOX ]; then
  echo "VirtualBox does not seem to be installed. Please install to run tests."
  echo "See the testing-utils README for more information."
  exit 1
fi

if [ -e "$PWD/test/testing_utils_plugin.sh" ]; then
  . "$PWD/test/testing_utils_plugin.sh"
  HAS_PLUGIN=TRUE
else
  HAS_PLUGIN=FALSE
fi

POSITIONAL=()
PID=${$}
logfile=/tmp/run_tests.${PID}.log
exit_value=0

echo "PARAMETERS: $@" > $logfile

while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -e|--use-emerge)
    echo "INFO: Using emerge repos"
    export USE_EMERGE=TRUE
    shift
    ;;
    -h|--help)
    echo "Usage: run_tests [options] [instance pattern]"
    echo "Options:"
    echo "  --use-emerge          Use the emerge repositories"
    echo "  --update [box]        Update the Vagrant boxes and exit. Update single box if specified."
    echo "  --cleanup [instance]  Destroy VMs matching instance pattern. All if not specified."
    echo "                        The instance pattern is passed to kitchen to match the instances upon"
    echo "                        which to run the tests. This can be a string or regex."
    echo "  --with-cleanup        Destroy all instances after testing, even if it has errors. By default,"
    echo "                        if a instance has errors it is not destroyed."

    if [ "$HAS_PLUGIN" == 'TRUE' ]; then
      echo ''
      echo "Options for $(plugin_name) tests"
      show_plugin_help
    fi

    rm -f $logfile
    exit 0
    ;;
    --update)
    echo "Pruning old Vagrant boxes, updating boxes and exiting"
    vagrant box prune
    if [ -z "$2" ]; then
      echo "Checking all boxes"
      for box in $($VAGRANT box outdated --global | grep outdated | cut -f 2 -d "'" | sort ); do
        $VAGRANT box update --box $box
      done
    else
      echo "Updating specified box: $2"
      $VAGRANT box update --box "$2"
    fi
    rm $logfile
    exit 0
    ;;
    --with-cleanup)
    export WITH_CLEANUP=TRUE
    shift
    ;;
    --cleanup)
    echo "Destroying VMs and exiting"
    run_tests_cleanup_vms "$2"
    exit 0
    ;;
    *)
    POSITIONAL+=("$1") # save it in an array for later
    shift
    ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

if [ "$HAS_PLUGIN" == 'TRUE' ]; then
  parse_plugin_command_line "$@"
  set -- "${PLUGIN_POSITIONAL[@]}"
fi

filter_list=$1

run_tests_cleanup_vms "$filter_list"

for machine in $($KITCHEN list -b "${filter_list}"); do
  if $KITCHEN test $machine; then
    echo "PASSED: $machine" >> $logfile
  else
    echo "FAILED: $machine" >> $logfile
    exit_value=1
  fi
done

echo "Testing done"
cat $logfile
rm $logfile

unset USE_EMERGE

if [ "$HAS_PLUGIN" == 'TRUE' ]; then
  plugin_cleanup
fi

if [ "$WITH_CLEANUP" == 'TRUE' ]; then
  unset WITH_CLEANUP
  run_tests_cleanup_vms ${filter_list}
fi

exit $exit_value
