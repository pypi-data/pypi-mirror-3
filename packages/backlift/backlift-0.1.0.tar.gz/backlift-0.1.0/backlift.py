#!/usr/bin/python
import optparse
import os
import pprint
import resource 
import json
import sys

import requests
import yaml

version = '0.1.0'

default_backliftURL = 'http://backlift.com/'
backlift_configfile = '.backlift'
backlift_email = 'support@backlift.com'

# maxfiles is set to a few less than the system limit. 
maxfiles = resource.getrlimit(resource.RLIMIT_NOFILE)[0] - 6

def collectFiles(path, skip_hidden):
    files = {}        
    count = 0
    configfile = ''

    rootpath = os.path.normpath(os.path.abspath(path))
    print "Scanning %s" % rootpath

    for (dirpath, dirnames, filenames) in os.walk(rootpath):
        # import pdb; pdb.set_trace()
        hidden = reduce(lambda x, y: x or (y[0] == '.'), dirpath.split('/')[1:], False)

        if not hidden or not skip_hidden:

            for name in filenames:

                filepath = os.path.normpath(os.path.abspath(os.path.join(dirpath, name)))

                if name == backlift_configfile and dirpath == rootpath:
                    configfile = filepath
                elif skip_hidden and name[0] == '.':
                    continue

                count += 1

                if count > maxfiles:
                    continue

                if os.path.isfile(filepath):
                    filekey = filepath.replace(rootpath, '', 1).strip('/')
                    files[filekey] = (filekey, open(filepath, 'rb'))
                    print "Adding %s" % filekey

    return files, count, configfile

def response_error(r):
    if not (r.status_code / 100 == 2):
        if r.text:
            mtype = r.headers['Content-Type'].split(';')[0]
            if r.status_code == 500:
                print >> sys.stderr, \
                    "Ooops! Our server is having trouble. We're looking into it! \n" +\
                    "While we're at it, please check to make sure you're running \n" +\
                    "the latest version of the backlift command line interface at \n" +\
                    "www.backlift.com. You're currently running backlift cli "+version
            elif r.status_code == 404:
                print >> sys.stderr, \
                    "Ooops! We couldn't find the resource at %s.\n" % r.request.url +\
                    "To reset this app's URLs, delete the .backlift file in your " +\
                    "app's root folder."
            else:
                print >> sys.stderr, r.text

        else: 
            r.raise_for_status()
        return True
    return False

def create_app():
    try:
        # import pdb; pdb.set_trace()
        r = requests.post(backliftURL_createapp)

        if not response_error(r):
            r = json.loads(r.text)
            return r['_id']

    except requests.exceptions.ConnectionError:
        print >> sys.stderr, "Ooops! Our server is not responding. " +\
            "Hopefully this is temporary. \nIf this problem persists, " +\
            "please send an angry email to %s." % backlift_email

    return None

def download_template_files(path, template, params=None):
    files = []
    try:
        # import pdb; pdb.set_trace()

        manifest_url = os.path.join(backliftURL_templatefiles, template)
        r = requests.get(manifest_url)

        if not response_error(r):
            r = json.loads(r.text)
            files = r['files']

        if len(files) > 0:
            for f in files:

                file_url = os.path.join(backliftURL_templatefiles, template, f)
                r = requests.get(file_url, params=params)

                if not response_error(r):
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
                            print >> sys.stderr, "Ooops! We couldn't create the " +\
                                "app template. Please check to ensure you have " +\
                                "permission to write to %s." % filedir
                            return

                    newfile.write(r.content)
                    newfile.close()
                    print "creating %s" % os.path.join(path, f)

    except requests.exceptions.ConnectionError:
        print >> sys.stderr, "Ooops! Our server is not responding. " +\
            "Hopefully this is temporary. \nIf this problem persists, " +\
            "please send an angry email to %s." % backlift_email

    return None


def upload_files(id, files):
    try:
        r = requests.put(backliftURL_upload % id, files=files)

        for filekey, filedata in files.items():
            filedata[1].close()

        if not response_error(r):
            r = json.loads(r.text)

            print "%d files uploaded to the backlift sandbox\n" % r['count']
            print "Admin url -->> \n%s\n" % r['admin_url']
            print "Your app is hosted at -->> \n%s\n" % r['app_url']

    except requests.exceptions.ConnectionError:
        print >> sys.stderr, "Ooops! Our server is not responding. " +\
            "Hopefully this is temporary. \nIf this problem persists, " +\
            "please send an angry email to %s." % backlift_email


def create(path, name='', template='blank'):

    # import pdb; pdb.set_trace()
    
    app_root = os.path.normpath(
                    os.path.abspath(
                        os.path.join(path, name)))

    cfg_path = os.path.join(app_root, backlift_configfile)

    if (os.path.exists(cfg_path)):
        print >> sys.stderr, "This app has already been initialized."
        return

    id = create_app()
    if id:
        download_template_files(app_root, template, {
            'app_id': id
        })

    if not id:
        print >> sys.stderr, "Ooops! Something's wrong. " +\
            "I couldn't obtain an app id. " +\
            "Please send an angry email to %s." % backlift_email
        return

def init(path):
    create(path)

def push(path, skip_hidden):

    # scan path for files to upload 

    files, count, configfile = collectFiles(path, skip_hidden)
    if count > maxfiles:
        print >> sys.stderr, "Too many files. Total: %d,  max: %d" % \
            (count, maxfiles)
        return

    id = ''

    # try to obtain app id from configfile, or create one

    # import pdb; pdb.set_trace()

    try:
        handle = open(configfile, 'r')
        cfg_str = handle.read()
        cfg_data = yaml.safe_load(cfg_str)
        handle.close()
        id = cfg_data['_app_id']
    except Exception as e:
        pass

    if not id:
        print >> sys.stderr, "Ooops! Something's wrong. I couldn't obtain\n"+\
            "an app id. To use the push command, you need an existing\n"+\
            "backlift app created with either the startapp or init commands. "
        return

    upload_files(id, files)



def execute_command_line():

    global backliftURL
    global backliftURL_createapp
    global backliftURL_templatefiles
    global backliftURL_upload

    usagetxt = '%prog COMMAND [options]\n\n' +\
        'Commands:\n' +\
        '  startapp NAME\t\tCreate a new backlift app\n' +\
        '  init\t\t\tInitialize backlift for an existing app\n' +\
        '  push\t\t\tPush files up to backlift'

    parser = optparse.OptionParser(usagetxt, version='%prog cli '+version)

    parser.add_option('-p', '--path', dest='path', default='.', 
        help='The path to the root of your app. Defaults to "%default"')
    parser.add_option('-u', '--url', dest='url', default=default_backliftURL, 
        help='The URL to backlift\'s server. Defaults to "%default"')
    parser.add_option('-H', '--skip-hidden', 
        dest='skip_hidden', action='store_const', const=False, default=True,
        help='Toggle uploading of hidden files. (Files that start with a ".") ' +\
            'Defaults to "%default"')

    (options, args) = parser.parse_args()

    backliftURL = options.url
    backliftURL_createapp = os.path.join(backliftURL, 'app-admin')
    backliftURL_templatefiles = os.path.join(backliftURL, 'app-templates')
    backliftURL_upload = os.path.join(backliftURL, 'app-admin/%s')

    if len(args) < 1:
        parser.print_help()
    else:
        if   args[0].lower() == 'startapp':
            if len(args) < 2:
                parser.print_help()
            else:
                create(options.path, args[1], 'basic')
        elif args[0].lower() == 'init':
            init(options.path)
        elif args[0].lower() == 'push':
            push(options.path, options.skip_hidden)

if __name__ == "__main__":
    execute_command_line()
