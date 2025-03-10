<!-- markdownlint-disable MD041 -->
[![GitHub release](https://img.shields.io/github/v/release/ggeerraarrdd/geofinder)](https://github.com/ggeerraarrdd/geofinder/releases)
[![Maintenance](https://img.shields.io/badge/maintained-no-red.svg)](https://github.com/ggeerraarrdd/geofinder/commits/main/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/236a15d715984d5c8c529261d53d8408)](https://app.codacy.com/gh/ggeerraarrdd/geofinder/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![codecov](https://codecov.io/gh/ggeerraarrdd/geofinder/graph/badge.svg?token=5C67LR1L0L)](https://codecov.io/gh/ggeerraarrdd/geofinder)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ggeerraarrdd_geofinder&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ggeerraarrdd_geofinder)
[![Renovate enabled](https://img.shields.io/badge/renovate-disabled-red.svg)](https://renovatebot.com/)
<!-- markdownlint-enable MD041 -->

# Geofinder

An online game that's like _Where's Waldo?_ but for houses

## Table of Contents

> [!NOTE]
> ALL CONTENTS IN THIS REPO ARE FOR EDUCATIONAL PURPOSES ONLY.

* [Description](#description)
* [Target Users](#target-users)
* [Features](#features)
* [Project Structure](#project-structure)
* [Quick Start](#quick-start)
* [Local Setup](#local-setup)
  * [Prerequisites](#prerequisites)
  * [Dependencies](#dependencies)
  * [Installation](#installation)
  * [Configuration](#configuration)
* [Usage](#usage)
* [Production Setup](#production-setup)
* [System Administration](#system-administration)
* [Author(s)](#authors)
* [Version History](#version-history)
  * [Release Notes](#release-notes)
  * [Initial Release](#initial-release)
* [Future Work](#future-work)
* [License](#license)
* [Contributing](#contributing)
* [Acknowledgments](#acknowledgments)
* [Screenshots](#screenshots)

## Description

_Geofinder_ is an online scavenger hunt game. Its gameplay is simple: Given a photo of a house somewhere in the world, your task is to look for that house inside a marked area on a map. While that may sound straightforward, how you will go about looking might not be.

_Geofinder_ comes in two modes.

1. In the Wordle-like **default mode**, you are given one house a day and have until the end of the day (CST time) to find it.
2. In the Netflix-like **challenge mode**, aka Geo50x, you are given 50 houses at once.

_Geofinder_ is inspired by such childhood games as _[Where's Waldo?](https://en.wikipedia.org/wiki/Where%27s_Wally%3F)_ and _[Where in the World is Carmen Sandiego?](https://en.wikipedia.org/wiki/Carmen_Sandiego)_. And the simple pleasures of looking out through vehicle windows and just gazing at the passing landscapes and cityscapes.

![Screenshot](assets/geofinder_00.png)

## Target Users

* TBD

## Features

* TBD

## Project Structure

* TBD

## Quick Start

* TBD

## Local Setup

### Prerequisites

* TBD

### Dependencies

* See `requirements.txt`

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/ggeerraarrdd/geofinder.git
    ```

2. **Navigate into the project directory:**

    ```bash
    cd geofinder # For example
    ```

3. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Set up a PostgreSQL Database:**

    TBD

6. **Set up a Google Maps API Key:**

    For the embedded map to work, you need to set up an API Key. Before you can create one, you will need to create a Google Cloud project, for which you need a Google Cloud account.

    * [Set up a Google Cloud account](https://cloud.google.com)
    * [Set up your Google Cloud project](https://developers.google.com/maps/documentation/javascript/cloud-setup)
    * [Using API Keys](https://developers.google.com/maps/documentation/javascript/get-api-key)

7. **Create an `.env` file and set the environment variables:**

    Create a file named `.env` in the `app` directory of the project and add the following variables:

    TBD

### Configuration

* TBD

## Usage

1. **Go into the app directory and run the command:**

    ```bash
    flask run
    ```

2. **Open the film series website:**

    Copy and open the URL displayed after 'Running on' in the terminal.

3. **Register an account:**

    TBD

4. **Login:**

    TBD

## Production Setup

* TBD

## System Administration

* TBD

## Author(s)

* [@ggeerraarrdd](https://github.com/ggeerraarrdd/)

## Version History

### Release Notes

* See [https://github.com/ggeerraarrdd/geofinder/releases](https://github.com/ggeerraarrdd/geofinder/releases)

### Initial Release

The [initial release](https://github.com/ggeerraarrdd/geofinder/releases/tag/v1.0.0) of _Geofinder_, as _Geo50x_, was submitted as the final project for [CS50x: CS50's Introduction to Computer Science](https://cs50.harvard.edu/x/2023/) (HarvardX, 2023). Read the [project brief](https://cs50.harvard.edu/x/2023/project/) as of September 2023.

## Future Work

Development is ongoing.

## License

* [MIT License](https://github.com/ggeerraarrdd/geofinder/blob/main/LICENSE)

## Contributing

* TBD

## Acknowledgments

* The distribution code for CS50's Finance problem served as a template for the app.
* The documentations for the Google Maps Platform were a daily, often hourly, read.
* Too many StackOverflow [Q&As](https://meta.stackoverflow.com/questions/267822/if-stack-overflow-doesnt-have-threads-what-the-heck-should-they-be-called) and Medium articles to mention but a couple proved immensely useful in developing two key functions
  * [Offset Latitude and Longitude by some meters accurately - Reverse Haversine](https://gis.stackexchange.com/questions/411859/offset-latitude-and-longitude-by-some-meters-accurately-reverse-haversine)
  * [Algorithm for offsetting a latitude/longitude by some amount of meters](https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters)
* The folks at CS50 for a mind-altering course.

## Screenshots

![Screenshot](assets/geofinder_01.png)
![Screenshot](assets/geofinder_02.png)
![Screenshot](assets/geofinder_03.png)
![Screenshot](assets/geofinder_04.png)
![Screenshot](assets/geofinder_05.png)
![Screenshot](assets/geofinder_06.png)

## Frontispiece

Screenshot of Playing with Geofinder web interface. Image taken from web-based game interface (Personal Collection, 2024). In the public domain.
