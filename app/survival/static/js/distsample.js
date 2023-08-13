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
                        param3:"gamma, optional offset parameter"}
}

function updateform(){
  var dist = $( "#dist" ).val();

  for(param of ["param1","param2","param3"]){
    if(distributions[dist][param]=="hidden"){
      $("#"+param).attr( "type", "hidden")
      $("label[for='"+param+"']").css("display","none")
    } else {
      $("label[for='"+param+"']").text(distributions[dist][param])
      $("label[for='"+param+"']").css("display","inline-block")
      $("#"+param).attr("type","number")
    }
  }  
}

$( "#dist" ).on( "change", function() {
  updateform();
})

$( window ).on( "load", function() {
  updateform();
} );

