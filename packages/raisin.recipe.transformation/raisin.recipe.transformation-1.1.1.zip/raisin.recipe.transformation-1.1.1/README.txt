============================
raisin.recipe.transformation
============================
------------------------------------------
Tranform Raisin data warehouse information
------------------------------------------

**raisin.recipe.transformation** transforms information for the Raisin data warehouse

Background
==========

The Raisin project builds a data warehouse for Grape (Grape RNA-Seq Analysis Pipeline
Environment). Grape is a pipeline for processing and analyzing RNA-Seq data developed at 
the Bioinformatics and Genomics unit of the Centre for Genomic Regulation (CRG) in 
Barcelona. 

Important Note
==============

The raisin.recipe.transformation package is a Buildout recipe used by Grape, and is not
a standalone Python package. It is only going to be useful as installed by the 
grape.buildout package.

To learn more about Grape, and to download and install it, go to the Bioinformatics 
and Genomics website at:

http://big.crg.cat/services/grape

Motivation
==========

The Raisin data warehouse is used to configure the Raisin web server. It is also very
useful for any projects that need access to meta data concerning the RNA-Seq pipelines.
 
Here at the CRG, we configure all our RNASeq pipeline runs in a central place
before running the Grape pipelines. A data warehouse with all the meta data provides
a great overview of all RNA-Seq projects.

Installation
============

The grape.recipe.transformation package is already installed by grape.buildout, so
you don't have to do this. 

Configuration
=============

The buildout part that configures the raisin.recipe.transformation needs to know about
the location of the staging folder

[transform]
recipe = raisin.recipe.transformation
staging = ${buildout:directory}/etl/staging

The staging folder is the place where the raisin.recipe.transformation will put the 
transformed information.
