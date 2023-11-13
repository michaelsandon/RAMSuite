const loaded_model_id = document.querySelector("#loaded-model-id")
const loaded_model_title = document.querySelector("#loaded-model-title")

$("#run-ram").submit( function(eventObj) {
    $("<input />").attr("type", "hidden")
        .attr("name", "model_id")
        .attr("value", Number(loaded_model_id.innerText))
        .appendTo("#run-ram");
    return true;
});


$("#draw-rbd").submit( function(eventObj) {
    $("<input />").attr("type", "hidden")
        .attr("name", "model_id")
        .attr("value", Number(loaded_model_id.innerText))
        .appendTo("#draw-rbd");
    return true;
});

