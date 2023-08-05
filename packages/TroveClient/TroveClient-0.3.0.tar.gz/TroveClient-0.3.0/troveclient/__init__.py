#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    A Trove Client API interface using OAuth2
    This is a big re-write using OAuth2 and /v2 API calls
"""
__all__ = ('TroveAPI', 'TroveError',
        'get_request_token', 'get_authorization_url', 'get_access_token','get_photos', 'push_photos', '__version__')
__author__ = 'Nick Vlku, Jesse Emery'
__status__ = "Beta"
__dependencies__ = ('python-dateutil', 'simplejson', 'urllib', 'urllib2', 'oauth')
__version__ = '0.3.0'

# This code is lovingly crafted in 
#   Brooklyn, NY (40°42′51″N, 73°57′12″W)
#   and San Francisco, CA (37°46′38″ N, 122°24′40″ W)
#
# Typical MIT license below:
#
# Copyright (c) 2011 YourTrove, Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import urllib
import urllib2
import random
import time

import datetime
import simplejson


from urllib2 import HTTPError
from dateutil.parser import *

from troveclient import JSONFactories
from troveclient.JSONFactories import make_nice

WEB_BASE = 'https://www.yourtrove.com'
API_WEB_BASE = 'https://api.yourtrove.com'

VERSION_WEB_BASE = '/v2'
PREVIOUS_VERSION_WEB_BASE = "/v1"

AUTHENTICATE_URL = WEB_BASE + '/oauth2/authenticate/'
ACCESS_TOKEN_URL = WEB_BASE + '/oauth2/access_token/' 

CONTENT_ROOT_URL = API_WEB_BASE + VERSION_WEB_BASE + '/content'
USER_INFO_URL = API_WEB_BASE + VERSION_WEB_BASE +'/user/'
ADD_URLS_FOR_SERVICES_URL = API_WEB_BASE + VERSION_WEB_BASE + '/services/'
CREATE_AND_AUTH_URL = API_WEB_BASE + VERSION_WEB_BASE + '/services/%s/bounceback/'

def _oauth_version():
    return '2'

class TroveError():
    """The :class:`~troveclient.TroveError` is returned when the client receives back an error. It contains a standard http_error object
    """
    def __init__(self, http_error, request):
        self.http_error = http_error
        self.request = request        
        
    def __repr__(self):
        return "<TroveError with Error Code: \"%s-%s\" and Body: \"%s\">" % (self.http_error.code, self.http_error.msg, self.http_error.read())
    
class RequiresAccessTokenError():
    """The :class:`~troveclient.RequiresAccessTokenError` is returned when a call is attempted that requires to be authenticated
    """
    def __init__(self):
        pass

    def __repr__(self):
        return "<RequiresAccessTokenError>"
    
class LocalError():
    """:class:`~troveclient.LocalError` is returned when a call is made with invalid or missing parameters
    """
    def __init__(self, msg):
        self.msg = msg
        
    def __repr__(self):
        return "<LocalError with msg: %s>" % (self.msg, )


class TroveAPI():
    """The base class for all Trove client actions
    
    :param client_id: A string of your application's YourTrove client ID
    :param client_secret:  A string of your application's YourTrove client Secret
    :param redirect_uri: URL that the user should be returned to when they are asked to authorize.  Needs to match your application settings
    :param scope: A list of strings for scopes of the client.Valid options: 'photos', 'checkins', 'status'
    :param access_token: An access token string that is used to make requests on behalf of a user
    """

    DEBUG = False

    def __init__(self, client_id, client_secret, redirect_uri, scope=None, access_token=None):
        self._access_token = access_token
        if scope is not None:
            self._scope = scope
        else:
            # se the default to all 
            self._scope = ['photos', 'checkins', 'status']
        self.client_id = client_id
        self.client_secret = client_secret
        self._urllib = urllib2
        self.redirect_uri = redirect_uri
        self._initialize_user_agent()
        
    def _initialize_user_agent(self):
        user_agent = 'YourTrove Python Client - Python-urllib/%s (python-trove/%s)' % \
                     (self._urllib.__version__, __version__)
        self.set_user_agent(user_agent)
                
    def set_access_token(self, access_token):
        self._access_token = access_token
        
    def set_user_agent(self, user_agent):
        self._useragent = user_agent
        
    def __make_oauth_request(self, url, parameters=None, token=None, method="POST"):
        if token is not None:
            parameters['access_token'] = access_token

        try:
            if method is "POST":
                request = self._urllib.Request(url)
                request.add_header('User-agent', self._useragent)
                encoded_params = urllib.urlencode(parameters)
                if self.DEBUG:
                    print url + " : Parameters=" + parameters.__str__() + " : Encoded Parameters=" + encoded_params
                    raw_input()
                response = self._urllib.urlopen(request, encoded_params)
                return response
            else:
                encoded_params = urllib.urlencode(parameters)
                request = self._urllib.Request(url + '?' + encoded_params)  
                request.add_header('User-agent', self._useragent)
                if self.DEBUG:
                    print url + '?' + encoded_params
                    raw_input()
                response = self._urllib.urlopen(request)
                return response
            
        except HTTPError, e:
            error = TroveError(e, request)
            raise error

    def get_authenticate_url(self):
        """      Returns an authentication URL that the user should be redirected to, so they can authorize your app.
            
        """
                    
        parameters = {  'client_id'     : self.client_id,
                        'response_type' : 'code',
                        'redirect_uri'  : self.redirect_uri 
                        }
        encoded_params = urllib.urlencode(parameters)
        return str.join("",[AUTHENTICATE_URL, "?", encoded_params])
    
    def __make_oauth2_request(self, base_url, parameters=None, signed=False, post=False):
        try:
            if signed and self._access_token is None:
                raise RequiresAccessTokenError()

            if parameters is not None:
                copied_params = parameters.copy()
            else:
                copied_params = {}
        
            if signed:
                copied_params['access_token'] = self._access_token
    
            encoded_params = urllib.urlencode(copied_params)
        
            if post:
                request = self._urllib.Request(base_url)
                request.add_header('User-agent', self._useragent)
                if self.DEBUG:
                    print base_url + " : Parameters=" + copied_params.__str__() + " : Encoded Parameters=" + encoded_params
                    raw_input()
                return self._urllib.urlopen(request, encoded_params)
            else:
                request = self._urllib.Request(base_url + '?' + encoded_params)  
                request.add_header('User-agent', self._useragent)
                if self.DEBUG:
                    print base_url + '?' + encoded_params
                    raw_input()
                
                return self._urllib.urlopen(request)
        except HTTPError, e:
            error = TroveError(e, request)
            raise error

    def get_access_token(self, code=None):
        """      Returns an access_token string that is used to make requests on behalf of a user

                :param code: A string representing the code returned from a user auth request
        """
        parameters = {  'client_id'     : self.client_id,
                        'grant_type' : 'authorization_code',
                        'redirect_uri'  : self.redirect_uri,
                        'client_secret' : self.client_secret,
                        'code'          : code
                        }
        response = self.__make_oauth2_request(ACCESS_TOKEN_URL, parameters=parameters)

        r = simplejson.loads(response.read())
        access_token = r.get('access_token')
        self._access_token = access_token
        return access_token
        
    def get_user_info(self):
        """     Gets meta information about a User.  *This call requires an access token.*
        
                Returns a map of User Metainformation, including their name, email address and identities for scope you've initialized this client for.  
                User's will have the ability to restrict what is being sent back, so you make no assumptions.
        """

        if self._access_token is None:
            raise RequiresAccessTokenError()
        response = self.__make_oauth2_request(USER_INFO_URL, signed=True)
        
        return simplejson.loads(response.read())
    
    def __get_internal(self, query=None, content_type='photos'):
        if self._access_token is None:
            raise RequiresAccessTokenError()
        
        base_url = CONTENT_ROOT_URL + "/" + content_type + '/'
        parameters = {}
        if query is not None:
            query_post = simplejson.dumps(query, cls=JSONFactories.encoders.get_encoder_for(query))
            parameters['query'] = query_post

        response = self.__make_oauth2_request(base_url, parameters=parameters, signed=True, post=True)
        
        results = simplejson.loads(response.read())
        results = make_nice.make_it_nice(results)
        return results
        
    def get_photos(self,query=None): 
        """     Retrieves a user's photos based on the Query passed in. *This call requires an access token.*
                Returns a :class:`~troveclient.Objects.Result` object that contains the results of your query
                
                :param query: An instance of :class:~`troveclient.Objects.Query~ object.  If none is passed, assumes page 1 with a count of 50.
        """
        return self.__get_internal(query)
        
    def get_checkins(self,query=None): 
        """     Retrieves a user's checkins based on the Query passed in. *This call requires an access token.*
                Returns a :class:`~troveclient.Objects.Result` object that contains the results of your query
                
                :param query: An instance of :class:~`troveclient.Objects.Query~ object.  If none is passed, assumes page 1 with a count of 50.
        """
        return self.__get_internal(query,'checkins')

    def get_status(self,query=None): 
        """     Retrieves a user's status updates based on the Query passed in. *This call requires an access token.*
                Returns a :class:`~troveclient.Objects.Result` object that contains the results of your query
                
                :param query: An instance of :class:~`troveclient.Objects.Query~ object.  If none is passed, assumes page 1 with a count of 50.
        """
        return self.__get_internal(query,'status')


    def push_photos(self, user_id,  photos_list= []):
        """     Pushes a list of photos for user_id specified into Trove associated to your service. *This call requires an access token.*
                Returns a map of the status of your push.
                
                :param user_id: The user id of the user on YOUR service.
                :param photos_list: A list of :class:~`troveclient.Objects.Photo`
        """
        if self._access_token is None:
            raise RequiresAccessTokenError()
        
        if photos_list is None: 
            return
        
        parameters = {}
        json_photos_list = simplejson.dumps(photos_list, cls=JSONFactories.encoders.get_encoder_for(photos_list[0]))
                                            
        parameters['object_list'] = json_photos_list
        parameters['number_of_items'] = len(photos_list)
        parameters['content_type'] = 'photos'
        parameters['user_id'] = user_id
        
        base_url = CONTENT_ROOT_URL + "/" + "photos" + '/'
        
        response = self.__make_oauth2_request(base_url, parameters=parameters, signed=True, post=True)

        return simplejson.loads(response.read())
        
    def get_services(self):
        """     Gets all the services Trove provides for the scope set for this client.  *This call requires an access token.*
                Returns a list of service names
        """        
        if self._access_token is None:
            raise RequiresAccessTokenError()

        response = self.__make_oauth2_request(ADD_URLS_FOR_SERVICES_URL, signed=True)
        services_json = simplejson.loads(response.read())
        service_decoder = make_nice.get_decoder_for("service")
        services = [service_decoder.get_object(service_json) for service_json in services_json]
            
        return services
    
    def get_url_for_service(self, service_name, redirect_url=None):
        """     This creates a URL that allows a user to add a service to their Trove and then immediately bounce back to your service.  If a 
                redirect_url URL is specified it uses that, otherwise it uses your application's default.  *This call requires an access token.*
                Returns a one-time use URL for the user
                
                :param service: The service name, usually from the list returned by get_services
                :param redirect_url: A redirect URL override.  The default is your application's callback.
        """        
        
        services = self.get_services()
        found_it = False
        for service in services:
            if str.lower(str(service.name)) == str.lower(str(service_name)):
                found_it = True
                break
        if found_it:            
            parameters = {}
            if redirect_url is not None:
                parameters['redirect_url'] = redirect_url
            else:
                parameters['redirect_url'] = self.redirect_uri
            url = API_WEB_BASE + VERSION_WEB_BASE + "/services/%s/bounceback/"  % (str.lower(service.name),)
            response = self.__make_oauth2_request(url, parameters=parameters, signed=True)
            return response.read()
        else: 
            raise LocalError("Could not find service name " + service_name)
        
    def login_and_auth_via_service(self, service, redirect_url=None):
        """     This creates a URL that allows a user to create a Trove account implicitly by adding this service to their Trove.
                It immediately bounces back to your service.  If a  redirect_url URL is specified it uses that, otherwise it uses your
                application's default.  *This call requires an access token.*
                
                Returns a one-time use URL for the user
                
                :param service: The service name, usually from the list returned by get_services
                :param redirect_url: A redirect URL override.  The default is your application's callback.
        """        

        parameters = {}
        parameters['client_id'] = self.client_id
        if redirect_url is None:
            redirect_url = self.redirect_uri
        parameters['redirect_url'] = redirect_url
        
        encoded_parameters = urllib.urlencode(parameters)
        
        req = urllib2.Request(API_WEB_BASE + VERSION_WEB_BASE + "/services/%s/login_and_auth/?%s"  % (service, encoded_parameters))
        self.response = urllib2.urlopen(req)
        return self.response.read()
