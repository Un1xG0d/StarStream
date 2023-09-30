import math
import requests

def earth_radius_in_meters(latitude_radians):
	# latitudeRadians is geodetic, i.e. that reported by GPS.
	# http:#en.wikipedia.org/wiki/Earth_radius
	a = 6378137.0 # equatorial radius in meters
	b = 6356752.3 # polar radius in meters
	cos = math.cos(latitude_radians)
	sin = math.sin(latitude_radians)
	t1 = a * a * cos
	t2 = b * b * sin
	t3 = a * cos
	t4 = b * sin
	return math.sqrt((t1*t1 + t2*t2) / (t3*t3 + t4*t4))

def geocentric_latitude(lat):
	# Convert geodetic latitude "lat" to a geocentric latitude "clat".
	# Geodetic latitude is the latitude as given by GPS.
	# Geocentric latitude is the angle measured from center of Earth between a point and the equator.
	# https:#en.wikipedia.org/wiki/Latitude#Geocentric_latitude
	e2 = 0.00669437999014
	return math.atan((1.0 - e2) * math.tan(lat))


def location_to_point(c):
	d = {}
	# Convert (lat, lon, elv) to (x, y, z).
	lat = c["lat"] * math.pi / 180.0 
	lon = c["lon"] * math.pi / 180.0
	radius = earth_radius_in_meters(lat)
	geo_centric_lat   = geocentric_latitude(lat)

	cos_lon = math.cos(lon)
	sin_lon = math.sin(lon)
	cos_lat = math.cos(geo_centric_lat)
	sin_lat = math.sin(geo_centric_lat)
	x = radius * cos_lon * cos_lat
	y = radius * sin_lon * cos_lat
	z = radius * sin_lat

	# We used geocentric latitude to calculate (x,y,z) on the Earth"s ellipsoid.
	# Now we use geodetic latitude to calculate normal vector from the surface, to correct for elevation.
	cos_glat = math.cos(lat)
	sin_glat = math.sin(lat)
	nx = cos_glat * cos_lon
	ny = cos_glat * sin_lon
	nz = sin_glat

	x = x + (c["elv"] * nx)
	y = y + (c["elv"] * ny)
	z = z + (c["elv"] * nz)

	d["x"] = x
	d["y"] = y
	d["z"] = z
	d["radius"] = radius
	d["nx"] = nx
	d["ny"] = ny
	d["nz"] = nz
	return d

def distance(ap, bp):
	dx = ap["x"] - bp["x"]
	dy = ap["y"] - bp["y"]
	dz = ap["z"] - bp["z"]
	return math.sqrt (dx*dx + dy*dy + dz*dz)

def rotate_globe (b, a, bradius, aradius):
	d = {}
	# Get modified coordinates of "b" by rotating the globe so that "a" is at lat=0, lon=0.
	br = {"lat": b["lat"], "lon": (b["lon"] - a["lon"] ), "elv": b["elv"]}
	brp = location_to_point(br)

	# Rotate brp cartesian coordinates around the z-axis by a.lon degrees,
	# then around the y-axis by a.lat degrees.
	# Though we are decreasing by a.lat degrees, as seen above the y-axis,
	# this is a positive (counterclockwise) rotation (if B"s longitude is east of A"s).
	# However, from this point of view the x-axis is pointing left.
	# So we will look the other way making the x-axis pointing right, the z-axis
	# pointing up, and the rotation treated as negative.

	alat = geocentric_latitude(-a["lat"] * math.pi / 180.0)
	acos = math.cos(alat)
	asin = math.sin(alat)

	d["x"]  = (brp["x"] * acos) - (brp["z"] * asin)
	d["y"] =  brp["y"]
	d["z"] = (brp["x"] * asin) + (brp["z"] * acos)
	d["radius"] = bradius
	return d 

def normalize_vector_diff(b, a):
	d = {}
	# Calculate norm(b-a), where norm divides a vector by its length to produce a unit vector.
	dx = b["x"] - a["x"]
	dy = b["y"] - a["y"]
	dz = b["z"] - a["z"]
	dist2 = dx*dx + dy*dy + dz*dz
	if (dist2 == 0):
		return 
	dist = math.sqrt(dist2)
	d["x"] = dx/dist
	d["y"] = dy/dist
	d["z"] = dz/dist
	d["radius"] = 1.0
	return d

def calculate(a, b):
	d = {}
	ap = location_to_point(a)
	bp = location_to_point(b)
	distkm = 0.001 * distance(ap,bp)
	d["distkm"] = distkm

	# Let"s use a trick to calculate azimuth:
	# Rotate the globe so that point A looks like latitude 0, longitude 0.
	# We keep the actual radii calculated based on the oblate geoid,
	# but use angles based on subtraction.
	# Point A will be at x=radius, y=0, z=0.
	# Vector difference B-A will have dz = N/S component, dy = E/W component.
	br = rotate_globe (b, a, bp["radius"], ap["radius"])
	if (br["z"]*br["z"] + br["y"]*br["y"] > 1.0e-6):
		theta = math.atan2(br["z"], br["y"]) * 180.0 / math.pi
		azimuth = 90.0 - theta
		if (azimuth < 0.0):
			azimuth = azimuth + 360.0
		if (azimuth > 360.0):
			azimuth = azimuth - 360.0
	d["azimuth"] = azimuth

	bma = normalize_vector_diff(bp, ap)
	# Calculate altitude, which is the angle above the horizon of B as seen from A.
	# Almost always, B will actually be below the horizon, so the altitude will be negative.
	# The dot product of bma and norm = cos(zenith_angle), and zenith_angle = (90 deg) - altitude.
	# So altitude = 90 - acos(dotprod).
	altitude = 90.0 - (180.0 / math.pi)*math.acos(bma["x"]*ap["nx"] + bma["y"]*ap["ny"] + bma["z"]*ap["nz"])
	d["altitude"] = altitude
	return d

def get_home_location(coords):
	d = {}
	d["lat"] = coords[0]
	d["lon"] = coords[1]
	d["elv"] = get_elevation_of_location(coords)
	return d

def get_iss_location(coords):
	d = {}
	d["lat"] = coords[0]
	d["lon"] = coords[1]
	d["elv"] = coords[2] * 1000
	return d

def get_elevation_of_location(coords):
	return float(requests.get("https://api.open-meteo.com/v1/elevation?latitude=" + str(coords[0]) + "&longitude=" + str(coords[1])).json()["elevation"][0])

def get_distance_and_elevation_angle(coords_1, coords_2):
	a = get_home_location(coords_1)
	b = get_iss_location(coords_2)
	data = calculate(a, b)
	return data["distkm"], data["altitude"]
