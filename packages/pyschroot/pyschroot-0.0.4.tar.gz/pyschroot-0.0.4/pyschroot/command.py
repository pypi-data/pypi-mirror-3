# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import os

SCHROOT_BIN = 'schroot'

class Schroot(object):

    __chroot_name = None
    __session = None

    @classmethod
    def MyPopen(cls, args):
        cmd =  Popen(args, stdout=PIPE, stderr=PIPE)
        cmd.wait()
        if cmd.returncode:
            raise Exception(
                'Unable to run COMMAND: %s; EXITCODE: %s; STDOUT: %s; STDERR: %s' % (
                    ' '.join(args), cmd.returncode, cmd.stdout.read(), cmd.stderr.read()
                )
            )
        return cmd

    def __init__(self, chroot_name):
        os.chdir('/')
        self.__chroot_name = chroot_name
        self.__start_session()

    def __start_session(self):
        cmd = Schroot.MyPopen([
            SCHROOT_BIN,
            '-c', self.__chroot_name,
            '-b'
        ])
        self.__session = cmd.stdout.read()[:-1]

    def run_cmd(self, *args, **kwargs):
        if 'directory' in kwargs:
            directory = kwargs['directory']
        else:
            directory = '/'

        cmd = [
            SCHROOT_BIN,
            '-d', directory,
            '-r',
            '-c', self.__session
        ]

        if 'user' in kwargs:
           cmd += ['-u', kwargs['user']]

        return Schroot.MyPopen(cmd + ['--'] + list(args))

    def __del__(self):
        if not self.__session:
            return

        Popen([
            SCHROOT_BIN,
            '-e',
            '-c', self.__session
        ]).wait()
