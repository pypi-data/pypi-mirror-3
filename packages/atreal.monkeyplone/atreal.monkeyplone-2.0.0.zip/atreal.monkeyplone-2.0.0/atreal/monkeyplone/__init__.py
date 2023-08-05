from AccessControl.PermissionRole import PermissionRole
from Products.Archetypes.BaseFolder import BaseFolderMixin

# manage_delObjects is called on parent so Permission View is sufficient
setattr(BaseFolderMixin, 'manage_delObjects__roles__', PermissionRole("View", ("Authenticated",)))

# manage_cutObjects is called on parent so Permission View is sufficient
setattr(BaseFolderMixin, 'manage_cutObjects__roles__', PermissionRole("View", ("Authenticated",)))

# manage_cutObjects is called on parent so Permission Add portal content is sufficient
setattr(BaseFolderMixin, 'manage_pasteObjects__roles__', PermissionRole("Add portal content", ("Contributor",)))


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

