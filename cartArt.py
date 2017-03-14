import urllib, StringIO
from PIL import Image
from math import log, exp, tan, atan, pi, ceil

EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

print "Earth radius: {} \t Equator circum: {} \t Initial res: {} \t Origin shift: {}".format(EARTH_RADIUS, EQUATOR_CIRCUMFERENCE, INITIAL_RESOLUTION, ORIGIN_SHIFT)

def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * ORIGIN_SHIFT) /180.0
    res = INITIAL_RESOLUTION / (2**zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py

def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2**zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon

############################################

# a neighbourhood in Lajeado, Brazil:

upperleft =  '-29.44,-52.0'  
lowerright = '-29.45,-51.98'

zoom = 18   # be careful not to get too many images!

############################################

ullat, ullon = map(float, upperleft.split(','))
lrlat, lrlon = map(float, lowerright.split(','))

# Set some important parameters
scale = 1
maxsize = 640 #original

widthmaxsize = 1940
heightmaxsize = 900

# convert all these coordinates to pixels
ulx, uly = latlontopixels(ullat, ullon, zoom)
lrx, lry = latlontopixels(lrlat, lrlon, zoom)

# calculate total pixel dimensions of final image
dx, dy = lrx - ulx, uly - lry

# calculate rows and columns
cols, rows = int(ceil(dx/maxsize)), int(ceil(dy/maxsize))
print "Number of cols: {}".format(cols)
print "Number of rows: {}".format(rows)

# calculate pixel dimensions of each small image
bottom = 120
width = int(ceil(dx/cols))
height = int(ceil(dy/rows))
heightplus = height + bottom


final = Image.new("RGB", (int(dx), int(dy)))
for x in range(cols):
    for y in range(rows):
        dxn = width * (0.5 + x)
        dyn = height * (0.5 + y)
        latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom/2, zoom)
        position = ','.join((str(latn), str(lonn)))
        print x, y, position
        urlparams = urllib.urlencode({'center': position,
                                      'zoom': str(zoom),
                                      'size': '%dx%d' % (width, heightplus),
                                      'maptype': 'roadmap',
                                      'sensor': 'false',
                                      'scale': scale})
        url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
        f=urllib.urlopen(url)
        im=Image.open(StringIO.StringIO(f.read()))
        final.paste(im, (int(x*width), int(y*height)))
final.show()