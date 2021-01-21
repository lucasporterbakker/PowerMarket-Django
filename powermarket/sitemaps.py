from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from apps.solar.models import ExampleAssessment


class StaticPagesSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return [
            'landing_page',
            'press',
            'company',
            'blog',
            'technology',
            'faq',
            'commercial_solar',
            'financing',
            'incentives',
            'solar_101',
        ]

    def location(self, item):
        return reverse(item)


class BlogPagesSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return [
            reverse('blog', kwargs={'slug': 'installing-home-solar-in-the-uk-part-1'}),
            reverse('blog', kwargs={'slug': 'installing-home-solar-in-the-uk-part-2'}),
            reverse('blog', kwargs={'slug': 'why-is-installing-solar-good-for-my-business'}),
            reverse('blog', kwargs={'slug': 'the-6-key-questions-about-solar-for-an-SME'}),
        ]

    def location(self, url):
        return url


class DynamicPagesSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return [
            reverse('markets', kwargs={'country': 'uk'}),
            reverse('markets', kwargs={'country': 'united_states'}),
            reverse('markets', kwargs={'country': 'china'}),
            reverse('markets', kwargs={'country': 'germany'}),
        ]

    def location(self, url):
        return url


class AllauthSitemap(Sitemap):
    priority = 0.3
    changefreq = 'weekly'

    def items(self):
        return [
            'account_signup',
            'account_login',
        ]

    def location(self, item):
        return reverse(item)


class SupplierAppSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return [
            'supplier:supplier_info',
            'supplier:supplier_contact_success',
        ]

    def location(self, item):
        return reverse(item)


class SolarAppSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        example_urls = []
        for example in ExampleAssessment.objects.all():
            example_urls.append(reverse('solar:example_assessment', kwargs={'slug': example.slug}))
        return [
            reverse('solar:area'),
            reverse('solar:no_data'),
            reverse('solar:thank_you'),
        ] + example_urls

    def location(self, url):
        return url


class SupportAppSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'support:support',
            'support:call_request_success',
        ]

    def location(self, item):
        return reverse(item)
