#!/usr/bin/python2.5

import os
import re
import sys
import difflib
import optparse
import subprocess

parser = optparse.OptionParser()
parser.add_option("-n", "--dry-run",
                  action="store_true", dest="dry_run", default=False,
                  help="Don't actually make any changes.")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose output.")

re_vptf_sub = (
    re.compile(
    r'^from zope\.app\.pagetemplate(\.viewpagetemplatefile)? import ViewPageTemplateFile$',
    re.M),
    r'from z3c.ptcompat import ViewPageTemplateFile')

re_ptf_sub = (
    re.compile(
    r'^from zope\.pagetemplate(\.pagetemplatefile)? import PageTemplateFile$',
    re.M),
    r'from z3c.ptcompat import PageTemplateFile')

def log(msg):
    for line in msg.split('\n'):
        print ">>> %s" % line

def status(msg):
    for line in msg.split('\n'):
        print "    %s" % line

def main(options, args):
    if options.dry_run:
        status("Warning: Dry run---no changes will be made to the file-system.")

    path = os.getcwd()
    status("Working directory: %s" % path)

    log("Analyzing source-code...")
    registry = {}
    count = 0
    for arg, dirname, names in os.walk(path):
        for name in names:
            base, ext = os.path.splitext(name)
            if ext != '.py':
                continue

            if options.verbose and count > 0 and count % 500 == 0:
                status("Processed %d files." % count)

            count += 1
            filename = os.path.join(arg, name)

            diff = create_diff(filename)
            if diff is not None:
                registry[filename] = diff

    status("%d files processed" % count)
    log("Updating import-statements in %d files..." % len(registry.keys()))

    if options.dry_run:
        queue = ['patch', '-p0', '--dry-run'],
    else:
        queue = ['patch', '-p0', '--dry-run'], ['patch', '-p0']

    for args in queue:
        if options.verbose:
            args.append('--verbose')
        else:
            args.append('--quiet')

        proc = subprocess.Popen(
            " ".join(args),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            )

        diffs = []
        for filename, body in registry.iteritems():
            if options.verbose:
                changes = body.count('+++ ')
                status("%s (%d %s)." % (
                    filename, changes, 'changes' if (changes > 1) else 'change'))

            diffs.append(body)

        if not diffs:
            break

        output, err = proc.communicate("\n".join(diffs)+'\n')
        
        if proc.returncode != 0:
            map(status, output.split('\n'))
            status("An error occurred while applying patches.")
            break
    else:
        status("Succesfully patched files.")
        
    if '--dry-run' in args:
        status("No files were changed.")
    
    sys.exit(proc.returncode)

def create_diff(filename):
    original = open(filename).read()
    new = original

    # process regular expression substitutions
    for exp, replacement in (re_vptf_sub, re_ptf_sub):
        new = exp.sub(replacement, new)
            
    if original != new:
        return "\n".join(map(str.rstrip, difflib.unified_diff(
            original.split('\n'),
            new.split('\n'),
            filename,
            filename)))
        
if __name__ == "__main__":
    main(*parser.parse_args())

    
