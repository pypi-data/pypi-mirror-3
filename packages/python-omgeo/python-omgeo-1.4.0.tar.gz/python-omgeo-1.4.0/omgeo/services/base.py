import copy
from datetime import datetime
from json import loads
import logging
import socket
import time
from traceback import format_exc
from urllib import urlencode
from urllib2 import HTTPError, urlopen, URLError
from xml.dom import minidom

logger = logging.getLogger(__name__)

class UpstreamResponseInfo():
    """
    Class describing the API call result from an upstream provider.
    For cleaning and consistency, set attributes using the given methods.
    
    Required arguments:
    ===================
    geoservice       -- name of the upstream provider used
    
    Optional arguments:
    ===================
    response_code    -- HTTP response code (default None)
    response_time    -- time in milliseconds that it takes to get a
                        response (default None)
    success          -- indicates if the API call was successful. A 200 response
                        with no candidates is still considered a success.
                        (default True)
    errors           -- a list of human-readable error descriptions
    """
    def set_response_code(self, response_code):
        if response_code is not None and type(response_code) is not int:
            raise Exception('response_code must be an integer.')
        else:
            self.response_code = response_code
            
    def set_response_time(self, response_time):
        if response_time is not None:
            if type(response_time) not in (int, float):
                raise Exception('If response_time is provided,'
                                'it must be an integer or float.')
            elif response_time < 0:
                raise Exception('response_time cannot be negative.')
            self.response_time = int(round(response_time))
        else:
            self.response_time = None        
            
    def set_success(self, success):
        if type(success) is not bool:
            raise ('success must be a boolean value.')
        else:
            self.success = success
    
    def __init__(self, geoservice, response_code=None, response_time=None, 
                 success=True, errors=[]):
        self.geoservice = geoservice
        self.set_response_code(response_code)
        self.set_response_time(response_time)
        self.set_success(success)
        self.errors = errors


class GeocodeService():
    """
    A tuple of classes representing the geocoders that will be used
    to find addresses for the given locations
    """

    _endpoint = ''
    """
    API endpoint URL to use
    """

    def __init__(self, preprocessors=None, postprocessors=None,
                 settings=None):
        """
        Overwrite _preprocessors, _postprocessors, and _settings
        if they are set.
        """

        self._preprocessors = []
        """
        Preprocessor classes to apply to the given PlaceQuery, usually
        overwritten in subclass.
        """
        self._postprocessors = []
        """
        Postprocessor classes to apply to the list of Candidates obtained, 
        usually overwritten in subclass.
        """
        self._settings = {}
        """
        Settings for this geocoder, usually overwritten in subclass
        """
        if preprocessors is not None:
            self._preprocessors = preprocessors
        if postprocessors is not None:
            self._postprocessors = postprocessors
        if settings is not None:
            for key in settings:
                self._settings[key] = settings[key]

    def _settings_checker(self, required_settings=None, accept_none=True):
        """
        Take a list of required _settings dictionary keys
        and make sure they are set. This can be added to a custom
        constructor in a subclass and tested to see if it returns ``True``.

        Arguments:
        ==========
        required_settings   -- A list of required keys to look for.
        accept_none         -- Boolean set to True if None is an acceptable
                               setting. Set to False if None is not an
                               acceptable setting.

        Return values:
        ==============
         * bool ``True`` if all required settings exist, OR
         * str ``keyname`` for the first key that is not found in _settings.
        """
        if required_settings is not None:
            for keyname in required_settings:
                if keyname not in self._settings:
                    return keyname
                if accept_none is False and self._settings[keyname] is None:
                    return keyname
        return True
    
    def _get_response(self, endpoint, query):
        """Returns response or False in event of failure"""
        timeout_secs = self._settings.get('timeout', 10)
        try:
            response = urlopen('%s?%s' % (endpoint, urlencode(query)),
                               timeout=timeout_secs)
        except Exception as ex:
            if type(ex) == socket.timeout:
                raise Exception('API request timed out after %s seconds.') % timeout_secs
            else:
                raise ex
        if response.code != 200:
            raise Exception('Received status code %s for %s. Content is:\n%s'
                            % (self.get_service_name(), response.read()))
        return response
    
    def _get_json_obj(self, endpoint, query):
        """
        Return False if connection could not be made.
        Otherwise, return a response object from JSON.
        """
        response = self._get_response(endpoint, query)
        content = response.read()
        try:  
            return loads(content)
        except ValueError:
            raise Exception('Could not decode content to JSON:\n%s' % self.__class__.__name__, content)

    def _get_xml_doc(self, endpoint, query):
        """
        Return False if connection could not be made.
        Otherwise, return a minidom Document.
        """
        response = self._get_response(endpoint, query)
        return minidom.parse(response)

    def _geocode(self, place_query):
        """
        Given a (preprocessed) PlaceQuery object,
        return a list of of Candidate objects.
        """
        raise NotImplementedError(
            'GeocodeService subclasses must implement _geocode().')

    def geocode(self, pq):
        """
        Given an unprocessed PlaceQuery object, return a two-part tuple
        including a post-processed list of Candidate objects 
        and an UpstreamResponseInfo object if an API call was made.
        
        Examples:
        =========
        Preprocessor throws out request:
            ([], None)
            
        Postprocessor throws out some candidates:
            ([<Candidate obj>, <Candidate obj>], <UpstreamResponseInfo obj>)
            
        Postprocessor throws out all candidates:
            ([], <UpstreamResponseInfo obj>)
            
        An exception occurs while making the API call:
            ([], <UpstreamResponseInfo obj>)
        """
        processed_pq = copy.copy(pq)
        start_time = time.time()
        logger.debug('%s: BEGINNING PREPROCESSING FOR %s' % (time.time() - start_time,
                                                             self.get_service_name()))
        for p in self._preprocessors:
            processed_pq = p.process(processed_pq)
            logger.debug('%s: Preprocessed through %s' % (time.time() - start_time, p))
            if processed_pq == False:
                return [], None
        upstream_response_info = UpstreamResponseInfo(self.get_service_name())
        try:
            start = datetime.now()
            candidates = self._geocode(processed_pq)
            end = datetime.now()
            upstream_response_info.set_response_time(1000 * (end - start).total_seconds())
            logger.info('GEOCODER: %s; results %d; time %s;' %
                (self.get_service_name(), len(candidates), upstream_response_info.response_time))
        except:
            upstream_response_info.set_success(False)
            upstream_response_info.errors.append(format_exc())
            logger.info('GEOCODER: %s; EXCEPTION:\n%s' %
                (self.get_service_name(), format_exc()))
            return [], upstream_response_info
        if len(candidates) > 0:
            logger.debug('%s: BEGINNING POSTPROCESSING FOR %s' % (time.time() - start_time,
                                                                  self.get_service_name()))
            for p in self._postprocessors: # apply universal candidate postprocessing
                candidates = p.process(candidates) # merge lists
                logger.debug('%s: Postprocessed through %s' % (time.time() - start_time, p))
        return candidates, upstream_response_info
    
    def get_service_name(self):
        return self.__class__.__name__
