$(function(){
  $('td > a').on("click",function(event){
    add_loader(event.target);
  })
});