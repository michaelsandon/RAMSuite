const survivaldata = document.querySelector('#survivaldata');

const hot = new Handsontable(survivaldata, {
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

$("#survival-form").submit( function(eventObj) {
    $("<input />").attr("type", "hidden")
        .attr("name", "survivaltimes")
        .attr("value", JSON.stringify(hot.getDataAtCol(0)))
        .appendTo("#survival-form");
    $("<input />").attr("type", "hidden")
      .attr("name", "survivalcensor")
      .attr("value", JSON.stringify(hot.getDataAtCol(1)))
      .appendTo("#survival-form");
    $("<input />").attr("type", "hidden")
      .attr("name", "survivalqty")
      .attr("value", JSON.stringify(hot.getDataAtCol(2)))
      .appendTo("#survival-form");
    return true;
});
