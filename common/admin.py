from django.contrib import admin


class ReadOnlyTabularInline(admin.TabularInline):
    """
    A read-only tabular inline for Django admin.
    """

    can_delete = False
    extra = 0
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        """
        Override to make all fields readonly.
        """
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
