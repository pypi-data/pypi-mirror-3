
from __future__ import division, print_function

from functools import partial
from glob import glob
from hashlib import md5
from multiprocessing import Pool
from os import mkdir
from os.path import abspath, dirname, exists, join
from textwrap import dedent
from zipfile import is_zipfile, ZipFile

import bottle

from bottle import get, post, redirect, request, route, static_file


pool = Pool(processes=3)
views = join(dirname(abspath(__file__)), 'views')

bottle.TEMPLATE_PATH.insert(0, views)


def process_job(seqfile):
    pass

@get('/')
def form():
    return static_file('form.html', root=views)

@post('/')
def submit():
    data = request.files.data
    m = md5()
    if not is_zipfile(data.file):
        return static_file('invalid.html', root=views)
    data.file.seek(0)
    while True:
        p = data.file.read(8192)
        if not p:
            break
        m.update(p)
    while True:
        if not exists(m.hexdigest()):
            break
        m.update(m.digest())
    jid = m.hexdigest()
    data.file.seek(0)
    zipdata = ZipFile(data.file)
    mkdir(jid)
    zipdata.extractall(jid)
    seqfiles = glob(join(jid, '*.fna')) + glob(join(jid, '*.fasta')) + glob(join(jid, '*.fa'))
    if len(seqfiles) != 1:
            return static_file('invalid.html', root=views)
    pool.apply_async(process_job, (seqfiles[0],), callback=fill_job_templates, error_callback=partial(report_job_error, jid=jid))
    redirect('/job/%s/' % jid)

@route('/job/<jid>/<part>')
def job(jid=None, part='index'):
    if jid is None or not exists(jid):
        return static_file('404.html', root=views)
    elif not exists(join(jid, 'index.html')):
        return static_file('unfinished.html', root=views)
    else:
        return static_file(join(jid, part + '.html'))


parts = set( 'index'
           , 'download'
           , 'coverage'
           , 'majority'
           , 'coverage+majority'
           , 'maxdivergence'
           , 'sitewise'
           )

def partfile(jid, part):
    return join(jid, part + '.html')

def report_job_error(jid, exc):
    with open(join(jid, 'index.html'), 'w') as fh:
        fh.write('error occurred: %s' % str(exc))

def fill_job_templates(result):
    jid = result.get()
    with open(join(jid, jid + '.json')) as data:
        for part in parts:
            file = partfile(jid, part)
            if not exists(file):
                with open(file, 'w') as fh:
                    if part == 'index':
                        fh.write(dedent('''\
                        filtering of reads (downloads, coverage, majority, cov+maj
                        maximum divergence
                        sitewise mutation rate classes'''))
                    if part == 'download':
                        fh.write('treat this as a download of the filtered sequences')
                    if part == 'coverage':
                        fh.write('treat this as a download of the coverage pdf')
                    if part == 'majority':
                        fh.write('treat this as a download of the majority pdf')
                    if part == 'coverage+majority':
                        fh.write('treat this as a download of the coverage+majority pdf')
                    if part == 'maxdivergence':
                        fh.write('1 index for maximum divergence with 2 for each window: alignment and tree and 3 for the max window: pdf tree')
                    if part == 'sitewise':
                        fh.write('2 files, html and csv file, with 1 profile index for each site')
