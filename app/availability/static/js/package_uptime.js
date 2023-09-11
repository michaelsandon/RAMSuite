const ev_param_ids = ["ev_param1","ev_param2","ev_param3"]
const ev_dist_id = "ev_dist"

const dt_param_ids = ["dt_param1","dt_param2","dt_param3"]
const dt_dist_id = "dt_dist"

$( "#"+ev_dist_id ).on( "change", function() {
  updateform(ev_dist_id, ev_param_ids);
})

$( "#"+dt_dist_id ).on( "change", function() {
  updateform(dt_dist_id, dt_param_ids);
})

$( window ).on( "load", function() {
  updateform(ev_dist_id, ev_param_ids);
  updateform(dt_dist_id, dt_param_ids);
} );