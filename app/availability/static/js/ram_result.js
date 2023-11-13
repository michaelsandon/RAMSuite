$(function(){
  $('td > a').on("click",function(event){
    add_loader(event.target);
  })
});

/*
$(document).ready( function () {{
  $('table').each(function(){
      //if statement here 
      // use $(this) to reference the current div in the loop
      //you can try something like...
    $(this).DataTable({
        // paging: false,    
        // scrollY: 400,
    });

   });
  
}});
*/

$('#links').DataTable({});