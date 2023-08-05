from datetime import datetime
import argparse
import os
import os.path
import subprocess
import glob


def parse_zrm_index(contents):
    values = {}
    for line in contents.strip().split('\n'):
        key, val = line.strip().split('=')
        values[key] = val
    return values


def parse_timestamp(timestamp):
    return datetime.strptime(str(timestamp), '%Y%m%d%H%M%S')


class Manager(object):

    def __init__(self, args):
        self.host = args.host
        self.backupset = args.backupset
        self.database = args.database
        self.verbose = args.verbose
        self.user = args.user
        self.password = args.password

    def backup_dir(self):
        return os.path.join(os.getenv('HOME'), 'dumps', self.backupset)

    def sync_remote_paths(self, paths):
        """
        Sync the list of remote paths to the local backup directory.
        """
        for path in paths:
            if self.verbose:
                print "Syncing %s" % path
            subprocess.check_call(['rsync',
                                   '-avz',
                                   '%s:%s' % (self.host, path),
                                   self.backup_dir()])

    def sync_binlogs(self):
        pass

    def remote_command(self, *args):
        """
        Run the command specified by ``args`` on the remote host.
        """
        cmd = ['ssh', self.host]
        cmd.extend(args)
        return subprocess.check_output(cmd)

    def list_backups_for_now(self):
        """
        Returns a list of the absolute paths to be pulled from the remote
        server in order to be able to reconstruct current DB state.
        """
        # Run 'mysql-zrm-list --backup-set %(database)s --till-lastfull
        # --noindex on remote host.
        output = self.remote_command('mysql-zrm-list',
                                     '--backup-set', self.backupset,
                                     '--till-lastfull',
                                     '--noindex')
        paths = []
        for line in output.strip().split('\n'):
            full, path = line.strip().split()
            paths.append(path)
        return paths

    def list_backups_for_time(self, timestamp):
        """
        Returns a list of the absolute paths to be pulled from the remote
        server in order to be able to reconstruct DB state at time
        ``timestamp``.
        """
        # Run 'mysql-zrm-list --backup-set %(database)s --all-backups --noindex
        # on remote host.
        output = self.remote_command('mysql-zrm-list',
                                     '--backup-set', self.backupset,
                                     '--all-backups',
                                     '--noindex')

        # Include backups up to and including the first one after the desired
        # timestamp, so that the incremental backup including the desired
        # timestamp gets downloaded.
        lines = []
        for line in output.split('\n'):
            incremental, path = line.split()
            dir = os.path.basename(path)
            lines.append((incremental, path))
            if int(dir) > timestamp:
                break

        # We only need backups after and including the last full one.
        paths = []
        for incremental, path in reversed(lines):
            paths.insert(0, path)
            if incremental:
                break

        return paths

    def last_incremental_timestamp(self, paths):
        return int(os.path.basename(paths[-1]))

    def remote_path_to_local(self, path):
        return os.path.join(self.backup_dir(), os.path.basename(path))

    def mysql_cmd(self):
        return ['mysql',
                '--user=%s' % self.user,
                '--password=%s' % self.password]

    def restore_full(self, source_dir, index):
        """
        Restore the full backup referenced at source_dir.
        """
        if self.verbose:
            print "Restoring full backup %s" % source_dir
        assert int(index['backup-level']) == 0
        # Restore backup.sql.
        path = os.path.join(source_dir, 'backup.sql')
        subprocess.check_call(self.mysql_cmd(), stdin=open(path))

    def readback_binlog(self, paths, timestamp=None):
        # Read back binlogs up until timestamp.
        if self.verbose:
            print "Reading back binlogs: %r" % paths
        cmd = ['mysqlbinlog', '--database=%s' % self.database]
        if timestamp:
            # Parse timestamp and reformat it to mysql-format.
            dt = parse_timestamp(timestamp)
            ms_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            cmd.append('--stop-datetime')
            cmd.append(ms_timestamp)

        cmd.extend(paths)

        mysqlbinlog_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        mysql_proc = subprocess.Popen(self.mysql_cmd(),
                                      stdin=mysqlbinlog_proc.stdout)
        mysql_proc.wait()

    def restore_incremental(self, source_dir, index, timestamp=None):
        """
        Restore the incremental backup referenced at source_dir, and any
        necessary backups before it.
        """
        assert int(index['backup-level']) == 1
        # Restore all prior backups since last full.
        self.restore_backup(index['last-backup'])
        # Restore current backup.
        if self.verbose:
            print "Restoring incremental backup %s" % source_dir
        binlogs = glob.glob(os.path.join(source_dir, index['incremental']))
        self.readback_binlog(binlogs, timestamp)

    def restore_backup(self, remote_dir, timestamp=None):
        """
        Actually restore backup directories. Return the filename for the next
        binlog.
        """
        source_dir = self.remote_path_to_local(remote_dir)
        index_fn = os.path.join(source_dir, 'index')
        with open(index_fn) as f:
            index = parse_zrm_index(f.read())

            # Extract actual backup data.
            cmd = ['tar',
                   '-xzf', os.path.join(source_dir, 'backup-data'),
                   '-C', source_dir]
            subprocess.check_call(cmd)

            level = int(index['backup-level'])
            if level == 0:
                self.restore_full(source_dir, index)
            elif level == 1:
                self.restore_incremental(source_dir, index, timestamp)
            else:
                raise ValueError('unknown backup level %r' % level)

            return index['next-binlog']

    def restore(self, timestamp=None):
        """
        Restore local DB state to remote DB state for a given time. If
        timestamp is not specified, restore to the current live state.
        """
        if timestamp:
            timestamp = int(timestamp)
            paths = self.list_backups_for_time(timestamp)
        else:
            paths = self.list_backups_for_now()

        self.sync_remote_paths(paths)

        if ((not timestamp) or
            (timestamp > self.last_incremental_timestamp(paths))):
            # rsync all binlogs since most recent incremental backup
            self.sync_binlogs()

        # restore full backup
        next_binlog = self.restore_backup(paths[-1], timestamp)

        # play back each binlog since full backup


def main():
    p = argparse.ArgumentParser(description='Restore MySQL backups.')
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                   help='print detailed output')
    p.add_argument('host', type=str,
                   help='host string to restore from')
    p.add_argument('database', type=str,
                   help='database to restore from/to')
    p.add_argument('--user', dest='user', type=str,
                   default='root', help='local MySQL user')
    p.add_argument('--password', dest='password', type=str,
                   default='', help='local MySQL password')
    p.add_argument('--backupset', dest='backupset', type=str,
                   help=('ZRM backup set to restore from, '
                         'defaults to database capitalized'))
    p.add_argument('--timestamp', dest='timestamp', type=str,
                   help='timestamp to restore DB state from')
    args = p.parse_args()
    print "Restore %s from %s" % (args.database, args.host)

    if not args.backupset:
        args.backupset = args.database.capitalize()

    args.verbose = True

    manager = Manager(args)
    manager.restore(args.timestamp)


if __name__ == '__main__':
    main()
