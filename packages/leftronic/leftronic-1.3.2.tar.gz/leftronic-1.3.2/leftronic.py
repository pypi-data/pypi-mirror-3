import urllib2
import json


class Leftronic(object):

    """ Provides access to Leftronic Custom Data API """

    def __init__(self, authKey):
        # Sets accessKey
        self.accessKey = authKey
        self.apiUrl = 'https://www.leftronic.com/customSend/'

    def pushMultiple(self, points):
        """
        Pushes points to multiple streams.  Points is a list of dicts
        as returned by the `populate` methods provided below.

        e.g., pushMultiple([populateNumber("MyNumber", 42),
                            populateGeo("MyMap", 34, -118)])
        """
        if type(points) != list:
            raise TypeError
        else:
            return self.postData({"streams": points})

    def pushNumber(self, streamName, point):
        """
        Pushes a number (or list of numbers) to a Number, Horizontal/Vertical
        Bar, Dial widget, Stoplight or sparkline/line graph
        """
        return self.postData(self.populateNumber(streamName, point))

    def populateNumber(self, streamName, point):
        """
        Formats the provided number, list of numbers, or dict of
        numbers as a Python dict, e.g., to be pushed along with other
        streams.
        """
        if type(point) == float or type(point) == long or type(point) == int:
            point = {'number': point}
        elif type(point) == list:
            last = 0
            for i in point:
                if int(i['timestamp']) > last:
                    last = int(i['timestamp'])
                else:
                    # Timestamp values must increase
                    raise ValueError
        elif type(point) == dict:
            pass
        else:
            raise TypeError
        return {'streamName': streamName, 'point': point}

    def pushGeo(self, streamName, lati, longi, color=None):
        """
        Pushes a geographic location (latitude and longitude) to a Map
        widget.  Color can also be passed (red, green, blue, yellow,
        or purple).

        Default color is red.
        """
        return self.postData(self.populateGeo(streamName, lati, longi, color))

    def populateGeo(self, streamName, lati, longi, color=None):
        """
        Formats a geographic location (latitude and longitude) as a
        dict, e.g., to be supplied to 'pushMultiple()` Color can also
        be passed (red, green, blue, yellow, or purple).

        Default color is red.
        """
        if type(lati) != list and type(longi) != list and type(color) != list:
            point = {'latitude': lati, 'longitude': longi}
            if color:
                point['color'] = color

        elif type(lati) == list and type(longi) == list:
            if len(lati) != len(longi):
                raise ValueError
            point = []
            for i in range(len(lati)):
                obj = {'latitude': lati[i], 'longitude': longi[i]}
                if color and type(color) == list and color[i]:
                    obj['color'] = color[i]
                point.append(obj)
        else:
            raise TypeError
        return {'streamName': streamName, 'point': point}

    def pushText(self, streamName, myTitle, myMsg, imgUrl=None):
        """
        Pushes a title and message to a Text Feed widget.
        """
        return self.postData(self.populateText(streamName, myTitle,
                                               myMsg, imgUrl))

    def populateText(self, streamName, myTitle, myMsg, imgUrl=None):
        """
        Formats a title and message for a Text Feed widget as a dict,
        which can be passed to `pushMultiple()`
        """
        if (type(myTitle) != list and
            type(myMsg) != list and
            type(imgUrl) != list):
            point = {'title': myTitle, 'msg': myMsg}
            if imgUrl:
                point['imgUrl'] = imgUrl
        elif type(myTitle) == list and type(myMsg) == list:
            if len(myTitle) != len(myMsg):
                raise ValueError
            point = []
            for i in range(len(myTitle)):
                obj = {'title': myTitle[i], 'msg': myMsg[i]}
                if imgUrl and type(imgUrl) == list and imgUrl[i]:
                    obj['imgUrl'] = imgUrl[i]
                point.append(obj)
        else:
            raise TypeError

        return {'streamName': streamName, 'point': point}

    def pushLeaderboard(self, streamName, leaderArray):
        """ Pushes an array to a Leaderboard widget. """
        return self.postData(self.populateLeaderboard(streamName, leaderArray))

    def populateLeaderboard(self, streamName, leaderArray):
        """
        Formats a leaderboard array as a dict for, e.g., passing to
        `pushMultiple()`
        """
        return {'streamName': streamName,
                'point': {
                    'leaderboard': leaderArray
                    }}

    def pushList(self, streamName, listArray):
        """ Pushes an array to a List widget. """
        return self.postData(self.populateList(streamName, listArray))

    def populateList(self, streamName, listArray):
        """
        Formats a list as a dict to be pushed using, e.g., `pushMultiple()`.
        """
        if type(listArray) != list:
            raise TypeError
        for i in range(len(listArray)):
            if type(listArray[i]) != dict:
                listArray[i] = {'listItem': listArray[i]}

        return {'streamName': streamName,
                'point': {
                    'list': listArray
                    }}

    def pushPair(self, streamName, x, y):
        """ Pushes an x,y pair to a Pair widget"""
        return self.postData(self.populatePair(streamName, x, y))

    def populatePair(self, streamName, x, y):
        """
        Formats an x, y pair (or lists of x, y pairs) as
        """
        if type(x) == list and type(y) == list:
            point = []
            if len(x) != len(y): raise ValueError
            for i in range(len(x)):
                point.append({'x': x[i], 'y': y[i]})
        else:
            point = {'x': x, 'y': y}
        return {'streamName': streamName,
                'point': point}

    def pushImage(self, streamName, imgUrl):
        """ Pushes an image to an Image widget"""
        return self.postData(self.populateImage(streamName, imgUrl))

    def populateImage(self, streamName, imgUrl):
        """
        Formats a provided image url as a dict to be pushed using, e.g.,
        `pushMultiple()`
        """
        point = {'imgUrl': imgUrl}
        return {'streamName': streamName,
                'point': point}

    def pushLabel(self, streamName, label):
        """ Pushes a label to a Label widget"""
        return self.postData(self.populateLabel(streamName, label))

    def populateLabel(self, streamName, label):
        """
        Formats a label as a dict
        """
        point = {'label': label}
        return {'streamName': streamName,
                'point': point}

    def pushTable(self, streamName, headerRow, dataRows):
        """ Pushes a table to a Table widget """
        return self.postData(self.populateTable(streamName,
                                                headerRow,
                                                dataRows))

    def populateTable(self, streamName, headerRow, dataRows):
        dataRows.insert(0, headerRow)
        point = {'table': dataRows}
        return {'streamName': streamName,
                'point': point}

    def clear(self, streamName):
        parameters = {'streamName': streamName,
                      'command': 'clear'}
        return self.postData(parameters)

    def postData(self, parameters):
        """ Makes an HTTP POST to the API URL. """
        # add the access key
        parameters['accessKey'] = self.accessKey

        # Convert to JSON
        jsonData = json.dumps(parameters)

        # Make request
        response = urllib2.urlopen(self.apiUrl, jsonData)
        return response.read()
