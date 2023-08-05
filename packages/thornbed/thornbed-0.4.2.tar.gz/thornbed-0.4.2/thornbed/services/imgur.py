""" Imgur data processor

    Since Imgur doesn't provide oEmbed interface, we have to query data using
    their API, so this is a Wrapper for their API service.

    http://imgur.com/gallery/NiK0X
    http://imgur.com/BynR8
    http://i.imgur.com/BynR8.png
    http://i.imgur.com/BynR8s.png

    images can be png, jpg or gif

    json returned by imgur

    {
        "image":
            {
                "image": {
                            "title": null,
                            "caption": null,
                            "hash": "BynR8",
                            "datetime": "2011-08-30 23:45:13",
                            "type": "image\/jpeg",
                            "animated": "false",
                            "width": 500,
                            "height": 578,
                            "size": 75375,
                            "views": 358449,
                            "bandwidth": 27018093375
                            },
                "links": {
                            "original": "http:\/\/i.imgur.com\/BynR8.jpg",
                            "imgur_page": "http:\/\/imgur.com\/BynR8",
                            "small_square": "http:\/\/i.imgur.com\/BynR8s.jpg",
                            "large_thumbnail": "http:\/\/i.imgur.com\/BynR8l.jpg"
                         }
            }
    }
    
"""
from urlparse import urlparse
import re
from urllib2 import urlopen, HTTPError
import simplejson as json

imgur_endpoint = 'http://api.imgur.com/2/image/%s.json'

def lookup(url, **kwargs):
    pr = urlparse(url)
    path = pr.path
    # we are planning to support albums in a near future, not for now or not :P
    if not re.search('(i\.)?imgur.com', url) or re.search('imgur.com\/a\/', url):
        return None
    gallery = re.search('gallery', url)
    direct_link = re.search('\/(\w){5}(\.gif|\.jpg|\.png)$', path)
    thumb = re.search('\/(\w){5}(s|l|b|m|t)(\.gif|\.jpg|\.png)$', path)
    page = re.search('\/(\w){5}$', path)
    ptype = 'jpg'
    if gallery or page:
        pic_id = re.search('(\/gallery\/)?\/(\w)*$', path).group()[1:]
    elif thumb:
        pic_id = thumb.group()[1:-5]
    elif direct_link:
        rps = direct_link.group()
        pic_id = rps[1:-4]
        ptype = rps[-3:]
    else:
        return None

#    Reached API usage limits, create links by hand though
#    try:
#        buf = urlopen(imgur_endpoint % pic_id).read()
#    except HTTPError:
#        return None
#    data = json.loads(buf)
#    if 'error' in data:
#        # TODO: has oEmbed any kind of error status?
#        return None
    # thumbs are always .jpg
    thumbnail_url = 'http://i.imgur.com/%ss.jpg' % pic_id
    imgur_page = 'http://imgur.com/%s' % pic_id
    url = 'http://i.imgur.com/%s.%s' % (pic_id, ptype)
    res = {
        'type': 'photo',
        'version': '1.0',
        'provider_name': 'imgur.com',
        'provider_url': 'http://imgur.com',
        'thumbnail_url': thumbnail_url,
        'imgur_page': imgur_page,
        'url': url,
        'width': '',
        'height': '',
        }

    return res
