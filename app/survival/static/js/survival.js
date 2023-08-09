const container = document.querySelector('#example');

const hot = new Handsontable(container, {
  data: [
    [10, false,1],
    [8, true,null],
    [7, false,1],
    [8, true,3],
    [11, true,null],
    [10, true,1]
  ],
  rowHeaders: true,
  colHeaders: ['Lifetime','Suspended','Qty'],
  columns: [
    {
      data: 0,
      type: 'numeric'
      // 1nd column is simple text, no special options here
    },
    {
      data: 1,
      type: 'checkbox'
    },
    {
      data: 2,
      type: 'numeric'
    }
   ],
  height: 'auto',
  licenseKey: 'non-commercial-and-evaluation' // for non-commercial use only
});

function modify_rows_to_hot(rows=5){
  if(rows>0){
    hot.alter('insert_row_below', hot.countRows() ,rows);
  } else {
    hot.alter('remove_row', hot.countRows(), -rows);
  }
}

$("#weibull-form").submit( function(eventObj) {
    $("<input />").attr("type", "hidden")
        .attr("name", "survivaltimes")
        .attr("value", JSON.stringify(hot.getDataAtCol(0)))
        .appendTo("#weibull-form");
    $("<input />").attr("type", "hidden")
      .attr("name", "survivalcensor")
      .attr("value", JSON.stringify(hot.getDataAtCol(1)))
      .appendTo("#weibull-form");
    $("<input />").attr("type", "hidden")
      .attr("name", "survivalqty")
      .attr("value", JSON.stringify(hot.getDataAtCol(2)))
      .appendTo("#weibull-form");
    return true;
});
/*
$(document).on('submit', '#weibull-form', function(e){
  
  var formwb = $('#weibull-form');
  var submitButton = $('input[type=submit]', formwb);
  formwb.attr("action", '/survival/result/');*/
 /* e.preventDefault();
  $.ajax({
            data : {
              test : 'michael',
              tabledata : JSON.stringify(hot.getDataAtCol(0))
            },
            type : 'POST',
            url : '/survival/result/',
            success: function (response) {
            }
        });
   $.post('/survival/result/',{test: 'michael'})
       .done(function(data) {

            if (data.error) {
                $('#errorAlert').text(data.error).show();
                $('#successAlert').hide();
            }
            else {
                $('#successAlert').text(data.name).show();
                $('#errorAlert').hide();
            }

        })
});*/