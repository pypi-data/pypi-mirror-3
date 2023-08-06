from filer.models import Image
from easy_thumbnails.files import get_thumbnailer
i = Image.objects.get()
get_thumbnailer(i)