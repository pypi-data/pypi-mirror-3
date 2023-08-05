
=======================================
Shake-Files
=======================================


Shake-Files allows your application to flexibly and efficiently handle file
uploads. 

You can create different sets of uploads - one for document attachments, one
for photos, etc. - and configure them to save tthe files in different places, 
creating the directories on demand, according to a pattern defined by you.


Declaración
=============

from shake_files import FileSystemStorage, IMAGES


storage = FileSystemStorage(UPLOAD_ROOT, upload_to='{yyyy}/{mm}/{dd}',
    allowed=IMAGES, max_size=1024*1024)

Parámetros
-------------

:param root_path: Obligatorio. Ruta absoluta donde se subirán los archivos. Ejemplo:

    UPLOAD_ROOT = os.path.abspath(os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), '..', 'static', 'media')
        )
    )

:param upload_to:
    Un patrón de ruta para construir los directorios al guardar los archivos.
    los patrones disponibles son: 

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


:param secret:
    Si es True, en vez del nombre de archivo original se usa uno al
    azar.


:param prefix:
    Para evitar race-conditions entre varios usuarios subiendo archivos
    llamados igual al mismo tiempo. No se usa si `secret` es True


:param allowed:
    Lista de extensiones permitidas. `None` para cualquiera.
    Si el archivo no tiene una de estas extensiones se lanza
    un error :class:`UnsupportedMediaType`

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


:param denied:
    Lista de extensiones prohibidas. `None` para ninguna.
    Si el archivo tiene una de estas extensiones se lanza
    un error :class:`werkzeug.exceptions.UnsupportedMediaType`

:param max_size:
    Tamaño máximo, en bytes, permitido para archivos. El valor `max_content_length`
    definido en el objeto `request` tiene prioridad.


Uso
=============

Ejemplo:

    def upload(request):
        filesto = request.files.get('file')
        try:
            file_data = storage.save(filesto)
        except RequestEntityTooLarge, e:
            return 'TOO BIG'
        …


El método `save` tiene los mismos argumentos opcionales usados al crear
un objeto `FileSystemStorage, para poder sobreesscribirlos para esa subida
específica. Por ejemplo, para 


Guardando la información del archivo en la base de datos
=================================================================

Cada storage se encarga de subir el archivo y regresa un JSON con sus datos.
Es responsabilidad del controlador guardar esos datos en un almacenamiento.
permanente.

Si es que SQLAclhemy está instalado, shake_files incluye un tipo de columna
de SQLAclhemy para hacer fácil trabajar con esos datos.

Ejemplo:

    from shake_files import FileType


    class File(db.Model):
        
        data = db.Column(FileType(root_path), nullable=False)

        ...

El único parámetro es `root_path' que es la ruta base, la misma definida en 
el FileSystemStorage.

    …
    f = File(file_data)
    db.add(f)
    db.commit()

Al grabar, la columna acepta un JSON con la estructura devuelta por FileSystemStorage,
y devuelve un objeto shake_files.FileObj, que tiene las siguientes propiedades
y métodos:

Propiedades
-----------

name:
    Nombre del archivo, con extensión.

size:
    Tamaño del archivo, en bytes.

type:
    MIMEType del archivo

is_image:
    True si el MIMEType corresponde a una imagen.

path:
    La ruta absoluta del archivo.
    
url:
    La URL relativa a la ruta base


Métodos
----------

get_thumb_path(tname):
    Toma como argumento un tamaño de miniatura y devuelve la ruta absoluta
    de ella (presupone que existe).
    Ejemplo:
        >>> f.path
        /home/test/media/prueba.jpg

        >>> f.get_thumb_path('S')
        /home/test/media/S/prueba.jpg

get_thumb_url(tname):
    Toma como argumento un tamaño de miniatura y devuelve la URL relativa
    de ella (presupone que existe).
    Ejemplo:
        >>> f.url
        /media/prueba.jpg

        >>> f.get_thumb_path('S')
        /media/S/prueba.jpg

remove(*thumb_names):
    Intenta borrar el archivo del sistema de archivos.
    Opcionalmente, toma un lista de tamños de miniatura y hace lo mismo
    con ellas. No devuelve un error si los archivos ya no existen.









    