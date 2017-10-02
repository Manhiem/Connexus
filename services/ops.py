
# Database related operation
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from models import Image, Stream, Pigeon, Subscription


def create_stream(pigeon_id, name, cover_url,
                  sub_list, tag_list):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    stream = Stream()
    stream.key = ndb.Key(Stream, name, parent=pigeon_key)
    stream.name = name
    stream.cover_url = cover_url
    stream.tags = tag_list
    stream.put()
    for pid in sub_list:
        if not pigeon_exists(pid):
            create_pigeon(pid)
        create_subscription(pid, name)
    return


def stream_exists(name):
    if Stream.query(Stream.name == name).fetch():
        return True
    return False


def get_self_stream(pigeon_id):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    stream_list = Stream.query(ancestor=pigeon_key).fetch()
    return map(_get_stream_dict, stream_list)


def get_sub_stream(pigeon_id):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    sub_list = Subscription.query(
        Subscription.Pigeon_key == pigeon_key).fetch()
    stream_list = map(lambda sub: sub.Stream_key.get(), sub_list)
    return map(_get_stream_dict, stream_list)


def pigeon_exists(pigeon_id):
    if Pigeon.query(Pigeon.pigeon_id == pigeon_id).fetch():
        return True
    return False


def create_pigeon(pigeon_id):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    pigeon = Pigeon()
    pigeon.key = pigeon_key
    pigeon.pigeon_id = pigeon_id
    pigeon.put()
    return


def _get_stream_dict(stream):
    stream_dict = dict()
    stream_dict['Name'] = stream.name
    image_list = Image.query(ancestor=stream.key).order(Image.upload_date).fetch()
    if image_list:
        stream_dict['LastPictDate'] = image_list[0].upload_date
        stream_dict['NumberOfPict'] = len(image_list)
    else:
        stream_dict['LastPictDate'] = stream.create_date
        stream_dict['NumberOfPict'] = 0
    stream_dict['Views'] = stream.num_of_views
    return stream_dict


def get_all_stream():
    stream_list = Stream.query().order(Stream.create_date).fetch()
    return map(lambda s: {"Name": s.name, "CoverPage": s.cover_url},
               stream_list)


def get_single_stream(name):
    stream_list = Stream.query(Stream.name == name).fetch()
    if not stream_list:
        return []
    stream = stream_list[0]
    # count the number of views and discard the overtime logs
    delta = timedelta(hours=1)
    for i, dt in enumerate(stream.view_dates):
        if datetime.now() - dt < delta:
            stream.view_dates = stream.view_dates[i:]
            break
    stream.view_dates.append(datetime.now())
    stream.num_of_views = len(stream.view_dates)
    stream.put()
    # return images
    img_list = Image.query(ancestor=stream.key).order(Image.upload_date).fetch()
    return map(lambda img: img.url, img_list)


def delete_stream(name):
    stream_list = Stream.query(Stream.name == name).fetch()
    if stream_list:
        stream_list[0].key.delete()
    return


def create_subscription(pigeon_id, name):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    stream_key = ndb.Key(Stream, name, parent=pigeon_key)
    sub = Subscription()
    sub.Pigeon_key = pigeon_key
    sub.Stream_key = stream_key
    sub.put()
    return


def delete_subscription(pigeon_id, name):
    pigeon_key = ndb.Key(Pigeon, pigeon_id)
    stream_key = ndb.Key(Stream, name, parent=pigeon_key)
    sub_list = Subscription.query(Subscription.Pigeon_key == pigeon_key,
                                  Subscription.Stream_key == stream_key).fetch()
    if sub_list:
        sub_list[0].key.delete()
    return


def get_trending_stream():
    stream_list = Stream.query().order(Stream.num_of_views).fetch(3)
    return map(lambda s: {"Name": s.name,
                          "CoverPage": s.cover_url,
                          "NumberOfViews": s.num_of_views},
               stream_list)
