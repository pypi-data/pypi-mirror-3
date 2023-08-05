#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.gis.geos import Point
from base import BaseScraper, ScraperBroken

class SkipRecord(Exception):
    "Exception that signifies a detail record should be skipped over."
    pass

class StopScraping(Exception):
    "Exception that signifies scraping should stop."
    pass

class ListDetailScraper(BaseScraper):
    """
    A screen-scraper optimized for list-detail types of sites.

    A list-detail site is a site that displays a list of records, which might
    be paginated. Each record might have its own page -- a "detail" page -- or
    the list page might display all available information for that record.

    To use this class, subclass it and implement the following:

        * list_pages()
        * Either parse_list() or parse_list_re
        * existing_record()
        * save()

    If the scraped site does not have detail pages, implement the following:

        * has_detail = False

    If the scraped site has detail pages, implement the following:

        * detail_required()
        * get_detail()
        * Either parse_detail() or parse_detail_re

    These are additional, optional hooks:

        * clean_list_record()
        * clean_detail_record()
    """

    ################################
    # MAIN METHODS FOR OUTSIDE USE #
    ################################

    def display_data(self):
        """
        Retrieves all pages, parses them and prints the data as Python
        dictionaries to standard output.

        This is mainly useful for debugging.
        """
        from pprint import pprint
        for d in self.raw_data():
            pprint(d)

    def raw_data(self):
        """
        Iterator that yields current raw data for this scraper.
        Works like update() but doesn't save anything.

        Each record is represented as a {'list', 'detail'} dictionary,
        where `list` is the clean list record and `detail` is the clean
        detail record.
        """
        for page in self.list_pages():
            try:
                for data in self._raw_data(page):
                    yield data
            except StopScraping:
                break

    def _raw_data(self, page):
        for list_record in self.parse_list(page):
            try:
                list_record = self.clean_list_record(list_record)
            except SkipRecord:
                continue
            if self.has_detail:
                try:
                    page = self.get_detail(list_record)
                    detail_record = self.parse_detail(page, list_record)
                    detail_record = self.clean_detail_record(detail_record)
                except SkipRecord:
                    continue
            else:
                detail_record = None
            yield {'list': list_record, 'detail': detail_record}

    def xml_data(self):
        """
        Iterator that yields current raw data for this scraper, as
        serialized XML.
        """
        from xml.sax.saxutils import escape
        yield u'<data>'
        for d in self.raw_data():
            yield u'<object>'
            for datatype in ('list', 'detail'):
                for k, v in d[datatype].items():
                    if not isinstance(v, basestring):
                        v = str(v)
                    yield u'  <att name="%s-%s">%s</att>' % (datatype[0], k, escape(v))
            yield u'</object>'
        yield u'</data>'

    def update(self):
        """
        The main scraping method. This retrieves all pages, parses
        them, calls cleaning hooks, and saves the data.

        Subclasses should not have to override this method.
        """
        self.num_skipped = 0

        self.logger.info("update() in %s started" % str(self.__class__))
        try:
            for page in self.list_pages():
                self.update_from_string(page)
        except StopScraping:
            pass
        finally:
            self.logger.info("update() finished")

    def update_from_string(self, page):
        """
        Runs the equivalent of update() on the given string.

        This is useful if you've got cached versions of content that
        you want to parse; also, update() calls it under the hood.

        Subclasses should not have to override this method.
        """
        for list_record in self.parse_list(page):
            try:
                list_record = self.clean_list_record(list_record)
            except SkipRecord, e:
                self.num_skipped += 1
                self.logger.debug("Skipping list record for %r: %s " % (list_record, e))
                continue
            except ScraperBroken, e:
                # Re-raise the ScraperBroken with some addtional helpful information.
                raise ScraperBroken('%r -- %s' % (list_record, e))
            self.logger.debug("Clean list record: %r" % list_record)

            old_record = self.existing_record(list_record)
            self.logger.debug("Existing record: %r" % old_record)

            if self.has_detail and self.detail_required(list_record, old_record):
                self.logger.debug("Detail page is required")
                try:
                    page = self.get_detail(list_record)
                    detail_record = self.parse_detail(page, list_record)
                    detail_record = self.clean_detail_record(detail_record)
                except SkipRecord, e:
                    self.num_skipped += 1
                    self.logger.debug("Skipping detail record for list %r: %s" % (list_record, e))
                    continue
                except ScraperBroken, e:
                    # Re-raise the ScraperBroken with some additional helpful information.
                    raise ScraperBroken('%r -- %s' % (list_record, e))
                self.logger.debug("Clean detail record: %r" % detail_record)
            else:
                self.logger.debug("Detail page is not required")
                detail_record = None

            self.save(old_record, list_record, detail_record)

    def update_from_dir(self, dirname):
        """
        For scrapers with has_detail=False, runs the equivalent of update() on
        every file in the given directory, in sorted order.

        This is useful if you've got cached versions of HTML that you want to
        parse.

        Subclasses should not have to override this method.
        """
        import os
        filenames = os.listdir(dirname)
        filenames.sort()
        for filename in filenames:
            full_name = os.path.join(dirname, filename)
            self.logger.info("Reading from file %s" % full_name)
            page = open(full_name).read()
            self.update_from_string(page)

    ####################################################
    # INTERNAL METHODS THAT SUBCLASSES SHOULD OVERRIDE #
    ####################################################

    parse_list_re = None
    parse_detail_re = None
    has_detail = True

    def list_pages(self):
        """
        Iterator that yields list pages, as strings.

        Usually, this will only yield a single string, but it might yield
        multiple pages if the list is paginated.

        Subclasses need to override this.
        """
        raise NotImplementedError()

    def parse_list(self, page):
        """
        Given the full HTML (or XML, or whatever) of a list page,
        yields a dictionary of data for each record on the page.

        You must either override this method, or define a parse_list_re
        attribute. If you define a parse_list_re attribute, it should be set
        to a compiled regular-expression that finds all the records on a list
        page and uses named groups.
        """
        if self.parse_list_re is not None:
            count = 0
            for record in self.parse_list_re.finditer(page):
                yield record.groupdict()
                count += 1
            if count == 0:
                self.logger.info('%s.parse_list_re found NO records', self.__class__.__name__)
        else:
            raise NotImplementedError()

    def call_cleaners(self, record):
        """
        Given a dictionary returned by parse_list() or parse_detail(),
        calls any method defined whose name match a pattern based on a
        key in dictionary. The value at the key and the entire record
        are passed in as positional arguments. The patten is
        "_clean_KEY".

        For example, if the record contains a key "restaurant",
        call_cleaners() will call a method _clean_restaurant() if it
        exists.

        The _clean_KEY() callable should return a value that will
        replace the value at the key in the dictionary.

        It is up to the subclass's clean_list_record() and
        clean_detail_record() to call call_cleaners().
        """
        for key, value in record.items():
            meth_name = "_clean_%s" % key
            if hasattr(self, meth_name):
                method = getattr(self, meth_name)
                if callable(method):
                    record[key] = method(value, record)
        return record

    def clean_list_record(self, record):
        """
        Given a dictionary as returned by parse_list(), performs any
        necessary cleanup of the data and returns a dictionary.

        For example, this could convert date strings to datetime objects.
        """
        return record

    def existing_record(self, record):
        """
        Given a cleaned list record as returned by clean_list_record(), returns
        the existing record from the data store, if it exists.

        If an existing record doesn't exist, this should return None.

        Subclasses must override this.
        """
        raise NotImplementedError()

    def detail_required(self, list_record, old_record):
        """
        Given a cleaned list record and the old record (which might be None),
        returns True if the scraper should download the detail page for this
        record.

        If has_detail is True, subclasses must override this.
        """
        raise NotImplementedError()

    def get_detail(self, record):
        """
        Given a cleaned list record as returned by clean_list_record, retrieves
        and returns the HTML for the record's detail page.

        If has_detail is True, subclasses must override this.
        """
        raise NotImplementedError()

    def parse_detail(self, page, list_record):
        """
        Given the full HTML of a detail page, returns a dictionary of data for
        the record represented on that page.

        If has_detail is True, you must either implement this method
        or define a parse_detail_re attribute. If you define a
        parse_detail_re attribute, it should be set to a compiled
        regular-expression that parses the record on a detail page and
        uses named groups.
        """
        if self.parse_detail_re is not None:
            m = self.parse_detail_re.search(page)
            if m:
                self.logger.debug('Got a match for parse_detail_re')
                return m.groupdict()
            self.logger.debug('Did not get a match for parse_detail_re')
            return {}
        else:
            raise NotImplementedError()

    def clean_detail_record(self, record):
        """
        Given a dictionary as returned by parse_detail(), performs any
        necessary cleanup of the data and returns a dictionary.

        For example, this could convert date strings to datetime objects.

        Overriding is optional; the default does nothing.
        """
        return record

    def get_location(self, list_record):
        """Optional convenience method for extracting a geometry from
        a record.

        If a subclass implements this, it should return either an
        instance of django.contrib.gis.geos.geometry.GEOSGeometry (or
        a subclass), or None if no geometries are found.

        Implementing this is optional; scrapers that define it must
        call it explicitly.
        """
        raise NotImplementedError()

    def save(self, old_record, list_record, detail_record):
        """
        Saves the given record to storage.
        Subclasses must override this.

        list_record and detail_record are both dictionaries representing the
        data from the list page and detail page, respectively. If the scraped
        site does not have detail pages, detail_record will be None.

        old_record is the existing record, as returned by existing_record(). It
        will be None if there is no existing record.

        Subclasses are responsible for actually saving the data,
        or choosing not to save (eg. if old_record exists).
        """
        raise NotImplementedError()

class RssListDetailScraper(ListDetailScraper):
    """
    A ListDetailScraper for sites whose lists are RSS feeds.

    Subclasses should not have to implement parse_list() or get_detail().
    """
    def parse_list(self, page):
        # The page is an RSS feed, so use feedparser to parse it.
        import feedparser
        self.logger.debug("Parsing RSS feed with feedparser")
        feed = feedparser.parse(page)
        if not len(feed['entries']):
            # We might be parsing a paginated feed, and typically
            # there's no way to know how many pages there are, except
            # to keep incrementing the page number and stop when you
            # hit an empty page.
            raise StopScraping("No more entries to scrape")
        for entry in feed['entries']:
            yield entry

    def get_detail(self, record):
        # Assume that the detail page is accessible via the <link> for this
        # entry.
        return self.fetch_data(record['link'])

    def get_location(self, record):
        """Try both flavors of georss and geo attributes, as well as
        some other common non-standard conventions.

        Locations with both lat = 0 and lon = 0 are assumed to be bad; we
        return None for those.

        This is not called automatically; if you want to use it, your
        scraper should do ``newsitem.location = self.get_location(record)``
        sometime prior to ``self.save()``.
        """
        # This tries to work around feedparser bugs where depending on
        # whether you get a loose or strict parser, you might or might
        # not see the namespace prefix on the attribute name.

        # TODO: support other georss geometry types as per
        # http://www.georss.org/simple ... so far only handles Point.

        # TODO: support xCal geometries
        # https://tools.ietf.org/html/rfc6321#section-3.4.1.2

        if 'gml_point' in record:
            # Looks like georss gml.
            lat, lon = record['gml_pos'].split()
        elif 'point' in record:
            # Unfortunately, with broken namespace handling, this
            # might be georss_simple or georss gml. Try both.
            if 'where' in record and 'pos' in record:
                # It's GML.
                lat, lon = record['pos'].split()
            else:
                lat, lon = record['point'].split()
        elif 'georss_point' in record:
            # It's georss simple.
            lat, lon = record['georss_point'].split()
        elif 'geo_lat' in record:
            # It's the rdf geo namespace.
            lat, lon = record['geo_lat'], record['geo_lon']
        elif 'lat' in record:
            if 'lon' in record:
                # It's geo with broken namespace handling.
                lat, lon = record['lat'], record['lon']
            elif 'lng' in record:
                # This is not a standard AFAIK, but I've seen it eg. in
                # seeclickfix issues json.
                lat, lon = record['lat'], record['lng']
        elif 'latitude' in record:
            # Another common non-standard convention.
            lat, lon = record['latitude'], record['longitude']
        else:
            self.logger.debug(
                "no known geometry types found in record %s"
                % record)
            return None
        lat, lon = float(lat), float(lon)
        if (lat, lon) == (0.0, 0.0):
            self.logger.warn("Ignoring location with bad coordinates (0, 0)")
            return None
        return Point(lon, lat)
