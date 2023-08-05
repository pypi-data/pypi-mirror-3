#!/usr/bin/env python

# Copyright 2011 - Mickaël THOMAS

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, os.path
import argparse
import signal
import re

from itertools import chain
from time import sleep

from gett import *

url_re = re.compile(r'^(?:http://ge\.tt/|/)?(\w+)(?:/(?:v/(\d+)/?)?)?$')

def humansize(nbytes, pad=False):
    if nbytes is None:
        return ''

    for (exp, unit) in ((9, 'GB'), (6, 'MB'), (3, 'KB'), (0, 'B')):
       if nbytes >= 10**exp:
           break

    if pad:
        return '%6.2f %-2s' % (nbytes / 10**exp, unit)
    else:
        return '%.2f %s' % (nbytes / 10**exp, unit)

def shorten(filename, maxsize):
    base, ext = os.path.splitext(filename)
    max_base = maxsize - len(ext)

    if len(base) > max_base:
        base = base[:max_base - 2] + '..'

    return (base + ext).ljust(max_base + len(ext))

def print_status(upload, index, count):
        name = shorten(upload.file.name, 22)
        bar_size = int(40 * upload.percent_done / 100)
        bar = '[' + (bar_size * '#') + ((40 - bar_size) * '-') + ']'

        sys.stderr.write('\r%s (%3d/%d) %s %d %%' % (name, index, count, bar, upload.percent_done))

def show_share(share):
    print('--------------------------------------------------------------------------------')
    print('Share: %s (%d file(s)) [%s]' % (share.title or 'Untitled', len(share.files), share.url))
    print('--------------------------------------------------------------------------------')

    if share.files:
        max_url = max([len(_.url) for _ in share.files.values()])

        for file in share.files.values():
            print('- %s  %s  %s  %s' % (shorten(file.name, 29), humansize(file.size, True), file.url.ljust(max_url), file.readystate))
    else:
        print('- No files')

    print()

def entry_point():
    try:
        main()
    except APIError as ex:
        print('API error: %s' % ex)

def pattern(string):
    import glob

    ret = []

    if os.path.isfile(string):
        ret.append(open(string, 'rb'))
    else:
        if os.path.isdir(string):
            pattern = string + '/*'
        else:
            pattern = string

        for item in glob.iglob(pattern):
            if os.path.isfile(item):
                ret.append(open(item, 'rb'))

    if not ret:
        print('warning: %s: no match' % string)
    return ret

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    home = os.getenv('USERPROFILE') or os.getenv('HOME')

    parser = argparse.ArgumentParser(
            description="A command-line Ge.tt uploader and manager",
            epilog="Note that whenever http://ge.tt/<share_name>[/v/<fileid>] is expected, you can omit the http://ge.tt/ part.")
    parser.add_argument('-D', dest='debug', action='store_true', help='Debug API calls')

    upload_group = parser.add_argument_group('Upload options')
    upload_group.add_argument('file', nargs='*', type=pattern, help="Name of a file or a directory to upload. Patterns are allowed. This is not recursive.")
    upload_group.add_argument('-t', dest='title', help='Title of the newly created share')
    upload_group.add_argument('-s', dest='share', help='URL of the share to upload to (defaults to a newly created one)')
    upload_group.add_argument('-P', dest='parallel_upload', action='store_true', help='Upload files in parallel rather than sequentially, the progress bars are displayed in ascending file size order')

    other_group = parser.add_argument_group('Other actions')
    other_group.add_argument('--delete', nargs='+', dest='delete', metavar='URL', help='Delete a share or a file')
    other_group.add_argument('--list', nargs='*', dest='list', metavar='SHARE_URL', help='List the files in the specified share. If no share is specified, list all your shares.')

    auth_group = parser.add_argument_group('Authentification')
    auth_group.add_argument('-L', dest='ignore_token', action='store_true', help='Log-in with a different account than the stored one (if any)')
    auth_group.add_argument('-e', dest='email', help='Email to login with')
    auth_group.add_argument('-p', dest='password', help='Password to login with')
    auth_group.add_argument('-k', dest='tokenfile', help='Ge.tt token file path (~/.gett-token)', default=os.path.join(home, '.gett-token'))

    args = parser.parse_args()

    if args.debug:
        import gett
        gett.DEBUG = True

    user = User()
    logged = False

    # If not logging-in with a different account

    if not args.ignore_token and not args.email:
        try:
            # Try to log-in with the token

            token = open(args.tokenfile, 'r').read()
            user.login_token(token)

            logged = True
        except (APIError, IOError):
            pass

    if not logged:
        if not args.email:
            args.email = input('Please enter your Ge.tt email: ')

        if not args.password:
            import getpass
            args.password = getpass.getpass('Please enter your Ge.tt password: ')

        try:
            user.login_auth(args.email, args.password)
        except Exception as ex:
            print('Unable to login: %s' % ex.args[0])
            sys.exit(1)

        reply = input('Do you wish to store the session token? (y/n): ')

        if reply.lower() == 'y':
            # Save the refreshtoken to the user's home directory (by default)

            with open(args.tokenfile, 'w') as file:
                file.write(user.rtoken)


    # --list command

    if args.list is not None:
        for name in args.list:
            match = url_re.match(name)

            if not match or match.group(2):
                parser.error('argument --list: invalid format, please supply either share url or path')

            share = Share(match.group(1))
            show_share(share)

        if not args.list:
            found = False

            for share in user.list_shares():
                found = True
                show_share(share)

            if not found:
                print('You have no shares!')
                print()


    # --delete command

    if args.delete:
        for item in args.delete:
            match = url_re.match(item)

            if not match:
                parser.error('argument --delete: invalid format, please supply either file/share url or path')

            share = user.get_share(match.group(1))

            if match.group(2):
                try:
                    id = match.group(2)
                    file = share.files[id]
                    file.destroy()

                    print('Deleted file: %s [%s]' % (file.name, file.url))
                except KeyError:
                    print("No such file in the share")
            else:
                share.destroy()
                print('Deleted share: %s [%s]' % (share.title or 'Untitled', share.url))
        print()

    # File uploads

    if args.file:
        if args.share:
            # Upload to existing share

            match = url_re.match(args.share)

            if match:
                share = user.get_share(match.group(1))
            else:
                parser.error('argument --list: invalid share name, please supply either URL or name')
        else:
            # Upload to a new share

            if args.title:
                share = user.create_share(args.title)
            else:
                share = user.create_share()

        uploads = []

        # Create the file URLs

        print('Creating file(s)...')

        for fp in chain.from_iterable(args.file):
            name = os.path.basename(fp.name)
            file = share.create_file(name, os.path.getsize(fp.name))

            upload = FileUpload(file, fp)

            if args.parallel_upload:
                upload.start()

            uploads.append(upload)

        show_share(share)

        if args.parallel_upload:
            uploads.sort(key=lambda item: item.file_size)

        for i, upload in enumerate(uploads):
            if not args.parallel_upload:
                upload.start()

            while True:
                print_status(upload, i + 1, len(uploads))
                upload.join(0.5)

                if not upload.is_alive():
                    print_status(upload, i + 1, len(uploads))

                    if upload.ex:
                        sys.stderr.write(('\rError uploading %s: %s' % (upload.file.name, upload.ex)).ljust(80))

                    sys.stderr.write('\n')
                    break
        print()

    user.refresh()

    print('Storage used: %s out of %s (%d %%)' % (
            humansize(user.storage_used),
            humansize(user.storage_limit),
            int(100 * user.storage_used / user.storage_limit)))


if __name__ == '__main__':
    entry_point()
