Leftronic Python Package Documentation
======================================

What is Leftronic?
------------------

[Leftronic](https://beta.leftronic.com) makes powerful dashboards for business intelligence.

* Colorful and interactive data visualizations
* Templates to get you started right away
* Drag-and-drop editor makes it easy for anyone to create a powerful dashboard, customized to their needs
* Integration with Google Analytics, Twitter, Chartbeat, Zendesk, Basecamp, Pivotal Tracker, Facebook, and more to come!
* Dashboards can be protected or shared with a shortened URL
* Powerful API's for Javascript, PHP, Python, Ruby, and Java
* Python Package and Ruby Gem

Technical Notes
---------------

We also suggest checking out our [API](https://beta.leftronic.com/api) page. While the most detailed documentation is here, it has JSON and CURL examples in addition to a test form to send data to your custom widgets.

Authentication is handled by your API access key. We strongly encourage you to keep this key private. If you're logged in, your key can be found on our [API](https://beta.leftronic.com/api) page. If you plan on using one of our API libraries, you will find instructions below on how to set your access key.

All API requests are made by sending a POST request to https://beta.leftronic.com/customSend with a properly formatted JSON packet. We do not support XML.

Current API version is 1.0.
Current Python Package version is 1.2.1.

Getting Started
---------------

If you haven't already, create an account at https://beta.leftronic.com/accounts/login.

Get your API access key from the API overview page at https://beta.leftronic.com/api.

We recommend checking out our [Tutorials](https://beta.leftronic.com/tutorials) to familiarize yourself with your dashboard.

Python Package
--------------

Start by downloading the most recent version of our Python Package on [Github](https://github.com/sonofabell/leftronic-python) or on the [Python Package Index](http://pypi.python.org/pypi/leftronic).

### Installing Dependencies

Install [urllib2](http://docs.python.org/library/urllib2.html). (_Note_: Some versions of Python may ask for or install urllib3, that will work as well)

```
easy_install urllib2
```

Or, if you have [pip](http://pypi.python.org/pypi/pip) installed:

```
pip install urllib2
```

Install [simplejson](http://docs.python.org/library/json.html):

```
easy_install simplejson
```

Or, with [pip](http://pypi.python.org/pypi/pip):

```
pip install simplejson
```

### Installing the package

**Installing from source**

Download the file from [Github](https://github.com/sonofabell/leftronic-python) or [PyPI](http://pypi.python.org/pypi/leftronic) and extract if necessary. (_Note_: Be sure you're in the "leftronic" directory)

```
python setup.py install
```

**Installing remotely from [PyPI](http://pypi.python.org/pypi/leftronic)**

```
easy_install leftronic
```

Or, with [pip](http://pypi.python.org/pypi/pip):

```
pip install leftronic
```

Pushing to Your Dashboard
-------------------------

Import the file. Your location may vary.

```python
from leftronic import Leftronic
```

Create a class instance with your API key. Feel free to name it whatever you'd like.

```python
update = Leftronic("YOUR_ACCESS_KEY")
```

Here are some example functions to push to your dashboard. Be sure you have configured the correct widgets to accept custom data points. Also, be sure that you have entered your API access key correctly.

Let's start with pushing a number to a widget.

```python
update.pushNumber("yourNumberStream", 14600)
```

You can also push in a suffix or prefix for a number as follows:

```python
update.pushNumber("yourNumberStream", {"prefix": "$", "number": 4})
update.pushNumber("yourNumberStream", {"suffix": "m/s", "number": 35})
```

And for sparklines/line graphs, you can use a unix timestamp as follows:

```python
update.pushNumber("yourNumberStream", {"number": 13, "timestamp": 1329205474})
```

Finally, an array of numbers:

```python
update.pushNumber("yourSparklineStream", [{"number", 93, "timestamp": 1329205474}, {"number": 35, "timestamp": 1329206474}])
```

For number arrays, timestamps must be monotonically increasing, and each element of the array must have a timestamp.

Now we'll push some geographic coordinates to a map widget. You can use either the U.S. or world map widgets. The first coordinate (37.8) is the latitude and the second coordinate (-122.6) is the longitude. If your request is successful, you should see a data point appear on San Francisco, California. Optionally, if you'd like to set the color of your map point simply specify that in your function call. *Note*: only red, blue, green, purple, and yellow colors are supported at this time. Incorrect or missing color will default to red.

```python
update.pushGeo("yourGeoStream", 37.8, -122.6)
```

```python
update.pushGeo("yourGeoStream", 37.8, -122.6, "blue")
```

You can also push an array of latitude, longitude, and colors:

```python
update.pushGeo("yourGeoStream", [37.8, 12.3], [-122.6, 52], ["blue", "red"])
```

The above example will create two points. A blue point at (37.8, -122.6) and a red point at (12.3, 52). The color array is optional.

Here's how you push a title and message to a text feed widget:

```python
update.pushText("yourTextStream", "This is my title.", "Hello World!", "http://example.com/myimage.png")
```
The third parameter, the image URL, is optional.

Let's push an array of names and values to a leaderboard widget. Be sure to create the array first (you may call it whatever you'd like). Be careful to use the proper syntax. Next, push the array to your widget.

```python
leaderArray = [{"name": "Johnny", "value": 84}, {"name": "Jamie", "value": 75}, {"name": "Lance", "value": 62, "prefix": "$"}]

update.pushLeaderboard("yourBoardStream", leaderArray)
```

Similar to the last example, let's push a list of items to a list widget. Same rules as last time.

```python
listArray = ["Elizabeth", "Marshall", "Claire", "Nolan"]

update.pushList("yourListStream", listArray)
```

Image and Label widgets are now customizable through the API! Let's update an Image widget:

```python
update.pushImage("yourImageStream", "http://example.com/mypicture.png")
```

And a Label widget:

```python
update.pushLabel("yourLabelStream", "Uptime")
```

Updating an X-Y Pair widget:

```python
x = 15
y = 8
update.pushPair("yourPairStream", x, y)

# x and y can also be arrays, such as x = [10, 23, 45], y = [12, 90, 30]
# this would create three points at (10, 12), (23, 90) and (45, 30)
```

Updating a Table widget:

```python
headerRow = ['name', 'city', 'country']
dataRows = [ ['Lionel', 'Rosario', 'Argentina'], ['Andres', 'Albacete', 'Spain']]
update.pushTable("yourTableStream", headerRow, dataRows)
```

And clearing a widget. You can programmatically clear Map, Text Feed, Sparkline/Line Graph, and Pair widgets:

```python
update.clear("yourStreamName")
```

Feedback and Issues
-------------------

If you notice any bugs or other issues, submit a patch or send us a pull request. You can also send us an email at <support@leftronic.com>.
