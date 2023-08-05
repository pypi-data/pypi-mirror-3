# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

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
        self.__chroot_name = chroot_name
        self.__start_session()

    def __start_session(self):
        cmd = Schroot.MyPopen([
            SCHROOT_BIN,
            '-c', self.__chroot_name,
            '-b'
        ])
        self.__session = cmd.stdout.read()[:-1]

    def run_cmd(self, *args):
        cmd = Schroot.MyPopen([
            SCHROOT_BIN,
            '-r',
            '-c', self.__session,
            '--' ] + list(args)
        )
        return cmd.stdout

    def close(self):
        del(self)

    def __del__(self):
        if not self.__session:
            return

        Popen([
            SCHROOT_BIN,
            '-e',
            '-c', self.__session
        ])
