# -*- coding: utf-8 -*-
'''
Copyright (C) 2012 Karsten-Kai König <kkoenig@posteo.de>

This file is part of kppy.

kppy is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or at your option) any later version.

kppy is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
kppy.  If not, see <http://www.gnu.org/licenses/>.
'''

import struct
from datetime import datetime
from os import remove, path

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Cipher import AES


__doc__ = """This module implements the access to KeePass 1.x-databases."""

class StdGroup(object):
    """StdGroup represents a simple group of a KeePass 1.x database.
    
    Attributes:
    - id_ is the group id
    - title is the group title
    - image is the image number used in KeePassX
    - level is needed to create the group tree
    - parent is the previous group
    - children is a list of all following groups
    - entries is a list of all entries of the group
    - db is the database which holds the group
    
    """

    def __init__(self, id_ = None, title = None, image = 1, db = None,
                 level = 0, parent = None, children = [], entries = []):
        self.id_ = id_
        self.title = title
        self.image = image
        self.level = level
        self.parent = parent
        self.children = list(children)
        self.entries = list(entries)
        self.db = db

    def set_title(self, title = None):
        """ This method just calls set_group_title of the holding db."""
        
        return self.db.set_group_title(self.id_, title)

    def set_image(self, image = None):
        """This method just calls set_group_image of the holding db."""

        return self.db.set_group_image(self.id_, image)

    def move_group(self, index = None, parent = None):
        """This method just calls move_group of the holding db."""

        return self.db.move_group(self.id_, index, parent)

class StdEntry(object):
    """StdEntry represents a simple entry of a KeePass 1.x database.
    
    Attributes:
        - uuid is an "Universal Unique ID", that is it identifies the entry
        - group_id is the id of the holding group
        - group is the holding StdGroup instance
        - image is the image number
        - title is the entry title
        - url is an url to a website where the login information of this entry
          can be used
        - username is an username
        - password is the password
        - binary_desc is the description of meta-data which binary holds
        - creation is the creation date of this entry
        - last_mod is the date of the last modification
        - last_access is the date of the last access
        - expire is the date when the entry should expire
        
    """

    def __init__(self, group_id = None, group = None,
                 image = 1, title = None, url = None, username = None,
                 password = None, comment = None, 
                 creation = None, last_mod = None, last_access = None, 
                 expire = None, uuid = None, binary_desc = None,
                 binary = None):
        self.uuid = uuid
        self.group_id = group_id
        self.group = group
        self.image = image
        self.title = title
        self.url = url
        self.username = username
        self.password = password
        self.comment = comment
        self.binary_desc = binary_desc
        self.creation = creation
        self.last_mod = last_mod
        self.last_access = last_access
        self.expire = expire
        self.binary = binary

    def set_title(self, title = None):
        """ This method just calls set_entry_title of the holding db."""
        
        self.group.db.set_entry_title(self.uuid, title)
        
    def set_image(self, image = None):
        """ This method just calls set_entry_image of the holding db."""
        
        return self.group.db.set_entry_image(self.uuid, image)
        
    def set_url(self, url = None):
        """ This method just calls set_entry_url of the holding db."""
        
        return self.group.db.set_entry_url(self.uuid, url)
        
    def set_username(self, username = None):
        """ This method just calls set_entry_username of the holding db."""
        
        return self.group.db.set_entry_username(self.uuid, username)
        
    def set_password(self, password = None):
        """ This method just calls set_entry_password of the holding db."""
        
        return self.group.db.set_entry_password(self.uuid, password)
        
    def set_comment(self, comment = None):
        """ This method just calls set_entry_comment of the holding db."""
        
        return self.group.db.set_entry_comment(self.uuid, comment)
        
    def set_expire(self, y = 2999, mon = 12, d = 28, h = 23, min_ = 59, s = 59):
        """ This method just calls set_entry_expire of the holding db."""
        
        return self.group.db.set_entry_expire(self.uuid, y, mon, d, h, min_, s)

    def move_entry(self, id_ = None):
        """This method just calls move_entry of the holding db."""

        return self.group.db.move_entry(self.uuid, id_)

class KPError(Exception):
    """KPError is a exception class to handle exception raised by KPDB.
    
    Usage:
    
    Handle KPError like every else expection. You can print the error message
    via an expection instance.
    
    Example:
    
    except KPError as e:
        print(e)
        
    """

    def __init__(self, error):
        self.msg = error

    def __str__(self):
        return ("KPError: "+self.msg)

class KPDB(object):
    """KPDB represents the KeePass 1.x database.
    
    Attributes:
    - groups holds all groups of the database
    - read_only declares if the file should be read-only or not
    - filepath holds the path of the database
    - masterkey is the passphrase to encrypt and decrypt the database
    
    Usage:
    
    You can load a KeePass database by the filename and the passphrase or
    create an empty database. It's also possible to open the database read-only
    and to create a new one.
    
    Example:
    
    from kppy import KPDB, KPError
    
    try;
        db = KPDB(filepath, passphrase)
    except KPError as e:
        print(e)
    
    """

    def __init__(self, filepath=None, masterkey=None, read_only=False,
                 new = False):
        """ Initialize a new or an existing database.

        If a 'filepath' and a 'masterkey' is passed 'load' will try to open
        a database. If 'True' is passed to 'read_only' the database will open
        read-only. It's also possible to create a new one, just pass 'True' to
        new. This will be ignored if a filepath and a masterkey is given this
        will be ignored.
        
        """
        
        self.groups = []
        self.read_only = read_only
        self.filepath = filepath
        self.masterkey = masterkey

        # This are attributes that are needed internally. You should not
        # change them directly, it could damage the database!
        self._entries = []
        self._root_group = StdGroup()
        self._group_order = []
        self._entry_order = []
        self._unsupported_g_fields = []
        self._unsupported_e_fields = []
        self._signature1 = 0x9AA2D903
        self._signature2 = 0xB54BFB65
        self._enc_flag = 2
        self._version = 0x00030002
        self._final_randomseed = ''
        self._enc_iv = ''
        self._num_groups = 1
        self._num_entries = 0
        self._contents_hash = ''
        self._transf_randomseed = Random.get_random_bytes(32)
        self._key_transf_rounds = 50000

        # Load an existing database
        if filepath is not None and masterkey is not None:
            self.load()
        # To open a database two informations are needed
        elif (filepath is None and masterkey is not None) or (filepath is not \
            None and masterkey is None):
            raise KPError('Missing argument: file path or master key needed '
                          'additionally to open an existing database!')
        # Due to the design of KeePass, at least one group is needed.
        elif new:
            self._group_order = [("id", 1), (1,4), (2,9), (7,4), (8,2),
                                 (0xFFFF, 0)]
            group = StdGroup(1, 'Internet', 1, self, parent = self._root_group)
            self._root_group.children.append(group)
            self.groups.append(group)
        
    def load(self):
        """This method opens an existing database.

        self.masterkey and self.filepath needs to be set.
        
        """

        if self.masterkey is None or self.filepath is None:
            raise KPError('Can only load an existing database!')
            return False
        
        # Open the file
        try:
            handler = open(self.filepath, 'rb')
        except IOError:
            raise KPError('Can\'t open {0}!'.format(self.filepath))
            return False

        # Read the file and close it finally
        try:
            buf = handler.read()
            
            # There should be a header at least
            if len(buf) < 124:
                raise KPError('Unexpected file size. It should be more or'
                              'equal 124 bytes but it is {0}!'.format(len(buf)))
                return False
        except IOError:
            raise KPError('Can\'t read {0}!'.format(self.filepath))
            handler.close()
            return False
        finally:
            handler.close()
        
        # The header is 124 bytes long, the rest is content
        header = buf[:124]
        crypted_content = buf[124:]
        del buf
        
        # The header holds two signatures
        if not (struct.unpack('<I', header[:4])[0] == 0x9AA2D903 and
                struct.unpack('<I', header[4:8])[0] == 0xB54BFB65):
            raise KPError('Wrong signatures!')
            del crypted_content
            del header
            return False

        # Unpack the header
        self._enc_flag = struct.unpack('<I', header[8:12])[0]
        self._version = struct.unpack('<I', header[12:16])[0]
        self._final_randomseed = struct.unpack('<16s', header[16:32])[0]
        self._enc_iv = struct.unpack('<16s', header[32:48])[0]
        self._num_groups= struct.unpack('<I', header[48:52])[0]
        self._num_entries = struct.unpack('<I', header[52:56])[0]
        self._contents_hash = struct.unpack('<32s', header[56:88])[0]
        self._transf_randomseed = struct.unpack('<32s', header[88:120])[0]
        self._key_transf_rounds = struct.unpack('<I', header[120:124])[0]
        del header

        # Check if the database is supported
        if self._version & 0xFFFFFF00 != 0x00030002 & 0xFFFFFF00:
            raise KPError('Unsupported file version!')
            del crypted_content
            return False
        #Actually, only AES is supported.
        elif not self._enc_flag & 2:
            raise KPError('Unsupported file encryption!')
            del crypted_content
            return False
        
        # Create the key that is needed to...
        final_key = self._transform_key()
        # ...decrypt the content
        decrypted_content = self._cbc_decrypt(final_key, crypted_content)

        # Check if decryption failed
        if (len(decrypted_content) > 2147483446) or \
            (len(decrypted_content) == 0 and self._num_groups > 0):
            raise KPError("Decryption failed!\nThe key is wrong or the file is"
                          " damaged.")
            del decrypted_content
            del crypted_content
            return False

        sha_obj = SHA256.new()
        sha_obj.update(decrypted_content)
        if not self._contents_hash == sha_obj.digest():
            raise KPError("Hash test failed.\nThe key is wrong or the file is "
                          "damaged.")
            return False
        del final_key

        # Read out the groups
        pos = 0
        levels = []
        cur_group = 0
        group = StdGroup()

        while cur_group < self._num_groups:
            # Every group is made up of single fields
            field_type = struct.unpack('<H', decrypted_content[:2])[0]
            decrypted_content = decrypted_content[2:]
            pos += 2

            # Check if offset is alright
            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G1]')
                del decrypted_content
                del crypted_content
                return False
            
            field_size = struct.unpack('<I', decrypted_content[:4])[0]
            decrypted_content = decrypted_content[4:]
            pos += 4
            
            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G2]')
                del decrypted_content
                del crypted_content
                return False

            # Finally read out the content
            b_ret = self._read_group_field(group, levels, field_type,
                                           field_size, decrypted_content)

            # If the end of a group is reached append it to the groups array
            if field_type == 0xFFFF and b_ret == True:
                group.db = self
                self.groups.append(group)
                group = StdGroup()
                cur_group += 1
            
            # Some fields are currently not implemented
            if field_type == 0x0003 or field_type == 0x0004 or \
                field_type == 0x0005 or field_type == 0x0006 or \
                field_type == 0x0009 or field_type == 0x0000:
                self._unsupported_g_fields.append(decrypted_content[:field_size])
    
            decrypted_content = decrypted_content[field_size:]

            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G1]')
                del decrypted_content
                del crypted_content
                return False

            #This is needed to write changes
            if field_type == 0x0000:
               self._group_order.append(("id", group.id_))
            elif self._group_order:
                if field_type == 0x0001 and self._group_order[-1][0] != 0x0000:
                    self._group_order.append(("id", group.id_))
            self._group_order.append((field_type, field_size))

        # Now the same with the entries
        cur_entry = 0
        entry = StdEntry()
        
        while cur_entry < self._num_entries:
            field_type = struct.unpack('<H', decrypted_content[:2])[0]
            decrypted_content = decrypted_content[2:]
            pos += 2
             
            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G1]')
                del decrypted_content
                del crypted_content
                return False
            
            field_size = struct.unpack('<I', decrypted_content[:4])[0]
            decrypted_content = decrypted_content[4:]
            pos +=4
            
            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G2]')
                del decrypted_content
                del crypted_content
                return False
            
            b_ret = self._read_entry_field(entry, field_type, field_size,
                                      decrypted_content)
            
            if field_type == 0xFFFF and b_ret == True:
                self._entries.append(entry)
                if not entry.group_id:
                    raise KPError("Found entry without group!")
                    del decrypted_content
                    del crypted_content
                    return False

                entry = StdEntry()
                cur_entry += 1
            
            if field_type == 0x0000:
                self._unsupported_e_fields.append(decrypted_content[:field_size])

            decrypted_content = decrypted_content[field_size:]
            pos += field_size
            
            if pos >= len(crypted_content)+124:
                raise KPError('Unexpected error: Offset is out of range.[G1]')
                del decrypted_content
                del crypted_content
                return False
            if field_type == 0x0000:
                self._entry_order.append(("uuid", entry.uuid))
            elif field_type == 0x0001:
                if self._entry_order:
                    if not self._entry_order[-1] == 0x0000:
                        self._entry_order.append(("uuid", entry.uuid))
                else:
                    self._entry_order.append(("uuid", entry.uuid))
            self._entry_order.append((field_type, field_size))

        if self._create_group_tree(levels) is False:
            del decrypted_content
            del crypted_content
            return False

        del decrypted_content
        del crypted_content

        try:
            handler = open(self.filepath+'.lock', 'w')
            handler.write('')
        finally:
            handler.close()

        return True

    def save(self, filepath = None):
        """This method saves the database.

        It's possible to parse a data path to an alternative file.

        """

        if self.read_only:
            raise KPError("The database has been opened read-only.")
            return False
        elif self.masterkey is None or (self.filepath is None and \
            filepath is None):
            raise KPError("Need a passphrase and a filepath to save the file.")
            return False
        elif self._num_groups == 0:
            raise KPError("Need at least one group!")
            return False
        
        content = bytearray()
        pos = 0
        group = 0

        # First, read out all groups
        for field_type, field_size in self._group_order:
            if field_type == "id":
                continue

            # Get the packed bytes
            ret_save = self._save_group_field(field_type, field_size, 
                                                self.groups[group])

            # Catch illegal group fields, maybe the data was wrong manipulated
            if ret_save is False:
                raise KPError("Illegal group field found while saving")
                return False

            # The field type and the size is always in front of the data
            content += struct.pack('<H', field_type)
            content += struct.pack('<I', field_size)

            # Write unsupported fields
            if field_type == 0x0000 or field_type == 0x0003 or \
                field_type == 0x0004 or field_type == 0x0005 or \
                field_type == 0x0006 or field_type == 0x0009:
                content += self._unsupported_g_fields[pos]
                pos += 1
            elif not field_type == 0xFFFF:
                content += ret_save
            # If it's the end of the group, go to the next one
            elif field_type == 0xFFFF:
                group += 1

        pos = 0
        entry = 0

        # Same with entries
        for field_type, field_size in self._entry_order:
            if field_type == "uuid":
                continue
            ret_save = self._save_entry_field(field_type, field_size,
                                                self._entries[entry])

            if ret_save is False:
                raise KPError("Illegal entry field found while saving")
                return False

            content += struct.pack('<H', field_type)
            content += struct.pack('<I', field_size)

            if field_type == 0x0000:
                content += self._unsupported_e_fields[pos]
                pos += 1
            elif not field_type == 0xFFFF:
                content += ret_save
            elif field_type == 0xFFFF:
                entry += 1

        # Generate new seed and new vector; calculate the new hash
        self._final_randomseed = Random.get_random_bytes(16)
        self._enc_iv = Random.get_random_bytes(16)
        sha_obj = SHA256.new()
        sha_obj.update(bytes(content))
        self._contents_hash = sha_obj.digest()
        del sha_obj

        # Pack the header
        header = bytearray()
        header += struct.pack('<I', 0x9AA2D903)
        header += struct.pack('<I', 0xB54BFB65)
        header += struct.pack('<I', self._enc_flag)
        header += struct.pack('<I', self._version)
        header += struct.pack('<16s', self._final_randomseed)
        header += struct.pack('<16s', self._enc_iv)
        header += struct.pack('<I', self._num_groups)
        header += struct.pack('<I', self._num_entries)
        header += struct.pack('<32s', self._contents_hash)
        header += struct.pack('<32s', self._transf_randomseed)
        header += struct.pack('<I', self._key_transf_rounds)

        # Finally encrypt everything...
        final_key = self._transform_key()

        encrypted_content = self._cbc_encrypt(content, final_key)
        del content
        del final_key
        
        # ...and write it out
        try:
            if filepath is not None:
                handler = open(filepath, "wb")
                if self.filepath is None:
                    self.filepath = filepath
            elif filepath is None and self.filepath is not None:
                handler = open(self.filepath, "wb")
            else:
                raise KPError("Need a filepath.")
                return False
            handler.write(header+encrypted_content)
            
            if not path.isfile(self.filepath+".lock"):
                lock= open(filepath+".lock", "w")
                lock.write('')
                lock.close()
        finally:
            handler.close

        return True

    def close(self):
        """This method closes the database correctly."""
        
        if self.filepath is not None:
            remove(self.filepath+'.lock')
            return True
        else:
            raise KPError('Can\'t close a not opened file')
            return False

    def create_group(self, title = None, parent_id = None, image = 1):
        """This method creates a new group.

        A group title is needed or no group will be created.

        If a parent id is given, the group will be created as a sub-group.

        """
        
        if title is None:
            raise KPError("Need a group title to create a group.")
            return False

        id_ = 1
        for i in self.groups:
            if i.id_ >= id_:
                id_ = i.id_
        
        id_ += 1 
        group = StdGroup(id_, title, image, self)
        
        # If no parent is given, just append the new group at the end
        if parent_id is None:
            group.parent = self._root_group
            self._root_group.children.append(group)
            group.level = 0
            self.groups.append(group)
            self._group_order.append(("id", id_))
            self._group_order.append((1,4))
            self._group_order.append((2,len(title)+1))
            self._group_order.append((7,4))
            self._group_order.append((8,2))
            self._group_order.append((0xFFFF, 0))
        # If a parent is given it's more complex
        else:
            # First count through all groups...
            for i in self.groups:
                # ...until parent is found
                if i.id_ == parent_id:
                    # Append the group to the parent as a children and set
                    # the other trivial stuff
                    i.children.append(group)
                    group.parent = i
                    group.level = i.level+1
                    self.groups.insert(self.groups.index(i)+1, group)

                    # And now insert the field information at the right pos.
                    parent = False
                    index = 0
                    for j in self._group_order:
                        # The loop count through the order until the
                        # information of the parent are found. Then insert the 
                        # new field information.
                        if j[0] == "id" and j[1] == parent_id:
                            parent = True
                        elif j[0] == 0xFFFF and parent is True:
                            self._group_order.insert(index+1, (0xFFFF, 0))
                            self._group_order.insert(index+1, (8,2))
                            self._group_order.insert(index+1, (7,4))
                            self._group_order.insert(index+1, (2,len(title)+1))
                            self._group_order.insert(index+1, (1,4))
                            self._group_order.insert(index+1, ("id", id_))
                            break
                        elif index+1 == len(self._group_order):
                            raise KPError("Didn't find parent in group order")
                            return False
                        index += 1
                    break
                elif i is self.groups[-1]:
                    raise KPError("Given group doesn't exist")
                    return False
        
        self._num_groups += 1

        return True

    def remove_group(self, id_ = None):
        """This method removes a group.

        The group id is needed to remove the group.
        
        """

        if id_ is None:
            raise KPError("Need group id to remove a group")
            return False

        children = []
        entries = []

        # Search fo the given group
        for i in self.groups:
            if i.id_ == id_:
                # If the group is found save all children's and entries' ids to
                #  delete them later
                for j in i.children:
                    children.append(j.id_)
                for j in i.entries:
                    entries.append(j.uuid)
                # Finally remove group
                i.parent.children.remove(i)
                self.groups.remove(i)
                break
            elif i is self.groups[-1]:
                raise KPError("Given group doesn't exist")
                return False

        # Delete also group from group_order
        index = 0
        while True:
            if self._group_order[index][0] == "id" and \
                self._group_order[index][1] == id_:
                while True:
                    t = self._group_order[index][0]
                    del self._group_order[index]
                    if t == 0xFFFF:
                        break
                break
            elif index+1 == len(self._group_order):
                raise KPError("Didnt' find group in group order")
                return False
            index += 1

        self._num_groups -= 1
        
        '''
        #from python cookbook
        if children:
            children.sort()
            last = children[-1]
            for i in range(len(children)-2, -1, -1):
                if last == children[i]:
                    del children[i]
                else:
                    last = children[i]
        '''
        # Delete all children and entries
        for i in children:
            self.remove_group(i)
        for i in entries:
            self.remove_entry(i)     

        return True

    def set_group_title(self, id_ = None, title = None):
        """This method is used to change a group title.

        Two arguments are needed: The id of the group whose title should
        be changed and the new title.
        
        """
        
        if id_ is None or type(id_) is not int or title is None or \
            type(title) is not str:
            raise KPError("Need a group id and a new title!")
            return False

        # Search for group and update title
        for i in self.groups:
            if i.id_ == id_:
                i.title = title
                break
            elif i is self.groups[-1]:
                raise KPError("Given group doesn't exist.")
                return False

        # Now update group order
        found = False
        index = 0
        for i in self._group_order:
            # Go through order until the entries of the given group are reached
            if i[0] == "id" and i[1] == id_:
                found = True
            elif found is True and i[0] == 0x0002:
                # Remove tuple which holds information about title length and
                # create a new one
                del self._group_order[index]
                self._group_order.insert(index, (2, len(title)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._group_order[-1]):
                raise KPError("Given group hasn't an title. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._group_order):
                raise KPError("Given group doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1
    
        return True

    def set_group_image(self, id_ = None, image = None):
        """This method is used to change the image number if a group.

        Two arguments are needed: The id of the group whose image should
        be changed and the new image number.
        
        """
        
        if id_ is None or image is None or type(image) is not int:
            raise KPError("Need a group id and an image number!")
            return False

        for i in self.groups:
            if i.id_ == id_:
                i.image = image
                break
            elif i is self.groups[-1]:
                raise KPError("Given group doesn't exist.")
                return False
        
        return True

    def move_group(self, id_ = None,  index = None, parent = None):
        """Move group to a specific index in self.group.

        A valid group id and a valid index must be given. Index starts at 0 and
        ends at len(self.groups). Special index -1 means that the group will
        append at the end if self.groups.

        WARNING: If you parse a parent group make sure that no invalid group
        tree is going to created. For further details watch the tutorial.
        """

        if id_ is None or type(id_) is not int or index is None or \
            type(index) is not int or index < -1 or index >= len(self.groups):
            raise KPError("A valid group id and a valid index must be given.")
            return False

        if parent is None:
            parent = self._root_group

        for i in self.groups:
            if id_ == i.id_:
                i.parent.children.remove(i)
                i.parent = parent
                i.parent.children.append(i)
                if parent is self._root_group:
                    i.level = 0
                else:
                    i.level = i.parent.level + 1
                self.groups.remove(i)
                if index == -1:
                    self.groups.append(i)
                else:
                    self.groups.insert(index, i)
                reverse_children = []
                for j in i.children:
                    reverse_children.insert(0, j)
                group = i
                break
            elif i is self.groups[-1]:
                raise KPError("Didn't find given group.")
                return False

        index2 = 0
        index3 = 0
        index4 = 0
        for i in self._group_order:
            if i[0] == "id" and i[1] == id_:
                for j in self._group_order:
                    if index3 == index:
                        break
                    elif j[0] == 0xFFFF:
                        index3 += 1
                    index4 += 1
                while self._group_order[index2][0] != 0xFFFF:
                    self._group_order.insert(index4,
                                             self._group_order[index2])
                    del self._group_order[index2+1]
                    index2 += 1
                    index4 += 1
                self._group_order.insert(index4,
                                         self._group_order[index2])
                del self._group_order[index2+1]
                break
            elif index2+1 >= len(self._group_order):
                raise KPError("Given group doesn't exist in group order. "
                              "Something went very wrong.")
            index2 += 1

        for i in reverse_children:
            if index == -1:
                self.move_group(i.id_, -1, group)
            else:
                self.move_group(i.id_, index+1, group)

    def create_entry(self, group_id = None, title = "", image = 1, url = "",
                     username = "", password = "", comment = "",
                     y = 2999, mon = 12, d = 28, h = 23, min_ = 59,
                     s = 59):
        """This method creates a new entry.
        
        The group id of the group which should hold the entry is needed.
        
        There must be at least one of the following parameters given:
            - an entry title
            - an url
            - an username
            - a password
            - a comment
        
        It is possible to give an expire date in the following way:
            - y is the year between 1 and 9999 inclusive
            - mon is the month between 1 and 12
            - d is a day in the given month
            - h is a hour between 0 and 23
            - min_ is a minute between 0 and 59
            - s is a second between 0 and 59

        The special date 2999-12-28 23:59:59 means that entry expires never.
        
        """
        
        # Search for the group.
        group = None
        for i in self.groups:
            if group_id == i.id_:
                group = i
                break
            elif i is self.groups[-1]:
                raise KPError("No group for given group id.")
                return False
        
        if y > 9999 or y < 1 or mon > 12 or mon < 1 or d > 31 or d < 1 or \
            h > 23 or h < 0 or min_ > 59 or min_ < 0 or s > 59 or s < 0:
            raise KPError("No legal date")
            return False
        
        if ((mon == 1 or mon == 3 or mon == 5 or mon == 7 or mon == 8 or \
             mon == 10 or mon == 12) and d > 31) or ((mon == 4 or mon == 6 or \
             mon == 9 or mon == 11) and d > 30) or (mon == 2 and d > 28):
            raise KPError("Given day doesn't exist in given month")
            return False
            
        if title == "" and url == "" and username == "" and \
            password == "" and comment == "":
            raise KPError("Need at least one attribute to create an"
                          "entry.")
            return False
        
        uuid = Random.get_random_bytes(16)
        self._entry_order.append(("uuid", uuid))
        self._entry_order.append((0x0001, 16))
        self._entry_order.append((0x0002, 4))
        self._entry_order.append((0x0003, 4))
        self._entry_order.append((0x0004, len(title)+1))
        self._entry_order.append((0x0005, len(url)+1))
        self._entry_order.append((0x0006, len(username)+1))
        self._entry_order.append((0x0007, len(password)+1))
        self._entry_order.append((0x0008, len(comment)+1))
        self._entry_order.append((0x0009, 5))
        self._entry_order.append((0x000A, 5))
        self._entry_order.append((0x000B, 5))
        self._entry_order.append((0x000C, 5))
        self._entry_order.append((0xFFFF, 0))
        
        entry = StdEntry(group.id_, group, image, title, url, username,
                         password, comment, 
                         datetime.now().replace(microsecond = 0),
                         datetime.now().replace(microsecond = 0),
                         datetime.now().replace(microsecond = 0),
                         datetime(y, mon, d, h, min_, s),
                         uuid)
        self._entries.append(entry)
        group.entries.append(entry)
        self._num_entries += 1
        
        return True

    def remove_entry(self, uuid = None):
        """This method can remove entries.
        
        The uuid of the entry is needed.
        
        """
        
        if uuid is None:
            raise KPError("Need an uuid.")
            return False
        
        for i in self._entries:
            if uuid == i.uuid:
                i.group.entries.remove(i)
                self._entries.remove(i)
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False
        
        
        index = 0
        while True:
            if self._entry_order[index][0] == "uuid" and \
                self._entry_order[index][1] == uuid:
                while True:
                    t = self._entry_order[index][0]
                    del self._entry_order[index]
                    if t == 0xFFFF:
                        break
                break
            elif index+1 == len(self._entry_order):
                raise KPError("Didn't find entry's information in entry order.")
                return False
            index += 1

        self._num_entries -= 1
        
        return True

    def set_entry_comment(self, uuid = None, comment = None):
        """This method is used to change an entry comment.

        Two arguments are needed: The uuid of the entry whose comment should
        be changed and the new comment.
        
        """

        if uuid is None or comment is None or type(comment) is not str:
            raise KPError("Need an uuid and a new comment")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                if i.password == "" and i.title == "" and i.url == "" and \
                    i.username == "" and comment == "":
                    raise KPError("There must be at least one of the following" 
                                  "arguments given:\n\t- an entry title\n"
                                  "\t- an url\n"
                                  "\t- an username\n"
                                  "\t- a password\n"
                                  "\t- a comment\n")
                    return False
                i.comment = comment
                i.last_mod = datetime.now().replace(microsecond = 0)
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

        index = 0
        found = False
        for i in self._entry_order:
            if i[0] == "uuid" and i[1] == uuid:
                found = True
            elif found is True and i[0] == 0x0008:
                del self._entry_order[index]
                self._entry_order.insert(index, (0x0008, len(comment)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._entry_order[-1]):
                raise KPError("Given entry hasn't an comment. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._entry_order):
                raise KPError("Given entry doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1

    def set_entry_title(self, uuid = None, title = None):
        """This method is used to change an entry title.

        Two arguments are needed: The uuid of the entry whose title should
        be changed and the new title.
        
        """

        if uuid is None or title is None or type(title) is not str:
            raise KPError("Need an uuid and a new title")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                if i.password == "" and title == "" and i.url == "" and \
                    i.username == "" and i.comment == "":
                    raise KPError("There must be at least one of the following" 
                                  "arguments given:\n\t- an entry title\n"
                                  "\t- an url\n"
                                  "\t- an username\n"
                                  "\t- a password\n"
                                  "\t- a comment\n")
                    return False
                i.last_mod = datetime.now().replace(microsecond = 0)
                i.title = title
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

        index = 0
        found = False
        for i in self._entry_order:
            if i[0] == "uuid" and i[1] == uuid:
                found = True
            elif found is True and i[0] == 0x0004:
                del self._entry_order[index]
                self._entry_order.insert(index, (0x0004, len(title)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._entry_order[-1]):
                raise KPError("Given entry hasn't an title. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._entry_order):
                raise KPError("Given entry doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1

    def set_entry_password(self, uuid = None, password = None):
        """This method is used to change an entry password.

        Two arguments are needed: The uuid of the entry whose password should
        be changed and the new password.
        
        """

        if uuid is None or password is None or type(password) is not str:
            raise KPError("Need an uuid and a new password")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                if password == "" and i.title == "" and i.url == "" and \
                    i.username == "" and i.comment == "":
                    raise KPError("There must be at least one of the following" 
                                  "arguments given:\n\t- an entry title\n"
                                  "\t- an url\n"
                                  "\t- an username\n"
                                  "\t- a password\n"
                                  "\t- a comment\n")
                    return False
                i.last_mod = datetime.now().replace(microsecond = 0)
                i.password = password
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

        index = 0
        found = False
        for i in self._entry_order:
            if i[0] == "uuid" and i[1] == uuid:
                found = True
            elif found is True and i[0] == 0x0007:
                del self._entry_order[index]
                self._entry_order.insert(index, (0x0007, len(password)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._entry_order[-1]):
                raise KPError("Given entry hasn't an password. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._entry_order):
                raise KPError("Given entry doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1

    def set_entry_url(self, uuid = None, url = None):
        """This method is used to change an entry url.

        Two arguments are needed: The uuid of the entry whose url should
        be changed and the new url.
        
        """

        if uuid is None or url is None or type(url) is not str:
            raise KPError("Need an uuid and a new url")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                if i.password == "" and i.title == "" and url == "" and \
                    i.username == "" and i.comment == "":
                    raise KPError("There must be at least one of the following" 
                                  "arguments given:\n\t- an entry title\n"
                                  "\t- an url\n"
                                  "\t- an username\n"
                                  "\t- a password\n"
                                  "\t- a comment\n")
                    return False
                i.last_mod = datetime.now().replace(microsecond = 0)
                i.url = url
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

        index = 0
        found = False
        for i in self._entry_order:
            if i[0] == "uuid" and i[1] == uuid:
                found = True
            elif found is True and i[0] == 0x0005:
                del self._entry_order[index]
                self._entry_order.insert(index, (0x0005, len(url)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._entry_order[-1]):
                raise KPError("Given entry hasn't an url. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._entry_order):
                raise KPError("Given entry doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1

    def set_entry_username(self, uuid = None, username = None):
        """This method is used to change an entry username.

        Two arguments are needed: The uuid of the entry whose username should
        be changed and the new username.
        
        """

        if uuid is None or username is None or type(username) is not str:
            raise KPError("Need an uuid and a new username")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                if i.password == "" and i.title == "" and i.url == "" and \
                    username == "" and i.comment == "":
                    raise KPError("There must be at least one of the following" 
                                  "arguments given:\n\t- an entry title\n"
                                  "\t- an url\n"
                                  "\t- an username\n"
                                  "\t- a password\n"
                                  "\t- a comment\n")
                    return False
                i.last_mod = datetime.now().replace(microsecond = 0)
                i.username = username
                break
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

        index = 0
        found = False
        for i in self._entry_order:
            if i[0] == "uuid" and i[1] == uuid:
                found = True
            elif found is True and i[0] == 0x0006:
                del self._entry_order[index]
                self._entry_order.insert(index, (0x0006, len(username)+1))
                break
            elif found is True and (i[0] == 0xFFFF or \
                i is self._entry_order[-1]):
                raise KPError("Given entry hasn't an username. Something went "
                              "very wrong.")
                return False
            elif found is False and index + 1 == len(self._entry_order):
                raise KPError("Given entry doesn't exist in group order. "
                              "Something went very wrong.")
                return False
            index += 1

    def set_entry_image(self, uuid = None, image = None):
        """This method is used to change the image number of an entry.

        Two arguments are needed: The id of the group whose image should
        be changed and the new image number.
        
        """
        
        if uuid is None or image is None or type(image) is not int:
            raise KPError("Need an entry uuid and an image number!")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                i.image = image
                i.last_mod = datetime.now().replace(microsecond = 0)
                break
            elif i is self.groups[-1]:
                raise KPError("Given entry doesn't exist.")
                return False
        
        return True

    def set_entry_expire(self, uuid = None, y = 2999, mon = 12, d = 28, h = 23,
                         min_ = 59, s = 59):
        """This method is used to change the expire date of an entry.

            - y is the year between 1 and 9999 inclusive
            - mon is the month between 1 and 12
            - d is a day in the given month
            - h is a hour between 0 and 23
            - min_ is a minute between 0 and 59
            - s is a second between 0 and 59

        The special date 2999-12-28 23:59:59 means that entry expires never. If
        only an uuid is given the expire date will set to this one.
        
        """

        if uuid is None or type(uuid) is not bytes:
            raise KPError("Need an uuid")
            return False
        
        if y > 9999 or y < 1 or mon > 12 or mon < 1 or d > 31 or d < 1 or \
            h > 23 or h < 0 or min_ > 59 or min_ < 0 or s > 59 or s < 0:
            raise KPError("No legal date")
            return False
        
        if ((mon == 1 or mon == 3 or mon == 5 or mon == 7 or mon == 8 or \
             mon == 10 or mon == 12) and d > 31) or ((mon == 4 or mon == 6 or \
             mon == 9 or mon == 11) and d > 30) or (mon == 2 and d > 28):
            raise KPError("Given day doesn't exist in given month")
            return False

        for i in self._entries:
            if uuid == i.uuid:
                i.expire = datetime(y, mon, d, h, min_, s)
                i.last_mod = datetime.now().replace(microsecond = 0)
                return True
            elif i is self._entries[-1]:
                raise KPError("Given entry doesn't exist.")
                return False

    def move_entry(self, uuid = None, id_ = None):
        """Move an entry to another group.

        An entry uuid and a group id is needed.
        """

        if uuid is None or id_ is None or type(uuid) is not bytes or \
            type(id_) is not int:
            raise KPError("Need a valid entry uuid and a valid group id")
            return False

        for i in self._entries:
            if i.uuid == uuid:
                entry = i
            elif i is self._entries[-1]:
                raise KPError("No entry found for given uuid")
                return False
        
        for i in self.groups:
            if i.id_ is id_:
                entry.group.entries.remove(entry)
                i.entries.append(entry)
                entry.group_id = id_
            elif i is self.groups[-1]:
                raise KPError("No group found for given id")
                return False
                
    def _transform_key(self):
        """This method creates the key to decrypt the database"""

        # First, hash the masterkey
        sha_obj = SHA256.new()
        sha_obj.update(self.masterkey.encode())
        hashed_key = sha_obj.digest()
        aes = AES.new(self._transf_randomseed, AES.MODE_ECB)

        # Next, encrypt the created hash
        for i in range(self._key_transf_rounds):
            hashed_key = aes.encrypt(hashed_key)

        # Finally, hash it again...
        sha_obj = SHA256.new()
        sha_obj.update(hashed_key)
        hashed_key = sha_obj.digest()
        # ...and hash the result together with the randomseed
        sha_obj = SHA256.new()
        sha_obj.update(self._final_randomseed + hashed_key)
        return sha_obj.digest()

    def _cbc_decrypt(self, final_key, crypted_content):
        """This method decrypts the database"""

        # Just decrypt the content with the created key
        aes = AES.new(final_key, AES.MODE_CBC, self._enc_iv)
        decrypted_content = aes.decrypt(crypted_content)
        padding = decrypted_content[-1]
        decrypted_content = decrypted_content[:len(decrypted_content)-padding]
        
        return decrypted_content

    def _cbc_encrypt(self, content, final_key):
        """This method encrypts the content."""

        aes = AES.new(final_key, AES.MODE_CBC, self._enc_iv)
        padding = (16 - len(content) % AES.block_size)

        for i in range(padding):
            content += chr(padding).encode()

        temp = bytes(content)
        return aes.encrypt(temp)

    def _read_group_field(self, group, levels, field_type, field_size,  
                          decrypted_content):
        """This method handles the different fields of a group"""

        if field_type == 0x0000:
            # Ignored (commentar block)
            pass
        elif field_type == 0x0001:
            group.id_ = struct.unpack('<I', decrypted_content[:4])[0]
        elif field_type == 0x0002:
            group.title = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                        'utf-8')
            decrypted_content = decrypted_content[1:]
        elif field_type == 0x0003:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0004:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0005:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0006:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0007:
            group.image = struct.unpack('<I', decrypted_content[:4])[0]
        elif field_type == 0x0008:
            level = struct.unpack('<H', decrypted_content[:2])[0]
            group.level = level
            levels.append(level)
        elif field_type == 0x0009:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0xFFFF:
            pass
        else:
            return False
        return True

    def _read_entry_field(self, entry, field_type, field_size,
                          decrypted_content):
        """This method handles the different fields of an entry"""

        if field_type == 0x0000:
            # Ignored
            pass
        elif field_type == 0x0001:
            entry.uuid = decrypted_content[:16]
        elif field_type == 0x0002:
            entry.group_id = struct.unpack('<I', decrypted_content[:4])[0]
        elif field_type == 0x0003:
            entry.image = struct.unpack('<I', decrypted_content[:4])[0]
        elif field_type == 0x0004:
            entry.title = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                        'utf-8')
            decrypted_content = decrypted_content[1:]
        elif field_type == 0x0005:
            entry.url = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                        'utf-8')
            decrypted_content = decrypted_content[1:]
        elif field_type == 0x0006:
            entry.username = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                         'utf-8')
            decrypted_content = decrypted_content[1:]
        elif field_type == 0x0007:
            entry.password = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                        'utf-8')
        elif field_type == 0x0008:
            entry.comment = str(struct.unpack('<{0}s'.format(field_size-1),
                                        decrypted_content[:field_size-1])[0],
                                        'utf-8')
        elif field_type == 0x0009:
            date = self._get_date(decrypted_content)
            entry.creation = date
        elif field_type == 0x000A:
            date = self._get_date(decrypted_content)
            entry.last_mod = date
        elif field_type == 0x000B:
            date = self._get_date(decrypted_content)
            entry.last_access = date
        elif field_type == 0x000C:
            date = self._get_date(decrypted_content)
            entry.expire = date
        elif field_type == 0x000D:
            entry.binary_desc = str(struct.unpack('<{0}s'.format(field_size-1),
                                       decrypted_content[:field_size-1])[0],
                                       'utf-8')
        elif field_type == 0x000E:
            entry.binary = decrypted_content[:field_size]
        elif field_type == 0xFFFF:
            pass
        else:
            return False
        return True

    def _get_date(self, decrypted_content):
        """This method is used to decode the packed dates of entries"""
        
        # Just copied from original KeePassX source
        date_field = struct.unpack('<5B', decrypted_content[:5])
        dw1 = date_field[0]
        dw2 = date_field[1]
        dw3 = date_field[2]
        dw4 = date_field[3]
        dw5 = date_field[4]

        y = (dw1 << 6) | (dw2 >> 2)
        mon = ((dw2 & 0x03) << 2) | (dw3 >> 6)
        d = (dw3 >> 1) & 0x1F
        h = ((dw3 & 0x01) << 4) | (dw4 >> 4)
        min_ = ((dw4 & 0x0F) << 2) | (dw5 >> 6)
        s = dw5 & 0x3F
        return datetime(y, mon, d, h, min_, s)

    def _pack_date(self, date):
        """This method is used to encode dates"""
        
        # Just copied from original KeePassX source
        y, mon, d, h, min_, s = date.timetuple()[:6]

        dw1 = 0x0000FFFF & ((y>>6) & 0x0000003F)
        dw2 = 0x0000FFFF & ((y & 0x0000003F)<<2 | ((mon>>2) & 0x00000003))
        dw3 = 0x0000FFFF & (((mon & 0x0000003)<<6) | ((d & 0x0000001F)<<1) \
                | ((h>>4) & 0x00000001))
        dw4 = 0x0000FFFF & (((h & 0x0000000F)<<4) | ((min_>>2) & 0x0000000F))
        dw5 = 0x0000FFFF & (((min_ & 0x00000003)<<6) | (s & 0x0000003F))

        return struct.pack('<5B', dw1, dw2, dw3, dw4, dw5)        

    def _create_group_tree(self, levels):
        """This method creates a group tree"""

        if levels[0] != 0:
            raise KPError("Invalid group tree")
            return False
        
        for i in range(len(self.groups)):
            if(levels[i] == 0):
                self.groups[i].parent = self._root_group
                self.groups[i].index = len(self._root_group.children)
                self._root_group.children.append(self.groups[i])
                continue

            j = i-1
            while j >= 0:
                if levels[j] < levels[i]:
                    if levels[i]-levels[j] != 1:
                        raise KPError("Invalid group tree")
                        return False
                    
                    self.groups[i].parent = self.groups[j]
                    self.groups[i].index = len(self.groups[j].children)
                    self.groups[i].parent.children.append(self.groups[i])
                    break
                if j == 0:
                    raise KPError("Invalid group tree")
                    return False
                j -= 1
            
        for e in range(len(self._entries)):
            for g in range(len(self.groups)):
                if self._entries[e].group_id == self.groups[g].id_:
                    self.groups[g].entries.append(self._entries[e])
                    self._entries[e].group = self.groups[g]
                    # from original KeePassX-code, but what does it do?
                    self._entries[e].index = 0           
        return True

    def _save_group_field(self, field_type, field_size, group):
        """This method packs a group field"""
        
        if field_type == 0x0000:
            # Ignored (commentar block)
            pass
        elif field_type == 0x0001:
            return struct.pack('<I', group.id_)
        elif field_type == 0x0002:
            return (group.title+'\0').encode()
        elif field_type == 0x0003:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0004:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0005:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0006:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0x0007:
            return struct.pack('<I', group.image)
        elif field_type == 0x0008:
            return struct.pack('<H', group.level)
        elif field_type == 0x0009:
            # Not implemented by KeePassX but is defined by the original
            # KeePass standard
            # Will be implemented in a later release
            pass
        elif field_type == 0xFFFF:
            pass
        else:
            return False
        return True

    def _save_entry_field(self, field_type, field_size, entry):
        """This group packs a entry field"""

        if field_type == 0x0000:
            # Ignored
            pass
        elif field_type == 0x0001:
            return entry.uuid
        elif field_type == 0x0002:
            return struct.pack('<I', entry.group_id)
        elif field_type == 0x0003:
            return struct.pack('<I', entry.image)
        elif field_type == 0x0004:
            return  (entry.title+'\0').encode()
        elif field_type == 0x0005:
            return (entry.url+'\0').encode()
        elif field_type == 0x0006:
            return (entry.username+'\0').encode()
        elif field_type == 0x0007:
            return (entry.password+'\0').encode()
        elif field_type == 0x0008:
            return (entry.comment+'\0').encode()
        elif field_type == 0x0009:
            return self._pack_date(entry.creation)
        elif field_type == 0x000A:
            return self._pack_date(entry.last_mod)
        elif field_type == 0x000B:
            return self._pack_date(entry.last_access)
        elif field_type == 0x000C:
            return self._pack_date(entry.expire)
        elif field_type == 0x000D:
            return (entry.binary_desc+'\0').encode()
        elif field_type == 0x000E:
            return entry.binary
        elif field_type == 0xFFFF:
            pass
        else:
            return False
        return True
