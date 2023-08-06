#coding: utf8
import os
import sys
import time
import argparse
import subprocess



def run(application):
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('action', choices=['initdb', 'dropdb', 'upgradedb', 'genconf', 'web', 'services', 'all', 'killall'], help='choose one operation')
    args = parser.parse_args()
    if args.action == 'initdb':
        application.db_init()
    elif args.action == 'dropdb':
        application.db_drop()
    elif args.action == 'upgradedb':
        application.db_upgrade()
    elif args.action == 'web':
        application.http_serve_forever()
    elif args.action == 'services':
        application.start_services()
        application.join_services()
    elif args.action == 'genconf':
        application.genconf()
    elif args.action == 'killall':
        killall()
    elif args.action == 'all':
        killall()
        time.sleep(2)
        application.start_services()
        application.http_serve_forever()


def killall():
    p1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', sys.argv[0]], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()[0]
    lines = output.splitlines()
    lines = filter(lambda l:'grep' not in l, lines)
    pids = map(lambda l:l.split()[1], lines)

    # remove current pid
    pid = str(os.getpid())
    if pid in pids:
        pids.remove(pid)

    if pids:
        subprocess.check_call(['kill'] + pids)
        print 'kill pids:', pids

