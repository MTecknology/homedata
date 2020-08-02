  st_hyperv:
    - mine_function: cmd.powershell
    - 'get-vm | select name, state, automaticstartaction'
