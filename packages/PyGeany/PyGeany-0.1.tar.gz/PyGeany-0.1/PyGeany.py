# -*- coding: utf-8 -*-

import os
import socket

from gi.repository import GLib, Gdk


class GeanyPackage(object):
    def __init__(self, data):
        self.data = data

    def serialize(self):
        return '{}\n.\n'.format('\n'.join(self.data))


class GeanyCommandBase(object):
    def get_name(self):
        return self.name

    def get_data(self):
        raise NotImplementedError()

    def get_packages(self):
        data = [self.get_name(), ]
        data.extend(self.get_data())

        return [GeanyPackage(data)]

    def dispatch(self, connection):
        connection.send(self)


class GeanyCommandOpenFile(GeanyCommandBase):
    name = 'open'

    def __init__(self, *args):
        self.files = args

    def get_data(self):
        return self.files


class GeanyCommandOpenFileReadOnly(GeanyCommandOpenFile):
    name = 'openro'


class GeanyCommandGoto(GeanyCommandBase):
    def __init__(self, column=None, line=None):
        if column is None and line is None:
            raise ValueError(
                'at least one of argument needs to be specified!'
            )

        self.column = column
        self.line = line

    def get_packages(self):
        packages = []

        if self.line is not None:
            packages.append(GeanyPackage(['line', str(self.line)]))

        if self.column is not None:
            packages.append(GeanyPackage(['column', str(self.column)]))

        return packages


class GeanyConnection(object):
    class Error(Exception):
        pass

    class ErrorAlreadyConnected(Error):
        pass

    class ErrorNotConnected(Error):
        pass

    def __init__(self, socket_path=None):
        if socket_path is None:
            socket_path = self.find_socket_path()
        self.socket_path = socket_path

        self.socket = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc_info):
        self.close()

    def get_config_dir(self):
        return os.path.join(GLib.get_user_config_dir(), 'geany')

    def find_socket_path(self):
        display_name = Gdk.get_display()

        display_name_sep = display_name.rfind('.')
        if display_name_sep > display_name.rfind(':'):
            display_name = display_name[:display_name_sep]
        display_name = display_name.replace(':', '_')

        socket_name = 'geany_socket_{}_{}'.format(
            socket.gethostname(), display_name
        )

        return os.path.join(self.get_config_dir(), socket_name)

    def open(self, socket_path=None):
        if self.socket is not None:
            raise self.ErrorAlreadyConnected()

        if socket_path is None:
            socket_path = self.socket_path

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        try:
            self.socket.connect(socket_path)

        except:
            self.socket.close()
            self.socket = None

            raise

    def send(self, command):
        if self.socket is None:
            raise self.ErrorNotConnected()

        data = []
        for package_data in command.get_packages():
            data.append(package_data.serialize())

        self.socket.send(''.join(data))

    def close(self):
        if self.socket is None:
            raise self.ErrorNotConnected()

        self.socket.close()
        self.socket = None

    def send_open(self, *args):
        cmd = GeanyCommandOpenFile(*args)
        return cmd.dispatch(self)

    def send_open_ro(self, *args):
        cmd = GeanyCommandOpenFileReadOnly(*args)
        return cmd.dispatch(self)

    def send_goto(self, line=None, column=None):
        cmd = GeanyCommandGoto(line=line, column=column)
        return cmd.dispatch(self)

