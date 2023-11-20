
function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI

        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent.toFixed(2));

        status_div.children().eq(1).text(percent + '%');
        status_div.children().eq(2).text(data['status']);

        if (data['state'] == 'SUCCESS'){
          status_div.children().eq(1).text('Task Complete - Redirecting');
          location.reload();
        } else if (data['state'] == 'FAILURE') {
          $(status_div.childNodes[3]).text('Result: ' + data['state']);
        } else {
          setTimeout(function() {
              update_progress(status_url, nanobar, status_div);
          }, 5000);
        }
          
      
        /*if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if (data['state'] == 'SUCCESS') {
                // show result
                location.reload();;
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 5000);
        }*/
    });
}

$( window ).on( "load", function(){

  //const text = $( "#data" ).text().replace(/'/g, '"');
  var status_div = $("#progress")
  const status_url = $("#taskstatusurl").text()
      // create a progress bar
  var nanobar = new Nanobar({
      bg: '#44f',
      target: document.getElementById('bar')
  });

  update_progress(status_url, nanobar, status_div);



} );