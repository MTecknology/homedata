function action_change() {
  var e = document.getElementById('action');
  var action = e.options[e.selectedIndex].value;
  switch(action) {
    case "none":
    default:
      disable_element('curusr_row');
      disable_element('newusr_row');
      disable_element('curcnt_row');
      disable_element('newcnt_row');
      disable_element('submit_row');
      break;
    case "namechange":
      enable_element('curusr_row');
      enable_element('newusr_row');
      enable_element('curcnt_row');
      disable_element('newcnt_row');
      enable_element('submit_row');
      break;
    case "centerchange":
      enable_element('curusr_row');
      disable_element('newusr_row');
      enable_element('curcnt_row');
      enable_element('newcnt_row');
      enable_element('submit_row');
      break;
    case "termmove":
      enable_element('curusr_row');
      enable_element('newusr_row');
      enable_element('curcnt_row');
      disable_element('newcnt_row');
      enable_element('submit_row');
      break;
  }
}

function enable_element(id) {
  var e = document.getElementById(id);
  e.style.display = 'table-row';
}

function disable_element(id) {
  var e = document.getElementById(id);
  e.style.display = 'none';
}

function toggle_help() {
  var e = document.getElementById('helptext');
  if (e.style.display == 'none') {
    e.style.display = 'inline';
  } else {
    e.style.display = 'none';
  }
}
