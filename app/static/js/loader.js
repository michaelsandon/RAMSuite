function add_loader(node){
  var new_div = document.createElement('div');
  new_div.className = "loader";
  new_div.style.display = "inline-block";
  node.after(new_div)
}
  