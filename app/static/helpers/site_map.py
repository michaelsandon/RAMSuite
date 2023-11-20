def create_map_branch(branchname,desc, route = None):
  if route is None:
    route = branchname + '.index'
  branch = {'Name':branchname,
           'Route':route,
           'Desc':desc,
           'Children':[]}
  return branch

def create_map_branch_child(name,desc,route,branch = None):
  child = {'Name':name,'Route':route,'Desc': desc}
  if branch is not None:
    branch["Children"].append(child)
    result = branch
  else:
    result = child
  return result
    
    
def render_site_map():
  map = []
  home = create_map_branch("Home","Home page",route='main.index')
  map.append(home)

  survival = create_map_branch("Survival","Lifetime anaylsis modules to determine failure patterns",'survival.index')
  survival = create_map_branch_child("Sampling","Conduct random sampling from a distribution", 'survival.distsample',survival)
  survival = create_map_branch_child("Survival Fit","Use observed failure data to fit a failure distribution", 'survival.survivalfit',survival)
  map.append(survival)

  uptime = create_map_branch('Uptime','RAM simulation type model to determine stream uptime, throughput etc.',"availability.index")
  uptime = create_map_branch_child('Simple Parallel Package', 'Modeller to enable uptime to be estimated for a M out of N parallel scenario','availability.packageuptime',uptime)
  uptime = create_map_branch_child('RAM Modeller', 'Modeller to enable uptime to be estimated for a complex system or site','availability.ram',uptime)
  map.append(uptime)

  cost = create_map_branch("Cost","Lifecycle Cost evaluation module",'main.index')
  map.append(cost)

  maintenance = create_map_branch("Maintenance", "Reliability Centred Maintenance, Strategy Tester",'maintenance.index')
  map.append(maintenance)


  risk = create_map_branch("Risk", "Risk module supported safety assessments, safety availability and SIL levels, Risk target decomposer", 'main.index')
  map.append(risk)

  examples = create_map_branch("Examples","Worked examples to demonstrate how to apply the toolkit", 'examples.index')
  examples = create_map_branch_child("Survival Examples", "Examples using the survival toolkit",'examples.survival', examples)
  map.append(examples)

  resources = create_map_branch("Resources","Standards and Tools supporting the practice", 'resources.index')
  resources = create_map_branch_child("Standards and Journals", "International Standards and Journals for Guidance",'resources.standards_and_journals', resources)
  resources = create_map_branch_child("Data", "data to be used at user discretion",'resources.data', resources)
  resources = create_map_branch_child("Software", "Free and Licensed Software",'resources.software', resources)
  map.append(resources)
  
  return map
  
  

site_map = render_site_map()

