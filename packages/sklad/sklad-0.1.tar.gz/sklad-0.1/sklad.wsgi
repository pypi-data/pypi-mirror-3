import os.path as o
import os, sys
path = o.abspath( o.dirname(__file__))
sys.path.insert( 0, path)
try:
    import json
except:
    import simplejson as json
import cgi

tpath = path+'/logg/'

#import HTMLParser
#unescape = HTMLParser.HTMLParser().unescape
if 1:
    # Cannot use name2codepoint directly, because HTMLParser supports apos,
    # which is not part of HTML 4
    import re, htmlentitydefs
    entitydefs = {'apos':u"'"}
    for k, v in htmlentitydefs.name2codepoint.iteritems():
        entitydefs[k] = unichr(v)
    def replaceEntities(s):
        s = s.groups()[0]
        try:
            if s[0] == "#":
                s = s[1:]
                if s[0] in ['x','X']:
                    c = int(s[1:], 16)
                else:
                    c = int(s)
                return unichr(c)
        except ValueError:
            return '&#'+s+';'
        else:
            return entitydefs.get( s, '&'+s+';')

    def unescape( s):
        if '&' not in s:
            return s
        return re.sub(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));", replaceEntities, s)

def remove(x):
    try: os.remove(x)
    except: pass

def filenames( vfields):
    r = []
    for v in vfields:
        #fdebug( 'opa1', type(v) )
        #fdebug( 'opa1', v.__class__ )
        #fdebug( 'opa1', dict( (k,v) for k,v in v.__dict__.items() if k != 'value') )
        if isinstance( v, list):
            r += filenames( v)
        else: #if isinstance( i, cgi.FieldStorage):
            f = getattr( v, 'filename', None)
            if not f: continue
            length = getattr( v, 'length', -2)
            if length<0:
                length = o.getsize( v.fname() )
            lmeg = int( length//1024//1024)
            r.append( str( (f, v.name, length,'b', lmeg and '%sMb' % lmeg or '')) )
    return r

def fwrite( fname, t, mode='a'):
    f = open( fname, mode=mode)
    f.write( str(t)+'\n')
    f.close()

def fdebug( f, t):
    return
    import pprint
    return fwrite( tpath+f, pprint.pformat(t))

def application( environ, start_response):
    status = '200 OK'
    output = []
    head = ['''
<html><head><title>file upload</title>

<link rel='stylesheet' type='text/css' href='/sklad/fileupload.css' >
<script type="text/javascript" src="/sklad/jquery.js"></script>
<script type="text/javascript" src="/sklad/jquery.fileupload.js"></script>
<script type="text/javascript" src="/sklad/jquery.fileupload.auto.js"></script>

</head>
<body>
'''
    #, str(sys.path)
]
    tail = [ '''
<hr>
<h1>upload </h1>

<h3>js sample</h3>
<div id="forms"></div>
<script type="text/javascript">
   jQuery(document).ready(function() {
       jQuery('#forms').fileUpload({
        action:'',
        //success:function(){alert('Yeah !')}
        //use_iframes:false
        //"debug":true
        });
   });
</script>

<h3>html sample</h3>
<form action="" enctype="multipart/form-data" method='post' >
 <input type="file" name="my_file" size=80 /> <br>
 <input type="submit" />
</form>

''' ]
    if 0:
        envs = sorted( environ.items() )
        tail += [ x+'<br>' for x in [ #'Hello World!',
            '<table><tr><td>' ] + [str(kv) for kv in envs if kv[0].isupper() ] + [
                       '<td>' ] + [str(kv) for kv in envs if not kv[0].isupper() ] + [
                       '</table> <hr>' ]]


    response_headers = [('Content-type', 'text/html'), ]

    uri = environ.get( 'REQUEST_URI')
    if 'stat/' in uri:
        id = uri.split('?')[0].split('/')[-1]
    else:
        id = uri.split('=')[-1]
    tempfile = tpath+ 'cur'+id
    statfile = tpath+ 'all'+id
    if 'stat/' in uri:
#        fdebug( 'opa2', id)
#        fdebug( 'opa2', environ)
        length = -2
        r = dict( state= -1, percent=0, size=0, length=length)
        if o.isfile( statfile):
            length = long(open(statfile).read().strip())
            r.update( length=length)
            if o.isfile( tempfile) and length:
                size= state= 0
                fns = []
                try:
                    ss = [ s.strip() for s in open( tempfile).readlines()]
                    state=1
                except: pass
                else:
                    ok = ss[-1] == 'ok'
                    if ok: ss.pop()
                    fns = [ ( o.basename( s[1:] ), o.getsize( s[1:] ) )
                            for s in ss]
                    if ok: size = length
                    else: size = sum( fs[-1] for fs in fns )
                r.update( state=state, percent=int( (100L*size)/length), size=size, fn=fns)
            else:
                r.update( state=1, percent=100, size=length)
            if r['size']==length:
                remove( statfile)
                remove( tempfile)

        response_headers = [('Content-type', 'application/json')]
        out = json.dumps( r, sort_keys=True)
        fdebug( 'opa2', r)
        #if 'callback' in req.GET: out = req.GET['callback'] + '(' + out + ')'
        output = [ out ]
    else:
        output += head
        fdebug( 'opa1', id)
        fdebug( 'opa1', environ)
        if environ.get( 'REQUEST_METHOD')=='POST':
            FieldStorage.SCRIPT_FILENAME = environ['SCRIPT_FILENAME']
            length = environ.get( 'CONTENT_LENGTH')
            fwrite( statfile, length, mode='w' )   #may be bigger than actual file-size
            at = tempfile
            class xFieldStorage( FieldStorage):
                 tempfile= at

            fp= environ['wsgi.input']
            if 0:
                fp = fp.read()
                fwrite( tpath+'opa3', fp)
                fp = open( tpath+'opa3')

            fields = xFieldStorage(
                fp= fp, #environ['wsgi.input'],
                environ=environ,
                keep_blank_values=1)

            fwrite( tempfile, 'ok') #signal other part so upload finished
            output += [ f+'<br>'  for f in filenames( fields.list ) ]
#        fdebug( 'opa1', output)
        output += tail

    #output =  [ sys.version ]
    start_response( status, response_headers)
    return [ x.strip()+'\n' for x in output]

class FieldStorage( cgi.FieldStorage):
    SCRIPT_FILENAME = ''
    PATH= 'files'
    def fname( me):
        fn = (me.filename
            .rsplit( '/',1)[-1]
            .rsplit( '\\',1)[-1]
            )
        fdebug( 'opa4', fn)
        fn = unescape( fn)
        if not isinstance( fn, unicode):
            try: fn = fn.decode('utf-8')
            except:
                try: fn = fn.decode('cp1251')
                except: pass
        fn = fn.encode( 'utf-8')

        #me._filename_only = fn
        path = o.dirname( me.SCRIPT_FILENAME)
        pf = o.join( path, me.PATH, fn )
        #if o.exists( pf): ...
        return pf

    bufsize = 64*1024            # I/O buffering size for copy to file
    def make_file( me, ignore=1):
        fn = me.fname()
        fdebug( 'opa4', fn)
        f = open( fn, 'w+b')
        fwrite( me.tempfile, ':'+fn )
        return f

    #XXX HACK.. in original, files <1000b are never written
    def __write(self, line):
        #fdebug( 'opa4', 'eho')
        #fdebug( 'opa4', line)
        if self.__file is not None:
            if self.filename: #self.__file.tell() + len(line) > 1000:
                self.file = self.make_file('')
                self.file.write(self.__file.getvalue())
                self.__file = None
        self.file.write(line)
cgi.FieldStorage._FieldStorage__write = FieldStorage._FieldStorage__write

# vim:ts=4:sw=4:expandtab:ft=python
