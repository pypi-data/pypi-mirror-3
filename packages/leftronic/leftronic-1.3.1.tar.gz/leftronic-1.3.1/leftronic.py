import urllib2
import json

class Leftronic(object):

    """ Provides access to Leftronic Custom Data API """

    def __init__(self, authKey):
        # Sets accessKey
        self.accessKey = authKey
        self.apiUrl = 'https://beta.leftronic.com/customSend/'

    def pushNumber(self, streamName, point):
        """ 
        Pushes a number to a Number, Horizontal/Vertical Bar, Dial widget, Stoplight.
        or sparkline/line graph
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
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 'point': point}
        return self.postData(parameters)

    def pushGeo(self, streamName, lati, longi, color=None):
        """
        Pushes a geographic location (latitude and longitude) to a Map widget.
        Color can also be passed (red, green, blue, yellow, or purple).
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
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'point': point}
        return self.postData(parameters)

    def pushText(self, streamName, myTitle, myMsg, imgUrl=None):
        """ Pushes a title and message to a Text Feed widget. """
        if type(myTitle) != list and type(myMsg) != list and type(imgUrl) != list:
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

        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 'point': point}
        return self.postData(parameters)

    def pushLeaderboard(self, streamName, leaderArray):
        """ Pushes an array to a Leaderboard widget. """
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 'point': {
            'leaderboard': leaderArray
        }}
        return self.postData(parameters)

    def pushList(self, streamName, listArray):
        """ Pushes an array to a List widget. """
        if type(listArray) != list:
            raise TypeError
        for i in range(len(listArray)):
            if type(listArray[i]) != dict:
                listArray[i] = {'listItem': listArray[i]}
                
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 'point': {
            'list': listArray
        }}
        return self.postData(parameters)
    
    def pushPair(self, streamName, x, y):
        """ Pushes an x,y pair to a Pair widget"""
        if type(x) == list and type(y) == list:
            point = []
            if len(x) != len(y): raise ValueError
            for i in range(len(x)):
                point.append({'x': x[i], 'y': y[i]})
        else:
            point = {'x': x, 'y': y}
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'point': point}
        return self.postData(parameters)

    def pushImage(self, streamName, imgUrl):
        """ Pushes an image to an Image widget"""
        point = {'imgUrl': imgUrl}
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'point': point}
        return self.postData(parameters)

    def pushLabel(self, streamName, label):
        """ Pushes a label to a Label widget"""
        point = {'label': label}
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'point': point}
        return self.postData(parameters)

    def pushTable(self, streamName, headerRow, dataRows):
        """ Pushes a table to a Table widget """
        dataRows.insert(0, headerRow)
        point = {'table': dataRows}
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'point': point}
        return self.postData(parameters)

    def clear(self, streamName):
        parameters = {'accessKey': self.accessKey, 'streamName': streamName, 
                      'command': 'clear'}
        return self.postData(parameters)

    def postData(self, parameters):
        """ Makes an HTTP POST to the API URL. """
        # Convert to JSON
        jsonData = json.dumps(parameters)
        # Make request
        response = urllib2.urlopen(self.apiUrl, jsonData)
        return response.read()

    
