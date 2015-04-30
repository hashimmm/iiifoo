@discovery
Feature: Provide sitemap for crawlers.
    Allow search engine crawlers to discover manifest, image and application URLs
    For this, a sitemap or a sitemap index linking to sitemaps should be provided

    Scenario: Providing a sitemap index
        Given some defined discoverable source types
         When the sitemap index is requested
         Then a valid sitemap index is returned
          And the response status is 200
          And there must be one sitemap per discoverable source type

    @wip
    Scenario: Sitemaps are requested.
        Given some defined source types
         When a sitemap is requested
         Then a valid sitemap is returned
