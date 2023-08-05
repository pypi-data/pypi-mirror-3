import datetime 

class Query:
    
    def __init__(self):
        self.services = None
        self.content_types = []
        self.tags_optional = []
        #: A list of required tags
        self.tags_required = []
        #: Date "from" as a :class:`datetime.datetime` object
        self.date_from = None
        #: Date "to" as a :class:`datetime.datetime` object
        self.date_to = None
        self.force_update = False
        self.attributes = {}
        #: Page number for query
        self.page = 1
        #: Count for query
        self.count = 50
        self.geo = {} 
        #: Sort field for query.  Default is timestamp descending
        self.order_by = []       
        #: A list of identity ids (from :func:`~troveclient.TroveAPI.get_user_info`) that you are querying for.  Default is ALL.
        self.identities_by_id = []
        #: A request for a specific asset with specific Trove ID.  This causes all other parameters to be ignored.
        self.trove_id = None
        
    def add_geo_bounds(self, lower_left_coords, upper_right_coords):
        self.geo['bounds'] = { 'sw': lower_left_coords,
                            'ne': upper_right_coords}

    def add_geo_near(self, center_point, radius=5): 
        self.geo['near'] = {    
                            'center': center_point, 
                            'radius': radius
                        }
    
    def add_order_by(self, value):
        """ This controls the sort for a query.   The query is first executed by trove, and then sorted.
        
            :param value: A string representing the field.  Strings prefixed with a **-** are considered descending.  The default value is *-service_date*                
        """

        self.order_by.append(value)

    def remove_order_by(self, value):
        """ Removes an order_by from the list.  
            
            :param value: A string representing the field you'd like to remove from the sort.   
        """

        self.order_by.remove(value)

    def add_identity_id(self, id):
        """ Adds a specific identity to the query.  The default is empty (which means ALL identities you have access to.)
        
            :param id: An identity id from the Trove id.
        """
        self.identities_by_id.append(id)

    def remove_identity_id(self, id):
        """ Removes a specific identity to the query.  The default is empty (which means ALL identities you have access to.)
        
            :param id: An identity id from the Trove id.
        """        
        self.identities_by_id.remove(id)

    def add_content_type(self, id):
        self.content_types.append(id)
        
    def remove_content_type(self, id):
        self.content_types.remove(id)
       

    @classmethod
    def get_photo_by_trove_id(cls,id):
        """ A convenience method to load a specific single image from Trove by ID.
            
            :param id: The trove id of the specific item you want to pull (Note:  It has to be owned by the user.)
        """

        q = Query()
        q.trove_id = id
        return q
    
class Result:
    """ 
        This is returned by a query to Trove 
    """
    
    def __init__(self):
        #: Total number of results for a query on Trove's systems
        self.total_number_of_results = 0
        #: The number of results returned in this instance (*50* out of 450)
        self.count = 0
        #: The page number of results.  E.g., if page number 2 and count 50, this would be results 50-100.
        self.page = 1
        #: The actual objects of returned.  Typically an object like :class:`~troveclient.Objects.Photo`.
        self.objects = []
       
    def __str__(self):
        return "Result - Count: %s, Page %s, Total number of results: %s, Results: %s" % (self.count, self.page, self.total_number_of_results, self.objects) 
    
    def __repr__(self):
        return "<troveclient.Objects.Result instance with count %s, total_number_of_results %s and page %s>"  % (self.count, self.total_number_of_results, self.page)

    
class Photo:
    """ 
        Represents a Photo object returned from Trove
    """
    def __init__(self):
        #: The service this photo is from.
        self.service = ""
        #: The title of this photo
        self.title = ""
        #: The account that owns it
        self.owner = ""
        #: A description or summary of the photo
        self.description = ""
        #: The service\'s ID of the photo (not the Trove ID)  *REQUIRED FIELD*
        self.id = ""
        #: A dict of URLs.  All photos have at least "original", but most have thumbnail too.  *REQUIRED FIELD*
        self.urls = {}  # thumbnail, large  //tn:48,96,192  original is required
        #: Keywords for a photo
        self.tags = [] 
        #: Date photo was created in service.  *REQUIRED FIELD*
        self.date = datetime.datetime.now()
        #: An album or set id
        self.album_id = ""
        #: The license of this photo
        self.license = ""
        #: Photo height
        self.height = 0
        #: Photo width
        self.width = 0
        #: Geo coordinates for photo.  Either none or contains a [Latitude, Longitiude]
        self.loc = None
        #: Is this photo public or private?
        self.public = False
        #: The original web page context for this photo from the service.
        self.original_web_url = ""        
        #: The internal unique Trove ID for this photo
        self.trove_id = ""

    def __str__(self):
        return 'Photo "%s" from %s on %s' % (self.title, self.owner, self.service)
    
    def __repr__(self):
        return "<troveclient.Objects.Photo instance with id %s from %s@%s>" % (self.id, self.owner, self.service)
        
class Service:
    """
        Represents a Service that is available in Trove
    """
    def __init__(self):
        self.description = ""
        self.id = ""
        self.name = ""
        self.slug = ""
        self.service_icon = ""
        self.url = ""
        
    def __str__(self):
        return "Trove Service %s" % (self.name, )
    
    def __repr__(self):
        return "<troveclient.Objects.Service:%s:%s" % (self.id, self.name)
        
class Checkin:
    """ 
        Represents a Checkin object returned from Trove
    """    
    def __init__(self):
        self.description = ""
        self.id = ""
        self.trove_id = ""
        self.service = ""
        self.service_date = None
        self.shout = ""
        self.owner = ""


    def __str__(self):
        if self.venue is not None:
            return "Trove Checkin %s %s at %s" % (self.service,  self.owner, self.venue.name)
        else:
            return "Trove Checkin %s %s" % (self.service,  self.owner)
            

    def __repr__(self):
        return "<troveclient.Objects.Checkin:%s:%s:%s" % (self.id, self.service, self.owner)
        
class Venue:
    """ 
        Represents a Venue object returned from Trove
    """    
    def __init__(self):
        self.address = ""
        self.location = None
        self.city = ""
        self.state = ""
        self.category = ""
        self.cross_street = ""
        self.name = ""
        self.phone_number = ""
        self.postal_code = ""
        self.twitter_id = ""
        self.verified = False

    def __repr__(self):
        return "<troveclient.Objects.Venue:%s:%s>" % (self.service, self.name)

class Status:
    """
        Represents a Status update from a service in Trove
    """
    def __init__(self):
        self.trove_id = ""
        self.message = ""
        self.type = ""
        self.owner = ""
        self.id = ""
        self.service = ""
        self.date = ""
        self.location = None
        self.place_area = None
        self.public = False
        self.caption = ""
        self.description = ""
        self.name = ""
        
        
    def __str__(self):
        return "Trove Status on %s by %s: %s" % (self.service, self.owner, self.message)

    def __repr__(self):
        return "<troveclient.Objects.Status:%s:%s:%s:%s>" % (self.id, self.service, self.owner, self.message)

        
class Location:
    """ 
        Represents a location returned from Trove
    """    
    def __init__(self, lat=0, lng=0, geohash=""):
        self.lat = lat
        self.lng = lng
        self.geohash = geohash
    
    def from_lat_lng_list(lat_lng):
        l = Location()
        l.lat = lat_lng[0]
        l.lng = lat_lng[1]
        return l


    def __repr__(self):
        return "<troveclient.Objects.Location:[%s,%s]>" % (self.lat,self.lng)  

    def __str__(self):
        return "Location: [%s,%s]" % (self.lat,self.lng)

    from_lat_lng_list = staticmethod(from_lat_lng_list)
    
          
class PlaceArea:
    def __init__(self):
        self.country_code = ""
        self.full_name = ""
        self.service_id = ""
        self.service = ""
        self.name = ""
        self.placearea_type = ""
        self.bounding_box = BoundingBox()
        
    def __str__(self):
        return self.full_name
        
    def __repr__(self):
        return "<troveclient.Objects.PlaceArea:%s:%s:%s>" % (self.service, self.service_id, self.name)
        
class BoundingBox:
    def __init__(self):
        self.upper_left = Location()
        self.lower_right = Location()

    def __str__(self):
        return "BoundingBox: Upper Left: %s Lower Right: %s" % (self.upper_left, self_lower_right)

    def __repr__(self):
        return "<troveclient.Objects.BoundingBox:%s:%s>" % (self.upper_left, self.lower_right)
    
