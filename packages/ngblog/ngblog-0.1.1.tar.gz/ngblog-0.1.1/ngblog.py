# -*- coding: utf-8 -*-

# (c) 2011 Nerd Gordo <nerdgordo@nerdgordo.com>
# Licensed under the terms of the BSD 3-Clause License.
# <http://www.opensource.org/licenses/BSD-3-Clause>

from email.utils import formatdate
from werkzeug.contrib.atom import AtomFeed, FeedEntry

import argparse
import codecs
import ConfigParser
import datetime
import glob
import logging
import os
import posixpath
import subprocess
import sys
import textwrap
import time

# setup logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(name)s.%(levelname)s: %(message)s',
    '%Y-%m-%d %H:%M:%S %Z'))
log.addHandler(_log_handler)


class Config(object):

    def __init__(self, fname):
        self._cp = ConfigParser.ConfigParser()
        with codecs.open(fname, 'r', encoding='utf-8') as fp:
            self._cp.readfp(fp)

    def get(self, option, default=None):
        if self._cp.has_option('settings', option):
            return self._cp.get('settings', option)
        return default


class Post(object):

    def __init__(self, fname, line_width=72, author_name=None,
                 author_email=None):
        log.info('Parsing post/page: %s', fname)
        self._author_name = author_name
        self._author_email = author_email
        self.tw = textwrap.TextWrapper(line_width)
        self.tw_headers = textwrap.TextWrapper(line_width,
                                               subsequent_indent=' ')

        # validate file name
        self._fname = os.path.abspath(fname)
        self._fname_pieces = self._fname.split(os.sep)
        if len(self._fname_pieces) < 4:  # year/month/day/slug
            raise RuntimeError('Invalid file name: %s' % self._fname)
        self._fname_pieces = self._fname_pieces[len(self._fname_pieces) - 4:]
        for i in self._fname_pieces[:3]:
            if not i.isdigit():
                raise RuntimeError('Can\'t get the date from filename: %s' %
                                   self._fname)
        if not self._fname.endswith('.txt'):
            raise RuntimeError('Invalid file format: %s' % self._fname)
        # ridiculously simple parser
        self._paragraphs = []
        last_paragraph = []
        with codecs.open(self._fname, 'r', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if len(line) == 0:  # empty line may be the end of a paragraph
                    if len(last_paragraph) > 0:
                        self._paragraphs.append(
                            self.tw.fill(' '.join(last_paragraph)))
                        last_paragraph = []
                else:
                    last_paragraph.append(line)
            if len(last_paragraph) > 0:  # rescue last paragraph :)
                self._paragraphs.append(self.tw.fill(' '.join(last_paragraph)))

    @property
    def title(self):
        return self._paragraphs[0]  # first paragraph is the title

    @property
    def body(self):
        return (2 * os.linesep).join(self._paragraphs[1:])  # ignore title

    @property
    def date(self):
        return datetime.date(*[int(i) for i in self._fname_pieces[:3]])

    @property
    def slug(self):
        return self._fname_pieces[-1][:-4]  # last piece, without '.txt'

    @property
    def full_slug(self):
        # all pieces, without '.txt'
        return posixpath.sep.join(self._fname_pieces)[:-4]

    @property
    def html_file(self):
        return self.full_slug + '.html'

    def __str__(self):
        from_header = self.tw_headers.fill('From: "%s" &lt;%s&gt;' % \
                                           (self._author_name,
                                            self._author_email)) + '\n'
        subject_header = self.tw_headers.fill('Subject: ' + self.title) + '\n'
        date = time.mktime(self.date.timetuple())
        page = '<strong>'
        page += from_header.replace(self._author_email,
                                    '<a href="mailto:%s">%s</a>' % \
                                    (self._author_email, self._author_email))
        page += subject_header.replace(self.title,
                                       '<a href="%s">%s</a>' % \
                                       (self.html_file, self.title))
        page += self.tw_headers.fill('Date: ' + formatdate(date, True)) + '\n'
        page += '</strong>\n'
        page += self.body + '\n'
        return page

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.full_slug)


class Posts(list):

    def __init__(self, basedir, line_width=72, author_name=None,
                 author_email=None):
        log.info('Generating the list of posts.')
        files = glob.glob(os.path.join(basedir, '[0-9]*', '[0-9]*', '[0-9]*',
                                       '*.txt'))
        list.__init__(self, [Post(i, line_width, author_name, author_email) \
                             for i in files])
        self.sort(reverse=True, key=lambda x: x.date)


class Blog(object):

    template_header = u'''\
<html>
    <head>
        <title>%(fulltitle)s</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="alternate" type="application/atom+xml"
              href="atom.xml" title="%(title)s" />
        <base href="%(baseurl)s" />
        <style type="text/css">
            a { color: #006; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <pre>'''

    template_footer = u'''</pre>
    </body>
</html>
'''

    def __init__(self, srcdir=None, destdir=None, baseurl=None):
        if srcdir is None:
            srcdir = os.getcwd()
        if destdir is None:
            destdir = os.path.join(srcdir, '_build')
        if baseurl is None:
            baseurl = 'file://' + os.path.abspath(destdir) + '/'
        self.srcdir = srcdir
        self.destdir = destdir
        self.baseurl = baseurl
        config = Config(os.path.join(self.srcdir, 'config.ini'))
        self.title = config.get('title', 'my cool blog')
        self.headline = config.get('headline', 'move away!')
        self.footline = config.get('footline', 'nothing useful here...')
        self.author_name = config.get('author_name', 'myself')
        self.author_email = config.get('author_email', 'foo@example.com')
        try:
            self.logo = subprocess.check_output(['figlet', self.title])
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to run figlet. Maybe it isn\'t ' \
                               'installed.')
        self.line_width = max([len(i) for i in self.logo.split(os.linesep)])
        self.posts = Posts(self.srcdir, self.line_width, self.author_name,
                           self.author_email)

    def render_template(self, posts, title=None):
        fulltitle = self.title
        if title is not None:
            fulltitle += ' - ' + title
        page = self.template_header % {'fulltitle': fulltitle,
                                       'title': self.title,
                                       'baseurl': self.baseurl}
        page += '<strong>\n' + self.logo + '\n'
        page += ' ' * (self.line_width - len(self.headline))
        page += '<em>' + self.headline + '</em>\n\n'
        page += '=' * self.line_width + '</strong>\n'
        page += ('\n<strong>' + ('-' * self.line_width) + \
                 '</strong>\n').join([unicode(i) for i in posts])
        page += '\n<strong>'
        page += '=' * self.line_width + '\n'
        page += '(c) ' + self.author_name + ' &lt;'
        page += '<a href="mailto:' + self.author_email + '">'
        page += self.author_email + '</a>&gt;</strong>\n\n'
        footline = []
        tw = textwrap.TextWrapper(self.line_width)
        for i in self.footline.split('--'):
            footline.append(tw.fill(i.strip()))
        page += '\n\n'.join(footline)
        page += '\n<strong>'
        page += '=' * self.line_width + '\n'
        page += ((self.line_width - len('ngblog | Atom Feed')) / 2) * ' '
        page += '<em><a href="http://nerdgordo.com/git/?p=ngblog.git">ngblog'
        page += '</a> | <a href="atom.xml">Atom Feed</a></em></strong>'
        page += self.template_footer
        return page

    def build_index(self):
        log.info('Building index page.')
        return self.render_template(self.posts)

    def build_post(self, post):
        log.info('Building post: %s', post.html_file)
        return self.render_template([post], post.title)

    def build_feed(self):
        log.info('Building atom feed.')
        feed = AtomFeed(self.title, subtitle=self.headline, url=self.baseurl,
                        feed_url=posixpath.join(self.baseurl, 'atom.xml'),
                        author={'name': self.author_name,
                                'email': self.author_email})
        for post in self.posts:
            feed.add(
                FeedEntry(
                    title=post.title,
                    author={'name': self.author_name,
                            'email': self.author_email},
                    content='<pre>' + post.body + '</pre>',
                    url=posixpath.join(self.baseurl, post.html_file),
                    published=post.date,
                    updated=post.date,
                )
            )
        return feed.to_string()

    def _save_file(self, filename, content):
        destfile = os.path.join(self.destdir, filename)
        destdir = os.path.dirname(destfile)
        if not os.path.isdir(destdir):
            os.makedirs(destdir)
        with codecs.open(destfile, 'w', encoding='utf-8') as fp:
            log.info('Saved file: \'%s\' -> \'%s\'', filename, destfile)
            fp.write(content)

    def build(self):
        log.info('Starting the blog build.')
        self._save_file('index.html', self.build_index())
        self._save_file('atom.xml', self.build_feed())
        for post in self.posts:
            post_file = post.html_file
            self._save_file(post_file, self.build_post(post))

    def clean(self, fs_entry=None):
        # try to safely clean the destdir, removing .html and .xml files, and
        # all the directories that stay empty after removing these files.
        if fs_entry is None:
            log.info('Cleaning up the destination directory: %s', self.destdir)
            fs_entry = self.destdir
        if not os.path.isdir(fs_entry):
            return
        for entry in os.listdir(fs_entry):
            _entry = os.path.join(fs_entry, entry)
            if os.path.isdir(_entry):
                self.clean(_entry)
                if not len(os.listdir(_entry)):
                    log.info('Removing directory: %s', _entry)
                    os.rmdir(_entry)
            elif _entry.endswith('.html') or _entry.endswith('.xml'):
                log.info('Removing file: %s', _entry)
                os.unlink(_entry)


def main():
    parser = argparse.ArgumentParser(description='builds a plain-text-like ' \
                                     'static blog.')
    parser.add_argument('-s', '--srcdir', dest='srcdir', metavar='DIR',
                        help='set sources directory. default: current ' \
                        'directory.')
    parser.add_argument('-d', '--destdir', dest='destdir', metavar='DIR',
                        help='set destination directory. default: ' \
                        '`srcdir\'/_build')
    parser.add_argument('-b', '--baseurl', dest='baseurl', metavar='URL',
                        help='set base URL. default: (empty)')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='make the script less noisy.')
    parser.add_argument('-k', '--keep', dest='keep', action='store_true',
                        help='don\'t remove old HTML/XML files from ' \
                        '`destdir\'.')
    args = parser.parse_args()
    try:
        if args.quiet:
            log.setLevel(logging.ERROR)
        blog = Blog(args.srcdir, args.destdir, args.baseurl)
        if not args.keep:
            blog.clean()
        blog.build()
    except Exception, err:
        log.error('%s: %s' % (err.__class__.__name__, str(err)))
        return -1
    return 0

if __name__ == '__main__':
    sys.exit(main())
