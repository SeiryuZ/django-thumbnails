from optparse import make_option

from django.core.management.base import BaseCommand
from django.db.models import get_model

from thumbnails import images
from thumbnails.backends import metadata, storage


class Command(BaseCommand):
    """
    Delete all thumbnails from a field. For example:
    python manage.py delete_thumbnails --model='accounts.Profile' --field='picture' --size='small'
    """
    option_list = BaseCommand.option_list + (
        make_option('--model', dest='path_to_model',
                    help='Dotted path to model (e.g "polls.Poll" )'),
        make_option('--field', dest='field_name',
                    help='Thumbnail field name (e.g "picture"'),
        make_option('--size', dest='size',
                    help='Thumbnail size to delete (e.g "small"'),
    )

    def handle(self, path_to_model, field_name, size, *args, **kwargs):
        if not path_to_model:
            raise ValueError('--model argument is required')
        if not field_name:
            raise ValueError('--field argument is required')
        if not size:
            raise ValueError('--size argument is required')

        app_label, model_name = path_to_model.rsplit('.', 1)
        model = get_model(app_label, model_name)

        # Get model instances which has non empty fields
        exclude_args = {
            '%s__isnull' % field_name: True,
            field_name: ''
        }
        instances = model.objects.exclude(**exclude_args)

        metadata_backend = metadata.get_backend()
        storage_backend = storage.get_backend()

        for instance in instances:
            field = getattr(instance, field_name)
            images.delete(field.name, size, metadata_backend, storage_backend)
