# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import logging

import django.utils.simplejson as json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext

import ecm
from ecm.apps.corp.models import Corporation

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
WRONG_FINGERPRINT_MSG = '''The corporation "%s" (id: %s) tried to obtain our public info.
We already are in contact with this corporation, but the public key fingerprint they 
provided does not match the one we have in the database.'''
@csrf_exempt
@transaction.commit_on_success
def handle_contact(request):
    
    if request.method == 'POST':
        public_info = Corporation.objects.mine().get_public_info()
        
        try:
            corp_info = json.loads(request.body)
            ecm_url = corp_info['ecm_url']
            corporationID = corp_info['corporationID']
            corporationName = corp_info['corporationName']
            ticker = corp_info['ticker']
            allianceID = corp_info['allianceID']
            allianceName = corp_info['allianceName']
            allianceTicker = corp_info['allianceTicker']
            public_key = corp_info['public_key']
            key_fingerprint = corp_info['key_fingerprint']
            
            new_request = False
            if Corporation.objects.filter(corporationID=corporationID).exists():
                corp = Corporation.objects.get(corporationID=corporationID)
                if not corp.key_fingerprint:
                    # This corp was created by some internal task but we don't know their 
                    # public info yet.
                    corp.corporationName = corporationName
                    corp.ticker = ticker
                    corp.allianceID = allianceID
                    corp.allianceName = allianceName
                    corp.allianceTicker = allianceTicker
                    corp.ecm_url = ecm_url
                    corp.public_key = public_key
                    corp.key_fingerprint = key_fingerprint
                    corp.is_trusted = False
                    new_request = True
                else:
                    if corp.key_fingerprint != key_fingerprint:
                        # tentative of hack? return an error
                        LOG.error(WRONG_FINGERPRINT_MSG % (corporationName, corporationID))
                        raise ValueError('wrong key_fingerprint')
            else:
                # create the corp in our db
                corp = Corporation(corporationID=corporationID,
                                   corporationName=corporationName,
                                   ticker=ticker,
                                   allianceID=allianceID,
                                   allianceName=allianceName,
                                   allianceTicker=allianceTicker,
                                   ecm_url=ecm_url,
                                   public_key=public_key,
                                   key_fingerprint=key_fingerprint,
                                   is_trusted=False,
                                   )
                new_request = True
                
            if new_request:
                corp.save()
                # notify the admins that a new corp tried to contact us
                subject = ugettext('%s wants to exchange data with us') % corp.corporationName
                ctx_dict = {
                    'host_name': settings.EXTERNAL_HOST_NAME,
                    'use_https': settings.USE_HTTPS,
                    'corp': corp,
                }
                txt_content = render_to_string('ecm/corp/email/notify_contact.txt', 
                                               ctx_dict, Ctx(request))
                html_content = render_to_string('ecm/corp/email/notify_contact.html', 
                                                ctx_dict, Ctx(request))
                mail_admins(subject, txt_content, html_message=html_content)
            
            # if everything went well, return back our public info
            return HttpResponse(json.dumps(public_info))
            
        except (ValueError, KeyError), e:
            # invalid field value
            return HttpResponseBadRequest(str(e))
        
    else:
        # we send our version to the client (along with the CSRF cookie in the response) 
        return HttpResponse(ecm.VERSION)
