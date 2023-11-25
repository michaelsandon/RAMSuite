def risk_matrix(title,lrng,crng):
  matrix = {
    "meta":{"title":title,"likelihoodrange":lrng,"consequencerange":crng},
    "likelihoods":[],
    "consequences":[],
    "levels":[],
    "map":[],
    "categories":[]
  }
  return matrix

def likelihood(index,desc,matrix):
  matrix["likelihoods"].append({"index":index,"desc":desc})
  return matrix["likelihoods"][-1]

def consequence(index,desc,matrix):
  matrix["consequences"].append({"index":index,"desc":desc})
  return matrix["consequences"][-1]

def level(index,desc,colour,matrix):
  matrix["levels"].append({"index":index,"desc":desc,"colour":colour})
  return matrix["levels"][-1]

def riskmap(lindex,cindex,rindex,matrix):
  matrix["map"].append({"lindex":lindex,"cindex":cindex,"rindex":rindex})
  return matrix["map"][-1]

def categories(desc,matrix):
  matrix["categories"].append({"desc":desc})
  return matrix["categories"][-1]
  

def basic_matrix():
  matrix = risk_matrix(title="Simple Risk Matrix",lrng = 3, crng = 3)
  
  likelihood(1,"low",matrix)
  likelihood(2,"med",matrix)
  likelihood(3,"high",matrix)

  consequence(1,"low",matrix)
  consequence(2,"med",matrix)
  consequence(3,"high",matrix)

  level(1,"low","GreenYellow",matrix)
  level(2,"low","Yellow",matrix)
  level(3,"low","Orange",matrix)
  level(4,"low","Red",matrix)

  riskmap(1,1,1,matrix)
  riskmap(2,1,2,matrix)
  riskmap(1,2,2,matrix)
  riskmap(2,2,3,matrix)
  riskmap(3,1,3,matrix)
  riskmap(1,3,3,matrix)
  riskmap(2,3,4,matrix)
  riskmap(3,2,4,matrix)
  riskmap(3,3,4,matrix)

  categories("Financial",matrix)
  categories("Environment",matrix)
  categories("Health & Safety",matrix)

  return matrix
  
