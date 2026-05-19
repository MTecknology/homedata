# Tests to verify proper operation of SSH Key Scanner

base_path = '/test_local_files/juniper/keyscan'
is_ssh_ok = "#{base_path}/include/is_ssh_ok"
keys = "#{base_path}/test/keys"
keys2 = "#{base_path}/test/keys2"

# RSA Without Password
describe command("#{is_ssh_ok} -k #{keys}/id-rsa-nopw") do
  its('stdout') { should match /id-rsa-nopw.pub \(file exists\)/ }
  its('stdout') { should match /key material is unencrypted/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should be 1 }
end

# RSA With Password and >= 2048 bits
describe command("#{is_ssh_ok} -k #{keys}/id-rsa-pw-is-testing") do
  its('stdout') { should match /id-rsa-pw-is-testing.pub \(file exists\)/ }
  its('stdout') { should match /key material is encrypted using aes256-ctr/ }
  its('stdout') { should match /Key is Good/ }
  its('exit_status') { should eq 0 }
end

# RSA With Password and >= 2048 bits; missing public key
describe command("#{is_ssh_ok} -k #{keys}/id-rsa-testing") do
  its('stdout') { should match /id-rsa-testing.pub \(file NOT found\)/ }
  its('stdout') { should match /key material is encrypted using AES-128-CBC/ }
  its('stdout') { should match /compliance cannot be determined/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# RSA Key With Password and < 2048 bits
describe command("#{is_ssh_ok} -k #{keys}/id_bad") do
  its('stdout') { should match /id_bad.pub \(file exists\)/ }
  its('stdout') { should match /key material is encrypted using AES-128-CBC/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# DSA Key Without Password
describe command("#{is_ssh_ok} -k #{keys}/id_dsa-no-pw") do
  its('stdout') { should match /key material is unencrypted/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# DSA Key With Password
describe command("#{is_ssh_ok} -k #{keys}/id_dsa-with-pw") do
  its('stdout') { should match /key material is encrypted using aes256-ctr/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# RSA Key Without Password
describe command("#{is_ssh_ok} -k #{keys}/id_rsa-no-pw") do
  its('stdout') { should match /key material is unencrypted/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# RSA Key With Password < 2048 bits
describe command("#{is_ssh_ok} -k #{keys}/id_rsa-with-pw") do
  its('stdout') { should match /key material is encrypted using aes256-ctr/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# ED25519 Key Without Password
describe command("#{is_ssh_ok} -k #{keys}/id_ed25519-no-pw") do
  its('stdout') { should match /key material is unencrypted/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# ED25519 Key With Password
describe command("#{is_ssh_ok} -k #{keys}/id_ed25519-with-pw") do
  its('stdout') { should match /id_ed25519-with-pw.pub \(file exists\)/ }
  its('stdout') { should match /key material is encrypted using aes256-cbc/ }
  its('stdout') { should match /Key is Good/ }
  its('exit_status') { should eq 0 }
end

# ECDSA Key Without Password
describe command("#{is_ssh_ok} -k #{keys}/id_ecdsa-p256-no-pw") do
  its('stdout') { should match /key material is unencrypted/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# ECDSA Key With Password
describe command("#{is_ssh_ok} -k #{keys}/id_ecdsa-p256-with-pw") do
  its('stdout') { should match /key material is encrypted using aes256-ctr/ }
  its('stdout') { should match /Key is Good/ }
  its('exit_status') { should eq 0 }
end

# RSA1 Key Without Password
describe command("#{is_ssh_ok} -k #{keys}/id_rsa1-no-pw") do
  its('stdout') { should match /SSHv1 keys should not be used/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should be 1 }
end

# RSA1 Key With Password
describe command("#{is_ssh_ok} -k #{keys}/id_rsa1-with-pw") do
  its('stdout') { should match /SSHv1 keys should not be used/ }
  its('stdout') { should match /Key is BAD/ }
  its('exit_status') { should eq 1 }
end

# Test scanning multiple individual (-k) files
describe command("#{is_ssh_ok} -k #{keys}/id_ed25519-with-pw -k #{keys}/id_ecdsa-p256-with-pw -k #{keys}/id-rsa-nopw") do
  its('stdout') { should match /Unenrypted private key/ }
  its('stdout') { should match /Key is BAD/ }
  its('stdout') { should match /Key is Good/ }
  its('stderr') { should match /1 SSH key issue/ }
  its('exit_status') { should eq 1 }
end

# Check operation on a single directory
describe command("#{is_ssh_ok} #{keys}") do
  its('stderr') { should match /10 SSH key issue/ }
  its('exit_status') { should eq 1 }
end

# Check operation on multiple directories
# Second directory is intentionally missing pubkeys
describe command("#{is_ssh_ok} #{keys} #{keys2}") do
  its('stderr') { should match /12 SSH key issue/ }
  its('exit_status') { should eq 1 }
end
