# oosapy
# Copyright 11870.com
# See LICENSE for details.

from xml import etree

from datetime import datetime
from gdata import atom

def _get_extensions(cls, entry, names):
    def extract_value(string):
        if string is None:
            return None
        elif string == "true":
            return True
        elif string == "false":
            return False
        elif string.isdigit():
            return int(string)
        else:
            try:
                return float(string)
            except:
                return string

    for name in names:
        if len(entry.FindExtensions(name)) == 1:
            value = entry.FindExtensions(name)[0].text
            if name not in ["slug", "telephone"]:
                value = extract_value(value)
            setattr(cls, name.replace("-", "_"), value)

def _add_extension(entry, namespace, tag, text="", attributes=None):
    if attributes == None:
        attributes = {}
    ext = atom.ExtensionElement(namespace=namespace, tag=tag, text=text,
                                attributes=attributes)
    entry.extension_elements.append(ext)

def _get_link(entry, rel):
    res = filter(lambda l: l.rel == rel, entry.link)
    if len(res) == 1:
        return res[0].href

def _get_position(entry):
    w = entry.FindExtensions("where")
    if len(w) == 1:
        pos = w[0].FindChildren("Point")[0].FindChildren("pos")[0].text.split()
        return map(float, pos)

def _get_rating(entry):
    ext = entry.FindExtensions("rating")
    if len(ext) == 1:
        return int(ext[0].attributes["value"])
    return 0

def _get_categories(entry, scheme):
    cats = filter(lambda c: c.scheme.startswith(scheme), entry.category)
    return map(lambda c: c.term, cats)

def _build_dummy_entry():
    entry = atom.Entry()

    entry.id = atom.Id("http://11870.com")
    entry.title = atom.Title()
    entry.content = atom.Content()

    entry.author = atom.Author(name=atom.Name("11870.com"))
    entry.updated = atom.Updated(text="2000-01-01T00:00:00.000Z")

    return entry

def _parse_date(str_date):
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%fZ")


class ResultSet():
    """Class almost equivalent to a list which holds the API results."""

    def _load_feed(self, feed):
        # get the entries and store them
        for entry in feed.entry:
            self._list.append(self._cls.load_entry(self._api, entry))

        # get pagination parameters
        self.total_results = int( feed.FindExtensions("totalResults")[0].text )
        self.items_per_page = int( feed.FindExtensions("itemsPerPage")[0].text )
        if feed.GetNextLink() != None:
            self.next = feed.GetNextLink().href

    def __init__(self, cls, api, feed):
        self._cls = cls
        self._api = api
        self._list = []

        self._load_feed(feed)

    def append(self, object):
        self._list.append(object)

    def __len__(self):
        return self.total_results

    def __getitem__(self, item):
        if isinstance(item, slice):
            l = []
            start, stop, step = item.indices(len(self))
            for i in xrange(start, stop, step):
                l.append(self.__getitem__(i))
            return l

        elif isinstance(item, int):
            if item >= self.total_results:
                raise IndexError("list index out of range")
            while item >= len(self._list):
                response = self._api.auth_handler.get_response(self.next)
                feed = atom.FeedFromString(response[1])
                self._load_feed(feed)

            return self._list[item]

        else:
            raise TypeError("type not supported")


class Model(object):
    """Common class to all the models."""

    OOS_NS = "http://11870.com/api/oos"
    TRUSTED_SCHEME = "http://api.11870.com/api/v2/trusted"
    PRIVACY_SCHEME = "http://api.11870.com/api/v2/privacy"
    TAGS_SCHEME = "http://api.11870.com/api/v2/tags"
    LISTS_SCHEME = "http://api.11870.com/api/v2/lists"
    CATEGORIES_SCHEME = "http://api.11870.com/api/v2/categories"
    ATTRIBUTES_SCHEME = "http://api.11870.com/api/v2/attributes"

    def __init__(self, api=None):
        self._api = api

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        raise NotImplementedError

    @classmethod
    def parse(cls, api, atom_string):
        """Parse an atom string returning one single object or a ResultSet."""
        entry = atom.EntryFromString(atom_string)
        if entry != None:
            return cls.load_entry(api, entry)

        feed = atom.FeedFromString(atom_string)
        if feed != None:
            return ResultSet(cls, api, feed)

    def to_atom(self):
        """Return the object as an atom string."""
        raise NotImplementedError


class User(Model):
    """User class."""

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        user = cls(api)

        setattr(user, "nick", entry.title.text)
        setattr(user, "avatar",
                entry.author[0].FindExtensions("avatar")[0].text)
        setattr(user, "about", entry.content.text)
        setattr(user, "link", entry.GetAlternateLink().href)

        _get_extensions(user, entry, ["slug", "name", "surname", "telephone",
                                      "mail", "nomails", "nonewsletter",
                                      "onlycontacts", "nobulletin",
                                      "nomailonlikes", "nomailonmediacomments",
                                      "nomailoncommentsonreview",
                                      "nosuggestedcontacts"])

        return user

    @classmethod
    def load_author(cls, api, author):
        """Create an object starting with an author element."""
        user = cls(api)

        setattr(user, "nick", author.name.text)
        setattr(user, "avatar", author.FindExtensions("avatar")[0].text)

        slug = None
        if len(author.FindExtensions("slug")) == 1:
            slug = author.FindExtensions("slug")[0].text
        setattr(user, "slug", slug)

        return user

    def to_atom(self):
        """Return the object as an atom string."""
        entry = _build_dummy_entry()

        # Nick and about
        entry.title = atom.Title(text=self.nick)
        entry.content = atom.Content(text=self.about)

        # Personal data
        _add_extension(entry, self.OOS_NS, "name", self.name)
        _add_extension(entry, self.OOS_NS, "surname", self.surname)
        _add_extension(entry, self.OOS_NS, "telephone", str(self.telephone))
        _add_extension(entry, self.OOS_NS, "mail", self.mail)

        # Mail preferences
        _add_extension(entry, self.OOS_NS, "nomails",
                       "true" if self.nomails else "false")
        _add_extension(entry, self.OOS_NS, "nonewsletter",
                       "true" if self.nonewsletter else "false")
        _add_extension(entry, self.OOS_NS, "onlycontacts",
                       "true" if self.onlycontacts else "false")
        _add_extension(entry, self.OOS_NS, "nobulletin",
                       "true" if self.nobulletin else "false")
        _add_extension(entry, self.OOS_NS, "nomailonlikes",
                       "true" if self.nomailonlikes else "false")
        _add_extension(entry, self.OOS_NS, "nomailonmediacomments",
                       "true" if self.nomailonmediacomments else "false")
        _add_extension(entry, self.OOS_NS, "nomailoncommentsonreview",
                       "true" if self.nomailoncommentsonreview else "false")
        _add_extension(entry, self.OOS_NS, "nosuggestedcontacts",
                       "true" if self.nosuggestedcontacts else "false")

        return entry.ToString()

    def is_company(self):
        """Check if the user is a company."""
        return self.slug is None

    def update(self):
        """Update the user."""
        if self.is_company():
            return False
        else:
            return self._api.update_user(self)

    def get_avatar(self):
        """Return the user avatar in a file."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_avatar(self)

    def update_avatar(self, avatar_file, content_type="image/jpeg"):
        """Update the user avatar."""
        if self.is_company():
            return False
        else:
            return self._api.update_user_avatar(self, avatar_file, content_type)

    def get_reviews(self):
        """Return the reviews of the user with its service."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_reviews(self)

    def get_contacts(self):
        """Return the contacts that the user is following."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_contacts(self)

    def get_activity(self):
        """Return the user activity."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_activity(self, social=False)

    def get_social_activity(self):
        """Return the user and his contacts activity."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_activity(self, social=True)

    def get_check_ins(self):
        """Return the user check-ins."""
        if self.is_company():
            return False
        else:
            return self._api.get_user_check_ins(self)

    def check_in(self, service, latitude, longitude):
        """Make a new check-in for the user in the given place."""
        if self.is_company():
            return False
        else:
            return self._api.make_check_in(self, service, latitude, longitude)

    def add_contact(self, guru, nick=None, trusted=False):
        """Make a new contact."""
        contact = Contact.create_object(self._api, self, guru, nick, trusted)
        return self._api.create_contact(contact)

    def add_review(self, service, title="", content="", rating=0,
                   privacy="public", tags=[], lists=[]):
        """Create a new review."""
        review = ServiceReview.create_object(self._api, self, service, title,
                                             content, rating, privacy, tags,
                                             lists)
        return self._api.create_review(review)

    def discover_service(self, name, useraddress, locality_name, country_code,
                         telephone=None, url=None, title="", content="",
                         rating=0, privacy="public", tags=[], lists=[]):
        """Discover a place. Create the service and associate the review."""

        service = Service.create_object(self._api, name, useraddress,
                                        locality_name, country_code,
                                        telephone, url)

        review = ServiceReview.create_object(self._api, self, service, title,
                                             content, rating, privacy, tags,
                                             lists)

        return self._api.create_review(review)


class Contact(Model):
    """Contact relationship class."""

    @classmethod
    def create_object(cls, api, fan, guru, nick=None, trusted=False):
        """Create an object without atom string or entries."""
        contact = cls(api)

        setattr(contact, "fan", fan)
        setattr(contact, "guru", guru)
        if nick != None:
            contact.guru.nick = nick
        setattr(contact, "trusted", trusted)
        setattr(contact, "updated", datetime.now())

        return contact

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        contact = cls(api)

        setattr(contact, "updated", _parse_date(entry.updated.text))

        trusted = _get_categories(entry, cls.TRUSTED_SCHEME)
        if len(trusted) == 1:
            setattr(contact, "trusted", trusted[0])

        fan = User.load_author(api, entry.author[0])
        setattr(contact, "fan", fan)

        guru = User()
        setattr(guru, "nick", entry.title.text)
        setattr(guru, "link", entry.GetAlternateLink().href)
        _get_extensions(guru, entry, ["slug", "avatar"])
        setattr(contact, "guru", guru)

        return contact

    def to_atom(self):
        """Return the object as an atom string."""
        entry = _build_dummy_entry()

        # Nick and slug
        entry.title = atom.Title(text=self.guru.nick)
        _add_extension(entry, self.OOS_NS, "slug", self.guru.slug)

        # trusted
        if self.trusted != None:
            trusted_str = "true" if self.trusted else "false"
            cat = atom.Category(scheme=self.TRUSTED_SCHEME, term=trusted_str)
            entry.category.append(cat)

        return entry.ToString()

    def update(self):
        """Update the contact relationship."""
        return self._api.update_contact(self)

    def delete(self):
        """Delete the contact relationship."""
        return self._api.delete_contact(self)


class CheckIn(Model):
    """Check-in class."""

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        check_in = cls(api)

        setattr(check_in, "when", _parse_date(entry.updated.text))

        user = User.load_author(api, entry.author[0])
        setattr(user, "link", _get_link(entry, "alternate"))
        setattr(check_in, "user", user)

        service = Service.load_entry(api, entry);
        setattr(check_in, "service", service)

        return check_in


class Activity(Model):
    """Activity class. The object parameter depends on the activity type."""

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        activity = cls(api)

        # activity general data
        setattr(activity, "when", _parse_date(entry.updated.text))
        setattr(activity, "description", entry.title.text)
        verb = entry.FindExtensions("verb")[0].text.split("/")[-1]
        setattr(activity, "action", verb)

        # actor data
        entry_actor = entry.FindExtensions("actor")[0]
        actor = User()
        setattr(actor, "nick", entry_actor.FindChildren("title")[0].text)
        setattr(actor, "slug", entry_actor.FindChildren("slug")[0].text)
        setattr(actor, "avatar", entry_actor.FindChildren("avatar")[0].text)
        links = entry_actor.FindChildren("link")
        link_ext = filter(lambda l: l.attributes['rel'] == "alternate", links)
        setattr(actor, "link", link_ext[0].attributes['href'])
        setattr(activity, "actor", actor)

        # object data
        entry_object = entry.FindExtensions("object")[0]
        object_type = entry_object.FindChildren("object-type")[0].text
        object_type = object_type.split("/")[-1]
        setattr(activity, "object_type", object_type)

        object = None
        if object_type == "person":
            object = User()
            setattr(object, "nick", entry_object.FindChildren("title")[0].text)
            setattr(object, "slug", entry_object.FindChildren("slug")[0].text)
            setattr(object, "avatar",
                    entry_object.FindChildren("avatar")[0].text)
            links = entry_object.FindChildren("link")
            link_ext = filter(lambda l: l.attributes['rel'] == "alternate",
                              links)
            setattr(object, "link", link_ext[0].attributes['href'])

        elif object_type == "place":
            object = Service()
            setattr(object, "name", entry_object.FindChildren("title")[0].text)
            links = entry_object.FindChildren("link")
            link_ext = filter(lambda l: l.attributes['rel'] == "alternate",
                              links)
            setattr(object, "link", link_ext[0].attributes['href'])

        elif object_type == "area":
            object = Area()
            setattr(object, "name", entry_object.FindChildren("title")[0].text)
            links = entry_object.FindChildren("link")
            link_ext = filter(lambda l: l.attributes['rel'] == "alternate",
                              links)
            setattr(object, "link", link_ext[0].attributes['href'])

        elif object_type in ("picture", "video"):
            object = Media()
            type = "image" if object_type == "picture" else "video"
            setattr(object, "type", type)
            setattr(object, "fnv", entry_object.FindChildren("fnv")[0].text)
            links = entry_object.FindChildren("link")
            link_ext = filter(lambda l: l.attributes['rel'] == "alternate",
                              links)
            setattr(object, "link", link_ext[0].attributes['href'])
            link_ext = filter(lambda l: l.attributes['rel'] == "media", links)
            setattr(object, "src", link_ext[0].attributes['href'])

        setattr(activity, "object", object)

        return activity


class Area():
    """Area class used in activities."""
    pass


class Service(Model):
    """Service/place class."""

    @classmethod
    def create_object(cls, api, name, useraddress, locality_name, country_code,
                      telephone=None, url=None):
        """Create an object without atom string or entries."""
        service = cls(api)

        setattr(service, "name", name)
        setattr(service, "useraddress", useraddress)
        setattr(service, "locality", locality_name)
        setattr(service, "country", country_code)
        setattr(service, "telephone", telephone)
        setattr(service, "url", url)

        return service

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        service = cls(api)

        # General info
        setattr(service, "name", entry.title.text)
        _get_extensions(service, entry, ["id", "slug", "useraddress",
                                         "reviews-counter", "saved-counter",
                                         "subdependentlocality",
                                         "dependentlocality", "locality",
                                         "subadministrativearea", "country",
                                         "url", "telephone"])

        # Position
        position = _get_position(entry)
        if position != None:
            lat = position[0]
            lon = position[1]
        else:
            lat = None
            lon = None
        setattr(service, "latitude", lat)
        setattr(service, "longitude", lon)

        # Service link
        link = _get_link(entry, "service")
        if link == None:
            link = entry.GetAlternateLink().href
        setattr(service, "link", link)

        # Categories and attributes
        setattr(service, "categories",
                _get_categories(entry, cls.CATEGORIES_SCHEME))
        setattr(service, "attributes",
                _get_categories(entry, cls.ATTRIBUTES_SCHEME))

        return service

    def get_reviews(self):
        """Return the reviews of a service."""
        return self._api.get_service_reviews(self)

    def get_check_ins(self):
        """Return the check-ins made in a place."""
        return self._api.get_service_check_ins(self)


class SearchedService(Service):
    """Service/place class with more data provided in the searching"""

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        service = Service.load_entry(api, entry)

        setattr(service, "snippet", entry.summary.text)
        setattr(service, "tags", _get_categories(entry, cls.TAGS_SCHEME))

        # Returned snapshots links
        snapshots = []
        links = filter(lambda l: l.rel == "media", entry.link)
        for link in links:
            snapshots.append(link.href)
        setattr(service, "snapshots", snapshots)

        # Saved by
        saved_by = []
        extensions = entry.FindExtensions("saved-by")
        if len(extensions) == 1:
            for child in extensions[0].children:
                user = User()
                setattr(user, "nick", child.FindChildren("nick")[0].text)
                setattr(user, "slug", child.FindChildren("slug")[0].text)
                setattr(user, "avatar", child.FindChildren("avatar")[0].text)
                saved_by.append(user)
        setattr(service, "saved_by", saved_by)

        return service


class ServiceReview(Model):
    """Review class. The review is made by one user about one service."""

    @classmethod
    def create_object(cls, api, user, service, title="", content="",
                      rating=0, privacy="public", tags=[], lists=[]):
        """Create an object without atom string or entries."""
        review = cls(api)

        setattr(review, "user", user)
        setattr(review, "service", service)
        setattr(review, "title", title)
        setattr(review, "content", content)
        setattr(review, "rating", rating)
        setattr(review, "privacy", privacy)
        setattr(review, "tags", tags)
        setattr(review, "lists", lists)
        setattr(review, "updated", datetime.now())

        return review

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        review = cls(api)

        setattr(review, "title",
                entry.summary.text if entry.summary != None else "")
        setattr(review, "content",
                entry.content.text if entry.content != None else "")
        setattr(review, "link", entry.GetAlternateLink().href)
        setattr(review, "rating", _get_rating(entry))
        setattr(review, "updated", _parse_date(entry.updated.text))

        privacy = _get_categories(entry, cls.PRIVACY_SCHEME)
        if len(privacy) == 1:
            setattr(review, "privacy", privacy[0])

        setattr(review, "tags", _get_categories(entry, cls.TAGS_SCHEME))
        setattr(review, "lists", _get_categories(entry, cls.LISTS_SCHEME))

        service = Service.load_entry(api, entry);
        setattr(review, "service", service)

        user = User.load_author(api, entry.author[0])
        setattr(review, "user", user)

        return review

    def to_atom(self):
        """Return the object as an atom string."""
        entry = _build_dummy_entry()

        ##### Review data #####
        # summary and content
        entry.summary = atom.Summary(text=self.title)
        entry.content = atom.Content(text=self.content)

        # rating
        _add_extension(entry, self.OOS_NS, "rating",
                       attributes={"value": str(self.rating)})

        # service id
        if self.service.__dict__.get("id") != None:
            _add_extension(entry, self.OOS_NS, "id", str(self.service.id))

        # privacy
        if self.__dict__.get("privacy") != None:
            cat = atom.Category(scheme=self.PRIVACY_SCHEME, term=self.privacy)
            entry.category.append(cat)

        # tags
        for tag in self.tags:
            cat = atom.Category(scheme=self.TAGS_SCHEME + "/" + self.user.slug,
                                term=tag)
            entry.category.append(cat)

        # lists
        for list in self.lists:
            cat = atom.Category(scheme=self.LISTS_SCHEME + "/" + self.user.slug,
                                term=list)
            entry.category.append(cat)

        ##### Service data #####
        if self.service.__dict__.get("id") == None:
            entry.title = atom.Title(text=self.service.name)
            _add_extension(entry, self.OOS_NS, "useraddress",
                           self.service.useraddress)
            _add_extension(entry, self.OOS_NS, "locality",
                           self.service.locality)
            _add_extension(entry, self.OOS_NS, "url", self.service.url)
            _add_extension(entry, self.OOS_NS, "telephone",
                           self.service.telephone)
            _add_extension(entry, self.OOS_NS, "country", self.service.country,
                           {"slug": "/" + self.service.country.lower()})

        return entry.ToString()

    def update(self):
        """Update the review."""
        return self._api.update_review(self)

    def delete(self):
        """Delete the review."""
        return self._api.delete_user_review(self)

    def get_media(self):
        """Return the media entries of the review."""
        return self._api.get_review_media(self)

    def add_media(self, file, content_type="image/jpeg"):
        """Add new media to the review."""
        video = content_type.find("image") == -1
        media = Media.create_object(self._api, self.user, self.service, video)
        return self._api.create_media(media, file, content_type)


class Media(Model):
    """Media class. The multimedia element belongs to a review."""

    @classmethod
    def create_object(cls, api, user, service, video=False, description=""):
        """Create an object without atom string or entries."""
        media = cls(api)

        setattr(media, "user", user)
        setattr(media, "service", service)
        setattr(media, "description", description)
        if video:
            setattr(media, "type", "video")
        else:
            setattr(media, "type", "image")
        setattr(media, "updated", datetime.now())

        return media

    @classmethod
    def load_entry(cls, api, entry):
        """Create an object starting with one single entry."""
        media = cls(api)

        setattr(media, "updated", _parse_date(entry.updated.text))
        setattr(media, "description", entry.title.text)
        _get_extensions(media, entry, ["fnv"])
        setattr(media, "link", entry.GetAlternateLink().href)

        setattr(media, "src", entry.content.src)
        if entry.content.type == "image/jpg":
            setattr(media, "type", "image")
        else:
            setattr(media, "type", "video")
            setattr(media, "splash",  _get_link(entry, "splash"))

        user = User.load_author(api, entry.author[0])
        setattr(media, "user", user)

        return media

    def set_service(self, service):
        self.service = service

    def to_atom(self):
        """Return the object as an atom string."""
        entry = _build_dummy_entry()
        entry.title = atom.Title(text=self.description)
        return entry.ToString()

    def get_file(self):
        """Return the media in a file."""
        return self._api.get_media_file(self)

    def update(self):
        """Update the media metadata."""
        return self._api.update_media(self)

    def delete(self):
        """Delete the media."""
        return self._api.delete_media(self)


class AtomCategory():
    """Common class to all the atom categories."""

    def __init__(self, api=None):
        self._api = api

    @classmethod
    def parse(cls, api, atom_string):
        """Parse an atom string returning a ResultSet."""
        categories = etree.ElementTree.fromstring(atom_string)
        if categories.tag != "{http://www.w3.org/2007/app}categories":
            return None

        cats = []
        for category in categories.getiterator():
            if category.tag == "{http://www.w3.org/2005/Atom}category":
                cat = cls(api)
                for attr, value in category.attrib.iteritems():
                    # remove schema part and substitute hyphens
                    attr = attr.split("}")[-1].replace("-", "_")
                    setattr(cat, attr, value)
                cats.append(cat)
        return cats


class Tag(AtomCategory):
    "Tag class."
    pass


class List(AtomCategory):
    "List/section class."
    pass


class Category(AtomCategory):
    "11870.com category class."
    pass


class Attribute(AtomCategory):
    "11870.com attribute class."
    pass


class Privacy(AtomCategory):
    "Privacy class."
    pass


class Trusted(AtomCategory):
    "Trusted class."
    pass

