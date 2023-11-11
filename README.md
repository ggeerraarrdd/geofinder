# Geo50x

It's like _Where's Waldo?_ but for houses

## Description

_Geo50x_ is an online carto-architectural scavenger hunt. The gameplay is simple: Given a photo of a house somewhere in the world, you are tasked with locating that house on Google Maps. It's that straighforward, although how you will go about searching might not be.

_Geo50x_ is inspired by such childhood games as _[Where's Waldo?](https://en.wikipedia.org/wiki/Where%27s_Wally%3F)_ and _[Where in the World is Carmen Sandiego?](https://en.wikipedia.org/wiki/Carmen_Sandiego)_. And the simple pleasures of looking out through vehicle windows and just gazing at the passing landscapes and cityscapes.

![Screenshot](static/images/geo50x_5.jpg)

More screenshots below.

## Disclaimer

ALL CONTENTS IN THIS REPO ARE FOR EDUCATIONAL PURPOSES ONLY.

## Getting Started

### Dependencies

* Flask==2.2.5
* Flask-Session==0.4.1
* Flask_SocketIO==5.3.6
* geographiclib==2.0
* haversine==2.8.0
* Werkzeug==3.0.1

### Usage

Clone it!

```bash
git clone https://github.com/ggeerraarrdd/geo50x.git
```

Go into the project directory and run the command:

```bash
flask run
```

Open the URL after 'Running on'.

### Notes on Google Maps

For the embedded maps to work, you need to use your own API Key. Before you can create one, you will need to create a Google Cloud project, for which you need a Google Cloud account.

* [Set up a Google Cloud account](https://cloud.google.com)
* [Set up your Google Cloud project](https://developers.google.com/maps/documentation/javascript/cloud-setup)
* [Using API Keys](https://developers.google.com/maps/documentation/javascript/get-api-key)

In your terminal window, execute:

```bash
export MAP_API_KEY=value
```

where `value` is your API key.

Check to confirm if environmental variable is saved by executing

```bash
echo $MAP_API_KEY
```

### Database

You can recreate the database using the queries in `sql.txt`. Then populate the `locs` table with data in `geo50data.csv`. Use of the `geoids` table is not yet implemented (as of v1.0.0).

### Logging In

You can use the following credentials to log in to access a Search History with existing data.

```text
username: carto
password: carto
```

## Author(s)

* [@ggeerraarrdd](https://github.com/ggeerraarrdd/)

## Version History

### Release Notes

* See [https://github.com/ggeerraarrdd/geo50x/releases](https://github.com/ggeerraarrdd/geo50x/releases)

### Initial Release

The [initial realease](https://github.com/ggeerraarrdd/geo50x/releases/tag/v1.0.0) of _Geo50x_ was submitted as the final project for [CS50x: Introduction to Computer Science](https://cs50.harvard.edu/x/2023/) (HarvardX, 2023).

[Project brief](https://cs50.harvard.edu/x/2023/project/) as of September 2023:

_The climax of this course is its final project. The final project is your opportunity to take your newfound savvy with programming out for a spin and develop your very own piece of software. So long as your project draws upon this course’s lessons, the nature of your project is entirely up to you. You may implement your project in any language(s). You are welcome to utilize infrastructure other than the CS50 Codespace. All that we ask is that you build something of interest to you, that you solve an actual problem, that you impact your community, or that you change the world. Strive to create something that outlives this course._

### Future Work

New features development is ongoing.

* Add functionalities to Search History page such as ~~reviewing submitted locations~~ _(Update Nov 2, 2023: Done)_ and ~~more easily re-try locations attempted but not yet found~~ _(Update Nov 2, 2023: Done)_.
* Add administration interface for data management.
* Deploy app on AWS Lightsail.

## License

* [MIT License](https://github.com/ggeerraarrdd/large-parks/blob/main/LICENSE)

## Acknowledgments

* The distribution code for CS50's Finance problem served as a template for the app.
* The documentions for the Google Maps Platform were a daily, often hourly, read.
* Too many StackOverflow [Q&As](https://meta.stackoverflow.com/questions/267822/if-stack-overflow-doesnt-have-threads-what-the-heck-should-they-be-called) and Medium articles to mention but a couple proved immensely useful in developing two key functions
  * [Offset Latitude and Longitude by some meters accurately - Reverse Haversine](https://gis.stackexchange.com/questions/411859/offset-latitude-and-longitude-by-some-meters-accurately-reverse-haversine)
  * [Algorithm for offsetting a latitude/longitude by some amount of meters](https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters)
* The folks at CS50 for a mind-altering course.

## Screenshots

![Screenshot](static/images/geo50x_6.jpg)
![Screenshot](static/images/geo50x_7.jpg)
![Screenshot](static/images/geo50x_8.jpg)
![Screenshot](static/images/geo50x_9.jpg)
![Screenshot](static/images/geo50x_10.jpg)
