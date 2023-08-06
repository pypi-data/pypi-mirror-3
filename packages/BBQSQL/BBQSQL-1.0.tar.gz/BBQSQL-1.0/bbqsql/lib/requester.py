from .query import Query

from bbqsql import utilities
from bbqsql import settings

import grequests
import requests
import gevent 

from math import sqrt
from copy import copy
from time import time
from difflib import SequenceMatcher

__all__ = ['Requester','LooseNumericRequester','LooseTextRequester']

@utilities.debug 
def requests_pre_hook(request):
    #hooks for the requests module to add some attributes
    request.start_time = time()
    return request

@utilities.debug 
def requests_post_hook(request):
    #hooks for the requests module to add some attributes
    request.response.time = time() - request.start_time
    if hasattr(request.response.content,'__len__'): 
        request.response.size = len(request.response.content)
    else: 
        request.response.size = 0
    return request

class EasyMath():
    def mean(self,number_list):
        if len(number_list) == 0:
            return float('nan')

        floatNums = [float(x) for x in number_list]
        means = sum(floatNums) / len(number_list)
        return means

    def stdv(self,number_list,means):
        size = len(number_list)
        std = sqrt(sum((x-means)**2 for x in number_list) / size)
        return std

class Requester(object):
    '''
    This is the base requester. Initialize it with request parameters (url,method,cookies,data) and a 
    comparison_attribute (size,text,time) which is used for comparing multiple requests. One of the 
    request parameters should be a Query object. Call the make_request function with a value. That value
    will be compiled/rendered into the query object in the request, the request will be sent, and the response
    will be analyzed to see if the query evaluated as true or not. This base class compares strictly (if we are looking
    at size, sizes between requests must be identical for them to be seen as the same). Override _test to change this
    behavior.
    '''

    def __init__( self,comparison_attr = "size" , acceptable_deviation = .6, *args,**kwargs):
        '''
        :comparison_attr        - the attribute of the objects we are lookig at that will be used for determiniing truth
        :acceptable_deviation   - the extent to which we can deviate from absolute truth while still being consider true. The meaning of this will varry depending on what methods we are using for testing truth. it has no meaning in the Truth class, but it does in LooseTextTruth and LooseNumericTruth
        '''
        #Truth related stuff
        self.cases = {}

        self.comparison_attr = comparison_attr
        self.acceptable_deviation = acceptable_deviation

        # we require our own hooks for keeping track of time. 
        # if they defined hooks, we need to wrap them in our 
        # hooks so they both get called

        kwargs.setdefault('hooks',{})

        # if they defined pre_request hook, we wrap it with ours
        if 'pre_request' in kwargs['hooks']:
            orig = kwargs['hooks']['pre_request']
            wrapped = lambda request:requests_pre_hook(orig(request))
            kwargs['hooks']['pre_request'] = wrapped

        # otherwise, we just stick with our own hook
        else:
            kwargs['hooks']['pre_request'] = requests_pre_hook            

        # same for post_request hooks
        if 'post_request' in kwargs['hooks']:
            orig = kwargs['hooks']['post_request']
            wrapped = lambda request:requests_post_hook(orig(request))
            kwargs['hooks']['post_request'] = wrapped

        else:
            kwargs['hooks']['post_request'] = requests_post_hook            

        self.request = grequests.request(*args,**kwargs)
    
    @utilities.debug 
    def make_request(self,value="",case=None,rval=None,debug=False):
        '''
        Make a request. The value specified will be compiled/rendered into all Query objects in the
        request. If case and rval are specified the response will be appended to the list of values 
        for the specified case. if return_case is True then we return the case rather than the rval.
        this is only really used for recursing by _test in the case of an error. Depth keeps track of 
        recursion depth when we make multiple requests after a failure. 
        '''
        new_request = copy(self.request)

        #iterate over the __dict__ of the request and compile any elements that are 
        #query objects.
        for elt in [q for q in new_request.__dict__ if isinstance(new_request.__dict__[q],Query)]:
            opts = new_request.__dict__[elt].get_options()
            for opt in opts:
                opts[opt] = value
            new_request.__dict__[elt].set_options(opts)
            new_request.__dict__[elt] = new_request.__dict__[elt].render()
            if debug:
                print "Injecting into '%s' parameter" % elt
                print "It looks like this: %s" % new_request.__dict__[elt]

        #send request.
        glet = grequests.send(new_request)
        glet.join()
        if not glet.get() and type(new_request.response.error) is requests.exceptions.ConnectionError:
            raise utilities.SendRequestFailed("looks like you have a problem")

        #see if the response was 'true'
        if case is None:
            case = self._test(new_request.response)
            rval = self.cases[case]['rval']

        if debug and case:
            print "we will be treating this as a '%s' response" % case
            print "for the sample requests, the response's '%s' were the following :\n\t%s" % (self.comparison_attr,self.cases[case]['values'])
            print "\n"


        self._process_response(case,rval,new_request.response)

        return self.cases[case]['rval']

    @utilities.debug 
    def _process_response(self,case,rval,response):
        self.cases.setdefault(case,{'values':[],'rval':rval})

        #get the value from the response
        value = getattr(response,self.comparison_attr)

        #store value
        self.cases[case]['values'].append(value)

        #garbage collection
        if len(self.cases[case]['values']) > 10:
            del(self.cases[case]['values'][0])      

    def _test(self,response):
        '''test if a value is true'''
        value = getattr(response,self.comparison_attr)
        for case in self.cases:
            if value in self.cases[case]['values']:
                return case

class LooseNumericRequester(Requester):
    def _process_response(self,case,rval,response):
        self.cases.setdefault(case,{'values':[],'rval':rval,'case':case})

        #get the value from the response
        value = getattr(response,self.comparison_attr)

        #store value
        self.cases[case]['values'].append(value)

        #garbage collection
        if len(self.cases[case]['values']) > 10:
            del(self.cases[case]['values'][0])

        #statistics :D
        math = EasyMath()
        m = math.mean(self.cases[case]['values'])
        s = math.stdv(self.cases[case]['values'], m)

        self.cases[case]['mean'] = m
        self.cases[case]['stddev'] = s

        self._check_for_overlaps()

    def _check_for_overlaps(self):
        '''make sure that cases with different rvals aren't overlapping'''
        for outer in self.cases:
            for inner in self.cases:
                #if the return vals are the same, it doesn't really matter if they blend together.
                if self.cases[inner]['rval'] != self.cases[outer]['rval']:
                    math = EasyMath()
                    mean_stddev = math.mean([self.cases[inner]['stddev'],self.cases[outer]['stddev']])
                    diff = abs(self.cases[inner]['mean'] - self.cases[outer]['mean'])
                    if diff <= mean_stddev*2: 
                        raise utilities.TrueFalseRangeOverlap("truth and falsity overlap")

    def _test(self,response):
        '''test a value'''
        #make an ordered list of cases
        ordered_cases = []
        for case in self.cases:
            if len(ordered_cases) == 0:
                ordered_cases.append(self.cases[case])
            else:
                broke = False
                for index in xrange(len(ordered_cases)):
                    if self.cases[case]['mean'] <= ordered_cases[index]['mean']:
                        ordered_cases.insert(index,self.cases[case])
                        broke = True
                        break
                if not broke:
                    ordered_cases.append(self.cases[case])

        value = getattr(response,self.comparison_attr)

        #figure out which case best fits our value
        for index in xrange(len(ordered_cases)):
            lower_avg = None
            upper_avg = None
            math = EasyMath()
            if index != 0:
                lower_avg = math.mean([ordered_cases[index-1]['mean'],ordered_cases[index]['mean']])

            if index != len(ordered_cases) - 1:
                upper_avg = math.mean([ordered_cases[index]['mean'],ordered_cases[index+1]['mean']])

            if not lower_avg and value <= upper_avg:
                return ordered_cases[index]['case']

            elif not upper_avg and value >= lower_avg:
                return ordered_cases[index]['case']

            elif value >= lower_avg and value <= upper_avg:
                return ordered_cases[index]['case']

        #should never get here
        raise Exception('this is shit hitting the fan')


class LooseTextRequester(Requester):
    def _test(self,response):
        value = getattr(response,self.comparison_attr)

        max_ratio = (0,None)
        for case in self.cases:
            for case_value in self.cases[case]['values']:
                ratio = SequenceMatcher(a=str(value),b=str(case_value)).quick_ratio()
                if ratio > max_ratio[0]:
                    max_ratio = (ratio,case)

        return max_ratio[1]
