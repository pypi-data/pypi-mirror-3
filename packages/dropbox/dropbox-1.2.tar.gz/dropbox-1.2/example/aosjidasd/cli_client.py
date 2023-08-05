import ConfigParser
import getpass
import os
import pprint
import sys
#import webbrowser

from dropbox import client, rest, session

import cmd_plus

def ansi(s, code):
    return "\033[%dm%s\033[0m" % (code, s)

def login_checker(f):
    def wrapper(self, *args):
        if not self.sess.is_linked():
            self.stdout.write("Please 'login' to execute this command\n")
        else:
            return f(self, *args)
    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper

def rest_exception_catcher(f):
    def wrapper(self, *args):
        try:
            return f(self, *args)
        except rest.ErrorResponse, e:
            msg = e.user_error_msg or e.error_msg
            if msg:
                self.stdout.write("Error: %s\n" % msg)
            else:
                self.stdout.write("Error: Server error\n")
    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper

def command(login_required=True):
    def decorate(f):
        result = f
        result = cmd_plus.command()(result)
        if login_required: result = login_checker(result)
        result = rest_exception_catcher(result)
        return result
    return decorate

class StoredSession(session.DropboxSession):
    TOKEN_FILE = "token_store.txt"

    def load_creds(self):
        try:
            stored_creds = open(self.TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
            print "[loaded access token]"
        except IOError:
            pass # don't worry if it's not there

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        # uncomment following line to launch browser automatically
        # webbrowser.open(url)
        print "url:", url
        print "please authorize in the browser... after you're done, press enter."
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)

class DropboxTerm(cmd_plus.Cmd):
    def __init__(self, app_key, app_secret):
        cmd_plus.Cmd.__init__(self)
        self.sess = StoredSession(app_key, app_secret, root='dropbox')
        self.api_client = client.DropboxClient(self.sess)
        self.current_path = ''

        self.sess.load_creds()

    prompt = ansi("Dropbox>", 90) + " "

    @command()
    def do_ls(self):
        """list files in current remote directory"""
        resp = self.api_client.metadata(self.current_path)

        if 'contents' in resp.data:
            for f in resp.data['contents']:
                name = os.path.basename(f['path'])
                if f['is_dir']:
                    name = ansi(name, 92)
                self.stdout.write('%s\n' % name)

    @command()
    def do_cd(self, path):
        """change current working directory"""
        if path == "..":
            self.current_path = "/".join(self.current_path.split("/")[0:-1])
        else:
            self.current_path += "/" + path

    @command(login_required=False)
    def do_login(self):
        """log in to a Dropbox account"""
        try:
            self.sess.link()
            return
        except rest.ErrorResponse, e:
            self.stdout.write('Error: %s\n' % str(e))

    @command()
    def do_logout(self):
        """log out of the current Dropbox account"""
        self.sess.unlink()
        self.current_path = ''

    @command()
    def do_cat(self, path):
        """display the contents of a file"""
        f = self.api_client.get_file(self.current_path + "/" + path)
        self.stdout.write(f.read())

    @command()
    def do_mkdir(self, path):
        """create a new directory"""
        self.api_client.file_create_folder(self.current_path + "/" + path)

    @command()
    def do_rm(self, path):
        """delete a file or directory"""
        self.api_client.file_delete(self.current_path + "/" + path)

    @command()
    def do_mv(self, from_path, to_path):
        """move/rename a file or directory"""
        self.api_client.file_move(self.current_path + "/" + from_path, self.current_path + "/" + to_path)

    @command()
    def do_account_info(self):
        """display account information"""
        f = self.api_client.account_info()
        pprint.PrettyPrinter(indent=2).pprint(f.data, this.stdout)

    @command(login_required=False)
    def do_create_account(self):
        """create a new Dropbox account"""
        self.stdout.write("Email: ")
        email = self.stdin.readline().strip()

        password = getpass.getpass().strip()

        self.stdout.write("First Name: ")
        fname = self.stdin.readline().strip()

        self.stdout.write("Last Name: ")
        lname = self.stdin.readline().strip()

        r = self.api_client.account(email=email, password=password, first_name=fname, last_name=lname)
        pprint.PrettyPrinter(indent=2).pprint(r.data, this.stdout)


def main(prog_name, args):
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, "config.ini")
    if not os.path.exists(config_path):
        sys.stderr.write("Couldn't find \"%s\".  It should look something like:\n" % config_path)
        sys.stderr.write("\n")
        sys.stderr.write("[app]\n")
        sys.stderr.write("key = <your-dropbox-app-key>\n")
        sys.stderr.write("secret = <your-dropbox-app-secret>\n")
        sys.stderr.write("\n")
        sys.exit(1)

    config = ConfigParser.SafeConfigParser()
    config.read(config_path)

    def get_option(section, option):
        try:
            return config.get(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            sys.stderr.write("Invalid \"%s\": Section \"%s\" is missing option \"%s\"\n"
                             % (config_path, section, option))
            sys.exit(1)

    app_key = get_option("app", "key")
    app_secret = get_option("app", "secret")

    term = DropboxTerm(app_key, app_secret)
    term.cmdloop()

if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
