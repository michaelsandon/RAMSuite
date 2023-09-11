const distributions = {
  'Beta_Distribution':{param1:"alpha, shape parameter 1",
                       param2:"beta, shape parameter 2",
                       param3:"hidden"},
  'Exponential_Distribution':{param1:"Lambda, scale parameter",
                              param2:"gamma, optional offset parameter",
                              param3:"hidden"},
  'Gamma_Distribution':{param1:"alpha, scale parameter",
                        param2:"beta, shape parameter",
                        param3:"gamma, optional offset parameter"},
  'Gumbel_Distribution':{param1:"mu – Location parameter",
                         param2:"sigma – Scale parameter. Must be > 0",
                        param3:"hidden"},
  'Loglogistic_Distribution':{param1:"alpha, scale parameter",
                              param2:"beta, shape parameter",
                              param3:"gamma, optional offset parameter"},
  'Lognormal_Distribution':{param1:"mu – Location parameter",
                            param2:"sigma – Scale parameter. Must be > 0",
                           param3:"gamma, optional offset parameter"},
  'Normal_Distribution':{param1:"mu – Location parameter",
                         param2:"sigma – Scale parameter. Must be > 0",
                        param3:"hidden"},
  'Weibull_Distribution':{param1:"alpha, scale parameter",
                        param2:"beta, shape parameter",
                        param3:"gamma, optional offset parameter"},
  'constant':{param1:"constant value",
             param2:"hidden",
             param3:"hidden"}
}

function updateform(dist_id, param_ids){
  var dist = $( "#"+dist_id ).val();

  for(i of [0,1,2]){
    param = "param"+(i+1)
    param_id = param_ids[i]
    if(distributions[dist][param]=="hidden"){
      $("#"+param_id).val("")
      $("#"+param_id).attr( "type", "hidden")
      $("label[for='"+param_id+"']").css("display","none")
      $("#"+param_id).removeAttr("required")
    } else {
      $("label[for='"+param_id+"']").text(distributions[dist][param])
      $("label[for='"+param_id+"']").css("display","inline-block")
      $("#"+param_id).attr("type","number")
      if(distributions[dist][param].includes("optional")){
        $("#"+param_id).removeAttr("required")
      } else {
        $("#"+param_id).attr("required","")
      }
    }
  }  
}
