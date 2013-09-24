from django.contrib.sitemaps import Sitemap

# Return a set of items corresponding to the static pages in the site which
# can't be enumerated using the normal model-based sitemap framework.
class StaticSitemap (Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items (self):
        return [
            '/',
            '/member/',
            '/updates/',
            '/information/',
            '/promo/',
            '/news/',
            '/feedback/',
            '/rss/',
            '/atom/',
            '/quotes/',
            '/minutes/',
            '/events/',
            '/events/photos/',
            '/wus/',
            '/wus/djinfo/',
            '/wus/dj/',
            '/wus/date/',
            '/gallery/',
            '/gallery/members/',
            '/stash/',
        ]

    def location (self, loc):
        return loc
