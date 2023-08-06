# -*- coding: utf-8 -*-

"""
This module contains the data structures that power ``turses`` and
the Twitter entities represented into it.
"""

import time
from re import sub
from re import compile as compile_regex
from bisect import insort
from calendar import timegm
from functools import partial, total_ordering
from htmlentitydefs import entitydefs

from turses.meta import (ActiveList, UnsortedActiveList, Updatable, Observable,
                         notify)
from turses.utils import is_url, matches_word


TWEET_MAXIMUM_CHARACTERS = 140
STATUS_URL_TEMPLATE = 'https://twitter.com/#!/{user}/status/{id}'

# -- Helpers ------------------------------------------------------------------

# username
username_regex = compile_regex(r'[A-Za-z0-9_]+')
is_username = partial(matches_word, username_regex)
sanitize_username = partial(filter, is_username)
prepend_at = lambda username: '@%s' % username

# hashtag
hashtag_regex = compile_regex(r'#.+')
is_hashtag = partial(matches_word, hashtag_regex)


def is_DM(status):
    return status.__class__ == DirectMessage


def is_valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= TWEET_MAXIMUM_CHARACTERS


def is_valid_search_text(text):
    """Checks the validity of a search text."""
    return bool(text)


def timestamp_from_datetime(datetime):
    return timegm(datetime.utctimetuple())


def html_unescape(string):
    """Unescape HTML entities from ``string``."""
    def entity_replacer(m):
        entity = m.group(1)
        if entity in entitydefs:
            return entitydefs[entity]
        else:
            return m.group(0)

    return sub(r'&([^;]+);', entity_replacer, string)



def apply_attribute(string,
                    hashtag='hashtag',
                    attag='attag',
                    url='url'):
    """
    Apply an attribute to `string` dependending on wether it is
    a hashtag, a Twitter username or an URL.

    >>> apply_attribute('#Python')
    ('hashtag', u'#Python')
    >>> apply_attribute('@dialelo')
    ('attag', u'@dialelo')
    >>> apply_attribute('@dialelo',
                        attag='username')
    ('username', u'@dialelo')
    >>> apply_attribute('http://www.dialelo.com')
    ('url', u'http://www.dialelo.com')
    >>> apply_attribute('turses')
    u'turses'
    """
    string = unicode(string)

    if is_hashtag(string):
        return (hashtag, string)
    elif string.startswith('@') and is_username(string[1:]):
        return (attag, string)
    elif is_url(string):
        return  (url, string)
    else:
        return string


def parse_attributes(text,
                     hashtag='hashtag',
                     attag='attag',
                     url='url'):
    """
    Parse the attributes in `text` and isolate the hashtags, usernames
    and URLs with the provided attributes.

    >>> text = 'I love #Python'
    >>> parse_attributes(text=text,
    ...                  hashtag='hashtag')
    ['I love ', ('hashtag', '#Python')]
    """

    # nothing to do
    if not text:
        return u''

    words = text.split()
    parsed_text = [apply_attribute(word) for word in words]

    def add_withespace(parsed_word):
        if isinstance(parsed_word, tuple):
            # is an (attr, word) tuple
            return parsed_word
        else:
            return parsed_word + ' '

    tweet = [add_withespace(parsed_word) for parsed_word
                                         in parsed_text]

    # insert spaces after an attribute
    indices = []
    for i, word in enumerate(tweet[:-1]):
        word_is_attribute = isinstance(word, tuple)

        if word_is_attribute:
            indices.append(i + 1 + len(indices))

    for index in indices:
        tweet.insert(index, u' ')

    # remove trailing withespace
    if tweet and isinstance(tweet[-1], basestring):
        tweet[-1] = tweet[-1][:-1]

    return tweet

def extract_attributes(entities, hashtag, attag, url):
    """
    Extract attributes from entities.

    Return a list with (`attr`, string[, replacement]) tuples for each
    entity in the status.
    """
    def map_attr(attr, entity_list):
        """
        Return a list with (`attr`, string) tuples for each string in
        `entity_list`.
        """
        attributes = []
        for entity in entity_list:
            # urls are a special case, we change the URL shortened by
            # Twitter (`http://t.co/*`) by the URL returned in
            # `display_url`
            indices = entity.get('indices')
            url = entity.get('display_url', False)

            if url:
                mapping = (attr, indices, url)
            else:
                mapping = (attr, indices)
            attributes.append(mapping)
        return attributes

    entity_names_and_attributes = [
        ('user_mentions', attag),
        ('hashtags', hashtag),
        ('urls', url),
        ('media', url),
    ]

    attributes = []
    for entity_name, entity_attribute in entity_names_and_attributes:
        entity_list = entities.get(entity_name, [])
        attributes.extend(map_attr(entity_attribute, entity_list))

    # sort mappings to split the text in order
    attributes.sort(key=lambda mapping: mapping[1][0])

    return attributes


# -- Model --------------------------------------------------------------------


class TimelineList(UnsortedActiveList, Observable):
    """
    A list of :class:`~turses.models.Timeline` instances that implements the
    :class:`~turses.meta.UnsortedActiveList` interface, thus having an *active*
    element and a group of adjacent *visible* timelines.
    """

    def __init__(self):
        UnsortedActiveList.__init__(self)
        Observable.__init__(self)
        self.timelines = []
        self.visible = []

    def has_timelines(self):
        return self.active_index != self.NULL_INDEX and self.timelines

    @property
    def active_status(self):
        if self.has_timelines():
            active_timeline = self.active
            return active_timeline.active

    @notify
    def append_timeline(self, timeline):
        """Appends a new `Timeline` to the end of the list."""
        if self.active_index == self.NULL_INDEX:
            # `timeline` becomes the active and the only visible
            self.active_index = 0
            self.visible = [0]
            self.timelines.append(timeline)
            self._mark_read()
            return
        self.timelines.append(timeline)

    @notify
    def delete_active_timeline(self):
        """
        Deletes the active timeline (if any) and shifts the active index
        to the right.
        """
        if not self.has_timelines():
            return

        # delete timeline
        del self.timelines[self.active_index]
        if self.is_valid_index(self.active_index):
            pass
        else:
            # Shift cursor to left when we don't have any element
            # in the right. When deleting the last timeline in the
            # list, the `active_index` becomes -1 (NULL_INDEX).
            self.active_index -= 1

        # remove from visible
        try:
            self.visible.remove(self.active_index)
        except ValueError:
            pass
        finally:
            self._set_active_as_visible()

    @notify
    def update_active_timeline(self):
        if self.has_timelines():
            self.active.update()

    @property
    def visible_timelines(self):
        return [self.timelines[i] for i in self.visible]

    @property
    def active_index_relative_to_visible(self):
        return self.visible.index(self.timelines.index(self.active))

    def _set_active_as_visible(self):
        if self.active_index not in self.visible:
            self.visible = [self.active_index]

    @notify
    def expand_visible_previous(self):
        if not self.visible:
            return

        self.visible.sort()
        lowest = self.visible[0]
        previous = lowest - 1
        if self.is_valid_index(previous):
            self.visible.insert(0, previous)

    @notify
    def expand_visible_next(self):
        if not self.visible:
            return

        self.visible.sort()
        highest = self.visible[-1]
        next = highest + 1
        if self.is_valid_index(next):
            self.visible.append(next)

    @notify
    def shrink_visible_beggining(self):
        self.visible.sort()
        try:
            first = self.visible.pop(0)
            # if the active is the first one does not change
            if first == self.active_index:
                self.visible.insert(0, first)
        except IndexError:
            pass

    @notify
    def shrink_visible_end(self):
        self.visible.sort()
        try:
            last = self.visible.pop()
            # if the active is the last one does not change
            if last == self.active_index:
                self.visible.append(last)
        except IndexError:
            pass

    # magic

    def __iter__(self):
        return self.timelines.__iter__()

    def __len__(self):
        return self.timelines.__len__()

    # from `UnsortedActiveList`

    @property
    def active(self):
        if self.has_timelines():
            return self.timelines[self.active_index]

    def is_valid_index(self, index):
        return index >= 0 and index < len(self.timelines)

    @notify
    def activate_previous(self):
        UnsortedActiveList.activate_previous(self)
        self._mark_read()
        self._set_active_as_visible()

    @notify
    def activate_next(self):
        UnsortedActiveList.activate_next(self)
        self._mark_read()
        self._set_active_as_visible()

    @notify
    def activate_first(self):
        UnsortedActiveList.activate_first(self)
        self._mark_read()
        self._set_active_as_visible()

    @notify
    def activate_last(self):
        if self.has_timelines():
            last_index = len(self.timelines) - 1
            self.active_index = last_index
        self._mark_read()
        self._set_active_as_visible()

    def _swap_timelines(self, one, other):
        """
        Given the indexes of two timelines `one` and `other`, it swaps the
        `Timeline` objects contained in those positions.
        """
        if self.is_valid_index(one) and self.is_valid_index(other):
            self.timelines[one], self.timelines[other] = \
                    self.timelines[other], self.timelines[one]

    def _mark_read(self):
        if self.has_timelines():
            active_timeline = self.active
            active_timeline.mark_active_as_read()

    @notify
    def shift_active_previous(self):
        active_index = self.active_index
        previous_index = active_index - 1
        if self.is_valid_index(previous_index):
            self._swap_timelines(previous_index, active_index)
            self.active_index = previous_index
            self._set_active_as_visible()

    @notify
    def shift_active_next(self):
        active_index = self.active_index
        next_index = active_index + 1
        if self.is_valid_index(next_index):
            self._swap_timelines(active_index, next_index)
            self.active_index = next_index
            self._set_active_as_visible()

    @notify
    def shift_active_beggining(self):
        if self.has_timelines():
            first_index = 0
            active_timeline = self.active
            self.timelines.insert(first_index, active_timeline)
            del self.timelines[self.active_index + 1]
            self.active_index = first_index
            self._set_active_as_visible()

    @notify
    def shift_active_end(self):
        if self.has_timelines():
            last_index = len(self.timelines)
            active_timeline = self.active
            self.timelines.insert(last_index, active_timeline)
            self.delete_active_timeline()
            self.active_index = last_index - 1
            self._set_active_as_visible()


# -- Twitter entities ---------------------------------------------------------


class Timeline(ActiveList, Updatable):
    """
    List of Twitter statuses ordered reversely by date, optionally with
    a name and a function that updates the current timeline and its arguments.

    Its :class:`~turses.meta.Updatable` and implements the
    :class:`~turses.meta.ActiveList` interface.
    """

    def __init__(self,
                 name='',
                 statuses=None,
                 **kwargs):
        ActiveList.__init__(self)
        Updatable.__init__(self, **kwargs)
        self.name = name

        self.statuses = []
        if statuses:
            self.add_statuses(statuses)
            self.activate_first()
            self.mark_active_as_read()

    def add_status(self, new_status):
        """
        Adds the given status to the status list of the Timeline if it's
        not already in it.
        """
        if new_status in self.statuses:
            return

        if self.active_index == self.NULL_INDEX:
            self.active_index = 0

        # keep the same tweet as the active when inserting statuses
        active = self.active
        is_more_recent_status = lambda a, b: a.created_at < b.created_at

        if active and is_more_recent_status(active, new_status):
            self.activate_next()

        insort(self.statuses, new_status)

    def add_statuses(self, new_statuses):
        """
        Adds the given new statuses to the status list of the Timeline
        if they are not already in it.
        """
        if not new_statuses:
            return

        for status in new_statuses:
            self.add_status(status)

    def clear(self):
        """Clears the Timeline."""
        self.active_index = self.NULL_INDEX
        self.statuses = []

    @property
    def unread_count(self):
        def one_if_unread(tweet):
            if hasattr(tweet, 'read') and tweet.read:
                return 0
            return 1

        return sum([one_if_unread(tweet) for tweet in self.statuses])

    def mark_active_as_read(self):
        """Set active status' `read` attribute to `True`."""
        if self.active:
            self.active.read = True

    def mark_all_as_read(self):
        for status in self.statuses:
            status.read = True
    # magic

    def __len__(self):
        return len(self.statuses)

    def __iter__(self):
        return self.statuses.__iter__()

    def __getitem__(self, i):
        return self.statuses[i]

    # from `ActiveList`

    @property
    def active(self):
        if self.statuses and self.is_valid_index(self.active_index):
            return self.statuses[self.active_index]

    def is_valid_index(self, index):
        if self.statuses:
            return index >= 0 and index < len(self.statuses)
        else:
            self.active_index = self.NULL_INDEX
        return False

    def activate_previous(self):
        ActiveList.activate_previous(self)
        self.mark_active_as_read()

    def activate_next(self):
        ActiveList.activate_next(self)
        self.mark_active_as_read()

    def activate_first(self):
        ActiveList.activate_first(self)
        self.mark_active_as_read()

    def activate_last(self):
        if self.statuses:
            self.active_index = len(self.statuses) - 1
            self.mark_active_as_read()
        else:
            self.active_index = self.NULL_INDEX

    # from `Updatable`

    def update_callback(self, result):
        self.add_statuses(result)


class User(object):
    """
    A Twitter user.
    """

    def __init__(self,
                 id,
                 name,
                 screen_name,
                 description,
                 url,
                 created_at,
                 friends_count,
                 followers_count,
                 favorites_count,
                 status):
        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.description = description
        self.url = url
        self.created_at = created_at
        self.friends_count = friends_count
        self.followers_count = followers_count
        self.favorites_count = favorites_count
        self.status = status


@total_ordering
class Status(object):
    """
    A Twitter status.
    """

    def __init__(self,
                 id,
                 created_at,
                 user,
                 text,
                 is_reply=False,
                 is_retweet=False,
                 is_favorite=False,
                 # for replies
                 in_reply_to_user='',
                 # for retweets
                 retweeted_status=None,
                 retweet_count=0,
                 author='',
                 entities=None):
        self.id = id
        self.created_at = created_at
        self.user = user
        self.text = html_unescape(text)
        self.is_reply = is_reply
        self.is_retweet = is_retweet
        self.is_favorite = is_favorite
        self.retweet_count = retweet_count
        self.retweeted_status = retweeted_status
        self.author = author
        self.entities = {} if entities is None else entities

    def map_attributes(self, hashtag, attag, url):
        """
        Return a list of strings and tuples for hashtag, attag and
        url entities.

        For a hashtag, its tuple would be (`hashtag`, text).

        >>> from datetime import datetime
        >>> s = Status(id=0,
        ...            created_at=datetime.now(),
        ...            user='dialelo',
        ...            text='I love #Python',)
        >>> s.map_attributes('hashtag', 'attag', 'url')
        ['I love ', ('hashtag', '#Python')]
        """
        is_retweet = getattr(self, 'is_retweet', False)

        if is_retweet:
            # call this method on the retweeted status
            return self.retweeted_status.map_attributes(hashtag, attag, url)

        if not self.entities:
            # no entities defined, parse text *manually*
            #  - Favorites don't include any entities at the time of writing
            text = self.retweeted_status.text if is_retweet else self.text
            return parse_attributes(text, hashtag, attag, url)

        # we have entities, extract the (attr, string[, replacement]) tuples
        assert self.entities
        attribute_mappings = extract_attributes(entities=self.entities,
                                                hashtag=hashtag,
                                                attag=attag,
                                                url=url)

        text = []
        status_text = unicode(self.text)
        # start from the beggining
        index = 0
        for mapping in attribute_mappings:
            attribute = mapping[0]
            starts, ends = mapping[1]

            # this text has an attribute associated
            entity_text = status_text[starts:ends]

            if attribute == url and len(mapping) == 3:
                ## if the text is a url and a third element is included in the
                ## tuple; the third element is the original URL
                entity_text = mapping[2]

            # append normal text before the text with an attribute
            normal_text = status_text[index:starts]
            if normal_text:
                text.append(normal_text)

            # append text with attribute
            text_with_attribute = (attribute, entity_text)
            text.append(text_with_attribute)

            # update index, continue from where the attribute text ends
            index = ends

        # after parsing all attributes we can have some text left
        normal_text = status_text[index:]
        if normal_text:
            text.append(normal_text)

        return text

    @property
    def relative_created_at(self):
        """Return a human readable string representing the posting time."""
        # This code is borrowed from `python-twitter` library
        fudge = 1.25
        delta = long(time.time()) - timestamp_from_datetime(self.created_at)

        if delta < (1 * fudge):
            return "a second ago"
        elif delta < (60 * (1 / fudge)):
            return "%d seconds ago" % (delta)
        elif delta < (60 * fudge):
            return "a minute ago"
        elif delta < (60 * 60 * (1 / fudge)):
            return "%d minutes ago" % (delta / 60)
        elif delta < (60 * 60 * fudge) or delta / (60 * 60) == 1:
            return "an hour ago"
        elif delta < (60 * 60 * 24 * (1 / fudge)):
            return "%d hours ago" % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge) or delta / (60 * 60 * 24) == 1:
            return "a day ago"
        else:
            return "%d days ago" % (delta / (60 * 60 * 24))

    @property
    def url(self):
        return STATUS_URL_TEMPLATE.format(user=self.user, id=self.id)

    @property
    def mentioned_for_reply(self):
        """
        Return a list containing the author of `status` and all the mentioned
        usernames prepended with '@'.
        """
        author = self.authors_username
        mentioned = self.mentioned_usernames
        mentioned.insert(0, author)
        # avoid repetitions
        mentioned = list(set(mentioned))

        return [prepend_at(username) for username in mentioned]

    @property
    def authors_username(self):
        """Return the original author's username of the given status."""
        if is_DM(self):
            return self.sender_screen_name
        elif self.is_retweet:
            return self.retweeted_status.authors_username
        else:
            return self.user

    @property
    def mentioned_usernames(self):
        """
        Return mentioned usernames in `status` without '@'.
        """
        # TODO: use self.entities if available
        usernames = []
        for word in self.text.split():
            if len(word) > 1 and word.startswith('@'):
                word.strip('@')
                usernames.append(sanitize_username(word))
        return list(set(usernames))

    @property
    def hashtags(self):
        """
        Return a list of hashtags encountered in `status`.
        """
        # TODO: use self.entities
        return filter(is_hashtag, self.text.split())

    def dm_recipients_username(self, sender):
        """
        Return the recipient for a Direct Message depending on what `self`
        is.

        If is a `turses.models.Status` and sender != `status.user` I will
        return `status.user`.

        If is a `turses.models.DirectMessage` I will return the username that
        is not `sender` looking at the DMs sender and recipient.

        Otherwise I return `None`.
        """
        if is_DM(self):
            users = [self.sender_screen_name,
                     self.recipient_screen_name]
            if sender in users:
                users.pop(users.index(sender))
                return users.pop()
        elif self.user != sender:
            return self.user

    # magic

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        # statuses are ordered reversely by date
        return self.created_at > other.created_at


class DirectMessage(Status):
    """
    A Twitter direct message.
    """

    def __init__(self,
                 id,
                 created_at,
                 sender_screen_name,
                 recipient_screen_name,
                 text,
                 entities=None):
        self.id = id
        self.created_at = created_at
        self.sender_screen_name = sender_screen_name
        self.recipient_screen_name = recipient_screen_name
        self.text = html_unescape(text)
        self.entities = entities

    @property
    def url(self):
        return None


class List(object):
    """
    A Twitter list.
    """

    def __init__(self,
                 id,
                 owner,
                 created_at,
                 name,
                 description,
                 member_count,
                 subscriber_count,
                 private=False,):
        self.id = id
        self.owner = owner
        self.created_at = created_at
        self.name = name
        self.description = description
        self.member_count = member_count
        self.subscriber_count = subscriber_count
        self.private = private
