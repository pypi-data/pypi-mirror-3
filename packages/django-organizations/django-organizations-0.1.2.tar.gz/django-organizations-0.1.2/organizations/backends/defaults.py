import uuid

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext as _

from organizations.backends.tokens import RegistrationTokenGenerator
from organizations.backends.forms import (UserRegistrationForm,
        OrganizationRegistrationForm)
from organizations.utils import create_organization


class RegistrationBackend(object):
    activation_subject = 'organizations/activation_subject.txt'
    activation_body = 'organizations/activation_body.html'
    reminder_subject = 'organizations/reminder_subject.txt'
    reminder_body = 'organizations/reminder_body.html'
    form_class = UserRegistrationForm

    def get_register_form(self, **kwargs):
        return self.form_class(**kwargs)

    def register_by_email(self, email, sender=None, request=None, **kwargs):
        """
        Returns a User object filled with dummy data and not active, and sends
        an invitation email.
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(username=unicode(uuid.uuid1()), email=email,
                    password=User.objects.make_random_password())
            user.is_active = False
            user.save()
        self.send_activation(user, sender, **kwargs)
        return user

    def send_activation(self, user, sender=None, **kwargs):
        """
        Invites a user to join the site
        """
        if user.is_active:
            return False
        token = RegistrationTokenGenerator().make_token(user)
        kwargs.update({'token': token})
        self._send_email(user, self.activation_subject, self.activation_body,
                sender, **kwargs)

    def send_reminder(self, user, sender=None, **kwargs):
        """
        Sends a reminder email to the specified user
        """
        if user.is_active:
            return False
        token = RegistrationTokenGenerator().make_token(user)
        kwargs.update({'token': token})
        self._send_email(user, self.reminder_subject, self.reminder_body,
                sender, **kwargs)

    def _send_email(self, user, subject_template, body_template,
            sender=None, **kwargs):
        """
        Utility method for sending different emails to invited users
        """
        try:
            from_email = settings.DEFAULT_FROM_EMAIL
        except AttributeError:
            raise ImproperlyConfigured(_("You must define DEFAULT_FROM_EMAIL in your settings"))

        if sender:
            from_email = "%s %s <%s>" % (sender.first_name, sender.last_name,
                    from_email)
            reply_to = "%s %s <%s>" % (sender.first_name, sender.last_name,
                    sender.email)
        headers = {'Reply-To': reply_to} if sender else {}

        kwargs.update({'sender': sender, 'user': user})
        ctx = Context(kwargs)

        subject_template = loader.get_template(subject_template)
        body_template = loader.get_template(body_template)
        subject = subject_template.render(ctx).strip() # Remove stray newline characters
        body = body_template.render(ctx)
        return EmailMessage(subject, body, from_email, [user.email],
                headers).send()

    def create_view(self, request):
        """
        Initiates the organization and user account creation process
        """
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse("organization_add"))
        form = OrganizationRegistrationForm(request.POST or None)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
            except User.DoesNotExist:
                user = User.objects.create(username=unicode(uuid.uuid1()),
                        email=form.cleaned_data['email'],
                        password=User.objects.make_random_password())
                user.is_active = False
                user.save()
            else:
                return HttpResponseRedirect(reverse("organization_add"))
            organization = create_organization(user, form.cleaned_data['name'],
                    form.cleaned_data['slug'], is_active=False)
            return render_to_response('organizations/register_success.html',
                    {'user': user, 'organization': organization},
                    context_instance=RequestContext(request))
        return render_to_response('organizations/register_form.html',
                {'form': form}, context_instance=RequestContext(request))

    def activate_view(self, request, user_id, token):
        """
        Activates the given User by setting `is_active` to true if the provided
        information is verified.
        """
        try:
            user = User.objects.get(id=user_id, is_active=False)
        except User.DoesNotExist:
            raise Http404(_("Your URL may have expired."))
        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))
        form = self.get_register_form(data=request.POST or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            user = authenticate(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect(self.get_success_url())
        return render_to_response('organizations/register_form.html',
                {'form': form}, context_instance=RequestContext(request))

    def success_view(self, request):
        return render_to_response('organizations/register_success.html',
                {}, context_instance=RequestContext(request))

    def get_success_url(self):
        return reverse('registration_success')

    def get_urls(self):
        return patterns('',
            url(r'^complete/$', view=self.success_view,
                name="registration_success"),
            url(r'^(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                view=self.activate_view, name="registration_register"),
            url(r'^$', view=self.create_view, name="registration_create"),
            )


class InvitationBackend(object):
    """
    Defines the base functionality of an InvitationBackend
    """
    invitation_subject = 'organizations/invitation_subject.txt'
    invitation_body = 'organizations/invitation_body.html'
    reminder_subject = 'organizations/reminder_subject.txt'
    reminder_body = 'organizations/reminder_body.html'
    form_class = UserRegistrationForm

    def get_register_form(self, **kwargs):
        """
        Returns the form class to be used for registering based on an
        invitation
        """
        return self.form_class(**kwargs)

    def get_success_url(self):
        return reverse('organization_list')

    def get_urls(self):
        return patterns('',
            url(r'^(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                view=self.activate_view, name="invitations_register"),
            )

    def invite_by_email(self, email, sender=None, request=None, **kwargs):
        """
        Returns a User object filled with dummy data and not active, and sends
        an invitation email.
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(username=unicode(uuid.uuid1()), email=email,
                    password=User.objects.make_random_password())
            user.is_active = False
            user.save()
        self.send_invitation(user, sender, **kwargs)
        return user

    def send_invitation(self, user, sender=None, **kwargs):
        """
        Invites a user to join the site
        """
        if user.is_active:
            return False
        token = RegistrationTokenGenerator().make_token(user)
        kwargs.update({'token': token})
        self._send_email(user, self.invitation_subject, self.invitation_body,
                sender, **kwargs)

    def send_reminder(self, user, sender=None, **kwargs):
        """
        Sends a reminder email to the specified user
        """
        if user.is_active:
            return False
        token = RegistrationTokenGenerator().make_token(user)
        kwargs.update({'token': token})
        self._send_email(user, self.reminder_subject, self.reminder_body,
                sender, **kwargs)

    def activate_view(self, request, user_id, token):
        """
        Activates the given User by setting `is_active` to true if the provided
        information is verified.
        """
        try:
            user = User.objects.get(id=user_id, is_active=False)
        except User.DoesNotExist:
            raise Http404(_("Your URL may have expired."))
        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))
        form = self.get_register_form(data=request.POST or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            user = authenticate(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect(self.get_success_url())
        return render_to_response('organizations/register_form.html',
                {'form': form}, context_instance=RequestContext(request))


    def _send_email(self, user, subject_template, body_template,
            sender=None, **kwargs):
        """
        Utility method for sending different emails to invited users
        """
        try:
            from_email = settings.DEFAULT_FROM_EMAIL
        except AttributeError:
            raise ImproperlyConfigured(_("You must define DEFAULT_FROM_EMAIL in your settings"))

        if sender:
            from_email = "%s %s <%s>" % (sender.first_name, sender.last_name,
                    from_email)
            reply_to = "%s %s <%s>" % (sender.first_name, sender.last_name,
                    sender.email)
        headers = {'Reply-To': reply_to} if sender else {}

        kwargs.update({'sender': sender, 'user': user})
        ctx = Context(kwargs)

        subject_template = loader.get_template(subject_template)
        body_template = loader.get_template(body_template)
        subject = subject_template.render(ctx).strip() # Remove stray newline characters
        body = body_template.render(ctx)
        return EmailMessage(subject, body, from_email, [user.email], headers).send()
