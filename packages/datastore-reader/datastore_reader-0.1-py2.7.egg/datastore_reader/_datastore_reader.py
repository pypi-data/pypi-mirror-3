# -*- coding: utf-8 -*-
# python import
import json, os, tarfile
from datetime import datetime

# ds reader import
from datastore_reader.utils import _csv, config as c

# common relative store path
STORE_PATH = os.path.join(
                'home',
                'olpc',
                '.sugar',
                'default',
                'datastore',
                'store'
                )


def parse_meta_file(meta_path):
    """Returns an info dict from matadata content parsed.

    :param meta_path: '/somewhere/here/tmp/.../store/file.metadata'
    :return meta_dict: {'activity': 'paint', 'timestamp': '1324136292', ...}

    >>> datastore_path = './data/tmp/demo/home/olpc/.sugar/default/datastore/store'
    >>> meta_path      = os.path.join(datastore_path, 'demo.metadata')
    >>> parse_meta_file(meta_path)
    {u'activity_id': u'ec04b5191d6a0468ff1c23d4233a2e4438517a1a', u'title_set_by_user': u'0', u'uid': u'2f84e066-39d8-4e36-b389-79e430082ca0', u'vid': 2.0, u'title': u'Activit\\xe9 M\\xe9moriser', u'timestamp': 1308067572, u'mtime': u'2011-06-14T16:06:12.760893', u'keep': 0, u'icon-color': u'#00B20D,#FF8F00', u'activity': u'org.laptop.Memorize', u'mime_type': u''}

    """
    with open(meta_path, 'rb') as f:
        return json.load(f, 'utf-8')


def list_meta_files(datastore_path):
    """Iters the path for the metadata files found in the given datastore
    folder.

    :param datastore_path: ex.: '/somewhere/here/tmp/home/.../store'
    :return meta_path: ex.: ['/somewhere/here/tmp/.../store/file.metadata', ..]

    >>> path = './data/tmp/demo/home/olpc/.sugar/default/datastore/store'
    >>> [meta_path for meta_path in list_meta_files(path)]
    ['./data/tmp/demo/home/olpc/.sugar/default/datastore/store/demo.metadata']

    """
    for file_name in os.listdir(datastore_path):
        name, ext = os.path.splitext(file_name)
        if ext == '.metadata':
            yield os.path.join(datastore_path, file_name)


def extract_backup(backup_serial, backup_path):
    """Extracts backup archive in the tmp folder and the the corresponding
    datastore path.

    :param backup: a path, ex.: '/somewhere/here'
    :return backup: a path, ex.: '/somewhere/here/tmp/home/.../store'

    >>> extract_backup('demo', 'data/demo.tar.bz2')
    'data/tmp/demo/home/olpc/.sugar/default/datastore/store'

    """
    tmp_path = os.path.join(c.main.working_dir, 'tmp', backup_serial)
    with tarfile.open(backup_path) as t:
        t.extractall(tmp_path)
    # datastore should be as follow
    datastore_path = os.path.join(tmp_path, STORE_PATH)
    # check path or raise an error
    if os.path.exists(datastore_path):
        return datastore_path
    # Oups
    else:
        raise Exception('bad data store path for serial: %s!' % backup_serial)


def list_backups(working_dir):
    """Iters serial nb and path tuples according the backup files of the
    working dir, ex.: [('serial_1': '/somewhere/here')]

    Returns None if no working dir.

    :param working_dir: for testing issue otherwise use the value from
                        the config file.

    >>> [(s, p) for s, p in list_backups('data')]
    [('demo', 'data/demo.tar.bz2')]

    """
    for file_name in os.listdir(working_dir):
        name_tar, ext_bz2 = os.path.splitext(file_name)
        name, ext_tar = os.path.splitext(name_tar)
        if ext_bz2 == '.bz2' and ext_tar == '.tar':
            yield (name, os.path.join(working_dir, file_name))


def read_backups():
    # working dir check
    if not os.path.exists(c.main.working_dir):
        raise Exception('no working_dir found!')
    # out dir
    csv_dir = os.path.join(c.main.working_dir, 'out')
    if not os.path.exists(csv_dir):
        os.mkdir(csv_dir)
    # csv path
    csv_name = datetime.now().strftime('%Y-%m-%d_%H:%M_moulinette_result.csv')
    csv_path = os.path.join(csv_dir, csv_name)
    # columns shortcut
    columns = c.moulinette.columns.as_list()
    # init the csv writer
    with open(csv_path, 'wb') as f:
        # init csv writer
        writer = _csv.Writer(f, delimiter=';')
        # header line
        writer.writerow(columns)
        # list backups
        for backup_serial, backup_path in list_backups(c.main.working_dir):
            # extract backup
            datastore_path = extract_backup(backup_serial, backup_path)
            # list metadata
            for meta_path in list_meta_files(datastore_path):
                # parse the metadata file
                meta_dict = parse_meta_file(meta_path)
                # add serial do dict
                meta_dict['serial'] = backup_serial
                # write meta info in a new csv row according config
                row = list()
                for k in columns:
                    row.append(meta_dict[k] if k in meta_dict else '')
                # write row
                writer.writerow(row)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
