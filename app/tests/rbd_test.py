import sys
sys.path.append('/home/runner/RAMSuite')

from app.availability.static.helpers import ram_functions as ram

#blank_rbd = ram.new_rbd()
ex = ram.rbd_examples()

config_file = ex["small"]["firewater"]

rbd_file = ram.prepare_rbd(config_file = config_file)
print(rbd_file["config"])

image = ram.draw_rbd_image(rbd_file["size"],rbd_file["config"])

#print(image)