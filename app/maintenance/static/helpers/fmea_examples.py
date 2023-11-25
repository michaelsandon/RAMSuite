def fmea_document(title,desc):
  fmea = {"meta":{"title":title,
                  "desc":desc},
         "functions":[],
         "failuremodes":[],
         "failuremap":[]}
  return fmea

def fmea_function(desc,fmea_doc):
  func = {"meta":{"desc":desc},
         "functional_failure":[]}
  fmea_doc["functions"].append(func)
  return fmea_doc["functions"][-1]

def fmea_functional_failure(desc, fmea_function):
  fail = {"meta":{"desc":desc},
          "consequences":[]}
  fmea_function["functional_failure"].append(fail)
  return fmea_function["functional_failure"][-1]


def fmea_func_fail_cons(desc,riskCategoryId,riskConsequenceId,funcfail):
  fail_cons = {"desc":desc,"riskCategoryId":riskCategoryId,"riskConsequenceId":riskConsequenceId}
  funcfail["consequences"].append(fail_cons)
  return None


def fmea_failuremode(component,damage,mechanism,riskLikelihoodId,fmea_doc):
  fmode = {"component":component,
           "damage":damage,
           "mechanism":mechanism,
          "riskLikelihoodId":riskLikelihoodId}
  fmea_doc["failuremodes"].append(fmode)
  return None

def fmea_failuremap(ref_funcfailid,ref_failid,fmea_doc):
  mapitem = {"ref_funcfailid":ref_funcfailid,"ref_failid":ref_failid}
  fmea_doc["failuremap"].append(mapitem)
  return None


def psv_fmea():
  doc = fmea_document(title="Pressure Safety Valve",
                      desc = "Generic FMEA for PSV")

  func1 = fmea_function(desc = "Lift at set pressure", fmea_doc=doc)
  func2 = fmea_function(desc = "Maintain integrity", fmea_doc=doc)

  fail1 = fmea_functional_failure(desc = "PSV lifting early", fmea_function=func1)
  fail2 = fmea_functional_failure(desc = "PSV lifting late", fmea_function=func1)
  fail3 = fmea_functional_failure(desc = "Loss of fluid containment", fmea_function=func2)

  fmea_func_fail_cons(desc = "Financial impact from loss of fluid inventory e.g. burnt in flare stack, lost to environment",riskCategoryId=1,riskConsequenceId=1, funcfail=fail1)
  fmea_func_fail_cons(desc = "Environmental impact from fluid lost to environment. Potential for increased emissions",riskCategoryId=2,riskConsequenceId=1, funcfail=fail1)
  fmea_func_fail_cons(desc = "Potential for overpressure leading to equipment damage",riskCategoryId=1,riskConsequenceId=2, funcfail=fail2)
  fmea_func_fail_cons(desc = "Potential for overpressure leading to equipment damage and large process fluid inventory loss to env",riskCategoryId=2,riskConsequenceId=2, funcfail=fail2)
  fmea_func_fail_cons(desc = "Potential for overpressure leading to hazardous fluid loss of containment. Direct harm to humans or potential for escalation e.g. ignition",riskCategoryId=3,riskConsequenceId=3, funcfail=fail2)

  fmea_failuremode(component = "Seat, Disc",damage="Dented, Scratched, Corroded",mechanism="Abrasive fluid, repeated lifting", riskLikelihoodId = 1, fmea_doc=doc)
  fmea_failuremode(component = "Seat",damage="operational issue",mechanism="Failed to Reseat",riskLikelihoodId=2, fmea_doc=doc)
  fmea_failuremode(component = "Spring",damage="Lowered Stiffness",mechanism="Corroded",riskLikelihoodId=1, fmea_doc=doc)
  fmea_failuremode(component = "Assembly",damage="Incorrect CDSP",mechanism="Incorrectly set",riskLikelihoodId=1, fmea_doc=doc)
  fmea_failuremode(component = "Bellows",damage="pinhole",mechanism="corrosion",riskLikelihoodId=2, fmea_doc=doc)
  fmea_failuremode(component = "Bellows",damage="fatigue",mechanism="chatter", riskLikelihoodId=1, fmea_doc=doc)
  fmea_failuremode(component = "Guide,Stem",damage="Galling",mechanism="Design", riskLikelihoodId=1, fmea_doc=doc)
  fmea_failuremode(component = "Assembly",damage="operational issue",mechanism="High BackPressure", riskLikelihoodId=1, fmea_doc=doc)
  fmea_failuremode(component = "Body",damage="through wall defect",mechanism="corrosion", riskLikelihoodId=1, fmea_doc=doc)

  fmea_failuremap(ref_funcfailid=1,ref_failid=1,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=1,ref_failid=2,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=1,ref_failid=3,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=1,ref_failid=4,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=2,ref_failid=4,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=2,ref_failid=5,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=2,ref_failid=6,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=2,ref_failid=7,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=2,ref_failid=8,fmea_doc=doc)
  fmea_failuremap(ref_funcfailid=3,ref_failid=9,fmea_doc=doc)
  
  return doc



def fmea_examples():
  result = []
  result.append(psv_fmea())

  return result


  
  