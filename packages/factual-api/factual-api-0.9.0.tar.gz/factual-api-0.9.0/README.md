# About

Note: This driver is still in development and is not ready for production use. 

This is the Factual supported Python driver for [Factual's public API](http://developer.factual.com/display/docs/Factual+Developer+APIs+Version+3).


This API supports queries to Factual's Read, Schema, Crosswalk, and Resolve APIs. Full documentation is available on the Factual website:

*   [Read](http://developer.factual.com/display/docs/Factual+Developer+APIs+Version+3): Search the data
*   [Schema](http://developer.factual.com/display/docs/Core+API+-+Schema): Get table metadata
*   [Crosswalk](http://developer.factual.com/display/docs/Places+API+-+Crosswalk): Get third-party IDs
*   [Resolve](http://developer.factual.com/display/docs/Places+API+-+Resolve): Enrich your data and match it against Factual's

This driver is supported via the [Factual Developer Group](https://groups.google.com/group/factual_developers)

# Overview


## Dependencies
[Requests](http://docs.python-requests.org/en/v0.10.7/index.html)

[requests-oauth](https://github.com/maraujop/requests-oauth)


## Basic Design

The driver allows you to create an authenticated handle to Factual. With a Factual handle, you can send queries and get results back.

Queries are created using the Factual handle, which provides a fluent interface to constructing your queries.

## Tables
The Factual API is a generic API that sits over all tables available via the Factual v3 API. Some popular ones:

*   Table <tt>global</tt> for international places
*   Table <tt>restaurants-us</tt> for US restaurants only
*   Table <tt>places</tt> for US places only

## Setup
Obtain an OAuth key and secret from [Factual](http://www.factual.com/devtools/beta)

example.py is provided with the driver as a reference.

To get started, import the Factual python driver module and create a Factual object using your OAuth key and secret.

````python
from factual import *
factual = Factual(KEY, SECRET)
````


## Simple Read Examples

`````python
# Return entities from the Places dataset with names beginning with "starbucks"
factual.table("places").filters({"name":{"$bw":"starbucks"}}).data()
````

`````python
# Return entity names and non-blank websites from the Global dataset, for entities located in Thailand
factual.table("global").select("name,website").filters(
	{"$and":[{"country":"TH"}, {"website":{"$blank":"false"}}]}).data()
````

`````python
# Return highly rated U.S. restaurants in Los Angeles with WiFi
factual.table("restaurants-us").filters(
  {"$and":[{"locality":"los angeles"},{"rating":{"$gte":4}},{"wifi":"true"}]}).data()
````


## Simple Crosswalk Example

````python
# Concordance information of a place
FACTUAL_ID = "110ace9f-80a7-47d3-9170-e9317624ebd9"
query = factual.crosswalk().factual_id(FACTUAL_ID)
query.data()
````

````python
# Or specify a place with its namespace_id and namespace
SIMPLEGEO_ID = "SG_6XIEi3qehN44LH8m8i86v0"
query = factual.crosswalk().namespace('simplegeo',SIMPLEGEO_ID)
query.data()
````

## Simple Resolve Example

````python
# Returns resolved entities as an array of hashes
query = factual.resolve({"name":"McDonalds","address":"10451 Santa Monica Blvd","region":"CA","postcode":"90025"})
query.data()[1]["resolved"]  # true or false
query.data()
````


## Full Documentation
Full documentation is available at http://developer.factual.com
