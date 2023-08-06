# singleplatform

Python wrapper for the [SinglePlatform REST API](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration). Originally developed to power [Fondu](http://fondu.com).

Philosophy:

* Map SinglePlatform's REST endpoints one-to-one
* Clean, simple, Pythonic calls
* Only handle raw data, you define your own models

Features:

* Request signing
* Automatic retries
* Full REST endpoint coverage
* Full test coverage

Dependencies:

* httplib2
* simplejson (optional)

## Usage

### Instantiating a client [authentication docs](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-APIKey)
    client = singleplatform.SinglePlatform('YOUR_CLIENT_ID', 'YOUR_SIGNING_KEY', 'YOUR_API_KEY')


### Examples

#### Restaurants
##### [Search for restaurants](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantssearch)
    client.restaurants.search({'q': 'New York, NY'})
##### [Get details about a restaurant](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATION)
    client.restaurants.location('haru-7')
##### [Get a restaurant's menu](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATIONmenu)
    client.restaurants.menu('haru-7')
##### [Get a restaurant's short menu](https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATIONshortmenu)
    client.restaurants.shortmenu('haru-7')


## Improvements
What else would you like this library to do? Let me know. Feel free to send pull requests for any improvements you make.

### Todo
* Bring in new endpoints as they emerge

## License
MIT License. See LICENSE
Copyright (c) 2012 Mike Lewis
