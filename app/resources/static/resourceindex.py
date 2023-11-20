import pandas as pd

rtype = ["journal","standard","data","software","blog","open-source","template"]

def add_resource(type,title=None,desc=None,url=None,list=None):
  #types ["journal","standard","data","software"]
  result = {"type":type,
            "title":title,
            "desc":desc,
            "url":url}

  if list is not None:
    list.append(result)
    return
  else:
    return result

def resources():
  resources = []

  #data
  add_resource(type = rtype[2], title = "GE Weibull Database",url = "https://www.ge.com/digital/documentation/meridium/Help/V43050/Default/Subsystems/ReliabilityAnalytics/Content/WeibullDistrubution.htm", list=resources)
  add_resource(type = rtype[2], title = "OREDA",url = "https://www.oreda.com/", list=resources)
  add_resource(type = rtype[2], title = "SERH (Exida)",url = "https://www.exida.com/Books/Safety-Equipment-Reliability-Handbook-4th-Edition#", list=resources)
  add_resource(type = rtype[2], title = "silsafedata (Exida)",url = "https://silsafedata.com/#datacheck", list=resources)
  



  
                 
  

  #blogs
  add_resource(type = rtype[4], title = "US National Institute of Standards and Technology (NIST) Engineering Handbook",url = "https://www.itl.nist.gov/div898/handbook/index.htm", list=resources)
  add_resource(type = rtype[4], title = "Reliabiltiy Hotwire / Weibull.com",url = "https://www.weibull.com/hotwire/archive.htm", list=resources)
  add_resource(type = rtype[4], title = "Assetivity",url = "https://www.assetivity.com.au/articles/", list=resources)
  add_resource(type = rtype[4], title = "ReliaWiki",url = "https://www.reliawiki.com/index.php/Main_Page", list=resources)

  
  
  #software
  add_resource(type = rtype[3], title = "Reliability Analytics",url = "https://reliabilityanalyticstoolkit.appspot.com/", list=resources)
  add_resource(type = rtype[3], title = "RAPTOR", url = "https://github.com/boozallen/raptor", list=resources)
  add_resource(type = rtype[3], title = "DNV MAROS / TARO", url = "https://www.dnv.com/services/ram-analysis-software-for-upstream-oil-and-gas-maros-1152", list=resources)
  add_resource(type = rtype[3], title = "SPARC", list=resources)
  add_resource(type = rtype[3], title = "Reliasoft BlockSim", url = "https://www.hbkworld.com/en/products/software/analysis-simulation/reliability/blocksim-system-reliability-availability-maintainability-ram-analysis-software", list=resources)
  add_resource(type = rtype[3], title = "Reliasoft Weibull++", url = "https://www.hbkworld.com/en/products/software/analysis-simulation/reliability/weibull-life-data-analysis-software", list=resources)
  add_resource(type = rtype[3], title = "Isograph Availability Workbench", url = "https://www.isograph.com/software/availability-workbench/", list=resources)
  add_resource(type = rtype[3], title = "Isograph Reliabiltiy Workbench", url = "https://www.isograph.com/software/reliability-workbench/", list=resources)
  add_resource(type = rtype[3], title = "SuperSMITH Weibull", url = "http://www.weibullnews.com/SuperSMITH-Current-Version.html", list=resources)
  add_resource(type = rtype[3], title = "exSILentia (Exida)",url = "https://www.exida.com/Software", list=resources)

  resources = pd.DataFrame(resources)
  
  return resources
  
  
  