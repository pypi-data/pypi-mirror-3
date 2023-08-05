from troveclient.Objects import Query, Result, Photo, Service, Status, Location, PlaceArea, BoundingBox, Checkin, Venue

import datetime
import simplejson

class EncoderFactory:
    _encoders = {}

    def register(self, encoder_class):
        if encoder_class.object_name not in self._encoders:
            self._encoders[encoder_class.object_name] = encoder_class

    def deregister(self, encoder_class):
        if encoder_class.object_name not in self._encoders:
            del self._encoders[encoder_class.object_name]

    def get_encoder_for(self, object):
        name = object.__class__.__name__
        if name in self._encoders:
            return self._encoders[name]
        else:
            return None
    
class MakeNiceObjectThing:
    _object_hooks = {}
    
    def register(self, object_hook):
        if object_hook.object_name not in self._object_hooks:
            self._object_hooks[object_hook.object_name] = object_hook
    
    def deregister(self, object_hook):
        if object_hook.object_name not in self._object_hooks:
            del self._object_hooks[object_hook.object_name]

    def make_it_nice(self, dct):
        result = Result()
        result.count = dct['count']
        result.page = dct['page']
        result.total_number_of_results = dct['total_number_of_results']
        results = []
        for item in dct['results']:
            hook = self._object_hooks[item['object_type']]
            object = hook.get_object(item)
            results.append(object)
        result.objects = results
        return result
    
    def get_decoder_for(self, object_name):
        return self._object_hooks.get(object_name, None)

class SomeUsefulJSONUtilities:
    
    def make_it_utc(date_with_no_home):
        from dateutil.tz import tzutc

        if date_with_no_home.tzinfo is None or date_with_no_home.tzinfo=="":
            date_with_no_home = date_with_no_home.replace(tzinfo=tzutc())
        else:
            date_with_no_home = date_with_no_home.astimezone(tzutc())
        
        date_with_no_home = date_with_no_home.replace(tzinfo=None)  
        return date_with_no_home

    make_it_utc = staticmethod(make_it_utc)

# Now We Register Stuff

encoders = EncoderFactory()
make_nice = MakeNiceObjectThing()

class __QueryEncoder(simplejson.JSONEncoder):
    
    object_name = Query().__class__.__name__
    
    def default(self, object):
        
        encoded_list = {}
        if object.trove_id:
            encoded_list['trove_id'] = object.trove_id
        else:
            encoded_list['services'] = object.services
            encoded_list['tags-optional'] = object.tags_optional
            encoded_list['tags-required'] = object.tags_required
            encoded_list['force-update'] = object.force_update
            if object.date_from is not None:
                object.date_from = SomeUsefulJSONUtilities.make_it_utc(object.date_from)
                encoded_list['date-from'] = object.date_from.strftime("%Y-%m-%d %H:%M:%S %Z")
            if object.date_to is not None:
                object.date_to = SomeUsefulJSONUtilities.make_it_utc(object.date_to)
                encoded_list['date-to'] = object.date_to.strftime("%Y-%m-%d %H:%M:%S %Z")
    
            if object.geo is not None and object.geo.has_key('bounds'):
                    if object.geo['bounds'].has_key('sw'):
                        encoded_list['geo_sw'] = object.geo['bounds']['sw']
                    if object.geo['bounds'].has_key('ne'):
                        encoded_list['geo_ne'] = object.geo['bounds']['ne']
    
            if object.geo is not None and object.geo.has_key('near'):
                if object.geo['near'].has_key('center'):
                    encoded_list['geo_near_center'] = object.geo['near']['center']
                if object.geo['near'].has_key('radius'):
                    encoded_list['geo_near_radius'] = object.geo['near']['radius']        
            
            if object.order_by is not None:
                encoded_list['order_by'] = object.order_by
    
                
            encoded_list['count'] = object.count
            encoded_list['page'] = object.page
                    
            encoded_list['attributes'] = object.attributes
            
            encoded_list['identities_by_id'] = object.identities_by_id

        return encoded_list

class __ResultEncoder(simplejson.JSONEncoder):
    
    object_name = Result().__class__.__name__
    
    def default(self, object):
        result = {
                  'total_number_of_results' : object.total_number_of_results,
                  'count' : object.count,
                  'page' : object.page,
                  'results': object.objects
                  }
        return result

class __PhotoEncoder(simplejson.JSONEncoder):
    
    object_name = Photo().__class__.__name__
    
    def default(self, object):
        if object.date is None or object.date is "":
            object_date = ""
        else:
            object_date = object.date.strftime('%Y-%m-%d T %H:%M:%S')
        result = {'service': object.service, 
                    'title': object.title,
                    'owner': object.owner,
                    'description' : object.description,
                    'id': object.id,
                    'urls': object.urls,
                    'tags': object.tags,
                    'date': object_date,
                    'album_id': object.album_id,
                    'license': object.license,
                    'height': object.height,
                    'width': object.width,
                    'public': (object.public is 1 or True),
                    'tags': object.tags,
                    'original_web_url': object.original_web_url,
               }
        
        if object.trove_id is not None:
                result['trove_id'] = object.trove_id
        if object.loc is not None:
                result['latitude'] = object.loc['x']
                result['longitude'] = object.loc['y']                    
        return result

    
encoders.register(__QueryEncoder)
encoders.register(__ResultEncoder)
encoders.register(__PhotoEncoder)

class __PhotoDecoder(simplejson.JSONDecoder):
    object_name = "photo"
    
    def get_object(object):
        p = Photo()
        if object['date'] is None or object['date'] is "":
            p.date = ""
        else:
            date_str = object['date']
            p.date = datetime.datetime.strptime(date_str,'%Y-%m-%d T %H:%M:%S')            
        p.service = object['service']
        p.title = object['title']
        p.owner = object['owner']
        p.description = object['description']
        p.id = object['id']
        p.urls = object['urls']
        p.tags = object['tags']
        p.album_id = object['album_id']
        p.license = object['license']
        p.public = object['public']
        p.height = object['height']
        p.width = object['width']
        if object.has_key('latitude'):
            p.latitude = object['latitude']
        if object.has_key('longitude'):
            p.longitude = object['longitude']
        if object.has_key('trove_id'):
            p.trove_id = object['trove_id']
        return p
    
    get_object = staticmethod(get_object)
    
class __ServiceDecoder(simplejson.JSONDecoder):
    object_name = "service"
    
    def get_object(object):
        s = Service()
        s.description = object.get('description')
        s.id = object.get('id')
        s.name = object.get('name')
        s.slug = object.get('slug')
        s.url = object.get('url')
        s.service_icon = object.get('service_icon')
        return s

    get_object = staticmethod(get_object)
    
class __StatusDecoder(simplejson.JSONDecoder):
    object_name = "status"
    
    def get_object(object):
        s = Status()
        s.trove_id = object.get('trove_id')
        s.owner = object.get('owner')
        s.service = object.get('service')
        service_date = object.get('service_date', None)
        try:
            if service_date is not None:
                s.date = datetime.datetime.strptime(service_date,'%Y-%m-%d T %H:%M:%S')
        except: # Date Missing?
            pass
        s.message = object.get('message')
        s.type = object.get('type')
        s.id = object.get('id')
        s.public = object.get('public', False)
        
        if object.has_key('place'):
            place = object.get('place')
            s.place_area = PlaceArea()
            s.place_area.country_code = place.get("country_code")
            s.place_area.full_name = place.get('full_name')
            s.place_area.name = place.get('name')
            s.place_area.service_id = place.get('id')
            s.place_area.service = "Twitter"
            s.place_area.type = place.get('type')
            if place.has_key('bounding_box'):
                s.place_area.bounding_box = BoundingBox()
                s.place_area.bounding_box.lower_right = Location.from_lat_lng_list(place.get('bounding_box').get('lower_right'))
                s.place_area.bounding_box.upper_left = Location.from_lat_lng_list(place.get('bounding_box').get('upper_left'))
                
        if object.has_key('geolocation'):
            geo = object.get('geolocation')
            
            s.location = Location.from_lat_lng_list(geo.get('coordinates'))
            s.location.geohash = geo.get('geohash')
            
        if object.has_key('subfields'):
            subfields = object.get('subfields', {})
            s.description = subfields.get('description', "")
            s.caption = subfields.get('caption', '')
            s.name = subfields.get('name', '')
            
        return s

    get_object = staticmethod(get_object)

    
class __CheckinDecoder(simplejson.JSONDecoder):
    object_name = "checkin"

    def get_object(object): 
        c = Checkin()
        c.description = object.get('description')
        c.id = object.get('id')
        c.trove_id = object.get('trove_id')
        c.service = object.get('service')
        c.shout = object.get('shout')
        c.owner = object.get('owner')
        service_date = object.get('service_date', None)
        try:
            if service_date is not None:
                s.date = datetime.datetime.strptime(service_date,'%Y-%m-%d T %H:%M:%S')
        except: # Date Missing?
            pass
                    
        if object.has_key('venue'):
            venue_json = object.get('venue', {})
            v = Venue
            v.address = venue_json.get('address')
            v.city = venue_json.get('city')
            v.state = venue_json.get('state')
            if object.has_key('categories'):
                c = object.get('categories', [])
                if c is not None:
                    v.category = c[0].name
            v.cross_street = venue_json.get('cross_street')
            v.name = venue_json.get('name')
            v.phone_number = venue_json.get('phone_number')
            v.postal_code = venue_json.get('postal_code')
            v.twitter_id = venue_json.get('twitter_id')
            v.verified = venue_json.get('verified', False)
            c.venue = v
        
        return c

    get_object = staticmethod(get_object)

make_nice.register(__PhotoDecoder)
make_nice.register(__ServiceDecoder)
make_nice.register(__StatusDecoder)
make_nice.register(__CheckinDecoder)    