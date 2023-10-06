const equipment_table = document.querySelector('#equipment_table');
const system_table = document.querySelector('#system_table');

const url = "/availability/loadrammodel/0"


const hot = new Handsontable(equipment_table, {
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


hot2 = new Handsontable(system_table, {
  startRows: 8,
  startCols: 6,
  rowHeaders: true,
  colHeaders: true,
  height: 'auto',
  licenseKey: 'non-commercial-and-evaluation' // for non-commercial use only
})
                       
$("#load_ram_model").click(function(){
  alert("The ram model load was clicked.");
  $.getJSON(url, function(data) {
    data2 = data
    
    const res_array = [];
    res_array.push(Object.keys(data2))

    const_test = data2[Object.keys(data2)[0]];

    
    for(i of Object.keys(data2[Object.keys(data2)[0]])) {
      res_array2 = []
      for(j of Object.keys(data2)) {
        res_array2.push(data2[j][i])
      }
      res_array.push(res_array2); 
    }; 
    hot2.loadData(res_array)
  });
});