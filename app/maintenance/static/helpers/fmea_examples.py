def fmea_document(title,desc):
  fmea = {"meta":{"title":title,
                  "desc":desc},
         "functions":[]}
  return fmea

def fmea_function(desc,fmea_doc):
  func = {"meta":{"desc":desc},
         "functional_failure":[]}
  fmea_doc["functions"].append(func)
  return fmea_doc["functions"][-1]

def fmea_functional_failure(desc, fmea_function):
  fail = {"desc":desc}
  fmea_function["functional_failure"].append(fail)
  return fmea_function["functional_failure"][-1]


def psv_fmea():
  doc = fmea_document(title="Pressure Safety Valve",
                      desc = "Generic FMEA for PSV")

  func1 = fmea_function(desc = "Lift at set pressure", fmea_doc=doc)
  func2 = fmea_function(desc = "Maintain integrity", fmea_doc=doc)

  fail1 = fmea_functional_failure(desc = "PSV lifting early", fmea_function=func1)
  fail2 = fmea_functional_failure(desc = "PSV lifting late", fmea_function=func1)
  fail3 = fmea_functional_failure(desc = "Loss of fluid containment", fmea_function=func2)

  return doc



def fmea_examples():
  result = []
  result.append(psv_fmea())

  return result


  
  