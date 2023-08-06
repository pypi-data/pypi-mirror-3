# -*- coding: utf-8 -*-

"""
turses.core
~~~~~~~~~~~

This module contains the controller logic of turses.
"""


from gettext import gettext as _
from functools import partial

import urwid
from tweepy import TweepError

from turses.utils import (
        get_urls,
        spawn_process,
)
from turses.meta import async, wrap_exceptions
from turses.config import (
        HOME_TIMELINE,
        MENTIONS_TIMELINE,
        FAVORITES_TIMELINE,
        MESSAGES_TIMELINE,
        OWN_TWEETS_TIMELINE,
)
from turses.models import (
        is_DM,
        is_username,
        is_valid_status_text,
        is_valid_search_text,
        sanitize_username,

        Timeline,
        TimelineList,
)
from turses.api.base import AsyncApi


class KeyHandler(object):
    """
    Maps key bindings from configuration to calls to controllers' functions.
    """

    def __init__(self,
                 configuration,
                 controller):
        self.configuration = configuration
        self.controller = controller

    def is_bound(self, key, name):
        """
        Return True if `key` corresponds to the action specified by `name`.
        """
        try:
            bindings = self.configuration.key_bindings
            bound_key, bound_key_description = bindings[name]
        except KeyError:
            return False
        else:
            return key == bound_key

    def handle(self, key):
        """Handle keyboard input."""
        # remove user widget when receiving input
        if self.controller.is_in_user_info_mode():
            self.controller.timeline_mode()

        # Editor has priority
        if self.controller.is_in_editor_mode():
            size = 20,
            self.controller.editor.keypress(size, key)
            return

        # Global commands
        handled = not self._turses_key_handler(key)
        if handled:
            return

        # Timeline commands
        if not self.controller.is_in_help_mode():
            handled = not self._timeline_key_handler(key)
            if handled:
                return

        if self.controller.is_in_info_mode():
            return

        # Motion commands
        handled = not self._motion_key_handler(key)
        if handled:
            return

        # Help mode commands
        #  only accepts motion commands, timeline commands and <Esc>
        if self.controller.is_in_help_mode() and key == 'esc':
            self.controller.timeline_mode()
            self.controller.clear_status()
            return

        # Timeline mode commands

        # Buffer commands
        handled = not self._buffer_key_handler(key)
        if handled:
            return

        # Twitter commands
        handled = not self._twitter_key_handler(key)
        if handled:
            return

        # External programs
        handled = not self._external_program_handler(key)
        if handled:
            return
        else:
            return key

    def _turses_key_handler(self, key):
        # quit
        if self.is_bound(key, 'quit'):
            self.controller.exit()
        # redraw screen
        elif self.is_bound(key, 'redraw'):
            self.controller.redraw_screen()
        # help
        elif self.is_bound(key, 'help'):
            self.controller.help_mode()
        # reload configuration
        elif self.is_bound(key, 'reload_config'):
            self.controller.reload_configuration()
        else:
            return key

    def _motion_key_handler(self, key):
        ## up
        if self.is_bound(key, 'up') or key == 'up':
            self.controller.scroll_up()
        # down
        elif self.is_bound(key, 'down') or key == 'down':
            self.controller.scroll_down()
        # scroll to top
        elif self.is_bound(key, 'scroll_to_top'):
            self.controller.scroll_top()
        # scroll to bottom
        elif self.is_bound(key, 'scroll_to_bottom'):
            self.controller.scroll_bottom()
        else:
            return key

    def _buffer_key_handler(self, key):
        # Right
        if self.is_bound(key, 'right') or key == 'right':
            self.controller.next_timeline()
        # Left
        elif self.is_bound(key, 'left') or key == 'left':
            self.controller.previous_timeline()
        # Shift active buffer left
        elif self.is_bound(key, 'shift_buffer_left'):
            self.controller.shift_buffer_left()
        # Shift active buffer right
        elif self.is_bound(key, 'shift_buffer_right'):
            self.controller.shift_buffer_right()
        # Shift active buffer beggining
        elif self.is_bound(key, 'shift_buffer_beggining'):
            self.controller.shift_buffer_beggining()
        # Shift active buffer end
        elif self.is_bound(key, 'shift_buffer_end'):
            self.controller.shift_buffer_end()
        # Expand visible buffer left
        elif self.is_bound(key, 'expand_visible_left'):
            self.controller.expand_buffer_left()
        # Expand visible buffer right
        elif self.is_bound(key, 'expand_visible_right'):
            self.controller.expand_buffer_right()
        # Shrink visible buffer left
        elif self.is_bound(key, 'shrink_visible_left'):
            self.controller.shrink_buffer_left()
        # Shrink visible buffer right
        elif self.is_bound(key, 'shrink_visible_right'):
            self.controller.shrink_buffer_right()
        # Activate first buffer
        elif self.is_bound(key, 'activate_first_buffer'):
            self.controller.activate_first_buffer()
        # Activate last buffer
        elif self.is_bound(key, 'activate_last_buffer'):
            self.controller.activate_last_buffer()
        # Delete buffer
        elif self.is_bound(key, 'delete_buffer'):
            self.controller.delete_buffer()
        # Clear status
        elif self.is_bound(key, 'clear'):
            # TODO: clear active buffer
            #self.controller.clear_body()
            self.controller.clear_status()
        # Mark all as read
        elif self.is_bound(key, 'mark_all_as_read'):
            self.controller.mark_all_as_read()
        else:
            return key

    def _timeline_key_handler(self, key):
        # Show home Timeline
        if self.is_bound(key, 'home'):
            self.controller.append_home_timeline()
        # Own tweets
        elif self.is_bound(key, 'own_tweets'):
            self.controller.append_own_tweets_timeline()
        # Favorites timeline
        elif self.is_bound(key, 'favorites'):
            self.controller.append_favorites_timeline()
        # Mention timeline
        elif self.is_bound(key, 'mentions'):
            self.controller.append_mentions_timeline()
        # Direct Message timeline
        elif self.is_bound(key, 'DMs'):
            self.controller.append_direct_messages_timeline()
        # Search
        elif self.is_bound(key, 'search'):
            self.controller.search()
        # Search User
        elif self.is_bound(key, 'search_user'):
            self.controller.search_user()
        # Thread
        elif self.is_bound(key, 'thread'):
            self.controller.append_thread_timeline()
        # User info
        elif self.is_bound(key, 'user_info'):
            self.controller.user_info()
        # Follow hashtags
        elif self.is_bound(key, 'hashtags'):
            self.controller.search_hashtags()
        # Authors timeline
        elif self.is_bound(key, 'user_timeline'):
            self.controller.focused_status_author_timeline()
        else:
            return key

    def _twitter_key_handler(self, key):
        # Update timeline
        if self.is_bound(key, 'update'):
            self.controller.update_active_timeline()
        # Update all timelines
        if self.is_bound(key, 'update_all'):
            self.controller.update_all_timelines()
        # Tweet
        elif self.is_bound(key, 'tweet'):
            self.controller.tweet()
        # Reply
        elif self.is_bound(key, 'reply'):
            self.controller.reply()
        # Retweet
        elif self.is_bound(key, 'retweet'):
            self.controller.retweet()
        # Retweet and Edit
        elif self.is_bound(key, 'retweet_and_edit'):
            self.controller.manual_retweet()
        # Delete (own) tweet
        elif self.is_bound(key, 'delete_tweet'):
            self.controller.delete_tweet()
        # Follow Selected
        elif self.is_bound(key, 'follow_selected'):
            self.controller.follow_selected()
        # Follow User using `text`
        elif self.is_bound(key, 'follow_user'):
            self.controller.follow_user()
        # Unfollow Selected
        elif self.is_bound(key, 'unfollow_selected'):
            self.controller.unfollow_selected()
        # Unfollow User using `text`
        elif self.is_bound(key, 'unfollow_user'):
            self.controller.unfollow_user()
        # Send Direct Message
        elif self.is_bound(key, 'send_dm'):
            self.controller.direct_message()
        # Create favorite
        elif self.is_bound(key, 'fav'):
            self.controller.favorite()
        # Destroy favorite
        elif self.is_bound(key, 'delete_fav'):
            self.controller.unfavorite()
        # Tweet with hashtags
        elif self.is_bound(key, 'tweet_hashtag'):
            self.controller.tweet_with_hashtags()
        else:
            return key

    def _external_program_handler(self, key):
        # Open URL
        if self.is_bound(key, 'openurl'):
            self.controller.open_urls()
        if self.is_bound(key, 'open_status_url'):
            self.controller.open_status_url()
        else:
            return key


class Controller(object):
    """Controller of the program."""

    INFO_MODE = 0
    TIMELINE_MODE = 1
    HELP_MODE = 2
    EDITOR_MODE = 3
    USER_INFO_MODE = 4

    # -- Initialization -------------------------------------------------------

    def __init__(self, configuration, ui, api_backend):
        self.configuration = configuration
        self.ui = ui
        self.editor = None

        # Mode
        self.mode = self.INFO_MODE

        # API
        self.info_message(_('Initializing API'))
        oauth_token = self.configuration.oauth_token
        oauth_token_secret = self.configuration.oauth_token_secret
        self.api = AsyncApi(api_backend,
                            access_token_key=oauth_token,
                            access_token_secret=oauth_token_secret,)
        self.api.init_api(on_error=self.api_init_error,
                          on_success=self.init_timelines,)

        # start main loop
        try:
            self.main_loop()
        except TweepError:
            self.error_message(_('API error'))
        except:
            exit(1)

    def main_loop(self):
        """
        Main loop of the program, `Controller` subclasses must override this
        method.
        """
        raise NotImplementedError

    def exit(self):
        """Exit the program."""
        raise NotImplementedError

    @async
    def init_timelines(self):
        # API has to be authenticated
        while (not self.api.is_authenticated):
            pass
        self.user = self.api.verify_credentials()
        self.info_message(_('Initializing timelines'))
        self.timelines = TimelineList()
        self.append_default_timelines()
        seconds = self.configuration.update_frequency
        self.loop.set_alarm_in(seconds, self.update_alarm)

    def reload_configuration(self):
        raise NotImplementedError

    # -- Callbacks ------------------------------------------------------------

    def api_init_error(self):
        # TODO retry
        self.error_message(_('Couldn\'t initialize API'))

    def update_alarm(self, *args, **kwargs):
        seconds = self.configuration.update_frequency
        self.update_all_timelines()
        self.loop.set_alarm_in(seconds, self.update_alarm)

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self):
        """
        Activates the Timeline mode if there are Timelines.

        If not, shows program info.
        """
        if self.is_in_user_info_mode():
            self.ui.hide_user_info()

        if self.is_in_timeline_mode():
            return

        elif self.timelines.has_timelines():
            self.mode = self.TIMELINE_MODE
            self.draw_timelines()
        else:
            self.mode = self.INFO_MODE
            self.ui.show_info()
        if self.is_in_help_mode():
            self.clear_status()
        self.redraw_screen()

    def is_in_timeline_mode(self):
        return self.mode == self.TIMELINE_MODE

    def info_mode(self):
        self.mode = self.INFO_MODE
        self.ui.show_info()
        self.redraw_screen()

    def is_in_info_mode(self):
        return self.mode == self.INFO_MODE

    def help_mode(self):
        """Activate help mode."""
        if self.is_in_help_mode():
            return
        self.mode = self.HELP_MODE
        self.ui.show_help(self.configuration)
        self.redraw_screen()

    def is_in_help_mode(self):
        return self.mode == self.HELP_MODE

    def editor_mode(self, editor):
        """Activate editor mode."""
        self.editor = editor
        self.mode = self.EDITOR_MODE

    def is_in_editor_mode(self):
        return self.mode == self.EDITOR_MODE

    def user_info_mode(self, user):
        """Activate user info mode."""
        self._user_info = user
        self.mode = self.USER_INFO_MODE

    def is_in_user_info_mode(self):
        return self.mode == self.USER_INFO_MODE

    # -- Timelines ------------------------------------------------------------

    @wrap_exceptions
    def append_timeline(self,
                        name,
                        update_function,
                        update_args=None,
                        update_kwargs=None):
        """
        Given a name, function to update a timeline and optionally
        arguments to the update function, it creates the timeline and
        appends it to `timelines`.
        """
        timeline = Timeline(name=name,
                            update_function=update_function,
                            update_function_args=update_args,
                            update_function_kwargs=update_kwargs)
        timeline.update()
        timeline.activate_first()
        self.timelines.append_timeline(timeline)
        if self.is_in_info_mode():
            self.timeline_mode()
        self.draw_timelines()

    @async
    def append_default_timelines(self):
        default_timelines = {
            HOME_TIMELINE:       self.append_home_timeline,
            MENTIONS_TIMELINE:   self.append_mentions_timeline,
            FAVORITES_TIMELINE:  self.append_favorites_timeline,
            MESSAGES_TIMELINE:   self.append_direct_messages_timeline,
            OWN_TWEETS_TIMELINE: self.append_own_tweets_timeline,
        }

        timelines = [
            HOME_TIMELINE,
            MENTIONS_TIMELINE,
            FAVORITES_TIMELINE,
            MESSAGES_TIMELINE,
            OWN_TWEETS_TIMELINE,
        ]

        is_any = any([self.configuration.default_timelines[timeline]
                      for timeline in timelines])

        if is_any:
            self.timeline_mode()
        else:
            message = _('You don\'t have any default timelines activated')
            self.info_message(message)
            return

        for timeline in timelines:
            append = default_timelines[timeline]
            if self.configuration.default_timelines[timeline]:
                append()
                self.draw_timelines()
        self.clear_status()

    def append_home_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Home timeline fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch home timeline'))

        self.append_timeline(name=_('tweets'),
                             update_function=self.api.get_home_timeline,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_user_timeline(self, username):
        success_message = _('@%s\'s tweets fetched' % username)
        timeline_fetched = partial(self.info_message,
                                   success_message)
        error_message = _('Failed to fetch @%s\'s tweets' % username)
        timeline_not_fetched = partial(self.error_message,
                                       error_message)

        self.append_timeline(name='@%s' % username,
                             update_function=self.api.get_user_timeline,
                             update_kwargs={'screen_name': username},
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_own_tweets_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Your tweets fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch your tweets'))

        if not hasattr(self, 'user'):
            self.user = self.api.verify_credentials()
        self.append_timeline(name='@%s' % self.user.screen_name,
                             update_function=self.api.get_own_timeline,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_mentions_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Mentions fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch mentions'))

        self.append_timeline(name=_('mentions'),
                             update_function=self.api.get_mentions,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_favorites_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Favorites fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch favorites'))

        self.append_timeline(name=_('favorites'),
                             update_function=self.api.get_favorites,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_direct_messages_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Messages fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch messages'))

        self.append_timeline(name=_('messages'),
                             update_function=self.api.get_direct_messages,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_thread_timeline(self):
        status = self.timelines.active_status
        if status is None:
            return

        timeline_fetched = partial(self.info_message,
                                   _('Thread fetched'))
        timeline_not_fetched = partial(self.error_message,
                                       _('Failed to fetch thread'))

        if is_DM(status):
            self.error_message(_('Doesn\'t look like a public conversation'))
        else:
            participants = status.mentioned_usernames
            author = status.authors_username
            if author not in participants:
                participants.insert(0, author)

            name = _('thread: %s' % ', '.join(participants))
            self.append_timeline(name=name,
                                 update_function=self.api.get_thread,
                                 update_args=status,
                                 on_error=timeline_not_fetched,
                                 on_success=timeline_fetched)

    @async
    def update_all_timelines(self):
        for timeline in self.timelines:
            timeline.update()
            self.draw_timelines()
            self.info_message(_('%s updated' % timeline.name))
        self.clear_status()

    # -- Timeline mode --------------------------------------------------------

    def draw_timelines(self):
        if self.is_in_timeline_mode():
            self.update_header()
            self.draw_timeline_buffer()

    def update_header(self):
        template = self.configuration.styles['tab_template']
        name_and_unread = [(tl.name, tl.unread_count) for tl in self.timelines]

        tabs = [template.format(timeline_name=name, unread=unread)
                for (name, unread) in name_and_unread]
        self.ui.set_tab_names(tabs)

        # highlight the active
        active_index = self.timelines.active_index
        self.ui.activate_tab(active_index)

        # colorize the visible tabs
        visible_indexes = self.timelines.visible
        self.ui.header.set_visible_tabs(visible_indexes)

    def draw_timeline_buffer(self):
        # draw visible timelines
        visible_timelines = self.timelines.visible_timelines
        self.ui.draw_timelines(visible_timelines)
        # focus active timeline
        active_timeline = self.timelines.active
        active_pos = self.timelines.active_index_relative_to_visible
        # focus active status
        self.ui.focus_timeline(active_pos)
        self.ui.focus_status(active_timeline.active_index)

    def mark_all_as_read(self):
        """Mark all statuses in active timeline as read."""
        active_timeline = self.timelines.active
        for tweet in active_timeline:
            tweet.read = True
        self.update_header()

    @async
    def update_active_timeline(self):
        """Updates the timeline and renders the active timeline."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.active
            try:
                newest = active_timeline[0]
            except IndexError:
                return
            active_timeline.update(since_id=newest.id)
            if self.is_in_timeline_mode():
                self.draw_timelines()
            self.info_message('%s updated' % active_timeline.name)

    @async
    def update_active_timeline_with_newer_statuses(self):
        """
        Updates the active timeline with newer tweets than the active.
        """
        active_timeline = self.timelines.active
        active_status = active_timeline.active
        if active_status:
            active_timeline.update(since_id=active_status.id)

    @async
    def update_active_timeline_with_older_statuses(self):
        """
        Updates the active timeline with older tweets than the active.
        """
        active_timeline = self.timelines.active
        active_status = active_timeline.active
        if active_status:
            active_timeline.update(max_id=active_status.id)

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self.draw_timelines()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self.draw_timelines()

    def shift_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_previous()
            self.draw_timelines()

    def shift_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_next()
            self.draw_timelines()

    def shift_buffer_beggining(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_beggining()
            self.draw_timelines()

    def shift_buffer_end(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_end()
            self.draw_timelines()

    def expand_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.expand_visible_previous()
            self.draw_timelines()

    def expand_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.expand_visible_next()
            self.draw_timelines()

    def shrink_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.shrink_visible_beggining()
            self.draw_timelines()

    def shrink_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.shrink_visible_end()
            self.draw_timelines()

    def activate_first_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_first()
            self.draw_timelines()

    def activate_last_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_last()
            self.draw_timelines()

    def delete_buffer(self):
        self.timelines.delete_active_timeline()
        if self.timelines.has_timelines():
            self.draw_timelines()
        else:
            self.info_mode()

    # -- Motion ---------------------------------------------------------------

    def scroll_up(self):
        self.ui.focus_previous()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            # update with newer tweets when scrolling down being at the bottom
            if active_timeline.active_index == 0:
                self.update_active_timeline_with_newer_statuses()
            active_timeline.activate_previous()
            self.draw_timelines()

    def scroll_down(self):
        self.ui.focus_next()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            # update with older tweets when scrolling down being at the bottom
            if active_timeline.active_index == len(active_timeline) - 1:
                self.update_active_timeline_with_older_statuses()
            active_timeline.activate_next()
            self.draw_timelines()

    def scroll_top(self):
        self.ui.focus_first()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            active_timeline.activate_first()
            self.draw_timelines()

    def scroll_bottom(self):
        self.ui.focus_last()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            active_timeline.activate_last()
            self.draw_timelines()

    # -- Footer ---------------------------------------------------------------

    def error_message(self, message):
        self.ui.status_error_message(message)
        self.redraw_screen()

    def info_message(self, message):
        self.ui.status_info_message(message)
        self.redraw_screen()

    def clear_body(self):
        """Clear body."""
        self.ui.body.clear()

    def clear_status(self):
        """Clear the status bar."""
        self.ui.clear_status()
        self.redraw_screen()

    # -- UI -------------------------------------------------------------------

    def redraw_screen(self):
        raise NotImplementedError

    # -- Editor event handlers ------------------------------------------------

    def tweet_handler(self, text):
        """Handle the post as a tweet of the given `text`."""
        self.ui.hide_editor(self.tweet_handler)
        self.timeline_mode()

        self.info_message(_('Sending tweet'))

        if not is_valid_status_text(text):
            # <Esc> was pressed
            self.info_message(_('Tweet canceled'))
            return

        tweet_sent = partial(self.info_message, _('Tweet sent'))
        tweet_not_sent = partial(self.error_message, _('Tweet not sent'))

        # API call
        self.api.update(text=text,
                        on_success=tweet_sent,
                        on_error=tweet_not_sent,)

    def direct_message_handler(self, username, text):
        """Handle the post as a DM of the given `text` to `username`."""
        self.ui.hide_editor(self.direct_message_handler)
        self.timeline_mode()

        self.info_message(_('Sending DM'))

        if not is_valid_status_text(text):
            # <Esc> was pressed
            self.info_message(_('DM canceled'))
            return

        dm_info = _('Direct Message to @%s sent' % username)
        dm_sent = partial(self.info_message, dm_info)
        dm_error = _('Failed to send message to @%s' % username)
        dm_not_sent = partial(self.error_message, dm_error)

        self.api.direct_message(screen_name=username,
                                text=text,
                                on_success=dm_sent,
                                on_error=dm_not_sent,)

    def follow_user_handler(self, username):
        """
        Handles following the user given in `text`.
        """
        self.ui.hide_editor(self.follow_user_handler)
        self.timeline_mode()

        if username is None:
            self.info_message(_('Search cancelled'))
            return

        username = sanitize_username(username)
        if username == self.user.screen_name:
            self.error_message(_('You can\'t follow yourself'))
            return

        # TODO make sure that the user EXISTS and THEN follow
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Following @%s' % username))

        success_message = _('You are now following @%s' % username)
        follow_done = partial(self.info_message,
                              success_message)

        error_template = _('We can not ensure that you are following @%s')
        error_message = error_template % username
        follow_error = partial(self.error_message,
                               error_message)

        self.api.create_friendship(screen_name=username,
                                   on_error=follow_error,
                                   on_success=follow_done)

    def unfollow_user_handler(self, username):
        """
        Handles unfollowing the user given in `text`.
        """
        self.ui.hide_editor(self.unfollow_user_handler)
        self.timeline_mode()

        if username is None:
            self.info_message(_('Search cancelled'))
            return

        username = sanitize_username(username)
        if username == self.user.screen_name:
            self.error_message(_('That doesn\'t make any sense'))
            return

        # TODO make sure that the user EXISTS and THEN follow
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Unfollowing @%s' % username))

        success_message = _('You are no longer following %s' % username)
        unfollow_done = partial(self.info_message,
                                success_message)

        error_template = _('We can not ensure that you are not following %s')
        error_message = error_template % username
        unfollow_error = partial(self.error_message,
                                 error_message)

        self.api.destroy_friendship(screen_name=username,
                                    on_error=unfollow_error,
                                    on_success=unfollow_done)

    # NOTE:
    # `search_handler` and `search_user_handler` create timelines when
    # they are called. That's why, if we are in INFO mode, the TIMELINE
    # mode is activated.

    def search_handler(self, text):
        """
        Handles creating a timeline tracking the search term given in
        `text`.
        """
        if self.is_in_info_mode():
            self.timeline_mode()
        self.ui.hide_editor(self.search_handler)
        self.timeline_mode()

        if text is None:
            self.info_message(_('Search cancelled'))
            return

        text = text.strip()
        if not is_valid_search_text(text):
            self.error_message(_('Invalid search'))
            return
        else:
            self.info_message(_('Creating search timeline for "%s"' % text))

        success_message = _('Search timeline for "%s" created' % text)
        timeline_created = partial(self.info_message,
                                   success_message)
        error_message = _('Error creating search timeline for "%s"' % text)
        timeline_not_created = partial(self.info_message,
                                       error_message)

        self.append_timeline(name=_('Search: %s' % text),
                             update_function=self.api.search,
                             update_args=text,
                             on_error=timeline_not_created,
                             on_success=timeline_created)

    def search_user_handler(self, username):
        """
        Handles creating a timeline tracking the searched user's tweets.
        """
        if self.is_in_info_mode():
            self.timeline_mode()
        self.ui.hide_editor(self.search_user_handler)
        self.timeline_mode()

        if username is None:
            self.info_message(_('Search cancelled'))
            return

        # TODO make sure that the user EXISTS and THEN fetch its tweets
        username = sanitize_username(username)
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Fetching latest tweets from @%s' % username))

        success_message = _('@%s\'s timeline created' % username)
        timeline_created = partial(self.info_message,
                                   success_message)
        error_message = _('Unable to create @%s\'s timeline' % username)
        timeline_not_created = partial(self.error_message,
                                       error_message)

        self.append_timeline(name='@%s' % username,
                             update_function=self.api.get_user_timeline,
                             update_args=username,
                             on_success=timeline_created,
                             on_error=timeline_not_created)

    # -- Twitter --------------------------------------------------------------

    def search(self, text=None):
        text = '' if text is None else text
        handler = self.search_handler
        editor = self.ui.show_text_editor(prompt='Search',
                                          content=text,
                                          done_signal_handler=handler)
        self.editor_mode(editor)

    def search_user(self):
        prompt = _('Search user (no need to prepend it with "@"')
        handler = self.search_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                 content='',
                                 done_signal_handler=handler)
        self.editor_mode(editor)

    def search_hashtags(self):
        status = self.timelines.active_status
        if status is None:
            return
        hashtags = ' '.join(status.hashtags)
        self.search_handler(text=hashtags)

    def focused_status_author_timeline(self):
        status = self.timelines.active_status
        if status is None:
            return
        author = status.authors_username
        self.append_user_timeline(author)

    def tweet(self,
              prompt=_('Tweet'),
              content='',
              cursor_position=None):
        handler = self.tweet_handler
        editor = self.ui.show_tweet_editor(prompt=prompt,
                                           content=content,
                                           done_signal_handler=handler,
                                           cursor_position=cursor_position)
        self.editor_mode(editor)

    def retweet(self):
        status = self.timelines.active_status
        if status is None:
            return

        if is_DM(status):
            self.error_message(_('You can\'t retweet direct messages'))
            return

        retweet_posted = partial(self.info_message,
                                 _('Retweet posted'))
        retweet_post_failed = partial(self.error_message,
                                      _('Failed to post retweet'))
        self.api.retweet(on_error=retweet_post_failed,
                         on_success=retweet_posted,
                         status=status,)

    def manual_retweet(self):
        status = self.timelines.active_status

        if status is None:
            return

        rt_text = ''.join([' RT @%s: ' % status.authors_username,
                           status.text])
        if is_valid_status_text(rt_text):
            self.tweet(content=rt_text,
                       cursor_position=0)
        else:
            self.error_message(_('Tweet too long for manual retweet'))

    def reply(self):
        status = self.timelines.active_status
        if status is None:
            return
        if is_DM(status):
            self.direct_message()
            return

        author = status.authors_username
        mentioned = status.mentioned_for_reply
        try:
            mentioned.remove('@%s' % self.user.screen_name)
        except ValueError:
            pass

        handler = self.tweet_handler
        editor = self.ui.show_tweet_editor(prompt=_('Reply to %s' % author),
                                           content=' '.join(mentioned),
                                           done_signal_handler=handler)
        self.editor_mode(editor)

    def direct_message(self):
        status = self.timelines.active_status
        if status is None:
            return
        recipient = status.dm_recipients_username(self.user.screen_name)
        if recipient:
            handler = self.direct_message_handler
            editor = self.ui.show_dm_editor(prompt=_('DM to %s' % recipient),
                                            content='',
                                            recipient=recipient,
                                            done_signal_handler=handler)
            self.editor_mode(editor)
        else:
            self.error_message(_('What do you mean?'))

    def tweet_with_hashtags(self):
        status = self.timelines.active_status
        if status is None:
            return
        hashtags = ' '.join(status.hashtags)
        if hashtags:
            handler = self.tweet_handler
            content = ''.join([' ', hashtags])
            editor = self.ui.show_tweet_editor(prompt=_('%s' % hashtags),
                                               content=content,
                                               done_signal_handler=handler,
                                               cursor_position=0)
            self.editor_mode(editor)

    def delete_tweet(self):
        status = self.timelines.active_status
        if status is None:
            return
        if is_DM(status):
            self.delete_dm()
            return

        author = status.authors_username
        if (author != self.user.screen_name and
            status.user != self.user.screen_name):
            self.error_message(_('You can only delete your own tweets'))
            return

        status_deleted = partial(self.info_message,
                                 _('Tweet deleted'))
        status_not_deleted = partial(self.error_message,
                                     _('Failed to delete tweet'))

        self.api.destroy_status(status=status,
                                on_error=status_not_deleted,
                                on_success=status_deleted)

    def delete_dm(self):
        dm = self.timelines.active_status
        if dm is None:
            return

        if dm.sender_screen_name != self.user.screen_name:
            self.error_message(_('You can only delete messages sent by you'))
            return

        dm_deleted = partial(self.info_message,
                             _('Message deleted'))
        dm_not_deleted = partial(self.error_message,
                                 _('Failed to delete message'))

        self.api.destroy_direct_message(status=dm,
                                        on_error=dm_not_deleted,
                                        on_success=dm_deleted)

    def follow_selected(self):
        status = self.timelines.active_status
        if status is None:
            return
        username = status.authors_username
        if username == self.user.screen_name:
            self.error_message(_('You can\'t follow yourself'))
            return

        success_message = _('You are now following @%s' % username)
        follow_done = partial(self.info_message,
                              success_message)

        error_template = _('We can not ensure that you are following @%s')
        error_message = error_template % username
        follow_error = partial(self.error_message,
                               error_message)

        self.api.create_friendship(screen_name=username,
                                   on_error=follow_error,
                                   on_success=follow_done)

    def follow_user(self,
                    prompt=_('Follow user (no need to prepend it with "@"'),
                    content='',
                    cursor_position=None):
        handler = self.follow_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                          content=content,
                                          done_signal_handler=handler,
                                          cursor_position=cursor_position)
        self.editor_mode(editor)

    def unfollow_user(self,
                      prompt=_('Unfollow user (no need to prepend it with "@"'),
                      content='',
                      cursor_position=None):
        handler = self.unfollow_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                          content=content,
                                          done_signal_handler=handler,
                                          cursor_position=cursor_position)
        self.editor_mode(editor)

    def unfollow_selected(self):
        status = self.timelines.active_status
        if status is None:
            return
        username = status.authors_username
        if username == self.user.screen_name:
            self.error_message(_('That doesn\'t make any sense'))
            return

        success_message = _('You are no longer following %s' % username)
        unfollow_done = partial(self.info_message,
                                success_message)

        error_template = _('We can not ensure that you are not following %s')
        error_message = error_template % username
        unfollow_error = partial(self.error_message,
                                 error_message)

        self.api.destroy_friendship(screen_name=username,
                                    on_error=unfollow_error,
                                    on_success=unfollow_done)

    def favorite(self):
        status = self.timelines.active_status
        if status is None:
            return
        favorite_error = partial(self.error_message,
                                 _('Failed to mark tweet as favorite'))
        favorite_done = partial(self.info_message,
                                _('Tweet marked as favorite'))
        self.api.create_favorite(on_error=favorite_error,
                                 on_success=favorite_done,
                                 status=status,)

    def unfavorite(self):
        status = self.timelines.active_status
        if status is None:
            return
        unfavorite_error = partial(self.error_message,
                                   _('Failed to remove tweet from favorites'))
        unfavorite_done = partial(self.info_message,
                                  _('Tweet removed from favorites'))
        self.api.destroy_favorite(on_error=unfavorite_error,
                                  on_success=unfavorite_done,
                                  status=status,)

    def user_info(self):
        status = self.timelines.active_status
        if status is None:
            return
        user = self.api.get_user(status.authors_username)
        self.ui.show_user_info(user)
        self.user_info_mode(user)

    # - Browser ---------------------------------------------------------------

    def open_urls(self):
        """
        Open the URLs contained on the focused tweets in a browser.
        """
        status = self.timelines.active_status
        if status is None:
            return
        urls = get_urls(status.text)

        if not urls:
            self.info_message(_('No URLs found on this tweet'))
            return

        args = ' '.join(urls)
        self.open_urls_in_browser(args)

    def open_status_url(self):
        """
        Open the focused tweet in a browser.
        """
        status = self.timelines.active_status
        if status is None:
            return

        if is_DM(status):
            message = _('You only can open regular statuses in a browser')
            self.info_message(message)
            return

        self.open_urls_in_browser(status.url)

    def open_urls_in_browser(self, urls):
        """
        Open `urls` in $BROWSER if the environment variable is set.
        """
        command = self.configuration.browser
        if not command:
            message = _('You have to set the BROWSER environment variable'
                        ' to open URLs')
            self.error_message(message)
            return

        try:
            spawn_process(command, urls)
        except:
            self.error_message(_('Unable to launch the browser'))


class Turses(Controller):
    """Controller for the curses implementation."""

    def main_loop(self):
        if not hasattr(self, 'loop'):
            self.key_handler = KeyHandler(self.configuration, self)
            handler = self.key_handler.handle
            self.loop = urwid.MainLoop(self.ui,
                                       self.configuration.palette,
                                       handle_mouse=False,
                                       #input_filter=self.input_filter,
                                       unhandled_input=handler)
        self.loop.run()

    def exit(self):
        raise urwid.ExitMainLoop()

    def redraw_screen(self):
        if hasattr(self, "loop"):
            try:
                self.loop.draw_screen()
            except AssertionError:
                pass

    def reload_configuration(self):
        self.configuration.reload()
        self.redraw_screen()
        self.info_message(_('Configuration reloaded'))
