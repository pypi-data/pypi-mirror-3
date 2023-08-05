#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Djalil Chafaï http://djalil.chafai.net/'
__version__ = '0.2'
__date__ = '2012-01-01'
__copyright__ = 'Copyright (c), 2011, 2012, Djalil CHAFAÏ'
__license__ = 'GNU General Public License (GPL)'

"""
 DESCRIPTION
   w2m.py is a www spider producing an adjacency matrix and playing with it.
   This file can be used as a module with "import w2m" (provides w2m.W2M).
   This file can be used as a demonstrator script, see main() at the end.
   w2m.py was written for Python 2.7 and tested on Debian GNU/Linux wheezy.
 
 WARNING 
   This code is experimental and must be used with care.

 CHANGELOG
   v0.2 2012-01-01 
     Code clean-up.
     In this version, w2m.py can be used as a module and also as a script.
     BeautifulSoup was replaced by HTMLParser (which belongs to the std. lib.).
     The sole imported modules not in the std. lib. are numpy and matplotlib. 
     This will hopefully make the 2to3 transition easier.  
   v0.1 2011-12-28 
     Initial version.

 TODO
   Add a graphical user interface (GUI, for instance based on wx)
   Add a MSN version by deriving a class which overloads W2M._url_get()
   Add support for multiple edges (weighted graph)
   Add support for redirections (url synonyms and HTTP redirections)
   Add support for ignore url by content (not only content-type)
   Improve thread code by using more standard mechanisms
   Improve speed and memory requirements (parallel sockets for HTTP HEAD?)
   Improve data types to speedup (lists or named dictionaries or tuples)

 HISTORY
   Years ago, I was intrigued by the co-authorship graph of the Mathematical
   Reviews database, which can be extracted in principle by a program. 
   I discussed this project with Susan Holmes at that time, in Bordeaux. She
   pointed out that the MR database is proprietary. More recently, my co-author 
   Charles Bordenave asked if one can extract the adjacency matrix of a subset 
   of the World Wide Web. So I decided finally to write this Python code :-)
"""

import os # http://docs.python.org/library/os.html
import re # http://docs.python.org/library/re.html
import time # http://docs.python.org/library/time.html

# urlparse must be placed before urllib2 (strange unicode problems)
import urlparse # http://docs.python.org/library/urlparse.html
import urllib2 # http://docs.python.org/library/urllib2.html
import HTMLParser # http://docs.python.org/library/htmlparser.html

import threading # http://docs.python.org/library/threading.html
import logging # http://docs.python.org/library/logging.html
import operator # http://docs.python.org/library/operator.html

try: # we check if the additional modules numpy and matplotlib are available
    import numpy.linalg
    import matplotlib.pyplot
except:
    _numerics_missing = True
else:
    _numerics_missing = False

class W2M():
    """ 
    Web spider producing an adjacency matrix.
    See example.py for an example of usage.
    You may overload method _url_get(). 
    """
    def __init__(self, **kwargs):
        """ 
        Constructor. kwargs is a dictionary of named arguments.
        """
        ## Handling arguments (all have a default value, see below)
        # starting url, e.g. http://kab.wikipedia.org/wiki
        self.start = kwargs.get('start','')
        if self.start == '':
            logging.error('Missing start URL.')
            raise StandardError('Start URL not provided.')
        # urls matching this pattern are in our network 
        self.base = kwargs.get('base',self.start)
        # urls matching these patterns are ignored 
        self.ignore = kwargs.get('ignore',self.start+'/.*:')
        # maximum number of urls analyzed
        self.maxu = kwargs.get('maxu',10000000)
        # maximum number of concurrent threads (url analysis)
        self.maxt = kwargs.get('maxt',20)
        # logging level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
        self.log_level = kwargs.get('log_level',20)
        # filenames for outputs
        self.adjacency_filename = kwargs.get(
            'adjacency_filename','adjacency.png')
        self.spectrum_filename = kwargs.get(
            'spectrum_filename','spectrum.png')
        self.octave_filename = kwargs.get(
            'octave_filename','octave.mat')
        self.vertices_filename = kwargs.get(
            'vertices_filename','vertices.lst')
        ## Creating further internal variables
        # creating compiled regex for ignore list
        self.ignore_regex = re.compile(self.ignore)
        # list of urls to explore (used as a queue)
        self.urls = [self.start]
        # list of urls of accepted vertices
        self.vertices = []
        # list of edges i.e. couples of vertices ids
        self.edges = []
        # list of explored vertices id
        self.explored = []
        # list of HTTP HEAD and HTTP GET errors
        self.errors_head = []
        self.errors_get = []
        # list of analyzed urls
        self.analyzed_urls = []
        # dictionary of answers from _lookup()
        self.lookup_answers = {}
        # user agent for HTTP requests 
        now = time.strftime('%Y-%m-%d %H:%M',time.localtime())
        self.user_agent = "w2m.py " + now + " " + ' '.join(os.uname())
        # logging settings
        logging.basicConfig(
            format='%(levelname)s:%(threadName)s:%(funcName)s():%(message)s',
            level=self.log_level)
        # delay for threads
        self.dt = 0.25
    # end: W2M.__init__()
    def work(self):
        """
        Performs the work.
        """
        self._stamp('begin work()')
        # We attempt analyze each url in the queue.
        # The queue contains initially only the start url.
        # The queue is populated by analyze instances (threads).
        count = 0
        threads_list = []
        finished = False
        while (not finished):
            if (count > self.maxu):
                while (len(threading.enumerate()) > 1): time.sleep(self.dt)
                finished = True
            elif (len(self.urls) > 0): 
                while (len(threading.enumerate()) > self.maxt): 
                    time.sleep(self.dt)
                count += 1
                url = self.urls.pop(0)
                logging.info('urls=%i(%i,%i) edges=%i vertices=%i threads=%i',
                             len(self.analyzed_urls),
                             len(self.explored),
                             len(self.urls),
                             len(self.edges),
                             len(self.vertices),
                             len(threading.enumerate()))
                self.analyzed_urls.append(url)
                current = _Analyze(url,self)
                threads_list.append(current)
                current.start()
            else: 
                finished = (len(threading.enumerate()) == 1)
        self._stamp('end work()')
    # end: W2M.work()
    def show(self):
        """ 
        Provides post-work textual informations via logging.INFO.
        Saves an image view of the adjacency matrix (imshow).
        Saves the spectrum (computed with eig).
        Saves the adjacency matrix  (Octave sparse matrix file format).
        Saves the list of vertices (couples (id, url).
        """
        self._stamp('begin show()')
        logging.info('number of accepted vertices: %i',len(self.vertices))
        logging.info('number of accepted edges: %i', len(self.edges))
        logging.info('number of explored vertices: %i', len(self.explored))
        logging.info('number of http head errors: %i',len(self.errors_head))
        logging.info('number of http get errors: %i',len(self.errors_get))
        logging.info('number of analyzed urls: %i',len(self.analyzed_urls))
        logging.info('size of lookup dictionary: %i',len(self.lookup_answers))
        coverage = 100.*len(self.explored)/len(self.vertices)
        logging.info('vertices coverage %2.0f%%.',coverage)
        # adjacency matrix in sparse matrix Octave format
        logging.info('saving \'%s\', use load(\'%s\') in octave',
                      self.octave_filename,self.octave_filename)
        fmatrix = open(self.octave_filename, 'w')
        now = time.strftime('%Y-%m-%d %H:%M',time.localtime())
        print >> fmatrix, "# Created by w2m.py on %s from %s" % (now,self.start)
        print >> fmatrix, "# name: A"
        print >> fmatrix, "# type: sparse matrix"
        print >> fmatrix, "# nnz:", len(self.edges)
        print >> fmatrix, "# rows:", len(self.vertices)
        print >> fmatrix, "# columns:", len(self.vertices)
        # we sort first second column then first column
        for item in sorted(self.edges,key=operator.itemgetter(1,0)): 
            print >> fmatrix, 1+item[0], 1+item[1], "1"
        fmatrix.close()
        # list of vertices
        logging.info('saving \'%s\'',self.vertices_filename)
        fvertices = open(self.vertices_filename, 'w')
        count = 1
        for item in self.vertices: 
            print >> fvertices, count, item
            count += 1
        fvertices.close()
        # images of matrix and spectrum
        global _numerics_missing
        dim = len(self.vertices)
        if (dim > 4000):
            logging.warning('dimension %i is too high for numpy',dim)
            logging.warning(' therefore %s and %s not created.',
                            self.adjacency_filename, self.spectrum_filename)
        elif _numerics_missing:
            logging.warning('unable to import numpy and/or matplotlib') 
            logging.warning(' therefore %s and %s not created.',
                            self.adjacency_filename, self.spectrum_filename)
        else:
            # adjacency matrix creation
            A = numpy.zeros((dim,dim))
            for item in self.edges: A[item[0]-1,item[1]-1]=1
            matplotlib.pyplot.imshow(A,
                                     interpolation='bilinear', 
                                     cmap=matplotlib.cm.gray)
            #matplotlib.pyplot.show()
            logging.info('saving \'%s\'', self.adjacency_filename)
            matplotlib.pyplot.savefig(self.adjacency_filename)
            # computing eigenvalues and eigenvectors
            logging.info('computing eigenvalues and eigenvectors')
            [spectrum,V] = numpy.linalg.eig(A)
            #matplotlib.pyplot.plot(spectrum.real,spectrum.imag,'bo')
            #matplotlib.pyplot.show()
            localization = numpy.abs(V).max(0) # max abs of columns
            matplotlib.pyplot.clf()
            matplotlib.pyplot.hold(True)
            for i in range(0,len(spectrum)):
                matplotlib.pyplot.plot(
                    spectrum[i].real, spectrum[i].imag,
                    'o', color='%2.1f' % (localization[i]))
            #matplotlib.pyplot.show()
            logging.info('saving \'%s\'',self.spectrum_filename)
            matplotlib.pyplot.savefig(self.spectrum_filename)
            matplotlib.pyplot.close()
        self._stamp('end show()')
    # end: W2M.show()
    def _lookup(self,u):
        """
        Returns a couple (good,id) where
          good is a boolean, True if url u is retained as a vertex
          id is the vertex id the vertices list (if good is True)
        The computed answers are stored in the lookup_answers dictionary
        Appends new good vertices to the vertices list:
         a vertex is good if HTTP HEAD succeeded and doc-type is text/*.
        Appends new good striped urls (i.e. of good vertices) to the urls list
        Note that multiple urls may give identical vertices due to striping
        """
        # we strip the blob at the end of the url
        u = u.split('#')[0] 
        u = u.split('?')[0] 
        u = u.rstrip('/')
        # by convention, a concurrent thread is working on u 
        # if and only if u is in lookup_answers with id equal to -1
        try: # we check if the answer is already known.
            answer = self.lookup_answers[u]
        except: # no, we lock this u by setting the id to the special code -1
            self.lookup_answers[u] = (False,-1)
        else: # yes, we wait for the end of the locking thread if any
            locking_detected = False 
            while answer[1] == -1: 
                locking_detected = True
                time.sleep(self.dt)
                answer = self.lookup_answers[u]
            if locking_detected: 
                logging.debug('concurrent thread detected %s',u)
            return answer 
        # now we are responsible to handle u and no other thread will do it
        # it is crucial that lookup_answers[u][1] <> -1 before all "return"
        # we check if u is inside our network
        if not re.match(self.base,u): 
            logging.debug('outside network %s', u)
            self.lookup_answers[u] = (False,-2)
            return(False,-2) # not inside, we stop
        # we check u against our ignore pattern
        if self.ignore_regex.match(u):
            logging.debug('ignored by pattern %s', u)
            self.lookup_answers[u] = (False,-2)
            return(False,-2) # match found, we stop
        # we fetch the HTTP HEAD of u
        logging.debug('http head %s', u)
        (success,doctype) = self._url_head(u)
        if not success:
            # we stop if HEAD problem
            self.errors_head.append(u)
            logging.debug('http head problem %s', u)
            self.lookup_answers[u] = (False,-2)
            return(False,-2)
        # we check if doc-type is text/*
        if not re.match('text/',doctype): 
            logging.debug('not text/* %s', u)
            self.lookup_answers[u] = (False,-2)
            return(False,-2) # no, we stop
        # now we know that u is a valid new vertex
        self.urls.append(u) # we add u to list of urls to analyze
        self.vertices.append(u) # we add u to list of vertices
        i = self.vertices.index(u) 
        logging.debug('new vertex %i %s', 1+i, u)
        self.lookup_answers[u] = (True,i)
        return(True,i)
    # end: W2M._lookup()
    def _url_head(self,url):
        """
        Performs an HTTP HEAD on url and returns a couple (success,doctype)
         success is a boolean, True if HEAD was successful
         doctype contains the document type if success is True
        """
        request = urllib2.Request(url, 
                                  headers={'User-Agent':self.user_agent}) 
        request.get_method = lambda : 'HEAD'
        try:
            result = urllib2.urlopen(request)
            # (note: request.geturl() contains the redirection if any)
        except: # failure
            return (False, '')
        else: # success
            return (True,result.info().gettype())
    # end: W2M._url_head()
    def _url_get(self,url): 
        """
        Performs an HTTP GET on url and returns a couple (success, data)
          success is a boolean, True if the GET was a success
          data is the raw data of the page, when success is True
        This method is typically overloadable by derived classes, allowing
        the modification of data (typically filter and rewrite of hrefs).
        """
        request = urllib2.Request(url, 
                                  headers={'User-Agent':self.user_agent}) 
        request.get_method = lambda : 'GET'
        try:
            result = urllib2.urlopen(request)
            encoding = result.headers.getparam('charset')
            data = result.read().decode(encoding)
        except: # GET unsuccessful
            return(False,'')
        else: # GET successful
            return (True,data)
    # end: W2M._url_get()
    def _stamp(self,message):
        """ 
        Logs the date and time and print message 
        """
        now = time.strftime('%Y-%m-%d %H:%M',time.localtime())
        logging.info('w2m.py %s %s %s',message,now,self.start)
    # end: W2M._stamp()
# end: W2M

class _AnchorParser(HTMLParser.HTMLParser):
    """
    Provides the list of URLs found as href keys of HTML anchors
    in the data feeded by .feed(). See _Analyze.run() for an example.
    """
    def __init__(self):
        self.urls = []
        self.reset()
    # end: _AnchorParser.__init__()
    def handle_starttag(self, tag, attrs):
        """ overloads HTMLParser.handle_starttag() """
        if tag == "a":
            for key, value in attrs:
                if key == "href":
                    self.urls.append(value)
                    break
    # end: _AnchorParser.handle_starttag()
# end: _AnchorParser

class _Analyze(threading.Thread):
    """
    This class (inside the W2M class) is a wrapper for its run() method.
    Being outside W2M allows multi-threading, which is crucial for us.
    Without threading, run() may be converted to method W2M.analyze().
    """
    def __init__(self,url,w2m):
        """
        url is a url to analyze
        w2m is a W2M instance (typically the caller instance)
        """
        threading.Thread.__init__(self) # constructs ancestor
        self.url = url
        self.w2m = w2m
    # end: _Analyze.__init__()
    def run(self):
        """
        This method overloads threading.Thread.run().
        Analyzes the web page behind self.url
        w2m._lookup() is used to determine if self.url is a valid vertex
        Stores vertex id of self.url in the explored list
        w2m._url_get() is used to extract the data behind self.url
        _AnchorParser.anchors() is used to extract all anchors from data
        Each anchor gives a url which is looked up with _lookup()
        Any url not matching base or matching the ignore pattern is ignored
        Stores valid anchors urls in the urls list
        Stores valid anchors vertices in the vertices list
        Stores valid edges in the edges list
        """
        logging.debug('vertices accepted %i explored %i',
                      len(self.w2m.vertices),len(self.w2m.explored))
        logging.debug('edges accepted %i',len(self.w2m.edges))
        logging.debug('urls to analyze %i',len(self.w2m.urls))
        # we lookup the vertex in our memory
        (igood,i) = self.w2m._lookup(self.url)
        # we stop if not good url
        if not igood: return
        # we now try to fetch the web page itself
        logging.debug('http get id %i %s',1+i,self.url)
        (success,data) = self.w2m._url_get(self.url)
        if not success:
            self.w2m.errors_get.append(self.url)
            logging.debug('http get problem id %i %s', i, self.url)
            return # we stop if fetch problem
        self.w2m.explored.append(i)
        # we loop on the values of href for all anchors in data 
        anchor_parser = _AnchorParser()
        anchor_parser.feed(data)
        for u in anchor_parser.urls:
            # converts relative link to absolute link
            if not u.lower().startswith("http"): 
                u = urlparse.urljoin(self.url,u)
            # we lookup the link 
            (jgood,j) = self.w2m._lookup(u)
            # if the link is good, we add it
            if jgood:
                try: # if edge not known we add it to list of edges
                    self.w2m.edges.index([i,j]) 
                except: 
                    self.w2m.edges.append([i,j])
                    logging.debug('new edge %i %i', 1+i, 1+j)
    # end: _Analyze.run()
# end: _Analyse

def main():
    """
    Main program if we are executed as a script rather than as a module.
    """
    import argparse # URL:http://docs.python.org/library/argparse.html
    # handling the command line
    parser = argparse.ArgumentParser(
        description='Demonstrator for w2m module.')
    parser.add_argument(
        '--start', 
        metavar='URL',
        required=True,
        help='Starting URL (required!)')
    parser.add_argument(
        '--base', 
        metavar='base',
        default=argparse.SUPPRESS,
        help='Base of the network (default is URL)')
    parser.add_argument(
        '--ignore', 
        metavar='regex',
        default=argparse.SUPPRESS,
        help='Ignore pattern regex (default is URL/.*:.*')
    parser.add_argument(
        '--maxu', 
        metavar='maxu',
        type=int,
        default=argparse.SUPPRESS,
        help='Maximum number of analyzed URLs (default is 10000000')
    parser.add_argument(
        '--maxt', 
        metavar='maxt',
        type=int,
        default=argparse.SUPPRESS,
        help='Maximum number of concurrent threads (default is 20)')
    parser.add_argument(
        '--log_level', 
        metavar='level',
        type=int,
        default=argparse.SUPPRESS,
        help='Log level lower threshold for console output (default is 20=INFO, other useful values are 10=DEBUG, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    parser.add_argument(
        '--adjacency_filename', 
        metavar='afile.png',
        default=argparse.SUPPRESS,
        help='Adjacency image file (default is adjacency.png)')
    parser.add_argument(
        '--spectrum_filename', 
        metavar='sfile.png',
        default=argparse.SUPPRESS,
        help='Spectrum image file (default is spectrum.png)')
    parser.add_argument(
        '--octave_filename', 
        metavar='mfile.mat',
        default=argparse.SUPPRESS,
        help='.mat GNU-Octave file (default is octave.mat)')
    parser.add_argument(
        '--vertices_filename', 
        metavar='vfile.lst',
        default=argparse.SUPPRESS,
        help='Vertices list file (default is vertices.lst)')
    # creating object
    my_w2m = W2M(** vars(parser.parse_args()))
    # working
    my_w2m.work()
    # showing results
    my_w2m.show()
# end: main()
    
# we run main() if we are used as a script rather than as a module (via import)
if __name__ == "__main__":
    main()

#EOF
