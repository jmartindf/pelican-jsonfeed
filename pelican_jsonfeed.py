#!/usr/bin/env python
# encoding: utf-8

"""
JSON Feed Generator for Pelican.
"""

from __future__ import unicode_literals


import six
from jinja2 import Markup
from pelican import signals
from pelican.writers import Writer
from pelican.generators import Generator
from pelican.utils import set_date_tzinfo
from feedgenerator import SyndicationFeed, get_tag_uri
from feedgenerator.django.utils.feedgenerator import rfc2822_date, rfc3339_date
from feedgenerator.django.utils.encoding import force_text, iri_to_uri
from collections import OrderedDict
import json

class JSONFeed(SyndicationFeed):
	content_type = 'application/json; charset=utf-8'

	"""Helper class which generates the JSON based in the global settings"""
	def __init__(self, *args, **kwargs):
		"""Nice method docstring goes here"""
		super(JSONFeed, self).__init__(*args, **kwargs)

	def set_settings(self, settings):
		"""Helper function which just receives the podcast settings.
		:param settings: A dictionary with all the site settings.
		"""
		self.settings = settings
		if 'WEBSUB_HUB' in self.settings and self.settings['WEBSUB_HUB'] != "":
			self.feed["hub"] = self.settings['WEBSUB_HUB']

	def add_root_elements(self, handler):
		pass

	def add_item(self, title, link, description, author_email=None,
				 author_name=None, author_link=None, pubdate=None, comments=None,
				 unique_id=None, unique_id_is_permalink=None, enclosure=None,
				 categories=(), item_copyright=None, ttl=None, updateddate=None,
				 enclosures=None, external_url=None, **kwargs):
		"""
		Adds an item to the feed. All args are expected to be Python Unicode
		objects except pubdate and updateddate, which are datetime.datetime
		objects, and enclosures, which is an iterable of instances of the
		Enclosure class.
		"""
		def to_unicode(s):
			return force_text(s, strings_only=True)
		if categories:
			categories = [to_unicode(c) for c in categories]
		if ttl is not None:
			# Force ints to unicode
			ttl = force_text(ttl)
		enclosures = [] if enclosures is None else enclosures
		item = OrderedDict()
		item['title'] = to_unicode(title)
		if pubdate:
			item['date_published'] = rfc3339_date(pubdate)
		if updateddate:
			item['dated_modified'] = rfc3339_date(updateddate)
		#if unique_id:
		#	item["id"] = to_unicode(unique_id)
		item["id"] = iri_to_uri(link)
		item['url'] = iri_to_uri(link)
		if external_url:
			item['external_url'] = external_url
		author = {}
		has_author = False
		if author_email:
			author["url"] = "mailto:%s" % to_unicode(author_email)
			has_author = True
		if author_name:
			author["name"] = to_unicode(author_name)
			has_author = True
		if author_link:
			author["url"] = iri_to_uri(author_link)
			has_author = True
		if has_author:
			item["author"] = author
		item['content_html'] = to_unicode(description)

		if categories:
			item["tags"] = categories

		item.update(kwargs)
		self.items.append(item)

	def write(self, outfile, encoding):
		handler = OrderedDict()
		json_items = []

		handler["version"] = "https://jsonfeed.org/version/1"
		handler["title"] = self.feed["title"]
		if 'SITESUBTITLE' in self.settings:
			handler['description'] = self.settings['SITESUBTITLE']
		handler["home_page_url"] = self.feed["link"]
		handler["feed_url"] = self.feed["feed_url"]
		if self.feed["description"] != "":
			handler["description"] = self.feed["description"]
		author = {}
		has_author = False
		if 'AUTHOR_EMAIL' in self.settings:
			author["url"] = "mailto:%s" % to_unicode(self.settings['AUTHOR_EMAIL'])
			has_author = True
		if self.feed["author_name"] is not None:
			author["name"] = self.feed["author_name"]
			has_author = True
		elif 'AUTHOR' in self.settings:
			author['name'] = self.settings['AUTHOR']
			has_author = True
		if self.feed["author_link"] is not None:
			author["url"] = self.feed["author_link"]
			has_author = True
		elif 'AUTHOR_LINK' in self.settings:
			author['url'] = self.settings['AUTHOR_LINK']
			has_author = True
		if has_author:
			handler["author"] = author

		if "hub" in self.feed:
			handler["hubs"] = [{'type': 'WebSub','url':self.feed["hub"]}]

		handler["items"] = self.items
		json.dump(handler,outfile,indent=2)

class JSONFeedWriter(Writer):
	"""Writer class for our JSON Feed.  This class is responsible for
	invoking the RssPuSHFeed or Atom1PuSHFeed and writing the feed itself
	(using it's superclass methods)."""

	def __init__(self, *args, **kwargs):
		"""Class initializer"""
		super(JSONFeedWriter, self).__init__(*args, **kwargs)

	def _create_new_feed(self, *args):
		"""Helper function (called by the super class) which will initialize
		the Feed object."""
		if len(args) == 2:
			# we are on pelican <2.7
			feed_type, context = args
		elif len(args) == 3:
			# we are on Pelican >=2.7
			feed_type, feed_title, context = args
		else:
			# this is not expected, let's provide a useful message
			raise Exception(
				'The Writer._create_new_feed signature has changed, check the '
				'current Pelican source for the updated signature'
			)
		feed_class = JSONFeed

		sitename = Markup(context['SITENAME']).striptags()
		feed = feed_class(
			title=sitename,
			link=(self.site_url + '/'),
			feed_url=self.feed_url,
			description=context.get('SITESUBTITLE', ''))
		feed.set_settings(self.settings)
		return feed

	def _add_item_to_the_feed(self, feed, item):
		"""Performs an 'in-place' update of existing 'published' articles
		in ``feed`` by creating a new entry using the contents from the
		``item`` being passed.
		This method is invoked by pelican's core.

		:param feed: A Feed instance.
		:param item: An article (pelican's Article object).

		"""
		title = Markup(item.title).striptags()
		link = '%s/%s' % (self.site_url, item.url)
		appendContent = ""
		appendTitle = ""

		# :FIXME: Need to handle the link attribute, so that it can be added
		# as an external_url to the JSON feed
		#if hasattr(item,"link"):
		#	appendContent = '<p><a href="%s">%s</a></p>' % (link, self.settings.get('LINK_BLOG_PERMALINK_GLYPH','&infin;'))
		#	appendTitle = self.settings.get('LINK_BLOG_APPEND_TITLE','')
		#	link = item.link

		feed.add_item(
			title=title + appendTitle,
			link=link,
			unique_id=get_tag_uri(link, item.date),
			description=item.get_content(self.site_url) + appendContent,
			categories=item.tags if hasattr(item, 'tags') else None,
			author_name=getattr(item, 'author', ''),
			pubdate=set_date_tzinfo(
				item.modified if hasattr(item, 'modified') else item.date,
				self.settings.get('TIMEZONE', None)
			),
			external_url=item.link if hasattr(item,'link') else None,
		)


class JSONFeedGenerator(Generator):
	"""Generates content by inspecting all articles and invokes the
	JSONFeedWriter object, which will write the JSON Feed."""

	def __init__(self, *args, **kwargs):
		"""Starts a brand new feed generator."""
		super(JSONFeedGenerator, self).__init__(*args, **kwargs)
		# Initialize the number of posts and where to save the feed.
		self.posts = []

	def generate_context(self):
		"""Looks for all 'published' articles and add them to the posts
		list."""
		self.context['SITEURL'] = self.settings.get('SITEURL')
		self.context['FEED_DOMAIN'] = self.settings.get('FEED_DOMAIN')
		for article in self.context['articles']:
			if (article.status.lower()) == "published":
				self.posts.append(article)

	def generate_output(self, writer):
		"""Write out the link feed to a file.

		:param writer: A ``Pelican Writer`` instance.
		"""
		writer = JSONFeedWriter(self.output_path, self.settings)
		if self.settings.get('FEED_JSON'):
			writer.write_feed(self.posts, self.context, self.settings.get('FEED_JSON'), feed_type="json")

def get_generators(generators):
	"""Module function invoked by the signal 'get_generators'."""
	return JSONFeedGenerator


def register():
	"""Registers the module function `get_generators`."""
	signals.get_generators.connect(get_generators)
