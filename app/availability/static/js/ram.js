const equipment_table = document.querySelector('#equipment_table');

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