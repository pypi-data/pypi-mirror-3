# Django CCThumbs

## Status

Experiemental

## About

Django CCThumbs is a fork of [django-thumbs][0] and is available under the [3 Clause BSD license][1]

The main difference of from django-thumbs is that if the sizes argument is omitted from the ImageFileField then sizes picks up a default so that thumbnails are always generated.

If [south][2] is in your installed apps then an introspection rule will be made available to aid working with migrations.

[0]: http://code.google.com/p/django-thumbs/
[1]: http://www.opensource.org/licenses/bsd-3-clause
[2]: http://south.aeracode.org/
