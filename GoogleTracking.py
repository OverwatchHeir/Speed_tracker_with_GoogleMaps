
import os
import traceback
import urllib.request
import pyproj
import math
import serial

MAX_DISTANCE = 3
PROJ_SCALE_FACTOR = 0.9997
EARTH_RADIUS = 6371000

pathGoogle = "/Users/carlosdeantonio/Documents/UNIVERSIDAD/GPS/Practica 4/Python/mymap.png"


class GoogleTracking(object):

    def __init__(self, inicialLatitude=None, initialLongitude=None, actualLatitude=None, actuaLongitude=None,
                 speedPosition=None, lastTime=None, actualTime=None, speedMatrix=None, altitude =None,geoidialSeparation=None):

        self.INICIAL_LATITUDE = inicialLatitude
        self.INICIAL_LONGITUDE = initialLongitude

        self.ACTUAL_LATITUDE = actualLatitude
        self.ACTUAL_LONGITUDE = actuaLongitude

        self.ALTITUDE = altitude
        self.GEO_SEPARATION = geoidialSeparation

        self.SPEED_POSITION = speedPosition

        self.LAST_TIME = lastTime
        self.ACTUAL_TIME = actualTime

        self.speedMatrix = speedMatrix

    def read_insia_speed_limits(self):
        # FORMAT TXT  :  LONGITUDE LATITUDE SPEED

        filePath = "/Users/carlosdeantonio/Documents/UNIVERSIDAD/GPS/Practica 4/Python/coordenadasInsia.txt"

        with open(filePath, 'r') as reader:
            for line in reader:
                self.speedMatrix.append(line.strip().split())
            reader.close()


    def get_static_google_map(self, center=None, zoom=None, imgsize="640x640", imgformat="png", maptype="terrain"):

        request = "http://maps.google.com/maps/api/staticmap?"

        if center != None:
            request += "center=%s&" % center

        if center != None:
            request += "zoom=%i&" % zoom

        request += "size=%ix%i&" % (imgsize)
        request += "format=%s&" % imgformat
        request += "maptype=%s&" % maptype
        request += "markers=size:mid|label:B|color:red|%s&" % center
        request += "key=AIzaSyB6StLPJCUj56pI3PL18rMQELlg2Rp0sA0"

        fullfilename = os.path.join("/Users/carlosdeantonio/Documents/UNIVERSIDAD/GPS/Practica 4/Python/", "mymap." + imgformat)
        urllib.request.urlretrieve(request, fullfilename)


    # CALCULATES DISTANCE BETWEEN 2 COORDINATES
    def distance_coordinates(self, actualLongitude, actualLatitude, lastLongitude, lastLatitude,altitude,geodialSeparation):

        mapDistance = math.sqrt(((actualLongitude - lastLongitude) ** 2) + ((actualLatitude - lastLatitude) ** 2))

        elevScale = ((altitude + geodialSeparation) + EARTH_RADIUS) / EARTH_RADIUS
        combScaleFactor = elevScale * PROJ_SCALE_FACTOR

        groundDistance = mapDistance/combScaleFactor

        if( mapDistance == 0):
          percentage = 0.0
        else:
          percentage= (1-(mapDistance/groundDistance))*100

        print("\nDistancia sobre mapa : " + str(mapDistance) + " m")
        print("Distancia sobre terreno : "+str(groundDistance)+ " m")
        print( "Mejora Precision:" + str( round(percentage,3)) + " %" )

        return groundDistance


    def speed_calculation(self):  # SPEED VALUES BETWEEN 0-3

        if self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE, float(self.speedMatrix[self.SPEED_POSITION][0]),
                                float(self.speedMatrix[self.SPEED_POSITION][1]),self.ALTITUDE,self.GEO_SEPARATION) < MAX_DISTANCE:

            speedValue,speed = self.check_near()
        else:
            speedValue, speed = self.check_all()

        return speedValue,speed

    def check_near(self):

        if self.SPEED_POSITION == (len(self.speedMatrix) - 1):

            last = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                        self.speedMatrix[len(self.speedMatrix) - 1][0],
                                        self.speedMatrix[len(self.speedMatrix) - 1][1],self.ALTITUDE,self.GEO_SEPARATION)
            actual = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                          self.speedMatrix[self.SPEED_POSITION][0],
                                          self.speedMatrix[self.SPEED_POSITION][1],self.ALTITUDE,self.GEO_SEPARATION)
            next = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE, self.speedMatrix[0][0],
                                        self.speedMatrix[0][1],self.ALTITUDE,self.GEO_SEPARATION)

        else:

            last = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                        self.speedMatrix[len(self.speedMatrix) - 1][0],
                                        self.speedMatrix[len(self.speedMatrix) - 1][1],self.ALTITUDE,self.GEO_SEPARATION)
            actual = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                          self.speedMatrix[self.SPEED_POSITION][0],
                                          self.speedMatrix[self.SPEED_POSITION][1],self.ALTITUDE,self.GEO_SEPARATION)
            next = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                        self.speedMatrix[self.SPEED_POSITION + 1][0],
                                        self.speedMatrix[self.SPEED_POSITION + 1][1],self.ALTITUDE,self.GEO_SEPARATION)

        if last < actual and last < next:
            if self.SPEED_POSITION == 0:
                self.SPEED_POSITION = (len(self.speedMatrix) - 1)
            else:
                self.SPEED_POSITION -= 1
        elif next < last and next < actual:
            if self.SPEED_POSITION == (len(self.speedMatrix) - 1):
                self.SPEED_POSITION = 0
            else:
                self.SPEED_POSITION += 1

        distance = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE, self.INICIAL_LONGITUDE,
                                             self.INICIAL_LATITUDE, self.ALTITUDE, self.GEO_SEPARATION)

        if (self.ACTUAL_TIME - self.LAST_TIME)==0:
            speed= 0.0
        else:
            speed = float((distance / (self.ACTUAL_TIME - self.LAST_TIME)) * 3.6)

        print("Tiempo Actual : " + str(self.ACTUAL_TIME) + " - " + " Tiempo Anterior : " + str(self.LAST_TIME))

        if speed == 0:
            return 0,speed
        elif speed < (self.speedMatrix[self.SPEED_POSITION][2] - (self.speedMatrix[self.SPEED_POSITION][2] * 0.1)):
            return 1,speed
        elif (self.speedMatrix[self.SPEED_POSITION][2] - (self.speedMatrix[self.SPEED_POSITION][2] * 0.1)) < speed < (
                self.speedMatrix[self.SPEED_POSITION][2] + (self.speedMatrix[self.SPEED_POSITION][2] * 0.1)):
            return 2,speed
        elif speed > (self.speedMatrix[self.SPEED_POSITION][2] + (self.speedMatrix[self.SPEED_POSITION][2] * 0.1)):
            return 3,speed
        else:
            return 0,speed

    def check_all(self):

        distanceAll = []

        for i in range(len(self.speedMatrix)):
            distanceAll.append(self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE,
                                                         float(self.speedMatrix[i][0]), float(self.speedMatrix[i][1]),
                                                         self.ALTITUDE, self.GEO_SEPARATION))

        lowest = distanceAll[0]
        lowestPosition = 0

        for i in range(len(distanceAll)):
            if lowest > distanceAll[i]:
                lowest = distanceAll[i]
                lowestPosition = i

        distance = self.distance_coordinates(self.ACTUAL_LONGITUDE, self.ACTUAL_LATITUDE, self.INICIAL_LONGITUDE,
                                             self.INICIAL_LATITUDE, self.ALTITUDE, self.GEO_SEPARATION)

        if (self.ACTUAL_TIME - self.LAST_TIME)==0:
            speed= 0.0
        else:
            speed = float((distance / (self.ACTUAL_TIME - self.LAST_TIME)) * 3.6)

        print("Tiempo Actual : " +str(self.ACTUAL_TIME) + " - " + " Tiempo Anterior : " + str(self.LAST_TIME))

        if speed == 0:
            return 0,speed
        elif speed < (float(self.speedMatrix[lowestPosition][2]) - (float(self.speedMatrix[lowestPosition][2]) * 0.1)):
            return 1,speed
        elif (float(self.speedMatrix[lowestPosition][2]) - (float(self.speedMatrix[lowestPosition][2]) * 0.1)) < speed < (
                float(self.speedMatrix[lowestPosition][2]) + (float(self.speedMatrix[lowestPosition][2]) * 0.1)):
            return 2,speed
        elif speed > (float(self.speedMatrix[lowestPosition][2]) + (float(self.speedMatrix[lowestPosition][2]) * 0.1)):
            return 3,speed
        else:
            return 0,speed

    def read_data(self,q):

        serialPort = serial.Serial(port='/dev/tty.usbserial', baudrate=4800, parity=serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

        try:
            self.read_insia_speed_limits()

            print("Abriendo puerto ..")
            serialPort.isOpen()
            print("Puerto abierto ..\n")

            while True:
                print("leyendo..")

                lineGPS = serialPort.readline()
                data = lineGPS.decode().split(',')  # Split each GGA data

                if data[0] == "$GPGGA":
                    print("Formato GCA")
                    print(lineGPS)
                    print("transformando..\n")

                    gcaLatitude = data[2]
                    gcaLongitude = data[4]

                    if self.LAST_TIME == 0.0:
                        self.LAST_TIME = float(data[1])
                    else:
                        self.LAST_TIME = self.ACTUAL_TIME

                    self.ACTUAL_TIME = float(data[1])

                    degreeLatitude = float(gcaLatitude[0:2]) + (float(gcaLatitude[2:9]) / 60)  # GGA to Degrees
                    degreeLongitude = float(gcaLongitude[0:3]) + (float(gcaLongitude[3:9]) / 60)

                    self.ALTITUDE = float(data[9])
                    self.GEO_SEPARATION = float(data[11])

                    # North or South
                    if data[3] == "S":
                        degreeLatitude *= -1.0

                    # East or West
                    if data[5] == "W":
                        degreeLongitude *= -1.0

                    # Transforming degrees into UTM
                    p1 = pyproj.Proj(init="epsg:4326")
                    p2 = pyproj.Proj(init="epsg:32630")
                    utmLongitude, utmLatitude = pyproj.transform(p1, p2, degreeLongitude, degreeLatitude)

                    stringCenter = str(degreeLatitude)+","+str(degreeLongitude)

                    #GETTING IMAGE FROM GOOGLE MAPS API
                    self.get_static_google_map(center=stringCenter, zoom=18, imgsize=(640, 640),
                          imgformat="png", maptype="hybrid")

                    print("Imagen obtenida")

                    # DECIMAL format
                    print("\nFormato Decimal")
                    print("  Latitud Decimal : " + str(degreeLatitude))
                    print("  Longitud Decimal : " + str(degreeLongitude))

                    # UTM format
                    print("\nFormato UTM")
                    print("  Latitud UTM : " + str(utmLatitude))
                    print("  Longitud UTM : " + str(utmLongitude))

                    print("\nAltitud : " + str(self.ALTITUDE) + " m")
                    print("\nSeparacion Geoidial : " + str(self.GEO_SEPARATION) + " m")

                    self.INICIAL_LATITUDE = self.ACTUAL_LATITUDE
                    self.INICIAL_LONGITUDE = self.ACTUAL_LONGITUDE

                    self.ACTUAL_LATITUDE = utmLatitude
                    self.ACTUAL_LONGITUDE = utmLongitude

                    colorValue, speed = self.speed_calculation()

                    q.put(colorValue) #SETTING THE PANEL COLOUR IN THE QUEUE
                    q.put(speed) #SETTING THE SPEED IN THE QUEUE


        except Exception as e:
            serialPort.close()
            print("\nPuerto cerrado")
            traceback.print_exc()
            exit()