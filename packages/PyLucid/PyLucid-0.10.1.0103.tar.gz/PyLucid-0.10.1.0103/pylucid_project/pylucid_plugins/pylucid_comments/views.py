# coding: utf-8

"""
    PyLucid page comments plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    TODO:
     * Update existing unittest (e.g. blog, lexicon)

    :copyleft: 2010-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

import datetime

from django.conf import settings
from django.contrib import comments
from django.contrib import messages
from django.contrib.comments.signals import comment_will_be_posted, comment_was_posted
from django.contrib.comments.views.comments import post_comment
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from django_tools.decorators import render_to
from django_tools.utils.client_storage import ClientCookieStorage, InvalidCookieData

from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.apps.pylucid.shortcuts import bad_request
from pylucid_project.apps.pylucid.decorators import check_request

from pylucid_comments.preference_forms import PyLucidCommentsPrefForm



APP_LABEL = "pylucid_plugin.pylucid_comments"

COOKIE_KEY = "comments_data" # Used to store anonymous user information

# Important: The sign may not occur in a email address or in a homepage url!
# But it can occur in the username ;)
COOKIE_DELIMITER = ";"


def _get_preferences():
    """ return the comments preferences dict back """
    pref_form = PyLucidCommentsPrefForm()
    preferences = pref_form.get_preferences()
    return preferences


def _contains_spam_keyword(comment, preferences):
    """ contains the comment content a spam keywords defined in preferences? """
    spam_keywords = preferences["spam_keywords"]
    content = comment.comment
    for keyword in spam_keywords:
        if keyword in content:
            return True
    return False


def comment_will_be_posted_handler(sender, **kwargs):
    """ check comment before save """
    request = kwargs["request"]
    comment = kwargs["comment"]

    preferences = _get_preferences()
    if _contains_spam_keyword(comment, preferences):
        comment.is_public = False

    # Protection against DOS attacks.
    min_pause = preferences["min_pause"]
    ban_limit = preferences["ban_limit"]
    try:
        LogEntry.objects.request_limit(request, min_pause, ban_limit, app_label=APP_LABEL, action="post")
    except LogEntry.RequestTooFast, err:
        # min_pause is not observed
        error_msg = unicode(err) # ugettext_lazy
        messages.error(request, error_msg)


def comment_was_posted_handler(sender, **kwargs):
    """
    actions after a new comment saved
    TODO: Clean page cache witch contains the comment!
    """
#    print "comment_was_posted_handler", kwargs.keys()
    request = kwargs["request"]
    comment = kwargs["comment"]
    content_object = comment.content_object

    # Gives the user a feedback
    if comment.is_public:
        messages.success(request, _("Your comment has been saved."))
    else:
        messages.info(request, _("Your comment waits for moderation."))

    # Used to filter DOS attacks, see: comment_will_be_posted_handler()
    LogEntry.objects.log_action(app_label=APP_LABEL, action="post", message="comment created")

    preferences = _get_preferences()
    admins_notification = preferences["admins_notification"]
    if admins_notification:
        email_context = {
            "comment": comment,
            "content_object": content_object,
            "remote_addr": request.META["REMOTE_ADDR"],
            "now": datetime.datetime.utcnow(),
            "uri_prefix": request.build_absolute_uri("/").rstrip("/"), # FIXME
        }
        emailtext = render_to_string("pylucid_comments/admins_notification_email.txt", email_context)

        site_name = Site.objects.get_current().name
        absolute_url = content_object.get_absolute_url()
        subject = '[%s] New comment posted on "%s"' % (site_name, absolute_url)

        try:
            mail_admins(subject, emailtext, fail_silently=False)
        except Exception, err:
            LogEntry.objects.log_action(
                app_label=APP_LABEL, action="mail error", message="Admin mail, can't send: %s" % err,
            )


comment_will_be_posted.connect(comment_will_be_posted_handler)
comment_was_posted.connect(comment_was_posted_handler)


@check_request(APP_LABEL, "_get_form() error", must_post=True, must_ajax=True)
@render_to("pylucid_comments/comment_form.html")
def _get_form(request):
    """ Send the comment form to via AJAX request """
    try:
        ctype = request.POST["content_type"].split(".", 1)
        model = models.get_model(*ctype)
    except Exception, err:
        return bad_request(APP_LABEL, "error", "Wrong content type: %s" % err)

    try:
        object_pk = request.POST["object_pk"]
        target = model._default_manager.using(None).get(pk=object_pk)
    except Exception, err:
        return bad_request(APP_LABEL, "error", "Wrong object_pk: %s" % err)

    data = {}
    if not request.user.is_authenticated():
        # Get user data from secure cookie, set in the past, see _form_submission()
        c = ClientCookieStorage(cookie_key=COOKIE_KEY)
        try:
            raw_data = c.get_data(request)
        except InvalidCookieData, err:
            return bad_request(APP_LABEL, "error", "Wrong cookie data: %s" % err)

        if raw_data is not None:
            try:
                username, email, url = raw_data.rsplit(COOKIE_DELIMITER, 2)
            except ValueError, err:
                debug_msg = "Error split user cookie data: %r with %r" % (raw_data, COOKIE_DELIMITER)
                LogEntry.objects.log_action(
                    app_label=APP_LABEL, action="error", message=debug_msg,
                )
                if settings.DEBUG:
                    raise
            else:
                data = {"name": username, "email": email, "url": url}

    form = comments.get_form()(target, initial=data)

    return {"form":form}


@check_request(APP_LABEL, "_form_submission() error", must_ajax=True)
def _form_submission(request):
    """ Handle a AJAX comment form submission """
    # Use django.contrib.comments.views.comments.post_comment to handle a comment post.
    response = post_comment(request)
    if isinstance(response, HttpResponseRedirect):
        # reload the page after comment saved via JavaScript
        response = HttpResponse("reload")

        if not request.user.is_authenticated():
            # Store user data for anonymous users in a secure cookie, used in _get_form() to pre fill the form
            comments_data = COOKIE_DELIMITER.join([
                request.POST["name"], request.POST.get("email", ""), request.POST.get("url", "")
            ])
            # Store the user data with a security hash
            c = ClientCookieStorage(cookie_key=COOKIE_KEY)
            response = c.save_data(comments_data, response)

    return response




def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["pylucid_comments"]

    if action == "get_form":
        return _get_form(request)
    elif action == "submit":
        return _form_submission(request)
    else:
        debug_msg = "Wrong get view parameter!"
        return bad_request(APP_LABEL, "error", debug_msg) # Return HttpResponseBadRequest


def lucidTag(request):
    if (settings.DEBUG or request.user.is_superuser) and not settings.ADMINS:
        messages.info(request, "Please fill out settings.ADMINS!")

    object2comment = request.PYLUCID.object2comment

    if object2comment == False:
        # Don't display pylucid comments on this page
        # e.g. search get view display search results
        return ""

    form = comments.get_form()(object2comment)
    context = {
        "form":form,
        "object2comment": object2comment,
    }
    return render_to_response("pylucid_comments/comments.html",
        context, context_instance=RequestContext(request)
    )
