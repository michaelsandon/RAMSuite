import availability_functions as av
from datetime import datetime

start = datetime.now()
test = av.package_uptime_thread(n_parallel=3, n_req = 2, n_sims = 500)
#test = av.package_uptime_pool(n_sims=50)
test2 = av.uptime_statistics_pool(test)
end = datetime.now()
#test3 = av._package_uptime()
#print(test)
#print(list(test3.columns))
print(test2)
print(end - start)