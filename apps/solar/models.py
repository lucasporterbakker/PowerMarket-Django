from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from powermarket.email import send_templated_email

import uuid
from easy_thumbnails.fields import ThumbnailerImageField
from operator import add
import os.path

from powermarket.choices import CURRENCY_CHOICES
from powermarket.models import AbstractTimestampModel
from apps.location.models import Location
from apps.manager.models import Project
from apps.user.models import Contact
from .calculations import calc_monthly_profit

# ML imports
import scipy
import scipy.signal
from pathlib import Path
from io import BytesIO
import urllib.request
import json

import time
import math
from PIL import Image, ImageDraw
import numpy
numpy.set_printoptions(threshold=numpy.nan)
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from .calculations import (
    cum_timeseries,
    cum_lifetime_timeseries,
    environmental_benefits_serialized,
    get_system_cost,
    get_energy_price,
)

#Should probably put machine learning code in separate file but easiest to put it here for now
IMAGE_SIZE = 28
NUM_CHANNELS = 1
PIXEL_DEPTH_AZ = 255
PIXEL_DEPTH_ALT = 150  # 255
NUM_LABELS_AZ = 36
NUM_LABELS_ALT = 9
SEED = 66478  # Set to None for random seed.
BATCH_SIZE = 10000
NUM_EPOCHS = 1000
EVAL_BATCH_SIZE = 100
EVAL_FREQUENCY = 10000  # Number of steps between evaluations.
FLAGS = None
GMAPSIZE = 640
IMSCALEFACTOR = 1.0  # when generating the data, google maps with zoom level 17 are rescaled by this factor to match the lidar data which is approx 1sqm/pixel
OUTPUTSOLARMAP = False
ZOOM = 17
# From http://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map
MERCATOR_RANGE = 256

def bound(value, opt_min, opt_max):
    if (opt_min != None):
        value = max(value, opt_min)
    if (opt_max != None):
        value = min(value, opt_max)
    return value


def degreesToRadians(deg):
    return deg * (math.pi / 180)


def radiansToDegrees(rad):
    return rad / (math.pi / 180)


class G_Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class G_LatLng:
    def __init__(self, lt, ln):
        self.lat = lt
        self.lng = ln


class MercatorProjection:

    def __init__(self):
        self.pixelOrigin_ = G_Point(MERCATOR_RANGE / 2, MERCATOR_RANGE / 2)
        self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360
        self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2 * math.pi)

    def fromLatLngToPoint(self, latLng, opt_point=None):
        point = opt_point if opt_point is not None else G_Point(0, 0)
        origin = self.pixelOrigin_
        point.x = origin.x + latLng.lng * self.pixelsPerLonDegree_
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.  This is about a third of a tile past the edge of the world tile.
        siny = bound(math.sin(degreesToRadians(latLng.lat)), -0.9999, 0.9999)
        point.y = origin.y + 0.5 * math.log((1 + siny) / (1 - siny)) * -     self.pixelsPerLonRadian_
        return point

    def fromPointToLatLng(self, point):
        origin = self.pixelOrigin_
        lng = (point.x - origin.x) / self.pixelsPerLonDegree_
        latRadians = (point.y - origin.y) / -self.pixelsPerLonRadian_
        lat = radiansToDegrees(2 * math.atan(math.exp(latRadians)) - math.pi / 2)
        return G_LatLng(lat, lng)

    def getCorners(self, center, ZOOM, mapWidth, mapHeight):
        scale = 2 ** ZOOM
        proj = self #MercatorProjection()
        centerPx = proj.fromLatLngToPoint(center)
        SWPoint = G_Point(centerPx.x - (mapWidth / 2) / scale, centerPx.y + (mapHeight / 2) / scale)
        SWLatLon = proj.fromPointToLatLng(SWPoint)
        NEPoint = G_Point(centerPx.x + (mapWidth / 2) / scale, centerPx.y - (mapHeight / 2) / scale)
        NELatLon = proj.fromPointToLatLng(NEPoint)
        return {
            'N': NELatLon.lat,
            'E': NELatLon.lng,
            'S': SWLatLon.lat,
            'W': SWLatLon.lng,
        }

def ReadASCLidarData(filename):
  with open(filename) as f:
    content = f.readlines()

  l=content[0]
  cols=l.split()
  ncol=int(cols[1])
  l=content[1]
  rows=l.split()
  nrow=int(rows[1])
  data=numpy.zeros((nrow,ncol),dtype='float')
  for r in xrange(6,nrow+6):
    l=content[r]
    data[r-6,:]=numpy.array([float(i) for i in l.split()])

  return data


def applyML(inputpoly, id):

    imgfname=settings.MEDIA_ROOT+'/' #base for output filenames

    outhtml="<table>"

    # Need to get coordinates from tuple of tuples of tuples into an array of arrays
    tmppoly=inputpoly.coords

    tmppoly2=[]
    for i in range(len(tmppoly)):
        tmppoly3=[]
        for j in range(len(tmppoly[i][0])):
            tmppoly3.append([tmppoly[i][0][j][0],tmppoly[i][0][j][1]])
        tmppoly2.append(tmppoly3)

    mpoly=numpy.asarray(tmppoly2)

  # if len(sys.argv) >= 2:
  #   mpoly=numpy.array(eval(sys.argv[1]))
  # else:
  #   #Test polygons
  #   # Array of polygons of lat/lon coordinates in WGS84
  #   #mpoly=[]
  #   #mpoly=numpy.array([[[52.477886, 52.477468, 52.477455, 52.477864],[-1.859169,-1.85919,-1.860466,-1.860509]], [[52.479526,52.479239,52.479115,52.4794],[-1.857345,-1.857291,-1.858921,-1.858932]]])
  #   mpoly=numpy.array([[[52.477886,-1.859169],[52.477468,-1.85919],[52.477455,-1.860466],[52.477864,-1.860509]]])
  #   mpoly=numpy.array([[[52.477886,-1.859169],[52.477468,-1.85919],[52.477455,-1.860466],[52.477864,-1.860509]], [[52.479526,-1.857345],[52.479239,-1.857291],[52.479115,-1.858921],[52.4794,-1.858932],[52.4794,-1.858932]], [[52.478716,-1.862334],[52.478442,-1.862323],[52.478448,-1.863556],[52.478694,-1.863577]], [[52.476997,-1.861047],[52.476775,-1.861079],[52.476815,-1.861807],[52.477021,-1.861775]], [[52.478768,-1.857506],[52.478598,-1.857517],[52.47854,-1.859286],[52.478707,-1.859307]], [[52.477376,-1.859684],[52.477004,-1.859652],[52.476985,-1.860573],[52.477348,-1.860573]], [[52.477742,-1.861014],[52.477468,-1.861047],[52.47752,-1.862129],[52.477773,-1.862118]]])
  #   #mpoly=numpy.array([[[52.480924,-1.857034],[52.476442,-1.856937],[52.476527,-1.863835],[52.480798,-1.863599]]]) # large area in brum
  #   #  mpoly=numpy.array([[[23.242263,77.45961],[23.24041,77.459577],[23.24037,77.457207],[23.242249,77.457175]], [[23.242342,77.462356],[23.240646,77.462345],[23.240666,77.459954],[23.242328,77.459922]], [[23.246935,77.462335],[23.245595,77.462324],[23.245595,77.459933],[23.246922,77.4599]]]) #india factories
  #   ##  mpoly=numpy.array([[[23.242844,77.517277],[23.240765,77.516934],[23.240577,77.51598],[23.242634,77.516473]]]) #india farmland
  #   ##  mpoly=numpy.array([[[23.250928,77.541996],[23.249957,77.541685],[23.248671,77.541674],[23.246766,77.541677],[23.246753,77.540221],[23.246859,77.53913],[23.247281,77.538468],[23.24817,77.53843],[23.249019,77.538993],[23.2505,77.539691]]]) #india farmland


    #Work out the size of a pixel in metres at this latitude and for this google map zoom level
    METERSPERPIXEL = 156543.03392 * math.cos(mpoly[0][0][0] * math.pi / 180.0) / math.pow(2,ZOOM)
    IMSCALEFACTOR=METERSPERPIXEL #training was done at approx 1 pixel to 1m, so scale the image and any region coordinates to that scale
    print(IMSCALEFACTOR)

    #Loop through the regions (is there a better way to do this without repeatedly loading and applying models?)
    SystemAreas=[]
    SystemCapacities=[]
    PanelNumbers=[]
    SystemTilts=[]
    SystemOrientations=[]
    AnnualGenerationEstimates=[]
    MonthlyGenerationEstimates=[]
    for i in xrange(0,mpoly.shape[0]):
        mcentre=numpy.mean(mpoly[i], axis=0)

        # Calculate coordinates of image corners
        centerPoint = G_LatLng(mcentre[0], mcentre[1])
        proj=MercatorProjection()
        corners = proj.getCorners(centerPoint, ZOOM, GMAPSIZE, GMAPSIZE)

        # Get the google map image
        position = ','.join((str(mcentre[0]), str(mcentre[1])))
        urlparams = urllib.parse.urlencode({'center': position,
                                      'zoom': str(ZOOM),
                                      'size': '%dx%d' % (GMAPSIZE, GMAPSIZE),
                                      'maptype': 'satellite',
                                      'sensor': 'false',
                                      'scale': 1,
                                      'key': 'AIzaSyCiS7f7yHR4qZDm5ot2jwWbQQRteGA11k4'})

        url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
        f=urllib.request.urlopen(url)
        im=Image.open(BytesIO(f.read())).convert('RGB')
        im=im.resize((round(GMAPSIZE*IMSCALEFACTOR),round(GMAPSIZE*IMSCALEFACTOR)), resample=Image.BICUBIC)
        #im=gaussian_filter(im, sigma=0.5)

        ##  for i in xrange(0,4):
        ##    im.putpixel((mpolyc[1][i],mpolyc[0][i]),255)
        ##  im.show()


        ##    imgfname='D:/Documents/Powermarket/ML/CNNattempt/USETILEDMAPDATATOIMPROVEIMAGES/sp0986_DSM_1m_reproc_testim'
        ##    im = Image.open(imgfname+'.png')

        #Set up the input data
        rgb = numpy.array(im)
        gray = numpy.mean(rgb, -1)

        gray_az = (gray-(PIXEL_DEPTH_AZ/2.0))/PIXEL_DEPTH_AZ
        gray_alt = (gray-(PIXEL_DEPTH_ALT/2.0))/PIXEL_DEPTH_ALT
        sz=gray.shape


        mpolyc=numpy.zeros((len(mpoly[i]),2))
        for j in xrange(0, len(mpoly[i])):
          mpolyc[j][1]=round((GMAPSIZE*IMSCALEFACTOR*(1-(mpoly[i][j][0]-corners['S'])/(corners['N']-corners['S']))))
          mpolyc[j][0]=round((GMAPSIZE*IMSCALEFACTOR*(1-(mpoly[i][j][1]-corners['E'])/(corners['W']-corners['E']))))

        maskim = Image.new('L', (sz[0], sz[1]), 0)
        # Need the poly as a list of tuples
        thispoly=[]
        for j in xrange(0, len(mpolyc)):
          thispoly.append((mpolyc[j][0], mpolyc[j][1]))

        ImageDraw.Draw(maskim).polygon(thispoly, outline=1, fill=1)
        mask = numpy.array(maskim)

        numpixels=mask.sum() # sz[0]*sz[1]
        print("Numpixels: "+str(numpixels))
        test_data_az=numpy.zeros((numpixels, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS),dtype=numpy.float32)
        test_data_alt=numpy.zeros((numpixels, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS),dtype=numpy.float32)
        test_labels_az=numpy.zeros(numpixels, dtype=numpy.int64)
        test_labels_alt=numpy.zeros(numpixels, dtype=numpy.int64)

        ct=0;
        imszdiv2=round(IMAGE_SIZE/2)
        for r in xrange(0, sz[0]-IMAGE_SIZE):
            for c in xrange(0, sz[1]-IMAGE_SIZE):
                if mask[r+imszdiv2,c+imszdiv2]>0:
                    for rr in xrange(0,IMAGE_SIZE):
                        for cc in xrange(0,IMAGE_SIZE):
                            test_data_az[ct,rr,cc,0]=gray_az[r+rr,c+cc]
                            test_data_alt[ct,rr,cc,0]=gray_alt[r+rr,c+cc]
                    ct+=1



        ##  # Load the ground truth Lidar data for comparison
        ##  lidardata=ReadASCLidarData('H:/AllData/REPROC/sp0986_DSM_1m_reproc.asc')
        ##  blurred = lidardata #gaussian_filter(lidardata, sigma=1)
        ##
        ##  # Calculate orientation info from Lidar
        ##  sz=lidardata.shape
        ##  AZ=numpy.zeros(sz,dtype='float')
        ##  ALT=numpy.zeros(sz,dtype='float')
        ##  noS=numpy.zeros(sz,dtype='int')
        ##  angresdeg=10.0001
        ##  angleres=angresdeg*math.pi/180
        ##  for r in xrange(0,sz[0]-1):
        ##    for c in xrange(0,sz[1]-1):
        ##      if lidardata[r,c]<=-999:
        ##        noS[r,c]=1
        ##      else:
        ##        Gx=blurred[r,c+1]-blurred[r,c]
        ##        Gy=blurred[r+1,c]-blurred[r,c]
        ##        AZ[r,c]=math.atan2(-Gy, -Gx)
        ##        if AZ[r,c]<0:
        ##          AZ[r,c]+=2*math.pi
        ##        AZ[r,c]=math.floor(AZ[r,c]/angleres)
        ##        ALT[r,c]=math.acos(1.0/(Gx*Gx+Gy*Gy+1.0))
        ##        ALT[r,c]=math.floor(ALT[r,c]/angleres)
        ##
        ##        if ALT[r,c]==8:
        ##          ALT[r,c]=5
        ##        elif ALT[r,c]>3:
        ##          ALT[r,c]=4
        ##
        ##  # Output ground truth orientation info
        ##  rescaled = (255.0 / AZ.max() * (AZ - AZ.min())).astype(numpy.uint8)
        ##  im = Image.fromarray(rescaled)
        ##  im.save('tmptrueAZ.png')
        ##
        ##  rescaled = (255.0 / ALT.max() * (ALT - ALT.min())).astype(numpy.uint8)
        ##  im = Image.fromarray(rescaled)
        ##  im.save('tmptrueALT.png')

        ##  # Location of image
        ##  lat=52.561776 #brum
        ##  lon=-1.883420
        ##  lat=28.571778 #new delhi
        ##  lon=77.225461
        ##  lat=52.491192 #berlin
        ##  lon=13.362549
        ##  lat=53.235755 #macclesfield
        ##  lon=-2.130779

        # lookup new google map to save image: https://maps.googleapis.com/maps/api/staticmap?center=28.571778,%2077.225461&maptype=satellite&zoom=19&size=640x640

        # Load and run the ALT network
        new_graph = tf.Graph()
        with tf.Session(graph=new_graph) as sess:
        #       new_saver = tf.train.import_meta_graph('C:/Users/phil/Documents/Powermarket/ALTTrain/safemodelsmoothingpt5/latestmodel_alt.meta')
        #       new_saver.restore(sess, 'C:/Users/phil/Documents/Powermarket/ALTTrain/safemodelsmoothingpt5/latestmodel_alt')
        #       new_saver = tf.train.import_meta_graph('/Users/phil/PowerMarketWebsite/website/apps/solar/MLdata/basicapproach30khidden/latestmodel_alt.meta')
        #       new_saver.restore(sess, '/Users/phil/PowerMarketWebsite/website/apps/solar/MLdata/basicapproach30khidden/latestmodel_alt')

# Correct paths for demo sure it is not the better way because PROJECT_DIR and BASE_DIR are already in base.py
            PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
            BASE_DIR = os.path.dirname(PROJECT_DIR)
            ML_DIR = os.path.dirname(PROJECT_DIR, "/MLdata/")
            if  os.path.isfile(ML_DIR, "latestmodel_alt.meta"):
                #settings.DEBUG: #settings.DEBUG is true even on localhost, not sure why
                new_saver = tf.train.import_meta_graph(ML_DIR, "latestmodel_alt.meta")
                new_saver.restore(sess, ML_DIR, "latestmodel_alt")
            else:
                new_saver = tf.train.import_meta_graph(ML_DIR, "latestmodel_alt.meta")
                new_saver.restore(sess, ML_DIR, "latestmodel_alt")

            conv1_weights=tf.get_collection("conv1_weights")[0]
            conv1_biases=tf.get_collection("conv1_biases")[0]
            conv2_weights=tf.get_collection("conv2_weights")[0]
            conv2_biases=tf.get_collection("conv2_biases")[0]
            fc1_weights=tf.get_collection("fc1_weights")[0]
            fc1_biases=tf.get_collection("fc1_biases")[0]
            fc2_weights=tf.get_collection("fc2_weights")[0]
            fc2_biases=tf.get_collection("fc2_biases")[0]

            def model_alt(data, train=False):
                """The Model definition."""
                # 2D convolution, with 'SAME' padding (i.e. the output feature map has
                # the same size as the input). Note that {strides} is a 4D array whose
                # shape matches the data layout: [image index, y, x, depth].
                conv = tf.nn.conv2d(data,
                                    conv1_weights,
                                    strides=[1, 1, 1, 1],
                                    padding='SAME')
                # Bias and rectified linear non-linearity.
                relu = tf.nn.relu(tf.nn.bias_add(conv, conv1_biases))
                # Max pooling. The kernel size spec {ksize} also follows the layout of
                # the data. Here we have a pooling window of 2, and a stride of 2.
                pool = tf.nn.max_pool(relu,
                                        ksize=[1, 2, 2, 1],
                                        strides=[1, 2, 2, 1],
                                        padding='SAME')
                conv = tf.nn.conv2d(pool,
                                    conv2_weights,
                                    strides=[1, 1, 1, 1],
                                    padding='SAME')
                relu = tf.nn.relu(tf.nn.bias_add(conv, conv2_biases))
                pool = tf.nn.max_pool(relu,
                                      ksize=[1, 2, 2, 1],
                                      strides=[1, 2, 2, 1],
                                      padding='SAME')
                # Reshape the feature map cuboid into a 2D matrix to feed it to the
                # fully connected layers.
                pool_shape = pool.get_shape().as_list()
                reshape = tf.reshape(pool, [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]])
                # Fully connected layer. Note that the '+' operation automatically
                # broadcasts the biases.
                hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases)

                return tf.matmul(hidden, fc2_weights) + fc2_biases


            # Small utility function to evaluate a dataset by feeding batches of data to
            # {eval_data} and pulling the results from {eval_predictions}.
            # Saves memory and enables this to run on smaller GPUs.
            def eval_in_batches_alt(data, sess):
                """Get all predictions for a dataset by running it in small batches."""
                size = data.shape[0]
#                if size < EVAL_BATCH_SIZE:
#                    raise ValueError("batch size for evals larger than dataset: %d" % size)
                predictions = numpy.ndarray(shape=(size, NUM_LABELS_ALT), dtype=numpy.float32)
                for begin in xrange(0, size, EVAL_BATCH_SIZE):
                    end = begin + EVAL_BATCH_SIZE
                    if end <= size:
                        predictions[begin:end, :] = sess.run(
                                                        eval_prediction,
                                                        feed_dict={eval_data: data[begin:end, ...]})
                    else:
                        batch_predictions = sess.run(
                                                eval_prediction,
                                                feed_dict={eval_data: data[-EVAL_BATCH_SIZE:, ...]})
                        predictions[begin:, :] = batch_predictions[begin - size:, :]

                return predictions


            #test_labels=eval_in_batches(test_data, sess)
            eval_data = tf.placeholder(
                            tf.float32,
                            shape=(min(numpixels,EVAL_BATCH_SIZE), IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

            eval_prediction = tf.nn.softmax(model_alt(eval_data))

            test_labels = eval_in_batches_alt(test_data_alt, sess)
            test_labels_alt=numpy.argmax(test_labels, 1)

            newALT=numpy.zeros(sz, dtype=numpy.float32)
            ct=0;
            for r in xrange(0, sz[0]-IMAGE_SIZE):
                for c in xrange(0, sz[1]-IMAGE_SIZE):
                    if mask[r+imszdiv2,c+imszdiv2]>0:
                        newALT[r+imszdiv2,c+imszdiv2]=round(255.0*test_labels_alt[ct]/NUM_LABELS_ALT)
                        ct+=1
                    else:
                        newALT[r+imszdiv2,c+imszdiv2]=gray[r+imszdiv2,c+imszdiv2]

            newALT=numpy.uint8(newALT)

            #rescaled = (255.0 / newALT.max() * (newALT - newALT.min())).astype(numpy.uint8)
            im = Image.fromarray(newALT)
            fname=imgfname+'ALT_' + id + '_region' + str(i) + '.png'
            im.save(fname)



        new_graph=tf.Graph()
        # Load and run the AZ network
        with tf.Session(graph=new_graph) as sess:
            if os.path.isfile('/Users/phil/PowerMarketWebsite/website/apps/solar/MLdata/basicapproach30khidden/latestmodel_alt.meta'):
                new_saver_az = tf.train.import_meta_graph('/Users/phil/PowerMarketWebsite/website/apps/solar/MLdata/safemodel2/latestmodel_az.meta')
                new_saver_az.restore(sess, '/Users/phil/PowerMarketWebsite/website/apps/solar/MLdata/safemodel2/latestmodel_az')
            else:
                # Correct path for demo
                new_saver_az = tf.train.import_meta_graph('/opt/webapp/apps/solar/MLdata/safemodel2/latestmodel_az.meta')
                new_saver_az.restore(sess, '/opt/webapp/apps/solar/MLdata/safemodel2/latestmodel_az')

            conv1_weights_az=tf.get_collection("conv1_weights")[0]
            conv1_biases_az=tf.get_collection("conv1_biases")[0]
            conv2_weights_az=tf.get_collection("conv2_weights")[0]
            conv2_biases_az=tf.get_collection("conv2_biases")[0]
            fc1_weights_az=tf.get_collection("fc1_weights")[0]
            fc1_biases_az=tf.get_collection("fc1_biases")[0]
            fc2_weights_az=tf.get_collection("fc2_weights")[0]
            fc2_biases_az=tf.get_collection("fc2_biases")[0]

            def model(data, train=False):
                """The Model definition."""
                # 2D convolution, with 'SAME' padding (i.e. the output feature map has
                # the same size as the input). Note that {strides} is a 4D array whose
                # shape matches the data layout: [image index, y, x, depth].
                conv = tf.nn.conv2d(data,
                                conv1_weights_az,
                                strides=[1, 1, 1, 1],
                                padding='SAME')
                # Bias and rectified linear non-linearity.
                relu = tf.nn.relu(tf.nn.bias_add(conv, conv1_biases_az))
                # Max pooling. The kernel size spec {ksize} also follows the layout of
                # the data. Here we have a pooling window of 2, and a stride of 2.
                pool = tf.nn.max_pool(relu,
                                  ksize=[1, 2, 2, 1],
                                  strides=[1, 2, 2, 1],
                                  padding='SAME')
                conv = tf.nn.conv2d(pool,
                                conv2_weights_az,
                                strides=[1, 1, 1, 1],
                                padding='SAME')
                relu = tf.nn.relu(tf.nn.bias_add(conv, conv2_biases_az))
                pool = tf.nn.max_pool(relu,
                                  ksize=[1, 2, 2, 1],
                                  strides=[1, 2, 2, 1],
                                  padding='SAME')
                # Reshape the feature map cuboid into a 2D matrix to feed it to the
                # fully connected layers.
                pool_shape = pool.get_shape().as_list()
                reshape = tf.reshape(pool, [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]])
                # Fully connected layer. Note that the '+' operation automatically
                # broadcasts the biases.
                hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights_az) + fc1_biases_az)

                return tf.matmul(hidden, fc2_weights_az) + fc2_biases_az


            test_labels=numpy.zeros(numpixels, dtype=numpy.int64)


            # Small utility function to evaluate a dataset by feeding batches of data to
            # {eval_data} and pulling the results from {eval_predictions}.
            # Saves memory and enables this to run on smaller GPUs.
            def eval_in_batches(data, sess):
                """Get all predictions for a dataset by running it in small batches."""
                size = data.shape[0]
#                if size < EVAL_BATCH_SIZE:
#                    raise ValueError("batch size for evals larger than dataset: %d" % size)
                predictions = numpy.ndarray(shape=(size, NUM_LABELS_AZ), dtype=numpy.float32)
                for begin in xrange(0, size, EVAL_BATCH_SIZE):
                    end = begin + EVAL_BATCH_SIZE
                    if end <= size:
                        predictions[begin:end, :] = sess.run(
                                                eval_prediction,
                                                feed_dict={eval_data: data[begin:end, ...]})
                    else:
                        batch_predictions = sess.run(
                                                eval_prediction,
                                                feed_dict={eval_data: data[-EVAL_BATCH_SIZE:, ...]})
                        predictions[begin:, :] = batch_predictions[begin - size:, :]
                return predictions


            #test_labels=eval_in_batches(test_data, sess)
            eval_data = tf.placeholder(
                                    tf.float32,
                                    shape=(min(numpixels,EVAL_BATCH_SIZE), IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

            eval_prediction = tf.nn.softmax(model(eval_data))

            test_labels = eval_in_batches(test_data_az, sess)
            test_labels_az=numpy.argmax(test_labels, 1)

            newAZ=numpy.zeros(sz, dtype=numpy.float32)
            ct=0;
            for r in xrange(0, sz[0]-IMAGE_SIZE):
                for c in xrange(0, sz[1]-IMAGE_SIZE):
                    if mask[r+imszdiv2,c+imszdiv2]>0:
                        newAZ[r+imszdiv2,c+imszdiv2]=round(255.0*test_labels_az[ct]/NUM_LABELS_AZ)
                        ct+=1
                    else:
                        newAZ[r+imszdiv2,c+imszdiv2]=gray[r+imszdiv2,c+imszdiv2]

            newAZ=numpy.uint8(newAZ)
            #rescaled = (255.0 / newAZ.max() * (newAZ - newAZ.min())).astype(numpy.uint8)
            im = Image.fromarray(newAZ)
            im.save(imgfname+'AZ_' + id + '_region' + str(i) + '.png')

            lat=mcentre[0]
            lon=mcentre[1]


            if OUTPUTSOLARMAP:
                nreldatafile='nreldatafile_' + str(int(round(lat))) + '.npy'
                my_file = Path(nreldatafile)
                if my_file.exists():
                    nreldata=numpy.load(nreldatafile)
                else:
                    #NREL lookup data
                    nreldata=numpy.zeros((NUM_LABELS_AZ, NUM_LABELS_ALT),dtype=numpy.float32)
                    for r in xrange(0, NUM_LABELS_AZ):
                        for c in xrange(0, NUM_LABELS_ALT):
                            if c==0: #flat roof, orientation doesn't matter
                                nrelcall='https://developer.nrel.gov/api/pvwatts/v5.json?api_key=BXIEisO2pSE6bQPuuxys1fjiiHAM7UfcdAZPiPXH&system_capacity=4&dataset=intl&&lat=' + str(lat) + '&lon=' + str(lon) + '&module_type=0&losses=14&array_type=1&tilt=0&azimuth=180&dc_ac_ratio=1.1&gcr=0.4&inv_eff=96&radius=500'
                            elif c==NUM_LABELS_ALT-1:
                                nrelcall='https://developer.nrel.gov/api/pvwatts/v5.json?api_key=BXIEisO2pSE6bQPuuxys1fjiiHAM7UfcdAZPiPXH&system_capacity=4&dataset=intl&&lat=' + str(lat) + '&lon=' + str(lon) + '&module_type=0&losses=14&array_type=1&tilt=90&azimuth='+ str((90+r*10)%360) + '&dc_ac_ratio=1.1&gcr=0.4&inv_eff=96&radius=500'
                            else:
                                nrelcall='https://developer.nrel.gov/api/pvwatts/v5.json?api_key=BXIEisO2pSE6bQPuuxys1fjiiHAM7UfcdAZPiPXH&system_capacity=4&dataset=intl&&lat=' + str(lat) + '&lon=' + str(lon) + '&module_type=0&losses=14&array_type=1&tilt='+ str(c*10) +'&azimuth=' + str((90+r*10)%360) + '&dc_ac_ratio=1.1&gcr=0.4&inv_eff=96&radius=500'
                            print(nrelcall)
                            with urllib.request.urlopen(nrelcall) as url:
                                str_response = url.read().decode('utf-8')
                                tmp = json.loads(str_response)
                                nreldata[r,c]=tmp['outputs']['ac_annual']
                                print(nreldata[r,c])
                                time.sleep(2) # sleep for a bit to avoid API issues
                    numpy.save(nreldatafile, nreldata)


                solaroutput=rgb
                mns=nreldata.min()
                mxs=nreldata.max()
                ct=0;
                for r in xrange(0, sz[0]-IMAGE_SIZE):
                    for c in xrange(0, sz[1]-IMAGE_SIZE):
                        if mask[r+imszdiv2,c+imszdiv2]>0:
                            v=(nreldata[test_labels_az[ct], test_labels_alt[ct]]-mns)/(mxs-mns)
                            rv=255.0*v #min(255.0,3*255*v)
                            gv=255.0*v  #max(0, min(255.0,3*255*(v-0.33)))
                            bv=255.0*v #max(0, min(255.0,3*255*(v-0.67)))
                            solaroutput[r+imszdiv2,c+imszdiv2,0]=numpy.uint8(rv)
                            solaroutput[r+imszdiv2,c+imszdiv2,1]=numpy.uint8(gv)
                            solaroutput[r+imszdiv2,c+imszdiv2,2]=numpy.uint8(bv)
                            ct+=1

                im = Image.fromarray(solaroutput)
                im.save(imgfname+'SolarOutput_' + id + '_region' + str(i) + '.png')

        #Let's try to use some tricks to improve the consistency of the labels
        ct=0
        ALTlabs=numpy.zeros(mask.shape)
        AZlabs=numpy.zeros(mask.shape)
        for r in xrange(0, sz[0]-IMAGE_SIZE):
            for c in xrange(0, sz[1]-IMAGE_SIZE):
                if mask[r+imszdiv2,c+imszdiv2]>0:
                    AZlabs[r+imszdiv2,c+imszdiv2] =test_labels_az[ct]
                    ALTlabs[r+imszdiv2,c+imszdiv2] =test_labels_alt[ct]
                    ct+=1

        ##    AZlabs=scipy.signal.medfilt(AZlabs,3)
        ##    ALTlabs=scipy.signal.medfilt(ALTlabs,3)

        #Exclude regions facing away from sun and calculate an overall roof orientation for what's left
        ct=0
        hemi=0
        if lat>=-23 and lat<=23: #the tropics
            hemi=1
        elif lat<0:
            hemi=2

        azs=[]
        alts=[]
        suitableroof=rgb
        newmask=numpy.zeros(mask.shape)
        mnrow=1e10
        mxrow=-1
        mncol=1e10
        mxcol=-1
        for r in xrange(0, sz[0]-IMAGE_SIZE):
            for c in xrange(0, sz[1]-IMAGE_SIZE):
                if mask[r+imszdiv2,c+imszdiv2]>0:
                    if r+imszdiv2<mnrow:
                        mnrow=r+imszdiv2
                    if r+imszdiv2>mxrow:
                        mxrow=r+imszdiv2
                    if c+imszdiv2<mncol:
                        mncol=c+imszdiv2
                    if c+imszdiv2>mxcol:
                        mxcol=c+imszdiv2
                    if hemi==1:
                        #tropics, so include all azimuths
                        newmask[r+imszdiv2,c+imszdiv2]=1
                    elif hemi==0:
                        #northern hemi, so ignore north facing
                        if ALTlabs[r+imszdiv2,c+imszdiv2]<1 or (AZlabs[r+imszdiv2,c+imszdiv2]>=3 and AZlabs[r+imszdiv2,c+imszdiv2]<=15): #class 0 is east, class 8 is south, class 17 is west.  May want to reduce this range a bit
                            newmask[r+imszdiv2,c+imszdiv2]=1
                    else:
                        #southern hemi so ignore south facing
                        if ALTlabs[r+imszdiv2,c+imszdiv2]<1 or (AZlabs[r+imszdiv2,c+imszdiv2]>=20 and AZlabs[r+imszdiv2,c+imszdiv2]<=32): #class 0 is east, class 8 is south, class 17 is west.  May want to reduce this range a bit
                            newmask[r+imszdiv2,c+imszdiv2]=1
                    ct+=1

        mncol=max(0, mncol-50)
        mxcol=min(sz[1]-1, mxcol+50)
        mnrow=max(0, mnrow-50)
        mxrow=min(sz[0]-1, mxrow+50)

        #Use median filter to tidy up the regions
        newmask=scipy.signal.medfilt(newmask,5)

        ct=0
        for r in xrange(0, sz[0]-IMAGE_SIZE):
            for c in xrange(0, sz[1]-IMAGE_SIZE):
                if mask[r+imszdiv2,c+imszdiv2]>0 and newmask[r+imszdiv2,c+imszdiv2]>0: #need to make sure the pixel is inside the original region after medfilt
                    suitableroof[r+imszdiv2,c+imszdiv2,0]=numpy.uint8(0)
                    suitableroof[r+imszdiv2,c+imszdiv2,1]=numpy.uint8(0)
                    suitableroof[r+imszdiv2,c+imszdiv2,2]=numpy.uint8(128)
                    azs.append(AZlabs[r+imszdiv2,c+imszdiv2])
                    alts.append(ALTlabs[r+imszdiv2,c+imszdiv2])
                    ct+=1


        im = Image.fromarray(suitableroof[mnrow:mxrow, mncol:mxcol, :])
        im.save(imgfname+'SolarPanels_' + id + '_region' + str(i) + '.png')

        if len(azs)==0:
            #We need to handle no suitable roof area!
            outhtml += "<tr><td>"
            outhtml += "<p>This area doesn't seem to be suitable for solar panels.  This could be because of their tilt and orientation (e.g. they would be facing in the wrong direction) or because the machine learning has made a mistake</p>"
            outhtml += "<p><img style='width:90%' src='" + settings.MEDIA_URL + "SolarPanels_" + id + "_region" + str(i) + ".png'/></p>"
            outhtml += "</tr></td>"
            SystemAreas.append(0)
            SystemCapacities.append(0)
            PanelNumbers.append(0)
            SystemTilts.append(0)
            SystemOrientations.append(0)
            AnnualGenerationEstimates.append(0)
            MonthlyGenerationEstimates.append([0] * 12)
        else:
            mnALT=float(sum(alts)) / max(len(alts), 1)
            #estimate system size from the area, based on pixels representing approx 1 sqm (TODO: should ideally correct for foreshortening)
            numpanels=math.floor(len(azs)/(1.64*0.99))
            syscap=round(numpanels*0.265) #residential panels 1.64x0.99m, 265W. Commercial 1.96x0.99.  Using RESIDENTIAL here
            print('Estimated tilt: ' + str(round(numpy.mean(alts)*10)) + ' degrees')
            print('Estimated orientation: ' + str(round((90+numpy.mean(azs)*10)%360)) + ' degrees')
            print('Estimated system area: ' + str(len(azs)) + 'sqm')
            print('Approx number of panels: ' + str(numpanels))
            print('System capacity: '+str(syscap)+'kW')
            if round(mnALT)==0: #Assume flat and very low tilt roofs can have panels regardless of azimuth  TO DO: we could, for flat roofs, assume optimal tilt rather than flat
                nrelcall='https://developer.nrel.gov/api/pvwatts/v5.json?api_key=BXIEisO2pSE6bQPuuxys1fjiiHAM7UfcdAZPiPXH&system_capacity=' + str(syscap) + '&dataset=intl&&lat=' + str(lat) + '&lon=' + str(lon) + '&module_type=0&losses=14&array_type=1&tilt='+ str(0) +'&azimuth=180&dc_ac_ratio=1.1&gcr=0.4&inv_eff=96&radius=500'
            else:
                mnAZ=float(sum(azs)) / max(len(azs), 1)
                nrelcall='https://developer.nrel.gov/api/pvwatts/v5.json?api_key=BXIEisO2pSE6bQPuuxys1fjiiHAM7UfcdAZPiPXH&system_capacity=' + str(syscap) + '&dataset=intl&&lat=' + str(lat) + '&lon=' + str(lon) + '&module_type=0&losses=14&array_type=1&tilt='+ str(round(mnALT*10)) +'&azimuth=' + str(round((90+mnAZ*10)%360)) + '&dc_ac_ratio=1.1&gcr=0.4&inv_eff=96&radius=500'

            with urllib.request.urlopen(nrelcall) as url:
                str_response = url.read().decode('utf-8')
                tmp = json.loads(str_response)
                annualgen=tmp['outputs']['ac_annual']
                monthlygen = tmp['outputs']['ac_monthly']

            print('Estimated annual generation: ' + str(round(annualgen/1000,1)) + 'MWh')

            #Store the calculated results
            SystemAreas.append(len(azs))
            SystemCapacities.append(syscap)
            PanelNumbers.append(numpanels)
            SystemTilts.append(round(numpy.mean(alts)*10))
            SystemOrientations.append(round((90+numpy.mean(azs)*10)%360))
            AnnualGenerationEstimates.append(annualgen)
            MonthlyGenerationEstimates.append(monthlygen)

            outhtml += "<tr><td>"
            outhtml += "<p>System area: " + str(len(azs)) + "sqm</p>"
            outhtml += "<p>System capacity: " + str(syscap) + "kW</p>"
            outhtml += "<p>Estimated number of panels: " + str(numpanels) + "</p>"
            outhtml += "<p>Estimated tilt: " + str(round(numpy.mean(alts)*10)) + " degrees</p>"
            outhtml += "<p>Estimated orientation: " + str(round((90+numpy.mean(azs)*10)%360)) + " degrees</p>"
            outhtml += "<p>Estimated annual generation: " + str(round(annualgen/1000,1))  + "MWh</p>"
            outhtml += "<p><img style='width:90%' src='" + settings.MEDIA_URL +  "SolarPanels_" + id + "_region" + str(i) + ".png'/></p>"
            outhtml += "</tr></td>"

    outhtml+="</table>"

    return (outhtml, SystemAreas, SystemCapacities, PanelNumbers, SystemTilts, SystemOrientations, AnnualGenerationEstimates, MonthlyGenerationEstimates)



class Assessment(AbstractTimestampModel):
    TYPE_UNCATEGORIZED = 0
    TYPE_PRIVATE = 1
    TYPE_COMMERCIAL = 2
    TYPE_OPEN_SPACE = 3
    TYPE_CHOICES = (
        (TYPE_UNCATEGORIZED, '---'),
        (TYPE_PRIVATE, 'private home'),
        (TYPE_COMMERCIAL, 'commercial building'),
        (TYPE_OPEN_SPACE, 'open space'),
    )


    uuid = models.UUIDField(unique=True, blank=True, null=True, editable=False, default=uuid.uuid4)

    test = models.BooleanField(default=False, help_text=_('Use this flag to mark test assessments.'))
    supervised = models.BooleanField(default=False, help_text=_('Use this flag to mark supervised assessments.'))
    useless = models.BooleanField(default=False, help_text=_('Use this flag to mark useless assessments.'))
    duplicate = models.BooleanField(default=False, help_text=_('Use this flag to mark duplicate assessments.'))

    type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    contact = models.ForeignKey(Contact, null=True, blank=True, related_name='assessments', on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, null=True, blank=True, related_name='assessments')

    mpoly = models.MultiPolygonField(null=True, blank=True)

    num_points = models.IntegerField(null=True, blank=True)

    location = models.ForeignKey(Location, related_name='assessments', null=True, blank=True)

    selected_area = models.FloatField(_('selected area [sqm]'), null=True, blank=True)
    system_capacity_estimate = models.FloatField(_('system nameplate capacity estimate [kW]'), null=True, blank=True)
    monthly_energy_estimates = ArrayField(models.FloatField(), size=12, null=True, blank=True)
    monthly_savings_estimates = ArrayField(models.FloatField(), size=12, null=True, blank=True)
    monthly_earnings_estimates = ArrayField(models.FloatField(), size=12, null=True, blank=True)
    monthly_lifetime_savings_estimates = ArrayField(models.FloatField(), size=35*12, null=True, blank=True)
    monthly_lifetime_earnings_estimates = ArrayField(models.FloatField(), size=35*12, null=True, blank=True)
    annual_energy_estimate = models.FloatField(_('energy estimate [kWh/year]'), null=True, blank=True)
    annual_savings_estimate = models.FloatField(_('savings estimate [£]'), null=True, blank=True)
    annual_earnings_estimate = models.FloatField(_('earnings estimate [£]'), null=True, blank=True)

    nrel_version = models.CharField(_('version'), max_length=10, null=True, blank=True)
    nrel_station_distance = models.FloatField(_('station distance [km]'), null=True, blank=True)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0][0])

    email_sent = models.BooleanField(default=False)

    title = models.CharField(_('title'), max_length=255, null=True, blank=True)
    notes = models.TextField(_('notes'), null=True, blank=True)

    mlreport = models.TextField(_('mlreport'), null=True, blank=True)

    _short_link=""
    _in_ml_assessment=False

    @property
    def apply_ml(self):
        #This is a noddy way to work out if we are loading an existing ML-based assessment or starting a new one:
        imgfname = settings.MEDIA_ROOT + '/'  # base for output filenames
        testfname=imgfname + 'SolarPanels_' + str(self.uuid) + '_region0.png'
        existing_ml=False
        if os.path.isfile(testfname):
            existing_ml=True

        if not existing_ml:
            #we need to create a new assessment to avoid overwriting the standard assessment
            newassessment=Assessment(
                mpoly=self.mpoly,
                num_points=self.num_points,
                location=self.location,
                selected_area=self.selected_area,
                system_capacity_estimate=self.system_capacity_estimate,
                monthly_energy_estimates=self.monthly_energy_estimates,
                monthly_savings_estimates=self.monthly_savings_estimates,
                monthly_earnings_estimates=self.monthly_earnings_estimates,
                annual_energy_estimate=self.annual_energy_estimate,
                annual_savings_estimate=self.annual_savings_estimate,
                annual_earnings_estimate=self.annual_earnings_estimate,
                nrel_version=self.nrel_version,
                nrel_station_distance=self.nrel_station_distance,
                currency=self.currency,
            )
            newassessment.contact=self.contact
            newassessment.project=self.project

            self.__dict__.update(newassessment.__dict__)

        res = applyML(self.mpoly, str(self.uuid))
        self.mlreport = res[0]
        self.selected_area = sum(res[1])
        self.system_capacity_estimate = sum(res[2])
        self.monthly_energy_estimates = [sum(i) for i in zip(*res[7])]
        self.monthly_savings_estimates, self.monthly_earnings_estimates = calc_monthly_profit(
        self.monthly_energy_estimates, country=self.country, state=self.state)
        self.annual_energy_estimate = sum(res[6])
        self.annual_savings_estimate = sum(self.monthly_savings_estimates)
        self.annual_earnings_estimate = sum(self.monthly_earnings_estimates)
        self.save()  # save the updated assessment

        if not existing_ml:
            #Send a revised email report
            self._in_ml_assessment=True;
            self.short_link = '/solar/assessmentml/' + str(self.uuid) + '/'

            email = send_templated_email(
                subject='Your PowerMarket Solar Report - Advanced Artificial Intelligence Version',
                recipient_list=(self.contact.email),
                text_template='email/text/solar_potential_assessment.txt',
                html_template='email/html/solar_potential_assessment.html',
                context={
                    'name': self.contact.name,
                    'assessment': self,
                },
                fail_silently=True,
            )

        return "" #return empty string so we don't display anything in html

    @property
    def display_ml(self):
        return self.mlreport

    def __str__(self):
        return "%s" % self.uuid

    @property
    def num_panels(self):
        return math.floor(self.system_capacity_estimate/0.265)

    @property
    def unit_energy_price(self):
        if self.location.country:
            if self.location.administrative_area_level_1:
                return get_energy_price(1,self.location.country.name, self.location.administrative_area_level_1)
            else:
                return get_energy_price(1, self.location.country.name)
        else:
            return get_energy_price(1)

    @property
    def short_link(self):
        if not self._in_ml_assessment: #Need to be able to set the short link if in ML assessment (probably a better way to do this!)
            self._short_link=reverse('report_link', kwargs={'uuid': self.uuid})
        return self._short_link

    @short_link.setter #Need to be able to set the short link if in ML assessment (probably a better way to do this!)
    def short_link(self, value):
        self._short_link = value

    @property
    def full_short_link(self):
        site = Site.objects.first()
        if site:
            return "https://" + site.domain + self.short_link

    @property
    def is_example(self):
        return self.example is not None

    @property
    def country(self):
        try:
            return self.location.country.name
        except:
            pass

    @property
    def state(self):
        location = self.location
        if location:
            return location.administrative_area_level_1

    @property
    def postal_code(self):
        location = self.location
        if location:
            return self.location.postal_code

    # @property
    # def annual_energy_estimate_lower(self):
    #     if self.annual_energy_estimate:
    #         return self.annual_energy_estimate * .9
    #
    # @property
    # def annual_energy_estimate_higher(self):
    #     if self.annual_energy_estimate:
    #         return self.annual_energy_estimate * 1.1

    @property
    def system_cost_estimate(self):
        if self.system_capacity_estimate:
            return get_system_cost(self.system_capacity_estimate, country=self.country, state=self.state)

    # @property
    # def system_cost_estimate_lower(self):
    #     nominal = self.system_cost_estimate
    #     if nominal:
    #         return nominal * .9

    # @property
    # def system_cost_estimate_higher(self):
    #     nominal = self.system_cost_estimate
    #     if nominal:
    #         return nominal * 1.1

    @property
    def break_even_duration_estimate(self):
        if self.system_cost_estimate and self.annual_profit_estimate:
            return self.system_cost_estimate / self.annual_profit_estimate

    @property
    def annual_profit_estimate(self):
        if self.annual_savings_estimate or self.annual_earnings_estimate:
            annual_savings_estimate = self.annual_savings_estimate or 0
            annual_earnings_estimate = self.annual_earnings_estimate or 0
            return annual_savings_estimate + annual_earnings_estimate
        return 0

    @property
    def lifetime_gross_profit_estimate(self):
        return self.annual_profit_estimate * 25  # estimated for 25 years.

    # @property
    # def lifetime_gross_profit_estimate_lower(self):
    #     return self.lifetime_gross_profit_estimate * .9

    # @property
    # def lifetime_gross_profit_estimate_higher(self):
    #     return self.lifetime_gross_profit_estimate * 1.1

    @property
    def monthly_lifetime_savings_estimates(self):
        monthly_lifetime_savings_estimates = []
        if self.monthly_savings_estimates:
            # Loop through 35 years to generate monthly data
            monthly_lifetime_savings_estimates.append(self.monthly_savings_estimates[0])
            ct=1
            for i in range(0,35):
                for j in range(0,12):
                    monthly_lifetime_savings_estimates.append(monthly_lifetime_savings_estimates[ct-1]+self.monthly_savings_estimates[j])
                    ct+=1
        return monthly_lifetime_savings_estimates

    @property
    def monthly_lifetime_earnings_estimates(self):
        monthly_lifetime_earnings_estimates = []
        if self.monthly_earnings_estimates:
            monthly_lifetime_earnings_estimates.append(self.monthly_earnings_estimates[0])
            ct=1
            for i in range(0,35):
                for j in range(0,12):
                    monthly_lifetime_earnings_estimates.append(monthly_lifetime_earnings_estimates[ct-1]+self.monthly_earnings_estimates[j])
                    ct+=1
        return monthly_lifetime_earnings_estimates


    @property
    def lifetime_return_estimate(self):
        if self.system_cost_estimate:
            return self.lifetime_gross_profit_estimate - self.system_cost_estimate

    @property
    def formatted_monthly_savings(self):
        return [round(val, 0) for val in self.monthly_savings_estimates]

    @property
    def formatted_monthly_earnings(self):
        return [round(val, 0) for val in self.monthly_earnings_estimates]

    @property
    def monthly_profit(self):
        return list(map(
            add,
            self.formatted_monthly_earnings,
            self.formatted_monthly_savings,
        ))

    @property
    def max_monthly_profit(self):
        monthly_profit = self.monthly_profit
        return max(monthly_profit)

    @property
    def cum_savings(self):
        return cum_timeseries(self.monthly_savings_estimates)

    @property
    def cum_earnings(self):
        return cum_timeseries(self.monthly_earnings_estimates)

    @property
    def cum_profit(self):
        return cum_timeseries(
            self.monthly_savings_estimates +
            self.monthly_earnings_estimates
        )
    @property
    def cum_lifetime_profit(self):
        return cum_lifetime_timeseries(
            [a + b for a, b in zip(self.monthly_lifetime_savings_estimates, self.monthly_lifetime_earnings_estimates)]
        )

    @property
    def lat(self):
        return self.location.lat

    @property
    def lng(self):
        return self.location.lng

    @property
    def coordinates_str(self):
        return "{0}, {1}".format(self.lat, self.lng)

    @property
    def environmental_benefits(self):
        return environmental_benefits_serialized(self.annual_energy_estimate)

    @property
    def sharing_url_twitter(self):
        tweet = (
            "My PowerMarket report - "
            "savings - {currency} {total_savings:,.0f}, "
            "electricity - {electricity_generated:,.0f}kWh and "
            "CO2 - {co2_saved:,.0f}t, "
            "check out yours at: https://www.powermarket.net".format(
                currency=self.get_currency_display(),
                total_savings=self.lifetime_gross_profit_estimate,
                electricity_generated=self.annual_energy_estimate,
                co2_saved=self.environmental_benefits['tons_of_carbon_eliminated_annually'],
            )
        )
        url = "https://twitter.com/intent/tweet?text={}".format(tweet)
        return mark_safe(url)

    @property
    def sharing_url_linkedin(self):
        title = "My PowerMarket report".replace(" ", "%20")
        summary = (
            "savings - {currency} {total_savings:,.0f}, "
            "electricity - {electricity_generated:,.0f}kWh and "
            "CO2 - {co2_saved:,.0f}t, "
            "check out yours at: https://www.powermarket.net"
            .format(
                currency=self.get_currency_display(),
                total_savings=self.lifetime_gross_profit_estimate,
                electricity_generated=self.annual_energy_estimate,
                co2_saved=self.environmental_benefits['tons_of_carbon_eliminated_annually'],
            )
            .replace(" ", "%20")
        )
        url = (
            "https://www.linkedin.com/shareArticle"
            "?mini=true&url=https%3A//www.powermarket.net"
            "&title={title}&summary={summary}".format(
                title=title,
                summary=summary,
            )
        )
        return mark_safe(url)


class ExampleAssessment(models.Model):
    assessment = models.OneToOneField(Assessment, related_name='example')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    address = models.CharField(max_length=255, null=True, blank=True)
    info = models.TextField(null=True, blank=True, help_text=_('displayed on the assessment page.'))
    published = models.BooleanField(default=True, help_text=_('set to False to hide this example.'))
    image = ThumbnailerImageField(
        upload_to='uploads/examples/images/',
        help_text=_('Automatically cropped to the right dimensions.'),
        null=True, blank=True,
    )

    def __str__(self):
        return "{}".format(self.name or self.assessment.uuid)

