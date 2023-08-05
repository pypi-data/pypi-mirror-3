from django import template
from django.conf import settings
from django.core.cache import cache
import logging
from templatetag_sugar.parser import Optional, Constant, Name, Variable
from templatetag_sugar.register import tag
import ttp
import twitter


register = template.Library()
tweet_parser = ttp.Parser()


def get_cache_key(*args):
    return 'get_tweets_{0}'.format('_'.join([str(arg) for arg in args if arg]))


@tag(register, [Constant("for"), Variable(), Constant("as"), Name(),
                Optional([Constant("exclude"), Variable("exclude")]),
                Optional([Constant("limit"), Variable("limit")])])
def get_tweets(context, username, asvar, exclude='', limit=None):
    cache_key = get_cache_key(username, asvar, exclude, limit)
    tweets = []
    try:
        user_last_tweets = twitter.Api().GetUserTimeline(screen_name=username,
                                                         include_rts=('retweets' not in exclude),
                                                         include_entities=True)
    except twitter.TwitterError as e:
        logging.getLogger(__name__).error(e.message)
        context[asvar] = cache.get(cache_key, [])
        return ""

    for status in user_last_tweets:
        if 'replies' in exclude and status.GetInReplyToUserId() is not None:
            continue

        status.html = tweet_parser.parse(status.GetText()).html
        tweets.append(status)

    if limit:
        tweets = tweets[:limit]

    context[asvar] = tweets
    cache.set(cache_key, tweets)

    return ""