[pyramid_twitterauth][] is a package that extends [pyramid_simpleauth][] to allow
users to login via Twitter and / or connect their Twitter account:

    if request.twitter.has_write_access:
        request.twitter.client.update_status('OMG #lolcats')

To use, specify your Twitter app's OAuth consumer info in your `.ini` settings::

    twitterauth.oauth_consumer_key = <key>
    twitterauth.oauth_consumer_secret = <secret>

Views are exposed by default at `/oauth/twitter/...`.  To use a different path:

    twitterauth.url_prefix = 'a/n/other'

Then include the package:

    config.include('pyramid_twitterauth')

This adds an authenticated [Tweepy][] client as `request.twitter.client` and flags
for `request.twitter.has_read_access` and `request.twitter.has_write_access`.

[pyramid_simpleauth]: http://github.com/thruflo/pyramid_simpleauth
[pyramid_twitterauth]: http://github.com/thruflo/pyramid_twitterauth
[tweepy]: https://github.com/tweepy/tweepy
