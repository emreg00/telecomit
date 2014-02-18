
import numpy, datetime

class Timestep(object):

    def __init__(self, d_start, d_end, t_start=0, t_end=2350, t_interval=10):
	self.d_current = d_start
	self.d_end = d_end
	self.t_current = t_start
	self.t_end = t_end
	self.t_interval = t_interval

    def __iter__(self):
	return self

    def next(self):
	txt = "%s" % self.d_current
	txt2 = "%s" % self.t_current
	k = 4 - len(txt2)
	txt2 = "0"*k + txt2
	#print (int(txt[:4]), int(txt[4:6]), int(txt[6:]), int(txt2[:2]), int(txt2[2:])) 
	d = datetime.datetime(int(txt[:4]), int(txt[4:6]), int(txt[6:]), int(txt2[:2]), int(txt2[2:])) + datetime.timedelta(minutes = self.t_interval)
	self.d_current = d.year*10000 + d.month*100 + d.day
	self.t_current = d.hour*100 + d.minute
	#print self.d_current, self.d_end, self.t_current, self.t_end
	if self.d_current > self.d_end or (self.d_current == self.d_end and self.t_current > self.t_end):
	    raise StopIteration
	return self.d_current, self.t_current


class Weather(object):
    """
    (day, time) = [ (intensity, condition), ... ]
    4 quadrants
    condition: 1 rain, 2 snow
    """

    def __init__(self, file_name):
	self.day_to_time_to_values = None
	self._parse_weather_info(file_name)
	return

    def _parse_weather_info(self, file_name):
	f = open(file_name)
	self.day_to_time_to_values = {}
	i = 0
	for line in f.readlines():
	    i %= 4
	    i += 1
	    words = line.strip().split(",")
	    k = len("yyyymmdd")
	    day = int(words[0][:k])
	    time = int(words[0][k:])
	    #print day, time
	    quadrant, measured, intensity, condition = words[1:]
	    assert int(quadrant) == i
	    self.day_to_time_to_values.setdefault(day, {}).setdefault(time, []).append((int(intensity), int(condition)))
	#print len(self.day_to_time_to_values)
	#print self.day_to_time_to_values[20140101]
	#print self.day_to_time_to_values[20140101][2240]
	return 

    @staticmethod
    def get_quadrant(grid_id):
	y = grid_id / 100 
	x = grid_id % 100
	if x == 0:
	    y -= 1
	    x = 100
	quadrant = None
	if x >= 1 and x <= 50:
	    if y >= 50 and y <= 99:
		quadrant = 1
	    elif y >= 0 and y <= 49:
		quadrant = 4
	    else:
		raise ValueError("Inconsistent coordinates")
	elif x >= 51 and x <= 100:
	    if y >= 50 and y <= 99:
		quadrant = 2
	    elif y >= 0 and y <= 49:
		quadrant = 3
	    else:
		raise ValueError("Inconsistent coordinates")
	return quadrant


    def get_weather(self, day, time, grid_id):
	quadrant = Weather.get_quadrant(grid_id)
	try:
	    d = self.day_to_time_to_values[day][time]
	    val = d[quadrant-1]
	except:
	    val = None, None
	return val


class Transportation(object):
    """
    (day, time, grid_id) = [ (direction, speed, ...), ... ]
    4+1 directions
    """
    
    DIRECTION_TO_VALUE = { "none": 0, "NORTH": 1, "EST": 2, "SOUTH": 3, "WEST": 4 }
    HEADER_TO_IDX = dict((word, i) for i, word in enumerate(["direction", "speed", "deviation", "n_in", "n_out", "n_ignition", "n_moving", "n_stopped"]))

    def __init__(self, file_name):
	self.day_to_time_to_grid_to_values = None
	self._parse_transportation_info(file_name)
	return

    def _parse_transportation_info(self, file_name):
	f = open(file_name)
	self.day_to_time_to_grid_to_values = {}
	for line in f.readlines():
	    words = line.strip().split(",")
	    grid_id = int(words[0])
	    word = words[1].replace("-", "").replace(" ", "").replace(":","")
	    k = len("yyyymmdd")
	    day = int(word[:k])
	    time = int(word[k:])
	    direction = Transportation.DIRECTION_TO_VALUE[words[2]]
	    speed, deviation, n_in, n_out, n_ignition, n_moving, n_stopped = words[3:]
	    self.day_to_time_to_grid_to_values.setdefault(day, {}).setdefault(time, {}).setdefault(grid_id, []).append((direction, float(speed), float(deviation), int(n_in), int(n_out), int(n_ignition), int(n_moving), int(n_stopped)))
	#print len(self.day_to_time_to_grid_to_values), len(self.day_to_time_to_grid_to_values[20131223][1230])
	#print self.day_to_time_to_grid_to_values[20131223][1230][5168]

    def get_trafic(self, day, time, grid_id = None, direction = None):
	grid_to_values = None
	if day in self.day_to_time_to_grid_to_values:
	    time_to_grid_to_values = self.day_to_time_to_grid_to_values[day]
	    if time in time_to_grid_to_values:
		grid_to_values = time_to_grid_to_values[time]
	if grid_id is None or grid_to_values is None:
	    return grid_to_values
	val = None
	if grid_id in grid_to_values:
	    values = []
	    for direction_, speed, deviation, n_in, n_out, n_ignition, n_moving, n_stopped in grid_to_values[grid_id]:
		val = (speed, n_in + n_out, n_moving, n_stopped)
		if direction is not None and direction == direction_:
		    break
		else:
		    values.append(val)
	    if direction is None:
		val = numpy.mean(values, axis=0)
	return val


class Grid(object):

    def __init__(self, file_name):
	self.grid = None
	self._parse_grid_info(file_name)

    def _parse_grid_info(self, file_name):
	import json
	self.grid = json.load(open(file_name))
	#from pprint import pprint
	#pprint(self.grid)
	return 

    def get_coordinates(self, grid_id):
	coordinates = self.grid["features"][grid_id-1]["geometry"]["coordinates"][0]
	return coordinates


