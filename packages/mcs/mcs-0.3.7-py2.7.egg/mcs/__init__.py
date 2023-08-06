from __future__ import absolute_import
from __future__ import with_statement
import cmdln
import fnmatch
import logging
import StringIO
import textwrap
import zipfile

from .repositories import McRepository
from .versioninfo import VersionInfo

logging.basicConfig(level=logging.WARNING, 
                    format="%(levelname)s: %(message)s")
log = logging.getLogger('mcs')


def global_options(f):
    return reduce(lambda f, decorator: decorator(f), [
        cmdln.option("--traceback", action='store_true', help="print a traceback on exception"),
        cmdln.option("-v", "--verbose", action='store_true', help="print extra information")], f)


class Mcs(cmdln.Cmdln):
    name = "mcs"
    
    @cmdln.alias("ls")
    @cmdln.option("-p", "--pattern", action='store', help="only show items that match a pattern")
    @cmdln.option("-i", "--information", action='count', default=0, help="show author and timestamp, specify twice to show commit message")
    @global_options
    def do_list(self, subcmd, opts, url):
        """${cmd_name}: list all items in a repository
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        if opts.verbose:
            log.setLevel(logging.INFO)

        repo = McRepository.for_url(url)
        items = repo.list_items()
        for name in self.filter_list(items, opts.pattern):
            if opts.information == 0:
                print name
            elif opts.information >= 1:
                with zipfile.ZipFile(StringIO.StringIO(repo.load_item(name))) as archive:
                    version_info = VersionInfo.parse(archive.read("version"))
                
                print "%-40s %-5s %-.16s" % (name, version_info.author, version_info.timestamp().isoformat(" "))
                if opts.information >= 2:
                    for line in version_info.message.splitlines():
                        print textwrap.fill(line, initial_indent="  ", subsequent_indent="  ")
                    print
    
    @cmdln.alias("cp")
    @cmdln.option("-p", "--pattern", action='store', help="only show items that match a pattern")
    @cmdln.option("-a", "--all", action='store_true', help="copy all items even if they already exist in the target")
    @global_options
    def do_copy(self, subcmd, opts, from_url, to_url):
        """${cmd_name}: copy items from one repository to another
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        if opts.verbose:
            log.setLevel(logging.INFO)
        
        from_repo = McRepository.for_url(from_url)
        to_repo = McRepository.for_url(to_url)
        done = set(to_repo.list_items())
        todo = set(from_repo.list_items())
        if not opts.all:
            todo -= done
        for name in self.filter_list(todo, opts.pattern):
            print name
            to_repo.store_item(name, from_repo.load_item(name))
    
    def filter_list(self, items, pattern):
        if not pattern:
            return items
        return [item for item in items if fnmatch.fnmatchcase(item, pattern)]
