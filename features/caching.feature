@utils
@redis
Feature: Caching decorator.
    Some time consuming operations may be cached
    to reduce the delay in responding to a user's
    requests.

    Scenario: Sitemaps are requested.
        Given a cached method that returns current time
         When it is called twice
         Then the same time is returned
