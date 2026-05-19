function check_job() {
  var JSONObject = {'job_id': job_id};

  // code for IE7+, Firefox, Chrome, Opera, Safari
  if (window.XMLHttpRequest) {
    xmlhttp = new XMLHttpRequest();
  }
  // code for IE6, IE5
  else {
    xmlhttp = new ActiveXObject('Microsoft.XMLHTTP');
  }

  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      check_return(xmlhttp.responseText);
    }
  }

  xmlhttp.open('POST', '/files/job_status', true);
  xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xmlhttp.send(JSON.stringify(JSONObject));
}

function check_return(data) {
  // Get the data from the response
  j = JSON.parse(data);

  if (j.job_id != job_id) {
    // We got data for the wrong Job ID: Do nothing
    return 0;
  }

  if (j.status == 'running') {
    // The job is still running: Do nothing
    return 0;
  }
  else if (j.status == 'failed') {
    document.getElementById("REPLACE_DATA").innerHTML = '<h3>JOB FAILED!</h3>' + j.data;
    clearInterval(job_check);
  }
  else if (j.status == 'finished') {
    document.getElementById("REPLACE_DATA").innerHTML = j.data;
    clearInterval(job_check);
  }
}
