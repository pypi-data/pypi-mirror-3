#!/usr/bin/python
import optparse
import os
import pprint
import resource 
import json
import sys

import requests
import yaml
import time

VERSION = '0.1.3'

default_backliftURL = 'http://backlift.com/'
backlift_configfile = '.backlift'
backlift_email = 'support@backlift.com'

# maxfiles is set to a few less than the system limit. 
maxfiles = resource.getrlimit(resource.RLIMIT_NOFILE)[0] - 6

## ERROR MESSAGES -------------------------------------------------------------

ERR_ID =       "Ooops! Something's wrong. I couldn't obtain an app id. To\n"+\
               "use the push or watch commands, you need an existing\n"+\
               "backlift app created with either the create or init commands."

ERR_BADID =    "Ooops! Something's wrong. I couldn't obtain an app id from\n"+\
               "the server. Please send an angry email to %s." % backlift_email

ERR_MAXFILE =  "Too many files. Total: %d,  max: %d"

ERR_SERVER =   "Ooops! Our server is not responding. Hopefully this is\n"+\
               "temporary. If this problem persists, please send an angry\n"+\
               "email to %s." % backlift_email

ERR_WRITE =    "Ooops! We couldn't create a file. Please check to ensure\n"+\
               "you have permission to write to %s."

ERR_INIT =     "This app has already been initialized."

ERR_500 =      "Ooops! Our server is having trouble. We're looking into\n"+\
               "it! While we're at it, please check to make sure you're\n"+\
               "running the latest version of the backlift command line\n"+\
               "interface at www.backlift.com. You're currently running\n"+\
               "backlift cli %s." % VERSION

ERR_404 =      "Ooops! We couldn't find the resource at %s."

ERR_403 =      "Ooops! This action is forbidden. Either you haven't\n" +\
               "registered your early access code, or you used an\n"+\
               "invalid code. Please see backlift --help."

ERR_RESPONSE = "Oops! Something is wrong with the server. Please send an\n"+\
               "angry email to %s." % backlift_email


## UTILITIES ------------------------------------------------------------------

def fail(msg):
    print >> sys.stderr, msg
    sys.exit(1)


def check_response(r):
    if not (r.status_code / 100 == 2):
        if r.text:
            mtype = r.headers['Content-Type'].split(';')[0]
            if r.status_code == 500:
                fail(ERR_500)
            elif r.status_code == 404:
                fail(ERR_404 % r.request.url)
            elif r.status_code == 403:
                fail(ERR_403)
            else:
                fail(ERR_RESPONSE)
        else: 
            fail(ERR_RESPONSE)


def listFiles(path, skip_hidden):
    files = []        
    configfile = ''

    for (dirpath, dirnames, filenames) in os.walk(path):
        # import pdb; pdb.set_trace()
        path_hidden = reduce(lambda x, y: x or (y[0] == '.'), 
            dirpath.split('/')[1:], False)

        if not path_hidden or not skip_hidden:

            for name in filenames:

                filepath = os.path.normpath(os.path.join(dirpath, name))

                if name == backlift_configfile and dirpath == path:
                    configfile = filepath
                elif skip_hidden and name[0] == '.':
                    continue

                files.append(filepath)

    filecount = len(files)
    if filecount > maxfiles:
        fail(ERR_MAXFILE % (filecount, maxfiles))

    return files, configfile


def collectFiles(path, skip_hidden):
    # import pdb; pdb.set_trace()
    rootpath = os.path.normpath(os.path.abspath(path))
    print "Scanning %s" % rootpath

    filelist, configfile = listFiles(rootpath, skip_hidden)

    files = {}

    for filepath in filelist:
        filekey = filepath.replace(rootpath, '', 1).strip('/')
        files[filekey] = (filekey, open(filepath, 'rb'))
        print "Adding %s" % filekey

    return files, configfile


def scanFiles(path, skip_hidden):
    rootpath = os.path.normpath(os.path.abspath(path))
    filelist, configfile = listFiles(rootpath, skip_hidden)
    return dict ([(f, os.stat(f).st_mtime) for f in filelist]),\
           configfile


def get_id(configfile):
    id = ''
    try:
        handle = open(configfile, 'r')
        cfg_str = handle.read()
        cfg_data = yaml.safe_load(cfg_str)
        handle.close()
        id = cfg_data['_app_id']
    except Exception as e:
        pass

    if not id: fail(ERR_ID)

    return id





## REQUESTS -------------------------------------------------------------------

def register_key(key):
    # import pdb; pdb.set_trace()
    try:
        r = requests.post(backliftURL_registerkey, params={'access_key': key})
        check_response(r)
    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)


def create_app():
    try:
        # import pdb; pdb.set_trace()
        r = requests.post(backliftURL_createapp)
        check_response(r)

        r = json.loads(r.text)
        return r['_id']

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def download_template_files(path, template, params=None):
    files = []
    try:
        # import pdb; pdb.set_trace()

        manifest_url = os.path.join(backliftURL_templatefiles, template)
        r = requests.get(manifest_url)
        check_response(r)

        r = json.loads(r.text)
        files = r['files']

        if len(files) > 0:
            for f in files:

                file_url = os.path.join(backliftURL_templatefiles, template, f)
                r = requests.get(file_url, params=params)
                check_response(r)

                filepath = os.path.abspath(os.path.join(path, f))

                try:
                    newfile = open(filepath, 'wb')
                except IOError:
                    newfile = None

                if not newfile:
                    try:
                        filedir = os.path.split(filepath)[0]
                        os.makedirs(filedir, 0755)
                        newfile = open(filepath, 'wb')
                    except OSError:
                        fail(ERR_WRITE % filedir)

                newfile.write(r.content)
                newfile.close()
                print "creating %s" % os.path.join(path, f)

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def upload_files(id, files):
    try:
        r = requests.put(backliftURL_upload % id, files=files)

        for filekey, filedata in files.items():
            filedata[1].close()

        check_response(r)

        r = json.loads(r.text)

        print "%d files uploaded to the backlift sandbox\n" % r['count']
        print "Admin url -->> \n%s\n" % r['admin_url']
        print "Your app is hosted at -->> \n%s\n" % r['app_url']

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)


## COMMANDS -------------------------------------------------------------------

def register(key):
    register_key(key)


def create(path, name='', template='blank'):

    # import pdb; pdb.set_trace()

    app_root = os.path.normpath(
                    os.path.abspath(
                        os.path.join(path, name)))

    cfg_path = os.path.join(app_root, backlift_configfile)

    if (os.path.exists(cfg_path)):
        fail(ERR_INIT)
 
    id = create_app()
    if id:
        download_template_files(app_root, template, {
            'app_id': id
        })

        if not name: name='current'
        print "A new app has been created in the %s folder." % name
        print "This app will be called %s." % id

    else:
        fail(ERR_BADID)


def init(path):
    create(path)


def push(path, skip_hidden):

    # scan path for files to upload 

    files, configfile = collectFiles(path, skip_hidden)

    id = get_id(configfile)

    upload_files(id, files)

    return id


def watch(path, skip_hidden):
    # import pdb; pdb.set_trace()

    id = push(path, skip_hidden)

    before, configfile = scanFiles(path, skip_hidden)

    try:
        while 1:
            time.sleep (0.5)
            after, configfile = scanFiles(path, skip_hidden)
            
            added = [f for f in after if not f in before]
            removed = [f for f in before if not f in after]
            modified = [f for f in after if after[f] != before[f]]
            
            if added: print "Added: ", ", ".join (added)
            if removed: print "Removed: ", ", ".join (removed)
            if modified: print "Modified: ", ", ".join (modified)
            
            if added or removed or modified:    
                files, configfile = collectFiles(path, skip_hidden)        
                upload_files(id, files)
    
            before = after

    except KeyboardInterrupt:
        pass




## MAIN -----------------------------------------------------------------------

def execute_command_line():

    global backliftURL
    global backliftURL_registerkey
    global backliftURL_createapp
    global backliftURL_templatefiles
    global backliftURL_upload

    usagetxt = '%prog COMMAND [options]\n\n' +\
        'Commands:\n' +\
        '  register KEY\t\tRegister this computer for early access\n' +\
        '  create NAME\t\tCreate a new basic backlift app in the NAME folder\n' +\
        '  create:TYPE NAME\tCreate a new backlift app using the TYPE template\n' +\
        '  init\t\t\tInitialize backlift for an existing app\n' +\
        '  push\t\t\tPush files up to backlift\n' +\
        '  watch\t\t\tObserve path and push files to backlift whenever they change'

    parser = optparse.OptionParser(usagetxt, version='%prog cli '+VERSION)

    parser.add_option('-p', '--path', dest='path', default='.', 
        help='The path to the working folder. Defaults to "%default"')
    parser.add_option('-u', '--url', dest='url', default=default_backliftURL, 
        help='The URL to backlift\'s server. Defaults to "%default"')
    parser.add_option('-H', '--skip-hidden', 
        dest='skip_hidden', action='store_const', const=False, default=True,
        help='Toggle uploading of hidden files. (Files that start with a '+\
            '".") Defaults to "%default"')

    (options, args) = parser.parse_args()

    backliftURL = options.url
    backliftURL_registerkey = os.path.join(backliftURL, 'register-early')
    backliftURL_createapp = os.path.join(backliftURL, 'app-admin')
    backliftURL_templatefiles = os.path.join(backliftURL, 'app-templates')
    backliftURL_upload = os.path.join(backliftURL, 'app-admin/%s')

    if len(args) < 1:
        parser.print_help()
    else:
        if   args[0].lower() == 'register':
            if len(args) != 2:
                parser.print_help()
            else:
                register(args[1])
        elif args[0].lower().startswith('create'):
            if len(args) != 2:
                parser.print_help()
            else:
                tokens = args[0].lower().split(':')
                if len(tokens) > 1:
                    create(options.path, args[1], tokens[1])
                else:
                    create(options.path, args[1], 'basic')
        elif args[0].lower() == 'init':
            init(options.path)
        elif args[0].lower() == 'push':
            push(options.path, options.skip_hidden)
        elif args[0].lower() == 'watch':
            watch(options.path, options.skip_hidden)
        else:
            parser.print_help()

if __name__ == "__main__":
    execute_command_line()
