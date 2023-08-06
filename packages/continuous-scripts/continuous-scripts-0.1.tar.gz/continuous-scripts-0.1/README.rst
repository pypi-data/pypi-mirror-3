Continuous.io build scripts & services
======================================

For further documentation see: https://continuous.io/docs/contributing/

This repository contains the scripts responsible for building and running Continuous build servers.

bootstrap.sh
------------

This script bootstraps the build process. The main task of which is to download and extract an archive of the necessary scripts into a temporary directory on the build server. This will include the project's startup script, plus zero or more service scripts (see below).

continuousrc/
-------------

Example ``.continuousrc`` files for each of the supported project types.

services/
---------

Scripts for setting up the services a project may require.

startupscripts/
---------------

Scripts responsible for orchestrating the build overall build process for each of the supported project types.
