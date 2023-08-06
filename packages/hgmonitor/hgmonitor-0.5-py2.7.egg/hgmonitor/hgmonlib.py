# -*- coding: utf-8 -*-
"""
This is the class library for the mercurial extension hg-monitor with automated
monitor and backup facilities. 
"""

from mercurial import cmdutil, commands, hg, mail, patch, util
from mercurial.i18n import _
import mercurial
from hglib import *
import os
import re
import platform
import datetime
import zipfile
import shutil
import email.mime.text as textmsg

def repo_list(root_dirs,mq=False):
    repos = []
    
    def check_mq(repo):
        potential = os.path.join(repo,".hg","patches")
        if mq and os.path.exists(potential) and is_repo(potential):
            repos.append(potential)

    for root_dir in root_dirs:
        if is_repo(root_dir):
            # the directory itself is a repository, stop
            repos.append(os.path.realpath(root_dir))
            check_mq(root_dir)
        else:
            # no repository here, recurse
            kids = [os.path.join(root_dir,thisd) for thisd in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir,thisd))]
            for sub_dir in kids:
                if is_repo(sub_dir):
                    # the directory itself is a repository, stop
                    repos.append(sub_dir)
                    check_mq(sub_dir)

    return repos

def sanitize_standard_options(ui,opts):
    if opts["dir"] == []:
        opts["dir"] += ['.']
    #ui.status(_('options %s\n') % opts)

explanation = {}
explanation["?"] = "Files not known by version control"
explanation["A"] = "New files added, but uncommitted"
explanation["M"] = "Files modified, but uncommitted"
for s in special_dir_searches:
    explanation[s[0]] = s[2]

def monitor_cmd(ui, **opts):
    """
    Enumerates uncommitted and unpushed changes.
    """
    sanitize_standard_options(ui,opts)
    dirty_file_list = []

    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        ui.write("{0}\n".format(r))
        ui.pushbuffer()
        commands.status(ui,repo)
        
        for line in stat_parse(ui.popbuffer(), opts['unknown']):
            ui.write(' '.join(line)+'\n')
            dirty_file_list.append((r,) + line)
        def_path = repo.ui.config('paths','default')
        if def_path is not None and False:
            ui.pushbuffer()
            try:
                commands.outgoing(ui,repo,def_path)
            except Exception as e:
                ui.status("aborted outgoing:  {0}\n".format(e))
            for cset in parse_log_output(ui.popbuffer()):
                ui.write("""changeset:   {0.label}\nsummary:     {0.summary}\n""".format(cset))
        for s in special_dir_searches:
            for f in s[1](r):
                ui.write( '{0} {1}\n'.format(s[0], f) )
                dirty_file_list.append((r, s[0], f))

    # dirty file e-mail
    if len(dirty_file_list) > 0 and opts['email'] != '':
        smtp = mail.connect(ui)
        lastrepo = None
        lastreason = None
        body = ""
        for repo, reason, file in dirty_file_list:
            if (repo, reason) != (lastrepo, lastreason) and lastreason is not None:
                body += "</ul>\n"
            if repo != lastrepo:
                body += "<h1>Repository {0} has the following changes which are not upstream:</h1>\n".format(repo)
            if repo != lastrepo or reason != lastreason:
                body += "<h2>{0}</h2>\n".format(explanation[reason])
                body += "<ul>\n"
            lastrepo = repo
            lastreason = reason

            body += "<li>{0}</li>\n".format(file)
        if lastreason is not None:
            body += "</ul>\n"

        msg = textmsg.MIMEText(body, "html")
        msg["To"] = opts['email']
        msg["From"] = ui.username()
        msg["Subject"] = opts['subject'].format(basename=opts['dir'])
        smtp(ui.username(), [opts['email']], msg.as_string())
        ui.status('Summarized to {0}.\n'.format(opts['email']))

def mlist_cmd(ui, **opts):
    """
    Shows a list of repositories impacted by the given monitor settings.
    """
    sanitize_standard_options(ui,opts)
    #ui.write("Repositories in:  {dir}\n".format(dir=opts["dir"]))
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        ui.write("{0}\n".format(r))

class LazyZipFile:
    """
    This class wraps zipfile.ZipFile for the purposes of not actually 
    creating a file unless we actually have something to put into it.
    """
    def __init__(self,file,mode):
        self.file = file
        self.mode = mode
        self._zipfile = None

    def init_now(self):
        if self._zipfile is None:
            self._zipfile = zipfile.ZipFile(self.file,self.mode)

    def close(self):
        if self._zipfile is not None:
            self._zipfile.close()

    def write(self,filename,arcname=None):
        self.init_now()
        self._zipfile.write(filename,arcname)
        

def mbackup_cmd(ui, **opts):
    """
    Backs up uncommitted changes to .hg/mbackup and optionally copies this 
    backup to a (remote) file system.
    
    Destination dest is the name of the zip file name in .hg/mbackup which holds
    the backup.  Auxiliary files may also be created in .hg/mbackup having the
    same base name with-out the zip extension.  The dest parameter may contain
    the following place-holders which will be expanded:

    - clone: last path component of the directory containing the repository
    - fullclone: full path of repository directory with special chars replaced by '_'
    - date: current date formatted as YYYY-MM-DD
    - datetime: current date and time formatted as YYYY-MM-DD-HH-MM-SS
    - time: current time formatted as HH-MM-SS
    - sysname: the hostname of the computer
    """
    sanitize_standard_options(ui,opts)
    #ui.write('Repositories in:  {dir}\n'.format(dir=opts['dir']))
    for r in repo_list(opts['dir'], opts.has_key('mq') and opts['mq']):
        dest = opts['dest']
        d = datetime.datetime.now()
        dest = dest.format(
                    clone=os.path.basename(r),
                    fullclone=r.replace('/','_').replace('\\','_'),
                    date=d.strftime('%Y-%m-%d'),
                    datetime=d.strftime('%Y-%m-%d-%H-%M-%S'),
                    time=d.strftime('%H-%M-%S'),
                    sysname=platform.node())
        if not os.path.exists(os.path.join(r,'.hg','mbackup')):
            os.makedirs(os.path.join(r,'.hg','mbackup'))
        zipfilename = os.path.join(r,'.hg','mbackup',dest)
        zipdest = LazyZipFile(zipfilename,'w')

        repo = hg.repository(ui,r)
        ui.write('{0}\n'.format(r))
        ui.pushbuffer()
        commands.status(ui,repo)
        for line in stat_parse(ui.popbuffer(), opts['unknown']):
            if line[0] not in ['!', 'R']:
                zipdest.write(os.path.join(r,line[1]),line[1])
        def_path = repo.ui.config('paths','default')
        if def_path is not None:
            ui.pushbuffer()
            commands.outgoing(ui,repo,def_path)
            revs = parse_log_output(ui.popbuffer())
            for cset in revs:
                ui.write('''changeset:   {0.label}\nsummary:     {0.summary}\n'''.format(cset))
            if len(revs) > 0:
                bundle_base = int(min([x.rev for x in revs])) - 1
                bundle_file = os.path.join(r,'.hg','mbackup','bundle-backup-{datetime}.hg'.format(datetime=d.strftime('%Y-%m-%d-%H-%M-%S')))
                commands.bundle(ui,repo,bundle_file,base=[bundle_base],type='none')
                zipdest.write(bundle_file, os.path.basename(bundle_file))
        if os.path.exists(os.path.join(r,'.hg','attic')):
            for f in attic_files(r):
                f_ = os.path.join('.hg','attic',f)
                zipdest.write(os.path.join(r,f_),f_)
        if os.path.exists(os.path.join(r,'.hg','shelves')):
            for f in shelf_files(r):
                f_ = os.path.join('.hg','shelves',f)
                zipdest.write(os.path.join(r,f_),f_)
        if os.path.exists(os.path.join(r,'.hg','patches')) and \
                not (opts.has_key('mq') and opts['mq']):
            for f in mq_files(r):
                f_ = os.path.join('.hg','patches',f)
                zipdest.write(os.path.join(r,f_),f_)
        zipdest.close()
        if zipdest._zipfile is not None:
            ui.write('wrote {0}\n'.format(zipfilename))
            if opts['remote'] != '':
                shutil.copy(zipfilename,opts['remote'])

        # send e-mail with the zip file attached
        # http://snippets.dzone.com/posts/show/2038

def mpull_cmd(ui, **opts):
    """
    Pulls incoming changes for all directories in this group.
    """
    sanitize_standard_options(ui,opts)
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        def_path = repo.ui.config('paths','default')
        if def_path is None:
            ui.status( "skip {0}:  no default pull source\n".format(r) )
        else:
            ui.status( "pulling in {0}\n".format(r) )
            pull_args = {}
            if opts["update"]:
                pull_args["update"] = True
            if opts.has_key("fetch") and opts["fetch"]:
                pull_args["fetch"] = True
            if opts.has_key("rebase") and opts["rebase"]:
                pull_args["rebase"] = True
            try:
                commands.pull(ui,repo,def_path,**opts)
            except Exception as e:
                ui.status("aborted pull:  {0}\n".format(e))

def mpush_cmd(ui, **opts):
    """
    Pushs outgoing changes for all directories in this group.
    """
    sanitize_standard_options(ui,opts)
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        def_path = repo.ui.config('paths','default')
        if def_path is None:
            ui.status( "skip {0}:  no default push source\n".format(r) )
        else:
            ui.status( "pushing in {0}\n".format(r) )
            try:
                commands.push(ui,repo,def_path)
            except Exception as e:
                ui.status("aborted push:  {0}\n".format(e))
