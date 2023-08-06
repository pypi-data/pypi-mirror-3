rss2rest
========

- Configure your feeds in the `settings` file
- Turns RSS feeds into a RESTful API with the use of TastyPie and Feedparser (perfect for use with `backbone.js`)
- Map feeds to Django models, few convenienve models are provided (see below)
- Write your own mdels representing a feed item, you just need to provide a mapping from feed nodes to model fields
- Harvest feeds using `./manage.py syncdb` command
- Access your feeds direct via tastypie API resource

![](https://secure.travis-ci.org/gump/rss2rest.png "Travis CI build status")

Installation
============

Install via PIP:

    $ pip install django-rss2rest


Add to your `INSTALLED_APPS` the following:

    INSTALLED_APPS = [
        ...,
        'tastypie',
        'rss2rest',
    ]

Define your feeds:

    RSS2REST_FEEDS = [
        {'feed': 'http://feedurl/',
         'model': 'rss2rest.FeedItem'},
    ]

Add RESTful routing to your `urls.py`:

    from rss2rest.api import FeedItemResource
    feed_item_resource = FeedItemResource()
    urlpatterns += patterns('rss2rest',
        (r'^api/', include(feed_item_resource.urls)),
    )

Usage
=====

Synchronise Feeds:

    ./manage.py syncrss2rest

Consume feeds go to:

    http://127.0.0.1/rss2rest/api/<resource_name>


Models for your feeds
=====================

In order for the feed to be exposed as a RESTful resource the feed must be mapped to a django model.
`rss2rest` provides a few pre-defined models that fit some typical scenarios.


**Generic feed item models:**

* `FeedItem` - generic feed item
* `VimeoFeedItem` - maps well to Vimeo Likes RSS feed
* `FlickrFeedItem` - maps well to Flickr Likes RSS feed


**Writing your own feed item model:**

* Create your own model for the feed to provide custom mapping, etc
* Simply extend the abstract `AbstractFeedItem` class present in the `rss2rest.models` file.
* Put `MAPPING` dictionary as a class property and you're ready to go
* Make sure you put your new model class name (as string in the format of `app.ModelName`) into the `RSS2REST_FEEDS`
  setting
* If your model is pretty generic and maps to a public feed - make sure you submit it as a pull request with
  accompanying tests to be included in the `rss2rest`


**Generic tasty pie resources**

* `FeedItemResource` - resource name: `feed_item`
* `FlickrItemResource` - resource name: `flickr`
* `VimeoItemResource` - resource name: `vimeo`

**Custom resources**

* You can build your custom resource as per [Tastypie's documentation](http://django-tastypie.readthedocs.org/en/latest/index.html)

Contribute
==========

Set up in development mode:

    $ git clone git://github.com/gump/rss2rest.git
    $ cd rss2rest
    $ mkvirtualenv rss2rest
    $ python setup.py develop
    $ cd sandbox/
    $ cp local_settings_sample.py local_settings.py
    $ ./manage.py syncdb
    $ ./manage.py test rss2rest

Planned development
===================

* More tests for all types of feeds
* More generic feed item models to cater for other common use cases
* `published` flag on abstract model to drive presence in the RESTful API (configurable with publish/unpublish flag
  using django admin panel); way to define default behaviour using a setting
* Defining your feeds in the database

