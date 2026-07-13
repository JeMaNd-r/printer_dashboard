class MultipleSerializersMixin:
    """
    Mixin for ViewSets that allows to use multiple serializers
    for different actions. Defaults to serializer_class for all actions.
    """

    serializer_classes = {}
    '''The keys should be the actions names: "list", "retrieve", "create", "update", "partial_update", "destroy"'''

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_classes`.
        """
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            assert self.serializer_class is not None, (
                f"Serializer class for action '{self.action}' not found and no default serializer class set."
            )
            return self.serializer_class
