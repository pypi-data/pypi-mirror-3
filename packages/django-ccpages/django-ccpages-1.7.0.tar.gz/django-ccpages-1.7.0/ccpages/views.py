from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ccpages.models import Page
from ccpages.forms import PagePasswordForm


def index(request):
    """the index view returns the first page"""

    try:
        page = Page.custom.default()
    except Page.DoesNotExist:
        raise Http404()

    return HttpResponseRedirect(
            reverse('ccpages:view', args=[page.slug]))

def view(request, slug):
    """returns the page if there is no password.

    - if there is a password and the users session contains
        the correct hash then the page is returned

   - if there is a password and the users session does
       not contain the correct hash then they are redirected
       to the password view"""

    try:
        page = Page.custom.visible()\
                .get(slug=slug)
    except Page.DoesNotExist:
        raise Http404()

    # get the user_hash from the session
    try:
        user_hash = request.session['ccpage_%s_hash' % page.pk]
    except KeyError:
        user_hash = None

    # check the hash if the page is password protected
    password = page.password or ''
    if len(password) > 0 and user_hash != page.hash:
        messages.error(request,
                '"%s" is password protected' % page.title)
        return HttpResponseRedirect(
                reverse('ccpages:password', args=[page.slug]))
    # workout the template
    return render_to_response(
            page.layout or 'ccpages/view.html',
            {'page': page},
            RequestContext(request))


def password(request, slug):
    """ process the password for a page"""
    try:
        page = Page.custom.visible().get(slug=slug)
    except Page.DoesNotExist:
        raise Http404()

    # if there is no password for the page redirect back
    if not page.password:
        return HttpResponseRedirect(
                reverse('ccpages:view', args=[page.slug]))
    # make a form
    form = PagePasswordForm()

    # check the post
    if request.method == 'POST':
        form = PagePasswordForm(request.POST, page=page)
        if form.is_valid():
             request.session['ccpage_%s_hash' % page.pk] = form.hash
             return HttpResponseRedirect(
                     reverse('ccpages:view', args=[page.slug]))

    return render_to_response(
            'ccpages/password.html',
            {
                'page': page,
                'form': form },
            RequestContext(request))
