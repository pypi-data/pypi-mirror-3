from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from organizations.managers import OrgManager, ActiveOrgManager


class OrganizationsBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(OrganizationsBase):
    """
    This is the umbrella object under which all organization users fall.

    The class has multiple organization users and one that is designated the organization
    owner.
    """
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, through="OrganizationUser")
    is_active = models.BooleanField(default=True)

    objects = OrgManager()
    active = ActiveOrgManager()

    class Meta:
        ordering = ['name']
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def __unicode__(self):
        return u"%s" % self.name

    @permalink
    def get_absolute_url(self):
        return ('organization_detail', (), {'organization_pk': self.pk})

    def add_user(self, user, is_admin=False):
        return OrganizationUser.objects.create(user=user, organization=self,
                is_admin=is_admin)

    def is_member(self, user):
        return True if user in self.users.all() else False

    def is_admin(self, user):
        return True if self.organization_users.filter(user=user, is_admin=True) else False


class OrganizationUser(OrganizationsBase):
    """
    This relates a User object to the organization group. It is possible for a User
    to be a member of multiple organizations, so this class relates the OrganizationUser
    to the User model using a ForeignKey relationship, rather than a OneToOne
    relationship.

    Authentication and general user information is handled by the User class
    and the contrib.auth application.
    """
    user = models.ForeignKey(User, related_name="organization_users")
    organization = models.ForeignKey(Organization,
            related_name="organization_users")
    is_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['organization', 'user']
        verbose_name = _("organization user")
        verbose_name_plural = _("organization users")

    def __unicode__(self):
        return self.name if self.user.is_active else self.user.email

    def delete(self, using=None):
        """
        If the organization user is also the owner, this should not be deleted
        unless it's part of a cascade from the Organization.
        """
        from organizations.exceptions import OwnershipRequired
        if self.organization.owner.organization_user.id == self.id:
            raise OwnershipRequired(_("Cannot delete organization owner before organization or transferring ownership"))
        else:
            super(OrganizationUser, self).delete(using=using)

    @permalink
    def get_absolute_url(self):
        return ('organization_user_detail', (),
                {'organization_pk': self.organization.pk, 'user_pk': self.user.pk})

    @property
    def name(self):
        if self.user.first_name and self.user.last_name:
            return u"%s %s" % (self.user.first_name, self.user.last_name)
        return self.user.username


class OrganizationOwner(OrganizationsBase):
    """
    Each organization must have one and only one organization owner.
    """
    organization = models.OneToOneField(Organization, related_name="owner")
    organization_user = models.OneToOneField(OrganizationUser,
            related_name="owned_organization")

    class Meta:
        verbose_name = _("organization owner")
        verbose_name_plural = _("organization owners")

    def __unicode__(self):
        return u"%s: %s" % (self.organization, self.organization_user)

    def save(self, *args, **kwargs):
        """
        Ensure that the organization owner is actually an organization user
        """
        from organizations.exceptions import OrganizationMismatch
        if self.organization_user.organization != self.organization:
            raise OrganizationMismatch
        else:
            super(OrganizationOwner, self).save(*args, **kwargs)
