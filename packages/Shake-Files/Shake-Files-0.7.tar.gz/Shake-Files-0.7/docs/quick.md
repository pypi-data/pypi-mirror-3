
# Quickstart


## 1) Set one or more uploaders

    :::python
    from shake_files import FileSystemStorage, IMAGES

    storage = FileSystemStorage(UPLOAD_ROOT, '/static/media',
        upload_to='{yyyy}/{mm}/{dd}', allowed=IMAGES,
        max_size=1024*1024*10)

### Parameters
Except for `root_path`, all of these parameters are optional,
so only bother setting the ones relevant to your application.

root_path
:   Absolute path where the files will be stored. Example:
    `/var/www/static/media`.

        UPLOAD_ROOT = os.path.abspath(os.path.normpath(
            os.path.join(
                    os.path.dirname(__file__), '..',
                        'static', 'media')
            )
        )

base_url
:   The base path used when building the file's URL. By default
    is `/static/media`.

upload_to
:   A pattern used to build the upload path on the fly. 
    The wildcards avaliable are: 

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
     
    Instead of a string, this can also be a callable.

secret
:   If True, instead of the original filename, a random one'll
     be used.

prefix
:   To avoid race-conditions between users uploading files with
    the same name at the same time. If `secret` is True, this
    will be ignored.

allowed
:   List of allowed file extensions. `None` to allow all
    of them. If the uploaded file doesn't have one of these
    extensions, an `UnsupportedMediaType` exception will be
    raised.
     
    Shake-Files come with some pre-defined extension lists:

    IMAGES = ('jpg', 'jpeg', 'png', 'gif', 'bmp')
     
    AUDIO = ('wav', 'mp3', 'aac', 'ogg', 'oga', 'flac')
     
    DOCUMENTS = (
        'pdf', 'rtf', 'txt',
        'odf', 'odp', 'ods', 'odg',
        'pages', 'key', 'numbers', 'gnumeric', 'abw',
        'doc', 'ppt', 'xls', 'vsd',
        'docx', 'pptx', 'xlsx', 'vsx',
    )
    
    DATA = ('csv', 'json', 'xml', 'ini', 'plist', 'yaml', 'yml')

    ARCHIVES = ('zip', 'gz', 'bz2', 'tar', 'tgz', 'txz', '7z')

    DEFAULT = IMAGES + AUDIO + DOCUMENTS

denied
:   List of forbidden extensions. Set to `None` to disable.
    If the uploaded file *does* have one of these extensions, a
    `UnsupportedMediaType` exception will be raised.

max_size
:   Maximum file size, in bytes, that file can have.
    Note: The attribute `max_content_length` defined in the
    `request` object has higher priority.

## 2) Upload something

Example:

    :::python
    def upload(request):
        filesto = request.files.get('file')
        try:
            file = storage.save(filesto)
        except RequestEntityTooLarge, e:
            return 'TOO BIG'
        …

The `save` method has the same optional parameters than `FileSystemStorage` and can be used to overwrite those settings for a specific upload.

`save` returns the file's data wrapped as an instance of `shake_files.FileData` with the following attributes and methods:

### FileData Attributes

name
:   File name, including its extension.

path
:   Relative file path, eg: '2012/01/13'.

size
:   File size, in bytes

type
:   MIMEType (eg.: 'image/jpeg').

is_image
:   True if it has a MIMEType of an image.

remote_url
:   Use this to indicate the file has been uploaded at a remote
    prefered location (like Amazon S3 or a CDN).

### FileData Methods

get_path()
:   Returns the absolute path of the local copy of the file.
    
get_url()
:   If `remote_url` is set, it returns it. If not, returns the
    URL of the local copy of the file.

remove()
:   Try deleting the local file. It doesn't return any error if
    the file was deleted before.


## 3) Store the uploaded file data

While the `save` method uploads the file and returns its data, is the controller duty to save it in a permanent storage.

If SQLAclhemy is installed, shake_files provide a column type (`shake_files.FileType`) to make that job easier.

Example:

    :::python
    from shake_files import FileType
    
    class UploadedFile(…):
        ...
        data = Column(FileType(root_path, base_url))
        ...

### Parameters

root_path and base_url
:   The same as defined in `FileSystemStorage`.

default
:   An optional `FileData` object to return if no data is
    available. Perfect for things like default avatars.


This column type recieves the file data (as a `FileData` object) and automatically serialize and store it as a JSON string. Note that this happens only after commiting.

    :::python
    …
    f = UploadedFile(data=file_data)
    db.add(f)
    db.commit()
    …

When reading from the database, it loads the JSON and convert it to a `FileData` object again.
    

