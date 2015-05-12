# README #


"iiifoo" is a web application that is primarily a IIIF Metadata/Presentation
 manifest factory and a IIIF Metadata/Presentation API provider. The source also
 integrates a slightly modified [mirador][m2] implementation.

Anyone who runs a [IIIF Image API][img11] compliant image server but has not 
 implemented the [IIIF Metadata API][md1] can use "iiifoo" to generate the 
 metadata API endpoints for them and therefore be able to use
 other applications, eg. [Mirador][m2], to use them.

This project now works with the [IIIF Presentation API 2.0][md2] \(successor 
 to the older Metadata API\).
 
[img11]: http://www-sul.stanford.edu/iiif/image-api/1.1/
[m2]: http://dmstech.github.io/mirador/
[md1]: http://www.shared-canvas.org/datamodel/iiif/metadata-api.html
[img2]: http://iiif.io/api/image/2.0/
[md2]: http://iiif.io/api/presentation/2.0/


The primary use case is the fast and easy generation of an initial set of IIIF 
 presentation manifests by mapping existing sets of images for which this is 
 desirable (eg. each set is perhaps a manuscript) and exposing these over HTTP 
 in the same manner as described in the IIIF Presentation API.

This application provides two mechanisms for doing this:

1. "Exporting" (internally a feature of "authoring" sources):

    The user can extend a base interface to create a custom API that, for 
      example, given some group identifier, retrieves further details from an 
      external interface and extracts the required ones and saves them.
     
    An API that creates manifests given a IIIF image server path, image 
      identifier and manifest identifier is already provided (detailed in "Use 
      Case Examples").

2. "Mapping" (internally a feature of "mapped" sources):
    
    This works similar to the above but skips local storage and always resolves 
      against an external service to generate the manifest.

The two may be eventually merged.

__I hope to add functionality to allow creating manifests from scratch as well
as modifying created manifests through a RESTful API as well soon.__

## Running iiifoo #

### Installing dependencies and preparing environment #
_Note: The following assumes the use of **Ubuntu 12.04 LTS** as the OS._

To check out the project, `git` needs to be installed.

If postgresql will be used as the database, that will need to be installed too:

- `sudo apt-get install postgresql libpq-dev python-dev python-psycopg2`

Otherwise, SQLite may be used instead.

For caching, the application can use Redis (but this may be skipped as a file
 cache or memcached may be used instead):
```bash
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
sudo make install
```
Something like `sudo redis-server /etc/redis.conf` will start redis.

Check out the project and navigate to the directory 
 where it was checked out in order to set up the environment.


Next, first install 'libxml' and 'libxslt' \(required for some tests\):
 \(`sudo apt-get install libxml2-dev libxslt-dev python-dev`\). Also, install 
 `pip` via the instructions found at the [pip documentation]
 (https://pip.pypa.io/en/latest/installing.html), or by running the commands 
 listed below for convenience:

- `curl -O https://bootstrap.pypa.io/get-pip.py`
- `sudo python get-pip.py`

Then, install requirements via `sudo pip install -r requirements.txt`.

### Configuring #
The configuration file must be created before first run.

Create the configuration file using `python populate_settings.py`. Make
 sure to run this from the directory containing "populate_settings.py". This
 creates a file named "settings.py". Edit the settings in this file as required.
 The configuration parameters present in this file can also be overridden by
 environment variables.

The script populates the configuration file with the following order of
 precedence:

1. Environment variables

2. Pre-existing configuration

3. Defaults.
 

Make sure that the database configurations are correct and/or the database 
 has been configured accordingly.

If using a file as cache, make sure file_cache_dir is an existing empty dir.

Preferably, either set environment variables before generating the settings file,
 or simply edit the settings file after generating. Details regarding
 configurations are provided below.

When starting the server, settings can be overridden using environment 
 variables. Same rules apply as when running populate_settings.py.

#### Configuration parameters #
The configuration parameters are lowercase in "settings.py", __but are expected 
 to be in uppercase if provided in the environment__. To generate a 
 configuration file with desired configurations, the simplest way to do so is 
 set the required configuration environment variables and run 
 `python populate_settings.py`.

- __pids\_dir__ The directory to store pids. _Default: ""_
- __logs\_dir__: The directory in which to store logs. _Default: ""_
- __gunicorn\_proc_name__ Process name for gunicorn. *Default: "mira_gunicorn"*
- __gunicorn\_loglevel__: Log level for gunicorn (error, warning, debug or info) 
 _Default: "info"_
- __server\_debug__: Determines whether to run in debug mode. Does not affect 
 the gunicorn processes. _Default: ""_
- __profiler__: Whether to run with profiler. Leave blank for false, any 
 non-blank value is treated as truthy. Does not affect normal gunicorn serving. 
 _Default: ""_
- __test\_debug\_on\_fail__: Enter debugging mode when a test fails. Leave blank 
 for false, any non-blank value is treated as truthy. _Default: ""_
- __cache\_type__: Cache type. Can be "redis", "file", "memcached" or "memory".
 "Memory" is only recommended for single-process development environments. _Default: "file"_
- __server\_port__: Port to run the server on. _Default: "5678"_
- __db\_dialect__: Database type. _Default: "postgresql"_
- __db\_pass__: Database password. _Default: "iiifoo"_
- __db\_user__: Database user. _Default: "iiifoo"_
- __db\_host__: Database host. _Default: "localhost"_
- __db\_name__: Database name. _Default: "iiifoo"_
- __db\_port__: Database port. _Default: "5432"_
- __redis_port__: Redis server port. _Default: "6379"_
- __redis_host__: Redis server host. _Default: "localhost"_
- __redis_cache_key_prefix__: Redis cache key prefix. _Default: "iiifoo-cache"_
- __redis_db__: Redis database number. _Default: "0"_
- __redis_pw__: Redis password. _Default: ""_
- __redis_cache_default_timeout__: Redis default cache timeout. _Default: "86400"_
- __file\_cache\_dir__: Directory to store the file cache. Make sure it doesn't
 store anything else. _Default: "file_cache"_
- __file\_cache\_threshold__: Number of items to cache before starting to remove
 old ones. _Default: "500"_
- __file\_cache\_default_timeout__: Amount of time to keep cached items before
 expiry. _Default: "86400"_
- __file\_cache\_file_mode__: File mode. Default 0600. _Default: "384"_
- __memcached\_default_timeout__: Amount of time to keep cached items before
 expiry. _Default: "86400"_
- __memcached\_key\_prefix__: Memcached cache key prefix. _Default: "iiifoo-cache"_
- __memcached\_servers__: Comma-separated list of memcached servers. 
 _Default: "127.0.0.1:11211"_


### Starting #
Normally, all you have to do to start iiifoo is:
`./start_mira_gunicorn.sh`

### Stopping #
To stop:
`./scripts/killbypidfile.sh iiifoo-server.pid`

Adjust accordingly if the pidfile is in a different location.

### Testing #
'iiifoo' has behavior tests written using the "[behave]
 (https://pypi.python.org/pypi/behave)" Python BDD framework.

To run tests, simply navigate to project root and run:
`behave --tags=-wip` 

(`-wip` skips scenarios tagged as wip, i.e. work in progress.)

To generate junit-style test results, add:
 `--junit --junit-directory=test_results_junit`


## Development #
Some guidelines:

- Do NOT add new settings to settings.py, add them to populate_settings.py and 
 then run the script. Check docs in populate_settings for information.

- Keep related views in blueprints. Some blueprints may depend on others;
 specify in docstrings if so.

- Be sure to add tests for new features. The [`behave`]
 (https://pypi.python.org/pypi/behave) framework is used for tests.

- Run them, too.

- When writing tests, add any mock data to the mock_data module and ideally
 perform the mocking in environment.py.

- Make sure to add and use custom exceptions in the `exception` module for
 known exceptions.


## Use Case Examples #
This project comes with a helpful predefined source that can be used out of the 
 box for adding images to create manifests containing information regarding 
 images served by IIIF Image API compatible image servers.
For example, to add an image from the Stanford repository to a manifest:

`curl -X POST -d '{"images": [{"id":"qm670kv1873%2FW168_000002_300", "name": "foobar!"}], "iiif_image_server_url": "https://sul-stacks.stanford.edu/image/iiif/", "manifest_id": "fooOfBar"}' -H "Content-Type: application/json" localhost:5678/author/iiifsource_v0_1a`

The above adds an image labelled "foobar\!" to a manifest with id fooOfBar 
 and creates it if necessary.
The manifest may be retrieved with:

`http://localhost:5678/iiif/iiifsource_v0_1a/https%3A%252F%252Fsul-stacks.stanford.edu%252Fimage%252Fiiif%252F/fooOfBar/manifest`

To open it up in the demo Mirador 2 viewer:
`http://localhost:5678/viewer/iiifsource_v0_1a?iiif_image_server_url=https%3A%2F%2Fsul-stacks.stanford.edu%2Fimage%2Fiiif%2F&manifest_id=fooOfBar`

## Misc #
I had some library version issues because of an old OS installation which is why
 I had to specify it in the lines below. In that case, this is how I ended up 
 having to run this for debugging:

`PYTHONPATH=$(pwd) DYLD_LIBRARY_PATH=/Library/PostgreSQL/9.3/lib
 db_port=5434 python start_mira_server.py`


And for testing:

`DYLD_LIBRARY_PATH=/Library/PostgreSQL/9.3/lib db_port=5434 behave --tags=-wip --junit --junit-directory=test_results_junit`

## TODO #
- Fix url escaping issues with the manifest that gets saved via export 
(the @id that it has should end up something that can be GET'd to retrieve the
manifest... right now it's a bit bugged). **I think this is resolved now**
- Either move to a JSON store (mongoDB or something) or change model structure.
- Add memcached support.
- Autogenerated api docs.


## Acknowledgments #
Thanks to the following people for helping me out with this:
- [Najam Ahmed Ansari](https://github.com/najamansari)
