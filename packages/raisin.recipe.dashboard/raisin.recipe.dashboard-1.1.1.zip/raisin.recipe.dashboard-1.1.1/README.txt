=======================
raisin.recipe.dashboard
=======================
------------------------
Configure Raisin servers
------------------------

**raisin.recipe.dashboard** provides a dashboard for Raisin

Background
==========

The Raisin project provides web servers for the Grape (Grape RNA-Seq Analysis Pipeline
Environment). Grape is a pipeline for processing and analyzing RNA-Seq data developed at 
the Bioinformatics and Genomics unit of the Centre for Genomic Regulation (CRG) in 
Barcelona. 

Important Note
==============

The raisin.recipe.dashboard package is a Buildout recipe used by Grape, and is not
a standalone Python package. It is only going to be useful as installed by the 
grape.buildout package.

To learn more about Grape, and to download and install it, go to the Bioinformatics 
and Genomics website at:

http://big.crg.cat/services/grape

Motivation
==========

The Raisin web server has a default way of browsing the experiment data. The 
raisin.recipe.dashboard package produces static HTML dashboards that can be customized
for use a specific audience by choosing the rows and columns by which the
dashboard is navigated.

Installation
============

The grape.recipe.dashboard package is already installed by grape.buildout, so
you don't have to do this. 

Configuration
=============

The buildout part that configures raisin.recipe.dashboard may look like this:

[dashboard]
recipe = raisin.recipe.dashboard
database = ${buildout:directory}/etl/database/database.db
output_file = ${buildout:directory}/dashboards/index.html
title = Generic dashboard
description = All projects in one dashboard
rows = species
cols = read_length
subset_parameters = project_id

It needs pointers to the database, the location where the static HTML page should
be stored, and a title and description.
The rows and cols customize the hierarchy that is used when visualizing the dashboard.