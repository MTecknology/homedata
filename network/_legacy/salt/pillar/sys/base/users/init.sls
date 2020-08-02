#!jinja|yaml|gpg
include:
  - sys.base.users.root
  - sys.base.users.ssh_keys

admins:
  michael:
    uid: 1010
    gid: 1010
    pwd: '$6$sropzjhW$nPTbl7pp5PIT7mLE3Ias8Aa4iZWd0ahcWB1Z3Mm9A4.8CsLBt9kliFAPpMtRPILE1'
    gauth_key: K5GEG4GIQF7D6CWR6IBI
    keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAW8TZN+e+dHjhGyB07z5aA3GHTSYjnnoaPAwKQi03R6ySfBdFqz8KVxNeAEJiGCwCC5nvrOHu62Jw9O93jKLc06GvDlAm25w6axPpHcz0JY6HkF3YN30jWp61Arx8KyQq1ExeCR+wZD2W7Usj/vCUfDXcr47rnD36DMnHA+oX0UxpTgK4HVdpfbJsyj8c22NK+UTl4xU2RkcMcZuFWkkSliV25/N9mAsWHU77MgfLI13oC16IskChzDcpbi0f+WxmPxgTJb9EDBesWRekdCpqo82SFmzinktNDbvp5s= michael@panther
      - ssh-rsa AAAAB3NzaC1yc2EAAci5KD65QppiBbZA9rvuZvyF2gi9CINzoVq69B5fMiTGpUrCzhQk4XpuPzKa1pZzzWiDkwvh9NyQoNONNeAoAcBJtqWYo9HrCYQm5raVFDmuPSAUpYxV2pvBsQEbtCPe/gsGNWQsUTFkvPWipooZdQOwY3jn michael@liber
