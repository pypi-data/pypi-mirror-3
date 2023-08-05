"""ImageRepository widget.

Use this with a ImageRepositoryField to refer to repository images instead
of using an image stored on the object itself.

"""

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

class ImageRepositoryWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update(dict(
        macro='imagerepository_widget',
        helper_js=('imagerepository_widget.js',),
        # only display if size <= threshold, otherwise show link
        display_threshold=102400,
    ))

registerWidget(
    ImageRepositoryWidget, title='Image Repository image',
    description='Pick images from an image repository',
    used_for=('Products.ImageRepository.field.ImageRepositoryField',))
