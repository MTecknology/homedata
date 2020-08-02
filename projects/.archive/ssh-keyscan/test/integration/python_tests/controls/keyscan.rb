# Tests to verify proper operation of SSH Key Scanner

base_path = '/test_local_files/juniper/keyscan'

# Verify keyscan passes flake8
describe command("python2 -m flake8 #{base_path}/keyscan.py") do
  its('stdout') { should eq '' }
  its('exit_status') { should eq 0 }
end
describe command("python3 -m flake8 #{base_path}/keyscan.py") do
  its('stdout') { should eq '' }
  its('exit_status') { should eq 0 }
end

# Verify libraries pass flake8
describe command("python2 -m flake8 #{base_path}/lib/*.py") do
  its('stdout') { should eq '' }
  its('exit_status') { should eq 0 }
end
describe command("python3 -m flake8 #{base_path}/lib/*.py") do
  its('stdout') { should eq '' }
  its('exit_status') { should eq 0 }
end

# Verify unit tests pass
describe bash("cd #{base_path} && py.test") do
  its('stdout') { should_not match /failed/ }
  its('exit_status') { should eq 0 }
end
describe bash("cd #{base_path} && py.test-3") do
  its('stdout') { should_not match /failed/ }
  its('exit_status') { should eq 0 }
end
