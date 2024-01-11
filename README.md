# Geofinder

An online game that's like _Where's Waldo?_ but for houses

## Description

_Geofinder_ is an online carto-architectural scavenger hunt. The gameplay is simple: Given a photo of a house somewhere in the world, you are tasked with locating that house on Google Maps. It's that straighforward, although how you will go about searching might not be.

_Geofinder_ is inspired by such childhood games as _[Where's Waldo?](https://en.wikipedia.org/wiki/Where%27s_Wally%3F)_ and _[Where in the World is Carmen Sandiego?](https://en.wikipedia.org/wiki/Carmen_Sandiego)_. And the simple pleasures of looking out through vehicle windows and just gazing at the passing landscapes and cityscapes.

![Screenshot](static/images/geofinder_00.png)

More screenshots below.

## Disclaimer

ALL CONTENTS IN THIS REPO ARE FOR EDUCATIONAL PURPOSES ONLY.

## Getting Started

### Dependencies

* See `requirements.txt`

### Usage

Clone it!

```bash
git clone https://github.com/ggeerraarrdd/geofinder.git
```

Go into the project directory and run the command:

```bash
flask run
```

### Database

_Geofinder_ uses a Postgres database. Once provisioned, use your preferred DBMS to execute the queries in `database/sql.txt` to install PostGIS and to create the database's schema and tables. Then use `database/geofinderdata.csv` to populate the `locs` table.

Once the database is set up, register an initial user account using the web app. Then change the account's `status` to `admin` using your DMBS.

### Notes on Google Maps

For the embedded maps to work, you need to use your own API Key. Before you can create one, you will need to create a Google Cloud project, for which you need a Google Cloud account.

* [Set up a Google Cloud account](https://cloud.google.com)
* [Set up your Google Cloud project](https://developers.google.com/maps/documentation/javascript/cloud-setup)
* [Using API Keys](https://developers.google.com/maps/documentation/javascript/get-api-key)

### Environment Variables

Set up the following environment variables using your preferred method.

```text
SECRET_KEY=<Your_Flask_Session_Secret_Key>
MAP_API_KEY=<Your_Google_Maps_API_Key>
GEOFINDER_DB_HOST=<Your_Database_Host>
GEOFINDER_DB_PORT=5432
GEOFINDER_DB_NAME=<Your_Database_Name>
GEOFINDER_DB_USER=<Your_Database_Username>
GEOFINDER_DB_PASSWORD=<Your_Database_Password>
NEW_REGISTRATIONS=TRUE
```

## Author(s)

* [@ggeerraarrdd](https://github.com/ggeerraarrdd/)

## Version History

### Release Notes

* See [https://github.com/ggeerraarrdd/geofinder/releases](https://github.com/ggeerraarrdd/geofinder/releases)

### Initial Release

The [initial realease](https://github.com/ggeerraarrdd/geofinder/releases/tag/v1.0.0) of _Geofinder_, as _Geo50x_, was submitted as the final project for [CS50x: CS50's Introduction to Computer Science](https://cs50.harvard.edu/x/2023/) (HarvardX, 2023). Read the [project brief](https://cs50.harvard.edu/x/2023/project/) as of September 2023.

### Future Work

Development is ongoing.

## License

* [MIT License](https://github.com/ggeerraarrdd/geofinder/blob/main/LICENSE)

## Acknowledgments

* The distribution code for CS50's Finance problem served as a template for the app.
* The documentions for the Google Maps Platform were a daily, often hourly, read.
* Too many StackOverflow [Q&As](https://meta.stackoverflow.com/questions/267822/if-stack-overflow-doesnt-have-threads-what-the-heck-should-they-be-called) and Medium articles to mention but a couple proved immensely useful in developing two key functions
  * [Offset Latitude and Longitude by some meters accurately - Reverse Haversine](https://gis.stackexchange.com/questions/411859/offset-latitude-and-longitude-by-some-meters-accurately-reverse-haversine)
  * [Algorithm for offsetting a latitude/longitude by some amount of meters](https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters)
* The folks at CS50 for a mind-altering course.

## Screenshots

![Screenshot](static/images/geofinder_01.png)
![Screenshot](static/images/geofinder_02.png)
![Screenshot](static/images/geofinder_03.png)
![Screenshot](static/images/geofinder_04.png)
![Screenshot](static/images/geofinder_05.png)
