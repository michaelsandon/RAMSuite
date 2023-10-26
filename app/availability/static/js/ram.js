const equipment_table = document.querySelector('#equipment_table');
const sub_system_table = document.querySelector('#sub_system_table');
const system_table = document.querySelector('#system_table');
const load_progress_label = document.querySelector("label[for='load-progress-bar']")
const load_progress_bar = document.querySelector("#load-progress-bar")
const loaded_model_id = document.querySelector("#loaded-model-id")
const loaded_model_title = document.querySelector("#loaded-model-title")
// url = "/availability/loadrammodel/0"


/*const hot = new Handsontable(equipment_table, {
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
});*/

$('input[name="loadcreatetoggle"]').change(function(){
  $("#formloadmodel")[0].hidden = !$("#formloadmodel")[0].hidden
  $("#formcreatemodel")[0].hidden = !$("#formcreatemodel")[0].hidden
})

$("#formloadmodel").on("submit",function( event ) {
  event.preventDefault();
  target_id = $("#rammodelselect")[0].value
  requrl = "/availability/ram/model/"+target_id+"/detail/equipment/html"

  load_progress_label.hidden = false
  load_progress_bar.hidden = false

  load_progress_label.innerText = "loading equipment"
  load_progress_bar.value = 0
  
  fetch(requrl)
  .then((response) => response.text())
  .then((text) => {
    equipment_table.innerHTML = text
  });

  load_progress_label.innerText = "loading subsystems"
  load_progress_bar.value = 30
  
  requrl = "/availability/ram/model/"+target_id+"/subsystems/"

  fetch(requrl)
  .then((response) => response.text())
  .then((text) => {
    sub_system_table.innerHTML = text
  });

  load_progress_label.innerText = "loading system"
  load_progress_bar.value = 60

  requrl = "/availability/ram/model/"+target_id+"/detail/system/html"
  
  fetch(requrl)
  .then((response) => response.text())
  .then((text) => {
    system_table.innerHTML = text
  });

  requrl = "/availability/ram/model/"+target_id+"/detail/model/"
  
  fetch(requrl)
  .then((response) => response.json())
  .then((data) => {
    loaded_model_id.innerText = data[0].id
    loaded_model_title.innerText = data[0].title
  });


  load_progress_label.innerText = "load complete"
  load_progress_bar.value = 100
  
  load_progress_label.hidden = true
  load_progress_bar.hidden = true
  


});



$("#run-ram").submit( function(eventObj) {
    $("<input />").attr("type", "hidden")
        .attr("name", "model_id")
        .attr("value", Number(loaded_model_id.innerText))
        .appendTo("#run-ram");
    return true;
});