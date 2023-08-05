#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache

from lck.django.activitylog.models import UserAgent, IP, ProfileIP,\
    ProfileUserAgent
from lck.django.common import remote_addr


class ActivityMiddleware(object):
    """Updates the `last_active` profile field for every logged in user with
    the current timestamp. It pragmatically stores a new value every 40 seconds
    (one third of the seconds specified ``CURRENTLY_ONLINE_INTERVAL`` setting).
    """

    def process_request(self, request):
        # FIXME: use a single cache key with lck.django.cache to minimize
        # writes to cache

        # FIXME: don't use concurrent_get_or_create for pip and pua to maximize
        # performance
        now = datetime.now()
        seconds = getattr(settings, 'CURRENTLY_ONLINE_INTERVAL', 120)
        delta = now - timedelta(seconds=seconds)
        users_online = cache.get('users_online', {})
        guests_online = cache.get('guests_online', {})
        if request.user.is_authenticated():
            users_online[request.user.id] = now
            profile = request.user.get_profile()
            last_active = profile.last_active
            if not last_active or 3 * (now - last_active).seconds > seconds:
                # we're not using save() to bypass signals etc.
                profile.__class__.objects.filter(pk = profile.pk).update(
                    last_active = now)
            ip, _ = IP.concurrent_get_or_create(address=remote_addr(request))
            pip, _ = ProfileIP.concurrent_get_or_create(ip=ip,
                user=request.user, profile=profile)
            ProfileIP.objects.filter(pk = pip.pk).update(
                modified = now)
            agent, _ = UserAgent.concurrent_get_or_create(
                name=request.META['HTTP_USER_AGENT'])
            pua, _ = ProfileUserAgent.concurrent_get_or_create(agent=agent,
                user=request.user, profile=profile)
            ProfileUserAgent.objects.filter(pk = pua.pk).update(
                modified = now)
        else:
            guest_sid = request.COOKIES.get(settings.SESSION_COOKIE_NAME, '')
            guests_online[guest_sid] = now

        for user_id in users_online.keys():
            if users_online[user_id] < delta:
                del users_online[user_id]

        for guest_id in guests_online.keys():
            if guests_online[guest_id] < delta:
                del guests_online[guest_id]

        cache.set('users_online', users_online, 60*60*24)
        cache.set('guests_online', guests_online, 60*60*24)
