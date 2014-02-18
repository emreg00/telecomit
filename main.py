import os, cPickle, numpy
from toolbox import configuration
from telcomit import *

CONFIG = configuration.Configuration() 

def main():
    create_dir_hierarchy()
    output_values()
    return

def output_values():
    w = get_weather_info()
    t = get_transportation_info() 
    #g = get_grid_info()
    timestep = Timestep(d_start = 20131201, d_end = 20131231, t_start = 0000, t_end = 2350, t_interval = 10)
    file_name = CONFIG.get("output_dir") + "/combined.dat"
    f = open(file_name, 'w')
    f.write("t timestamp grid intensity condition speed n.in n.out n.all n.move n.stop\n")
    i = 0
    for day, time in timestep:
	print day, time
	grid_to_values = t.get_trafic(day, time)
	if grid_to_values is None:
	    continue
	for grid_id, values in grid_to_values.iteritems():
	    intensity, condition = w.get_weather(day, time, grid_id) 
	    if intensity is None or intensity == 0:
		continue
	    measurements = []
	    for vals in values:
		direction, speed, deviation, n_in, n_out, n_ignition, n_moving, n_stopped = vals
		measurements.append((speed, n_in, n_out, n_in + n_out, n_moving, n_stopped))
	    f.write("%d %s %d %d %d %s\n" % (i, str(day)+str(time), grid_id, intensity, condition, " ".join(map(str, numpy.mean(measurements, axis=0)))))
	    i += 1
    f.close()
    return


def create_dir_hierarchy():
    output_dir = CONFIG.get("output_dir") + "/" 
    if not os.path.exists(output_dir):
	os.mkdir(output_dir)
    return


def get_weather_info():
    file_name = CONFIG.get("weather_file")
    w = Weather(file_name)
    print w.get_weather(20131224, 710, 4723) # (88, 1)
    return w


def get_grid_info():
    file_name = CONFIG.get("grid_file")
    g = Grid(file_name)
    for x,y in g.get_coordinates(4723):
	print x, y # 9.077636776453351, 45.45819465173446
    return g


def get_transportation_info():
    file_name = CONFIG.get("transportation_file")
    t = Transportation(file_name)
    print t.get_trafic(20131224, 710, 4723) # [ 0.  1.  1.  0.]
    return t

if __name__ == "__main__":
    main()

