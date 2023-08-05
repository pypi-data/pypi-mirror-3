# -*- coding: utf-8 -*-
"""
    Shake-Files
    ----------------------------------------------

    Shake-Files allows your application to flexibly and efficiently handle file
    uploads. 

    You can create different sets of uploads - one for document attachments, one
    for photos, etc. - and configure them to save tthe files in different places, 
    creating the directories on demand, according to a pattern defined by you.

    
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
from __future__ import absolute_import
import datetime
import errno
import os
import random
import re
import uuid

from shake import json, RequestEntityTooLarge, UnsupportedMediaType
from werkzeug.utils import secure_filename


IMAGES = ('jpg', 'jpeg', 'png', 'gif', 'bmp')

AUDIO = ('wav', 'mp3', 'aac', 'ogg', 'oga', 'flac')

DOCUMENTS = ('pdf', 'rtf', 'txt',
    'odf', 'odp', 'ods', 'odg', 'ott', 'otp', 'ots', 'otg',
    'pages', 'key', 'numbers', 'gnumeric', 'abw',
    'doc', 'ppt', 'xls', 'vsd', 'docx', 'pptx', 'xlsx', 'vsx',
    )

DATA = ('csv', 'json', 'xml', 'ini', 'plist', 'yaml', 'yml')

ARCHIVES = ('zip', 'gz', 'bz2', 'tar', 'tgz', 'txz', '7z')

DEFAULT = IMAGES + AUDIO + DOCUMENTS


class FileObj(object):
    """
    """
    
    def __init__(self, data, root_path):
        data = data or {}
        self.name = data.get('name', u'')
        self.size = data.get('size', u'')
        self.type = data.get('type', u'')
        self.rel_path = data.get('path').strip('/')
        self.root_path = root_path
        self.is_image = self.type.startswith('image/')
        self.data = data
    
    def __nonzero__(self):
        return self.rel_path is not None
    
    def __repr__(self):
        return '<%s %s "%s">' % (self.__class__.__name__,
            self.type, self.name)
    
    @property
    def path(self):
        if self.rel_path is None:
            return u''
        return os.path.join(self.root_path, self.rel_path, self.name)
    
    @property
    def url(self):
        if self.rel_path is None:
            return u''
        lst_url = [self.rel_path, self.name]
        return '/'.join(lst_url)
    
    def get_thumb_path(self, tname):
        if self.rel_path is None:
            return u''
        return os.path.join(self.root_path, self.rel_path, tname, self.name)
    
    def get_thumb_url(self, tname):
        if self.rel_path is None:
            return u''
        lst_url = [self.rel_path, tname, self.name]
        return '/'.join(lst_url)
    
    def remove(self, *thumb_names):
        try:
            os.remove(self.path)
        except OSError:
            pass
        for tname in thumb_names:
            try:
                os.remove(self.get_thumb_path(tname))
            except OSError:
                pass


class FileSystemStorage(object):
    
    def __init__(self, root_path, upload_to='{yyyy}/{mm}/{dd}/', secret=False,
            prefix='', allowed=DEFAULT, denied=None, max_size=None):
        """
        Except for `root_path`, all of these parameters are optional, so only
        bother setting the ones relevant to your application.

        :param root_path:
        
        :param upload_to:
            Un patrón de ruta como los usados en `format_path`.
        
        :param secret:
            Si es True, en vez del nombre de archivo original se usa uno al
            azar.
        
        :param prefix:
            Para evitar race-conditions entre varios usuarios subiendo archivos
            llamados igual al mismo tiempo. No se usa si `secret` es True
        
        :param allowed:
            Lista de extensiones permitidas. `None` para cualquiera.
            Si el archivo no tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`
        
        :param denied:
            Lista de extensiones prohibidas. `None` para ninguna.
            Si el archivo tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`
        
        :param max_size:
            Tamaño máximo permitido para archivos. El valor `max_content_length`
            definido en el objeto `request` tiene prioridad.
        
        """
        self.root_path = root_path
        self.upload_to = upload_to
        self.secret = secret
        self.prefix = prefix
        self.allowed = allowed or []
        self.denied = denied or []
        self.max_size = max_size
    
    def __repr__(self):
        return '<%s "%s" secret=%s>' % (self.__class__.__name__,
            self.upload_to, self.secret)
    
    def save(self, filesto, upload_to=None, secret=None, prefix=None,
            allowed=DEFAULT, denied=None, max_size=None):
        """
        Except for `filesto`, all of these parameters are optional, so only
        bother setting the ones relevant to this upload.

        :param:filesto::
            Un objeto werkzeug.FileStorage.
        
        :param upload_to:
            Un patrón de ruta como los usados en `format_path`.
        
        :param secret:
            Si es True, en vez del nombre de archivo original se usa uno al
            azar.
        
        :param prefix:
            Para evitar race-conditions entre varios usuarios subiendo archivos
            llamados igual al mismo tiempo. No se usa si `secret` es True
        
        :param allowed:
            Lista de extensiones permitidas. `None` para cualquiera.
            Si el archivo no tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`
        
        :param denied:
            Lista de extensiones prohibidas. `None` para ninguna.
            Si el archivo tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`
        
        :param max_size:
            Tamaño máximo permitido para archivos. El valor `max_content_length`
            definido en el objeto `request` tiene prioridad.
        
        """
        upload_to = upload_to or self.upload_to
        secret = secret or self.secret
        prefix = prefix or self.prefix
        original_filename = filesto.filename
        self.validate(filesto, allowed, denied, max_size)

        tmplpath = upload_to
        if callable(tmplpath):
            tmplpath = tmplpath(original_filename)
        filepath = format_path(tmplpath, original_filename)
        name, ext = self._split_filename(original_filename)

        if secret:
            name = None
        else:
            name = prefix + name
        
        filename = get_unique_filename(self.root_path, filepath, name=name,
            ext=ext)
        fullpath = os.path.join(self.root_path, filepath)
        fullpath = os.path.abspath(fullpath)
        try:
            os.makedirs(fullpath)
        except (OSError), e:
            if e.errno != errno.EEXIST:
                raise
        fullpath = os.path.join(fullpath, filename)
        filesto.save(fullpath)
        filesize = os.path.getsize(fullpath)
        
        # Post check
        if max_size and filesize > max_size:
            try:
                os.remove(fullpath)
            except:
                pass
            raise RequestEntityTooLarge
        
        data = {
            'name': filename,
            'path': filepath,
            'size': filesize,
            'content_type': filesto.content_type
        }
        return data
    
    def validate(self, filesto, allowed=None, denied=None, max_size=None):
        max_size = max_size or self.max_size
        content_length = filesto.content_length
        if content_length == 0:
            filesto.seek(0, 2)
            content_length = filesto.tell()
            filesto.seek(0, 0)
        
        if max_size and content_length > max_size:
            raise RequestEntityTooLarge
        
        original_filename = filesto.filename
        name, ext = self._split_filename(original_filename)
        ext = ext.lower()
        self.check_file_extension(ext, allowed, denied)
    
    def check_file_extension(self, ext, allowed=None, denied=None):
        allowed = allowed or self.allowed
        denied = denied or self.denied

        if allowed and not ext in allowed:
            raise UnsupportedMediaType()
        if denied and ext in denied:
            raise UnsupportedMediaType()
    
    def _split_filename(self, filename):
        try:
            return filename.rsplit('.', 1)
        except ValueError, e:
            return filename, ''


def format_path(tmplpath, filename, now=None):
    """
    {yyyy},{yy}: Year
    {mm}, {m}: Month (0-padded or not)
    {ww}, {w}: Week number in the year (0-padded or not)
    {dd}, {d}: Day (0-padded or not)
    {hh}, {h}: Hours (0-padded or not)
    {nn}, {n}: Minutes (0-padded or not)
    {ss}, {s}: Seconds (0-padded or not)
    {a+}: Filename first letters
    {z+}: Filename last letters
    {r+}: Random letters and/or numbers
    
    >>> tmplpath = '{zzz}/{yyyy}/{a}/{a}/{a}'
    >>> filename = 'monkey.png'
    >>> now = datetime(2010, 1, 14)
    >>> format_path(tmplpath, filename, now)
    'png/2010/m/o/n/'
    
    """
    path = tmplpath.lower()
    filename = filename.lower()
    now = now or datetime.datetime.utcnow()
    srx = r'\{(y{4}|[ymdhnws]{1,2}|[azr]+)\}'
    rx = re.compile(srx, re.IGNORECASE)
    len_filename = len(filename)
    a_pos = 0
    z_pos = 0
    delta = 0
    for match in rx.finditer(path):
        pattern = match.groups()[0]
        len_pattern = len(pattern)
        replace = '%0' + str(len_pattern) + 'i'
        if pattern.startswith('y'):
            replace = str(now.year)
            replace = replace[-len_pattern:]
        elif pattern.startswith('m'):
            replace = replace % now.month
        elif pattern.startswith('w'):
            tt = now.timetuple()
            replace = '%0' + str(len_pattern) + 'i'
            week = (tt.tm_yday + 7 - tt.tm_wday) / 7 + 1
            replace = replace % week
        elif pattern.startswith('d'):
            replace = replace % now.day
        elif pattern.startswith('h'):
            replace = replace % now.hour
        elif pattern.startswith('n'):
            replace = replace % now.minute
        elif pattern.startswith('s'):
            replace = replace % now.second
        elif pattern.startswith('a'):
            if a_pos >= len_filename:
                replace = '_'
            else:
                new_a_pos = a_pos + len_pattern
                replace = filename[a_pos:new_a_pos]
                a_pos = new_a_pos
        elif pattern.startswith('z'):
            new_z_pos = z_pos + len_pattern
            if z_pos == 0:
                replace = filename[-new_z_pos:]
            else:
                replace = filename[-new_z_pos:-z_pos]
            z_pos = new_z_pos
        elif pattern.startswith('r'):
            allowed_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
            replace = ''.join([random.choice(allowed_chars) \
                for i in range(len_pattern)])
        else:
            raise ValueError
        x, y = match.span()
        path = '%s%s%s' % (path[:x - delta], replace, path[y - delta:])
        delta += len_pattern + 2 - len(replace)
    if not path.endswith('/'):
        path += '/'
    return path


def get_unique_filename(root_path, path, name=None, ext=''):
    """ """
    path = os.path.join(root_path, path)
    abspath = os.path.abspath(path)
    i = 0
    while True:
        if not name:
            filename = str(uuid.uuid4())
        elif i:
            filename = '%s_%i' % (name, i)
            filename = secure_filename(filename)
        else:
            filename = secure_filename(name)
        
        if ext:
            filename = '%s.%s' % (filename, ext)
        filepath = os.path.join(abspath, filename)
        if not os.path.exists(filepath):
            break
        i += 1
    return filename


try:
    from sqlalchemy.types import TypeDecorator, Text

    class FileType(TypeDecorator):
            """Saves a file structure as a JSON-encoded string and reads it back as
            a FileObj."""

            impl = Text
            fileobj_class = FileObj

            def __init__(self, root_path, default=None, **kwargs):
                self.root_path = root_path
                self.default = default
                TypeDecorator.__init__(self, **kwargs)
            
            def process_bind_param(self, value, dialect):
                if value is None:
                    return None
                return json.dumps(value)
            
            def process_result_value(self, value, dialect):
                value = value or self.default
                data = json.loads(value)
                return self.fileobj_class(data, self.root_path)
            
            def copy(self):
                return self.__class__(self.root_path, default=self.default)
    
except ImportError:
    pass

