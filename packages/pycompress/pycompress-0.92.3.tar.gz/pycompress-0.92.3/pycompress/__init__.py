# -*- coding: utf-8 *-*
import logging
from subprocess import call
import multiprocessing
import pycompress
import os


def run_command(command, sfilename=None, logfile=None, options=None):
    """
    Run commands for both compress and decompress
    """
    try:
        info = call(command)
        if 'l' in options:
            return info
        if 'n' in options:
            print "Compression Successful"
        else:
            if not logfile:
                logfile = 'compress.log'
            logging.basicConfig(filename=logfile, level=logging.DEBUG)
            logging.debug("%sCompression Successful" % (sfilename))
    except Exception, e:
        if not logfile:
            logfile = 'compress.log'
        logging.basicConfig(filename=logfile, level=logging.DEBUG)
        logging.debug(e)
        if options:
            if 'n' in options:
                print "Error occured while processing %s. For more details  \
                       check %s" % (sfilename, logfile)


def compress(sfilename, dfilename, options=None, logfile=None):
    """
    Description: Uses zpaq algorithm to compress the sfilename, and puts in to
    the dfilename

    Arguments
    sfilename - path to source file
    dfilename - path to destination zpaq file
    options
        n - logs to logfile if provided, else to compress.log
        s - silent - fail safe, succeeds/fails silently [default]
    """
    if os.name == 'posix':
        command = [pycompress.__file__.split("_")[0] + 'zpaq.so']
    else:
        command = [pycompress.__file__.split("_")[0] + 'zpaq.dll']
    if options:
        if 'n' in options:
            command.append('vc')
    else:
        command.append('qc')
    command.append(dfilename)
    command.append(sfilename)
    daemon = multiprocessing.Process(name='compress', target=run_command, \
                                args=[command, sfilename, logfile, options])
    daemon.start()


def decompress(dfilename, sfilename, options=None, logfile=None):
    """
    Description: Uses zpaq algorithm to decompress the sfilename, and puts in to
    the dfilename

    Arguments
    dfilename - path to destination file
    sfilename - path to source zpaq file
    options
        s - silent - fail safe, succeeds/fails silently [default]
        n - verbose mode, logs to logfile if provided, else to compress.log
        d - delete source after compression
    """
    if os.name == 'posix':
        command = [pycompress.__file__.split("_")[0] + 'zpaq.so']
    else:
        command = [pycompress.__file__.split("_")[0] + 'zpaq.dll']
    if options:
        if 'n' in options:
            command.append('vd')
    else:
        command.append('qx')
    command.append(dfilename)
    command.append(sfilename)
    daemon = multiprocessing.Process(name='decompress', target=run_command, \
                                args=[command, sfilename, logfile, options])
    daemon.start()


def listarchive(sfilename, logfile=None):
    """
    Description: Lists contents of an zpaq archive

    Arguments
    sfilename - path to source zpaq file
    """

    if os.name == 'posix':
        command = [pycompress.__file__.split("_")[0] + 'zpaq.so', 'l']
    else:
        command = [pycompress.__file__.split("_")[0] + 'zpaq.dll', 'l']
    command.append(sfilename)
    info = run_command(command, '', logfile, 'l')
    return info
