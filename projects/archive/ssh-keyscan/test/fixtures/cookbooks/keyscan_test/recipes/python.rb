# Cookbook::  keyscan_test
# Recipe::    python
#
# Copyright:: 2019, Juniper Networks

include_recipe 'testing_utils::setup_repos'

package 'python-pytest'
package 'python3-pytest'
package 'python-flake8'
package 'python3-flake8'
package 'python-six'
package 'python3-six'
