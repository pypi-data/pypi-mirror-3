#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

gpg
===

GPG handling functions

Provides
--------

 * is_pyme_present: Checks if pyme is installed
 * genkey: Generates gpg key
 * sign: Returns detached signature for file
 * verify: verifies stream against signature

"""

from src.config import config


try:
    from pyme import core, pygpgme
    import pyme.errors
    PYME_PRESENT = True
    
except ImportError:
    PYME_PRESENT = False
    

def is_pyme_present():
    """Returns True if pyme can be imported else false"""
    
    return PYME_PRESENT

def _passphrase_callback(hint='', desc='', prev_bad=''): 
    """Callback function needed by pyme"""
    
    return config["gpg_key_passphrase"]

def _get_file_data(filename):
    """Returns pyme.core.Data object of file."""
    
    # Required because of unicode bug in pyme
    
    infile = open(filename, "rb")
    infile_content = infile.read()
    infile.close()
    
    return core.Data(string=infile_content)


def genkey():
    """Creates a new standard GPG key"""
    
    gpg_key_parameters = \
        '<GnupgKeyParms format="internal">\n' + \
        'Key-Type: DSA\n' + \
        'Key-Length: 2048\n' + \
        'Subkey-Type: ELG-E\n' + \
        'Subkey-Length: 2048\n' + \
        'Name-Real: ' + config["gpg_key_uid"] + '\n' + \
        'Name-Comment: Pyspread savefile signature keys\n' + \
        'Name-Email: pyspread@127.0.0.1\n' + \
        'Passphrase: ' + config["gpg_key_passphrase"] + '\n' + \
        'Expire-Date: 0\n' + \
        '</GnupgKeyParms>'
    
    # Initialize our context.
    core.check_version(None)

    context = core.Context()
    context.set_armor(1)
    #context.set_progress_cb(callbacks.progress_stdout, None)
    
    # Check if standard key is already present
    keyname = config["gpg_key_uid"]
    context.op_keylist_start(keyname, 0)
    key = context.op_keylist_next()
    if key is None:
        # Key not present --> Create new one
        print "Generating new GPG key", keyname, \
              ". This may take some time..."
        context.op_genkey(gpg_key_parameters, None, None)
        print context.op_genkey_result().fpr



def sign(filename):
    """Returns detached signature for file"""
    
    plaintext = _get_file_data(filename)
    
    ciphertext = core.Data()
    
    ctx = core.Context()

    ctx.set_armor(1)
    ctx.set_passphrase_cb(_passphrase_callback)
    
    ctx.op_keylist_start(config["gpg_key_uid"], 0)
    sigkey = ctx.op_keylist_next()
    ##print sigkey.uids[0].uid
    
    ctx.signers_clear()
    ctx.signers_add(sigkey)
    
    ctx.op_sign(plaintext, ciphertext, pygpgme.GPGME_SIG_MODE_DETACH)
    
    ciphertext.seek(0, 0)
    signature = ciphertext.read()
    
    return signature

def verify(sigfilename, filefilename=None):
    """Verifies a signature, returns True if successful else False."""
    
    context = core.Context()

    # Create Data with signed text.
    __signature = _get_file_data(sigfilename)
    
    if filefilename:
        __file = _get_file_data(filefilename)
        __plain = None
    else:
        __file = None
        __plain = core.Data()

    # Verify.
    try:
        context.op_verify(__signature, __file, __plain)
    except pyme.errors.GPGMEError:
        return False
    
    result = context.op_verify_result()
    
    # List results for all signatures. Status equal 0 means "Ok".
    validation_sucess = False
    
    for signature in result.signatures:
        if (not signature.status) and signature.validity:
            validation_sucess = True
    
    return validation_sucess
