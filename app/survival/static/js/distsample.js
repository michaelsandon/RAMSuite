const param_ids = ["param1","param2","param3"]
const dist_id = "dist"

$( "#dist" ).on( "change", function() {
  updateform(dist_id, param_ids);
})

$( window ).on( "load", function() {
  updateform(dist_id, param_ids);
} );

