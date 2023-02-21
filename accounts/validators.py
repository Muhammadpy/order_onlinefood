from django.core.exceptions import ValidationError

import os

def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    print(ext)
    valid_exentions= ['.png', '.jpg', '.jpeg']
    if not  ext.lower() in valid_exentions:
        raise ValidationError('Unsupported file extention Allowed extentions : ' + str(valid_exentions))
    