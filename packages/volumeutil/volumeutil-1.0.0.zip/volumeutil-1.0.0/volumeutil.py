#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A small utility for mount/unmount volume in Windows.

This utility provides volume operation functions for command-line interface.
 * mount volue
 * unmount volume
 * dump volume information

And this utility provides Volume Management API wrapper.
"""
# Volume Management - http://msdn.microsoft.com/library/aa365728.aspx
__version__ = '1.0.0'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
__url__ = 'http://pypi.python.org/pypi/volumeutil'
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
__classifiers__ = [i.strip()  for i in '''\
    Development Status :: 4 - Beta
    Environment :: Console
    Environment :: Win32 (MS Windows)
    Intended Audience :: Developers
    Intended Audience :: System Administrators
    License :: OSI Approved :: Python Software Foundation License
    Operating System :: Microsoft :: Windows
    Programming Language :: Python :: 3
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Filesystems
    Topic :: Utilities
    '''.splitlines() if i.strip()]
import sys, argparse, re
from ctypes import *
from ctypes.wintypes import *


def SetVolumeMountPoint(mountpoint, volumename):
    if not mountpoint.endswith('\\'):
        mountpoint += '\\'
    if not volumename.startswith('\\\\?\\'):
        volumename = GetVolumeNameForVolumeMountPoint(volumename)
    if not windll.kernel32.SetVolumeMountPointW(mountpoint, volumename):
        raise WinError()


def DeleteVolumeMountPoint(mountpoint):
    if not mountpoint.endswith('\\'):
        mountpoint += '\\'
    if not windll.kernel32.DeleteVolumeMountPointW(mountpoint):
        raise WinError()


def GetLogicalDrives() -> iter(['X:\\']):
    buf = create_unicode_buffer(
        '', windll.kernel32.GetLogicalDriveStringsW(0, None))
    windll.kernel32.GetLogicalDriveStringsW(len(buf), buf)
    return filter(None, ''.join(buf).split('\0'))


def FindVolumes() -> iter(['\\\\?\\Volume{GUID}\\']):
    buf = create_unicode_buffer('', MAX_PATH)
    handle = windll.kernel32.FindFirstVolumeW(buf, len(buf))
    if handle == -1:
        raise WinError()
    try:
        yield buf.value
        while windll.kernel32.FindNextVolumeW(handle, buf, len(buf)):
            yield buf.value
    finally:
        windll.kernel32.FindVolumeClose(handle)


def FindVolumeMountPoints(volumename: '\\\\?\\Volume{GUID}\\'):
    """Get volume mount path "under" the *volumename*.
    Note that this function requires "Administrators" privilege.
    """
    buf = create_unicode_buffer('', MAX_PATH + 1)
    handle = windll.kernel32.FindFirstVolumeMountPointW(
        volumename, buf, len(buf))
    if handle == -1:
        raise StopIteration
    try:
        yield buf.value
        while windll.kernel32.FindNextVolumeMountPointW(handle, buf, len(buf)):
            yield buf.value
    finally:
        windll.kernel32.FindVolumeMountPointClose(handle)


GetDriveTypeMap = {
    0: 'unknown',
    1: 'no_root_dir',
    2: 'removable',
    3: 'fixed',
    4: 'remote',
    5: 'cdrom',
    6: 'ramdisk',
    }


def GetDriveType(volumename: '\\\\?\\Volume{GUID}\\') -> 'type':
    return GetDriveTypeMap[windll.kernel32.GetDriveTypeW(volumename)]


def GetVolumeInformation(volumename: '\\\\?\\Volume{GUID}\\') -> {
        'name': str, 'serialnumber': int, 'maxcomponentlength': int,
        'filesystemflags': int, 'filesystem': str}:
    name = create_unicode_buffer('', MAX_PATH + 1)
    serialnumber = DWORD(0)
    maxcomponentlength = DWORD(0)
    filesystemflags = DWORD(0)
    filesystem = create_unicode_buffer('', MAX_PATH + 1)
    if not windll.kernel32.GetVolumeInformationW(volumename, name, len(name),
                                                 byref(serialnumber),
                                                 byref(maxcomponentlength),
                                                 byref(filesystemflags),
                                                 filesystem, len(filesystem)):
        try:
            raise WinError()
        except WindowsError as e:
            # device is not ready for removable media drive
            if e.winerror != 21:
                raise
    return {
        'name': name.value,
        'serialnumber': serialnumber.value,
        'filesystemflags': filesystemflags.value,
        'maxcomponentlength': maxcomponentlength.value,
        'filesystem': filesystem.value,
        }


def GetDiskFreeSpace(volumename: 'path') -> {
        'available': int, 'used': int, 'free': int}:
    available = ULARGE_INTEGER(0)
    used = ULARGE_INTEGER(0)
    free = ULARGE_INTEGER(0)
    if not windll.kernel32.GetDiskFreeSpaceExW(volumename, byref(available),
                                               byref(used), byref(free)):
        try:
            raise WinError()
        except WindowsError as e:
            # device is not ready for removable media drive
            if e.winerror != 21:
                raise
    return {
        'available': available.value,
        'used': used.value,
        'free': free.value,
        }


def GetVolumeNameForVolumeMountPoint(volumename: 'path') \
        -> '\\\\?\\Volume{GUID}\\':
    """Get "\\?\Volume{GUID}\" format string."""
    buf = create_unicode_buffer('', MAX_PATH + 1)
    if not windll.kernel32.GetVolumeNameForVolumeMountPointW(volumename,
                                                             buf, len(buf)):
        raise WinError()
    return buf.value


def GetVolumePathName(path):
    buf = create_unicode_buffer('', MAX_PATH + 1)
    if not windll.kernel32.GetVolumePathNameW(path, buf, len(buf)):
        raise WinError()
    return buf.value


def _drivemap() -> {'X:\\': '\\\\?\\Volume{GUID}\\'}:
    return dict((drive, GetVolumeNameForVolumeMountPoint(drive))
                for drive in GetLogicalDrives())


def getuuid(volumename: 'path') -> 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx':
    m = re.match(
        '//\?/Volume\{([0-9A-Fa-f\-]{36})\}/',
        GetVolumeNameForVolumeMountPoint(volumename).replace('\\', '/'))
    if m:
        return m.group(1)
    else:
        return ''


def getvolumeinfo(volumename: '\\\\?\\Volume{GUID}\\') -> dict:
    result = GetVolumeInformation(volumename)
    result['type'] = GetDriveType(volumename)
    result['mountpoints'] = list(FindVolumeMountPoints(volumename))
    result['uuid'] = getuuid(volumename)
    result.update(GetDiskFreeSpace(volumename))
    return result


def getvolumes() -> [{'volume': '\\\\?\\Volume{GUID}\\'}]:
    result = []

    drives = _drivemap()
    mounts = {}
    for volumename in FindVolumes():
        volume = getvolumeinfo(volumename)
        volume['volume'] = volumename
        result.append(volume)
        for driveletter, devicepath in drives.items():
            if devicepath == volumename:
                mounts[driveletter] = devicepath
        for i in volume['mountpoints']:
            path = volumename + i
            mounts[path] = GetVolumeNameForVolumeMountPoint(path)

    for volume in result:
        volume['mount'] = [i[0] for i in mounts.items()
                                if i[1] == volume['volume']]
    return result


def annotate(**kwargs):
    def result(function):
        for i in kwargs.items():
            setattr(function, *i)
        return function
    return result


class Main(object):

    format = {
        'serialnumber': '%.8x',
        'filesystemflags': '0x%.8x',
        }

    def _print_volumeinfo(self, volume, noprintkey=(), lineprefix=''):
        for key, value in sorted(volume.items()):
            if key in noprintkey: continue
            if isinstance(value, list):
                print(lineprefix + key)
                for i in sorted(value):
                    print(lineprefix + '\t%s' % i)
            else:
                if key in self.format:
                    value = self.format[key] % value
                print(lineprefix + '%s %s' % (key, value))

    def _getvolume(self, args, volumes):
        if args.path:
            path = args.path
            if not path.endswith('\\'):
                path += '\\'

            # resolve mountpoint
            if not path.startswith('\\'):
                path = GetVolumePathName(path)
                path = GetVolumeNameForVolumeMountPoint(path)

            for volume in volumes:
                if volume['volume'] == path:
                    return volume
            raise LookupError(args.path)

        elif args.label:
            for volume in volumes:
                if volume['name'].lower() == args.label.lower():
                    return volume
            raise LookupError(args.label)

        elif args.uuid:
            # normalize ({UUID} -> UUID)
            if args.uuid.startswith('{') and args.uuid.endswith('}'):
                args.uuid = args.uuid[1:-1]
            for volume in volumes:
                if volume['uuid'].lower() == args.uuid.lower():
                    return volume
            raise LookupError(args.uuid)

        raise ValueError('no volume indicator')

    def list(self, args):
        """list volume"""
        for volume in getvolumes():
            print(volume['volume'])
            self._print_volumeinfo(volume, ('volume', ), '\t')
            print()

    @annotate(arg_volume=True, arg_extra=dict(name='key', type=str, nargs='?'))
    def info(self, args):
        """show volume information"""
        #TODO: extra argument (dump key)
        volumes = getvolumes()
        volume = self._getvolume(args, volumes)
        if args.key:
            try:
                value = volume[args.key]
            except LookupError:
                print('%s is not found.' % args.key, file=sys.stderr)
            else:
                if isinstance(value, list):
                    for i in value:
                        print(i)
                else:
                    if args.key in self.format:
                        value = self.format[args.key] % value
                    print(value)
        else:
            self._print_volumeinfo(volume)

    @annotate(arg_volume=True, arg_extra=dict(name='dir', type=str, nargs=1))
    def mount(self, args):
        """mount volume"""
        volumes = getvolumes()
        volume = self._getvolume(args, volumes)
        SetVolumeMountPoint(args.dir[0], volume['volume'])

    @annotate(arg_volume=True)
    def unmount(self, args):
        """unmount volume"""
        if args.path:
            DeleteVolumeMountPoint(args.path)
        else:
            volumes = getvolumes()
            volume = self._getvolume(args, volumes)
            for i in volume['mount']:
                DeleteVolumeMountPoint(i)

    @property
    def _argparser(self):
        result = argparse.ArgumentParser(description=__doc__)

        #result.add_argument('--verbose', '-v', action='count', default=0)
        result.add_argument(
            '--version', action='version', version='%(prog)s ' + __version__)

        subparsers = result.add_subparsers(title='command')
        for name in dir(self):
            if name.startswith('_'): continue
            handler = getattr(self, name)
            if not hasattr(handler, '__call__'): continue

            subparser = subparsers.add_parser(name, help=handler.__doc__)
            subparser.set_defaults(func=handler)

            if getattr(handler, 'arg_volume', False):
                #group = subparser.add_argument_group()
                group = subparser.add_mutually_exclusive_group(required=True)
                group.add_argument('path', type=str, nargs='?')
                group.add_argument(
                    '--name', '--label', type=str,
                    help='volume name (known as volume lable)')
                group.add_argument(
                    '--uuid', type=str,
                    help='volume uuid (dump by "list" command)')
                #result.error(argparse._('too few arguments'))

            if hasattr(handler, 'arg_extra'):
                extra = dict(getattr(handler, 'arg_extra'))
                subparser.add_argument(extra.pop('name'), **extra)

        return result

    def __call__(self, argv):
        args = self._argparser.parse_args(argv[1:])
        try:
            result = args.func(args)
        except EnvironmentError as e:
            print(e, file=sys.stderr)
            if isinstance(e, WindowsError) and e.winerror == 5:
                print('Maybe administrator privilege is required.',
                      file=sys.stderr)
            return e.winerror if isinstance(e, WindowsError) else e.errno
        return result if result is not None else 0


main = Main()


if __name__ == '__main__':
    #TODO: pywin32's win32com.server.register.ReExecuteElevated
    #      http://msdn.microsoft.com/library/bb756922.aspx
    sys.exit(main(sys.argv))


