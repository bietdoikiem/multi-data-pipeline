# Distributed Big Data Pipeline Using Kafka, Cassandra, Dash with Docker

You can use the resources in this github to deploy an end-to-end data pipeline on your local computer using Docker containerized Kafka (data streaming), Cassandra (NoSQL database) and Jupyter Lab, Dash (data analysis Visualization).

This bases on the repo https://github.com/salcaino/sfucmpt733/tree/main/foobar-kafka
Substantial changes and bug fixes have been made. Tested on Windows 10.

## Project Folder Structure

This is the original folder structure (not include the installation of packages)

```
+---.vscode
+---cassandra
+---consumers
|   +---nltk_data
|   +---python
+---cryptopanic-producer
|   +---src
+---dash-app
|   +---assets
|   +---pages
|   +---s3-temp
|   +---utils
+---data-vis
|   +---python
+---faker-producer
+---kafka
|   +---connect
+---kraken-producer
+---owm-producer
+---twitter-producer
```

## Quick-start instructions

You need to apply for some APIs to use with this. The APIs might take days for application to be granted access. Sample API keys are given, but it can be blocked if too many users are running this.

Twitter Developer API: https://developer.twitter.com/en/apply-for-access

OpenWeatherMap API: https://openweathermap.org/api

After obtaining the API keys, please update the files "twitter-producer/twitter_service.cfg" and "owm-producer/openweathermap_service.cfg" accordingly.

Now, a little script has been made for the automation of running the project more efficiently

Let's open the terminal and type in the following bash script. Please make sure to be in the root directory of the project!

```bash
./run.sh [start|build|clean|bash]
```

- **start**: automatically setup Cassandra and Kafka (including Kafka Connect) sequentially and effectively link necessary services together for a functional flow
- **build**: automatically indicates build process for each images required for the project as well as remove dangling images after being built (yes/No options)
- **clean**: automatically clean up all running containers and remove all mounted volumes
- **bash**: automatically ask for the name of the container you want to access and open interactive bash (for Cassandra container, there's an extra option for accessing CQLSH directly)

## Accessibility

<img src="https://i.ibb.co/gz84TYS/image.png"/>

To be able to access the UI for XtremeOLAP trading analytical web application, you have to run a container for `dash-app` image and access the website via `[localhost]:8050`.
