# pelican-jsonfeed #

A Pelican plugin to generate a [JSON Feed](https://jsonfeed.org). The initial version will implement a main feed, but won't support AUTHOR, CATEGORY, etc feeds.

Enable it by setting the `JSON_FEED` setting in `pelicanconf.py` or `publishconf.py`. This works the same as `RSS_FEED` or `ATOM_FEED`.

# Features #

- Supports author name from the `AUTHOR` setting in `pelicanconf.py`.
- Supports author URL from the `AUTHOR_LINK` setting in `pelicanconf.py`.
- Supports WebSub hubs, through the `WEBSUB_HUB` setting in `pelicanconf.py`. Right now, it only supports a single hub, not the array that it should be able to support.

# Limitations #

- Doesn't support a custom `user_comment`.
- Doesn't support `next_url`.
- Doesn't support `icon` or `favicon` for feed icons.
- Doesn't support author avatars.
- Doesn't support the feed level `expired` property.
- ID is forced to the item's permalink, which is different from Pelican's behavior.
- Doesn't support `content_text` for items.
- Doesn't support `summary` for items.
- Doesn't support `image` for items.
- Doesn't support `banner_image` for items.
- Doesn't support `attachments`, yet.
