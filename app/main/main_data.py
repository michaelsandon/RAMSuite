site_map = [{
  'Name': "Home",
  'Route': "main.index",
  'Desc': "Home"
}, {
  'Name':
  'Survival',
  'Route':
  "survival.index",
  'Desc':
  'lifetime anaylsis modules to determine failure patterns',
  'Children': [{
    'Name': "Sampling",
    'Route': "survival.distsample",
    'Desc': "main.index"
  }, {
    'Name': "Survival Fit",
    'Route': "survival.survivalfit",
    'Desc': "main.index"
  }]
}, {
  'Name':
  'Uptime',
  'Desc':
  'RAM simulation type model to determine stream uptime, throughput etc.',
  'Route':
  "availability.index",
  'Children': [{
    'Name': "Single Package Uptime",
    'Route': "availability.packageuptime",
    'Desc': "availability.packageuptime"
  }]
}, {
  'Name': 'Cost',
  'Desc': 'Lifecycle cost evaluation module',
  'Route': "main.index"
}, {
  'Name': 'Maintenance',
  'Desc': "RCM, Strategy tester",
  'Route': "main.index"
}, {
  'Name': 'Risk',
  'Desc': 'Tba',
  'Route': "main.index"
}]
