from django.forms import model_to_dict

from news.models import NewsModel


class BaseSerializer:
    """
    Base class for python -> json supported form

    Methods
    -------
    serialize
        Return python object that can be serialize to json
    """

    def serialize(self, obj):
        """Make serializable object

        Parameters
        ----------
        obj

        Returns
        -------
        object
            Json serializable object
        """
        raise NotImplementedError()


class NewsSerializer(BaseSerializer):
    """News serializer"""

    def serialize(self, obj: NewsModel):
        """

        Parameters
        ----------
        obj : NewsModel

        Returns
        -------
        dict
            json serializable dict
        """
        data = model_to_dict(obj)
        return data
