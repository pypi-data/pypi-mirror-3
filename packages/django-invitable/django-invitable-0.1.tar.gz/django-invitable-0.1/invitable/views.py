from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from invitable.forms import InvitableForm, INVITABLE_ACCOUNT_TYPES

@login_required
def form(request):
    if request.method == "POST":
        form = InvitableForm(request.POST)

        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.user = request.user
            invitation.save()

            messages.success(request, "Invitation sent to %s" % invitation.email)
    else:
        form = InvitableForm()

    account_types = INVITABLE_ACCOUNT_TYPES

    return render_to_response("invitable/form.html",
                              {'form': form, 'account_types': account_types},
                              context_instance=RequestContext(request))
