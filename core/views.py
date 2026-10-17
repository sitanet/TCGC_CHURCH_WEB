import json
import logging
import random
import re
import string
import threading
import time as _time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from .models import ConferenceRegistration, IMGCFeedingConfig, OnlineGiving, NewsletterSubscriber

logger = logging.getLogger(__name__)

# ============================================================================
# @dcitygatechurch YouTube Live Broadcast Integration
# ============================================================================
TCGC_YOUTUBE_CHANNEL_ID = 'UCCBbW2sdzT1ocV5YeNAhbqw'
TCGC_YOUTUBE_HANDLE = '@dcitygatechurch'
TCGC_YOUTUBE_CHANNEL_URL = 'https://www.youtube.com/@dcitygatechurch'

_DEFAULT_YOUTUBE_DATA = {
    'channel_id': TCGC_YOUTUBE_CHANNEL_ID,
    'channel_handle': TCGC_YOUTUBE_HANDLE,
    'channel_url': TCGC_YOUTUBE_CHANNEL_URL,
    'is_live': False,
    'video_id': '-C8U9kJSEYM',
    'video_title': 'IMAGE & GLORY PRE-CONFERENCE TEACHINGS || IMGPCT || 15-10-2026',
    'thumbnail_url': 'https://i.ytimg.com/vi/-C8U9kJSEYM/maxresdefault.jpg',
    'thumbnail': 'https://i.ytimg.com/vi/-C8U9kJSEYM/maxresdefault.jpg',
    'embed_url': 'https://www.youtube-nocookie.com/embed/-C8U9kJSEYM?autoplay=1&rel=0&enablejsapi=1',
    'channel_embed_url': f'https://www.youtube-nocookie.com/embed/live_stream?channel={TCGC_YOUTUBE_CHANNEL_ID}&autoplay=1&rel=0&enablejsapi=1',
    'watch_url': 'https://www.youtube.com/watch?v=-C8U9kJSEYM',
    'recent_videos': [],
}

_YOUTUBE_LIVE_CACHE = {
    'timestamp': 0,
    'refreshing': False,
    'data': dict(_DEFAULT_YOUTUBE_DATA),
}

# ============================================================================
# Image & Glory Conference (IMGC) Registration Constants & Helpers
# ============================================================================
CAMPING_DISPATCH_PHONE = "+2347065213082"       # Primary Camp & Accommodation Desk (+234 706 521 3082)
CAMPING_DISPATCH_PHONE_ALT = "+2347032055268"   # Secondary Camp Desk (+234 703 205 5268)
LUNCH_DISPATCH_PHONE = "+2347065213082"         # Dedicated WhatsApp contact for Day Attendee Lunch Meal Ticket Desk


def _generate_imgc_code(attendance_mode, feeding_subscription):
    """
    Generate unique random conference registration reference code (from TCGC_BACKEND):
    - IMGC-CAMP-XXXXX (Camping & Accommodation)
    - IMGC-MEAL-XXXXX (Non-Camping + Full Feeding: Lunch & Dinner)
    - IMGC-LUNCH-XXXXX (Non-Camping + Lunch Only)
    - IMGC-STREAM-XXXXX (Online Streamer)
    - IMGC-REG-XXXXX (Non-Camping General)
    """
    if attendance_mode == 'camping':
        prefix = 'IMGC-CAMP-'
    elif feeding_subscription == 'lunch_dinner':
        prefix = 'IMGC-MEAL-'
    elif feeding_subscription == 'lunch_only':
        prefix = 'IMGC-LUNCH-'
    elif attendance_mode == 'online':
        prefix = 'IMGC-STREAM-'
    else:
        prefix = 'IMGC-REG-'

    while True:
        random_num = ''.join(random.choices(string.digits, k=5))
        code = f"{prefix}{random_num}"
        if not ConferenceRegistration.objects.filter(registration_code=code).exists():
            return code


def _send_imgc_confirmation_email_sync(registration_id):
    """
    Send an automated HTML confirmation email to the attendee upon registration (runs in background thread).
    """
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings

        registration = ConferenceRegistration.objects.filter(id=registration_id).first()
        if not registration:
            return

        subject = f"Registration Confirmed: Image & Glory Conference 2026 [{registration.registration_code}]"
        action_html = ""
        action_text = ""

        if registration.requires_code_dispatch and registration.dispatch_phone_target:
            clean_phone = registration.dispatch_phone_target.replace('+', '').replace(' ', '').replace('-', '')
            clean_phone_alt = CAMPING_DISPATCH_PHONE_ALT.replace('+', '').replace(' ', '').replace('-', '')
            if registration.attendance_mode == 'camping':
                desk_name = "Camping & Accommodation Desk"
                dispatch_desc = "To finalize your Camp Accommodation and Feeding Allocation, please send your registration code to either of the camp desks via WhatsApp."
                wa_msg = (
                    f"Hello TCGC Protocol & Registration Team, my name is {registration.first_name} {registration.surname}. "
                    f"I have registered for Image & Glory Conference 2026 (IMGC 2026) as a CAMPER. "
                    f"My Registration Code is: {registration.registration_code}. "
                    f"Feeding Plan: {registration.get_feeding_subscription_display()}. "
                    f"Phone: {registration.phone_number}. Please verify my accommodation and feeding reservation."
                )
                encoded_msg = urllib.parse.quote(wa_msg)
                wa_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                wa_link_alt = f"https://wa.me/{clean_phone_alt}?text={encoded_msg}"

                action_text = (
                    f"\nIMPORTANT NEXT STEP:\n{dispatch_desc}\nSend your code ({registration.registration_code}) to:\n"
                    f"• Camp Desk 1: {registration.dispatch_phone_target} ({wa_link})\n"
                    f"• Camp Desk 2: {CAMPING_DISPATCH_PHONE_ALT} ({wa_link_alt})\n"
                )
                action_html = f"""
                <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 8px; padding: 18px 20px; margin: 24px 0; text-align: center;">
                    <h3 style="color: #15803D; margin-top: 0; font-size: 16px;">📲 Important Next Step ({desk_name})</h3>
                    <p style="color: #166534; font-size: 14px; line-height: 1.5; margin-bottom: 16px;">{dispatch_desc}</p>
                    <div style="margin-bottom: 10px;">
                        <a href="{wa_link}" target="_blank" style="background-color: #25D366; color: #000000; font-weight: bold; font-size: 14px; text-decoration: none; padding: 12px 24px; border-radius: 24px; display: inline-block;">
                            Send Code to Desk 1 (+234 706 521 3082)
                        </a>
                    </div>
                    <div>
                        <a href="{wa_link_alt}" target="_blank" style="background-color: #128C7E; color: #FFFFFF; font-weight: bold; font-size: 14px; text-decoration: none; padding: 12px 24px; border-radius: 24px; display: inline-block;">
                            Send Code to Desk 2 (+234 703 205 5268)
                        </a>
                    </div>
                </div>
                """
            else:
                desk_name = "Meal & Feeding Ticket Desk"
                plan_summary = registration.get_feeding_summary()
                fee_line = ""
                if registration.designation == 'church_worker' and registration.amount_paid and registration.amount_paid > 0:
                    fee_line = f" Expected Meal Fee: ₦{registration.amount_paid:,.2f} ({registration.feeding_days or 'All 5 Days'})."
                dispatch_desc = f"To confirm your {plan_summary},{fee_line} please send your registration code to either of our registration & meal desks via WhatsApp."
                wa_msg = (
                    f"Hello TCGC Protocol & Registration Team, my name is {registration.first_name} {registration.surname}. "
                    f"I have registered for Image & Glory Conference 2026 (IMGC 2026) (TCGC Service Team / Day Attendee with {plan_summary}). "
                    f"My Registration Code is: {registration.registration_code}.{fee_line} "
                    f"Phone: {registration.phone_number}. Please verify my meal subscription."
                )
                encoded_msg = urllib.parse.quote(wa_msg)
                wa_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                wa_link_alt = f"https://wa.me/{clean_phone_alt}?text={encoded_msg}"

                action_text = (
                    f"\nIMPORTANT NEXT STEP:\n{dispatch_desc}\nSend your code ({registration.registration_code}) to:\n"
                    f"• Desk 1: {registration.dispatch_phone_target} ({wa_link})\n"
                    f"• Desk 2: {CAMPING_DISPATCH_PHONE_ALT} ({wa_link_alt})\n"
                )
                action_html = f"""
                <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 8px; padding: 18px 20px; margin: 24px 0; text-align: center;">
                    <h3 style="color: #15803D; margin-top: 0; font-size: 16px;">📲 Important Next Step ({desk_name})</h3>
                    <p style="color: #166534; font-size: 14px; line-height: 1.5; margin-bottom: 16px;">{dispatch_desc}</p>
                    <div style="margin-bottom: 10px;">
                        <a href="{wa_link}" target="_blank" style="background-color: #25D366; color: #000000; font-weight: bold; font-size: 14px; text-decoration: none; padding: 12px 24px; border-radius: 24px; display: inline-block;">
                            Send Code to Desk 1 (+234 706 521 3082)
                        </a>
                    </div>
                    <div>
                        <a href="{wa_link_alt}" target="_blank" style="background-color: #128C7E; color: #FFFFFF; font-weight: bold; font-size: 14px; text-decoration: none; padding: 12px 24px; border-radius: 24px; display: inline-block;">
                            Send Code to Desk 2 (+234 703 205 5268)
                        </a>
                    </div>
                </div>
                """

        worker_fee_email_row = ""
        worker_fee_text_row = ""
        if registration.designation == 'church_worker' and registration.amount_paid and registration.amount_paid > 0:
            worker_fee_text_row = f"\nTotal Amount to Pay: ₦{registration.amount_paid:,.2f} ({registration.feeding_days or 'All 5 Days'})\n"
            worker_fee_email_row = f"""
            <tr style="background-color: #F0FDF4;">
                <td class="label" style="color: #166534; font-weight: bold;">Amount to Pay</td>
                <td class="val" style="color: #166534; font-weight: bold; font-size: 15px;">₦{registration.amount_paid:,.2f} ({registration.feeding_days or 'All 5 Days'})</td>
            </tr>
            """

        text_content = f"""Dear {registration.first_name} {registration.surname},

Thank you for registering for Image & Glory Conference 2026 powered by The CityGate Church, Ibadan!

REGISTRATION DETAILS:
------------------------------------------
Registration Code: {registration.registration_code}
Attendee Name: {registration.first_name} {registration.surname}
Email: {registration.email}
Phone: {registration.phone_number}
Location: {registration.city}, {registration.country}
Mode of Attendance: {registration.get_attendance_mode_display()}
Feeding Plan: {registration.get_feeding_summary()}{worker_fee_text_row}
------------------------------------------
{action_text}

We look forward to an unforgettable spiritual feast and divine transformation in the presence of God.

Warm regards,
The CityGate Church, Ibadan
https://thecitygatechurch.org
"""

        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #F8FAFC; margin: 0; padding: 20px; color: #334155; }}
.card {{ max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 32px 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
.header {{ text-align: center; border-bottom: 2px solid #F1F5F9; padding-bottom: 20px; margin-bottom: 24px; }}
.title {{ color: #8B1E2E; font-size: 22px; font-weight: 800; margin: 0 0 6px; }}
.sub {{ color: #64748B; font-size: 14px; margin: 0; }}
.pass {{ background-color: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 8px; text-align: center; padding: 18px; margin: 20px 0; }}
.code {{ font-family: monospace; font-size: 24px; font-weight: bold; color: #8B1E2E; letter-spacing: 2px; }}
.table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }}
.table td {{ padding: 10px 4px; border-bottom: 1px solid #F1F5F9; }}
.table td.label {{ color: #64748B; width: 40%; font-weight: 500; }}
.table td.val {{ color: #0F172A; font-weight: 600; }}
.footer {{ text-align: center; font-size: 12px; color: #94A3B8; margin-top: 24px; border-top: 1px solid #F1F5F9; padding-top: 16px; }}
</style>
</head>
<body>
<div class="card">
    <div class="header">
        <h1 class="title">Image & Glory Conference 2026</h1>
        <p class="sub">Powered by The CityGate Church, Ibadan</p>
    </div>
    <p style="font-size: 15px; line-height: 1.5; color: #0F172A;">
        Dear <strong>{registration.first_name} {registration.surname}</strong>,
    </p>
    <p style="font-size: 14px; line-height: 1.6; color: #334155;">
        Glory to God! Your registration for <strong>Image & Glory Conference 2026</strong> has been received successfully. Below is your official registration summary and unique reference code.
    </p>
    <div class="pass">
        <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: bold; letter-spacing: 1px; margin-bottom: 4px;">Your Registration Code</div>
        <div class="code">{registration.registration_code}</div>
        <div style="font-size: 12px; color: #0F172A; margin-top: 6px; font-weight: 600;">{registration.get_attendance_mode_display()} • {registration.get_feeding_summary()}</div>
    </div>
    {action_html}
    <table class="table">
        <tr><td class="label">Attendee Name</td><td class="val">{registration.first_name} {registration.surname}</td></tr>
        <tr><td class="label">Email Address</td><td class="val">{registration.email}</td></tr>
        <tr><td class="label">Phone Number</td><td class="val">{registration.phone_number}</td></tr>
        <tr><td class="label">Location</td><td class="val">{registration.city}, {registration.country}</td></tr>
        <tr><td class="label">Designation</td><td class="val">{registration.get_designation_display()}</td></tr>
        <tr><td class="label">Attendance Mode</td><td class="val">{registration.get_attendance_mode_display()}</td></tr>
        <tr><td class="label">Feeding Plan</td><td class="val">{registration.get_feeding_summary()}</td></tr>
        {worker_fee_email_row}
    </table>
    <p style="font-size: 14px; line-height: 1.6; color: #334155;">
        We eagerly anticipate your participation in this life-transforming conference. May God enrich and bless your spiritual journey!
    </p>
    <div class="footer">
        <p style="margin: 0 0 4px;">© 2026 The CityGate Church, Ibadan. All Rights Reserved.</p>
        <p style="margin: 0;"><a href="https://thecitygatechurch.org" style="color: #8B1E2E; text-decoration: none;">thecitygatechurch.org</a></p>
    </div>
</div>
</body>
</html>
"""

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@thecitygatechurch.org') or 'noreply@thecitygatechurch.org'
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[registration.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=True)
        logger.info(f"[IMGC_EMAIL] Confirmation email sent successfully to {registration.email}")
    except Exception as e:
        logger.debug(f"[IMGC_EMAIL_SKIPPED] {e}")


def _send_imgc_confirmation_email(registration):
    """Non-blocking background dispatch for IMGC confirmation email."""
    threading.Thread(
        target=_send_imgc_confirmation_email_sync,
        args=(registration.id,),
        daemon=True,
    ).start()


def _refresh_youtube_cache_sync():
    """Fetches @dcitygatechurch live status, latest stream, and thumbnail in the background."""
    global _YOUTUBE_LIVE_CACHE
    try:
        current_data = dict(_YOUTUBE_LIVE_CACHE.get('data') or _DEFAULT_YOUTUBE_DATA)
        live_url = f'{TCGC_YOUTUBE_CHANNEL_URL}/live'
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }

        is_live = False
        vid = None
        title = None

        # 1. Check if actively live
        try:
            req = urllib.request.Request(live_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as res:
                html = res.read().decode('utf-8', errors='ignore')
                can = re.findall(r'<link rel="canonical" href="https://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})">', html)
                if can and can[0] != 'otbTOpTpSpY':
                    vid = can[0]
                    is_live = ('"isLive":true' in html or '"isLiveContent":true' in html or ('"status":"LIVE"' in html and 'LIVE_STREAM_OFFLINE' not in html))
        except Exception as live_err:
            logger.debug(f'YouTube /live check skipped: {live_err}')

        # 2. If no active live stream found, check /streams tab for the latest stream broadcast
        if not vid:
            try:
                streams_url = f'{TCGC_YOUTUBE_CHANNEL_URL}/streams'
                req_streams = urllib.request.Request(streams_url, headers=headers)
                with urllib.request.urlopen(req_streams, timeout=4) as res_s:
                    html_s = res_s.read().decode('utf-8', errors='ignore')
                    raw_vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html_s)
                    valid_vids = [v for v in raw_vids if v != 'otbTOpTpSpY']
                    if valid_vids:
                        vid = valid_vids[0]
            except Exception as streams_err:
                logger.debug(f'YouTube /streams check skipped: {streams_err}')

        # 3. Fallback to default verified broadcast ID
        if not vid:
            vid = _DEFAULT_YOUTUBE_DATA['video_id']

        # 4. Fetch title via oEmbed
        try:
            oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json'
            with urllib.request.urlopen(oembed_url, timeout=3) as oresp:
                odata = json.loads(oresp.read().decode('utf-8'))
                title = odata.get('title')
        except Exception:
            pass

        if not title:
            title = current_data.get('video_title') or _DEFAULT_YOUTUBE_DATA['video_title']

        thumb_url = f'https://i.ytimg.com/vi/{vid}/maxresdefault.jpg'

        current_data.update({
            'channel_id': TCGC_YOUTUBE_CHANNEL_ID,
            'channel_handle': TCGC_YOUTUBE_HANDLE,
            'channel_url': TCGC_YOUTUBE_CHANNEL_URL,
            'is_live': is_live,
            'video_id': vid,
            'video_title': title,
            'thumbnail_url': thumb_url,
            'thumbnail': thumb_url,
            'embed_url': f'https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0&enablejsapi=1',
            'channel_embed_url': f'https://www.youtube-nocookie.com/embed/live_stream?channel={TCGC_YOUTUBE_CHANNEL_ID}&autoplay=1&rel=0&enablejsapi=1',
            'watch_url': f'https://www.youtube.com/watch?v={vid}',
        })

        # Also populate recent_videos from /streams
        recent = []
        try:
            streams_url = f'{TCGC_YOUTUBE_CHANNEL_URL}/streams'
            req_streams = urllib.request.Request(streams_url, headers=headers)
            with urllib.request.urlopen(req_streams, timeout=4) as res_s:
                html_s = res_s.read().decode('utf-8', errors='ignore')
                raw_vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html_s)
                seen = set()
                unique_vids = []
                for v in raw_vids:
                    if v != 'otbTOpTpSpY' and v not in seen:
                        seen.add(v)
                        unique_vids.append(v)

                for r_vid in unique_vids[:6]:
                    recent.append({
                        'video_id': r_vid,
                        'title': 'The CityGate Church Broadcast',
                        'thumbnail': f'https://i.ytimg.com/vi/{r_vid}/hqdefault.jpg',
                        'thumbnail_url': f'https://i.ytimg.com/vi/{r_vid}/maxresdefault.jpg',
                        'embed_url': f'https://www.youtube-nocookie.com/embed/{r_vid}?autoplay=1&rel=0&enablejsapi=1',
                        'watch_url': f'https://www.youtube.com/watch?v={r_vid}',
                    })
        except Exception as rec_err:
            logger.debug(f'Recent streams fetch skipped: {rec_err}')

        if recent:
            current_data['recent_videos'] = recent

        _YOUTUBE_LIVE_CACHE['data'] = current_data
        _YOUTUBE_LIVE_CACHE['timestamp'] = _time.time()
    except Exception as e:
        logger.debug(f'Background YouTube live check skipped: {e}')
        _YOUTUBE_LIVE_CACHE['timestamp'] = _time.time()
    finally:
        _YOUTUBE_LIVE_CACHE['refreshing'] = False


def get_youtube_live_info(force_refresh=False):
    """
    Returns cached @dcitygatechurch YouTube info immediately (0ms blocking on page navigations)
    and triggers a background refresh thread if cache is older than 5 minutes.
    """
    global _YOUTUBE_LIVE_CACHE
    now = _time.time()

    if force_refresh:
        _refresh_youtube_cache_sync()
        return _YOUTUBE_LIVE_CACHE['data']

    if (now - _YOUTUBE_LIVE_CACHE.get('timestamp', 0) > 300) and not _YOUTUBE_LIVE_CACHE.get('refreshing'):
        _YOUTUBE_LIVE_CACHE['refreshing'] = True
        threading.Thread(target=_refresh_youtube_cache_sync, daemon=True).start()

    return _YOUTUBE_LIVE_CACHE['data']


def api_live_video(request):
    """JSON API endpoint returning real-time @dcitygatechurch YouTube live broadcast info."""
    force = request.GET.get('force') in ['1', 'true']
    info = get_youtube_live_info(force_refresh=force)
    return JsonResponse(info)


def home(request):
    if request.method == 'POST' and request.POST.get('form_type') == 'give_online':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_country_code = request.POST.get('phone_country_code', '+234').strip() or '+234'
        phone_number = request.POST.get('phone_number', '').strip()

        if first_name and last_name and email and phone_number:
            OnlineGiving.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_country_code=phone_country_code,
                phone_number=phone_number,
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Thank you, {first_name}! Your online giving details have been received.'
                })
            messages.success(request, f'Thank you, {first_name}! Your online giving details have been received.')
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Please fill in all required fields.'}, status=400)
            messages.error(request, 'Please fill in all required fields.')

    youtube_live_info = get_youtube_live_info()
    return render(request, 'home.html', {
        'active_page': 'home',
        'youtube_live_info': youtube_live_info,
        'youtube_live_json': json.dumps(youtube_live_info),
    })


def registration(request):
    """
    Image & Glory Conference 2026 Registration View.
    Integrates the full backend business logic of https://tcgc.thecitygatechurch.org/imgc/
    inside the TCGC Figma Registration form design.
    """
    feeding_config = IMGCFeedingConfig.get_config()

    if request.method == 'POST':
        surname = request.POST.get('surname', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_country_code = request.POST.get('phone_country_code', '+234').strip() or '+234'
        raw_phone = request.POST.get('phone_number', '').strip()
        gender = request.POST.get('gender', '').strip().lower()
        age_range = request.POST.get('age_range', '').strip()
        designation = request.POST.get('designation', '').strip()
        other_designation = request.POST.get('other_designation', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', 'Nigeria').strip() or 'Nigeria'

        # Support both `is_first_time` (from /imgc/) and `first_time_attending`
        is_first_time_raw = (
            request.POST.get('is_first_time')
            or request.POST.get('first_time_attending')
            or 'no'
        ).strip().lower()
        is_first_time = is_first_time_raw in ['yes', 'true', '1']

        # Normalize attendance mode (`camping`, `non_camping`, `online`)
        raw_mode = request.POST.get('attendance_mode', 'camping').strip()
        mode_map = {
            'onsite_camp': 'camping',
            'camping': 'camping',
            'physical_day': 'non_camping',
            'non_camping': 'non_camping',
            'virtual_streaming': 'online',
            'online': 'online',
        }
        attendance_mode = mode_map.get(raw_mode, raw_mode or 'camping')

        feeding_subscription = request.POST.get('feeding_subscription', 'none').strip()
        special_notes = (
            request.POST.get('special_notes')
            or request.POST.get('expectation')
            or ''
        ).strip()

        # Format phone number with country code if needed
        if raw_phone:
            if raw_phone.startswith('+'):
                phone_number = raw_phone
            elif raw_phone.startswith('0') and phone_country_code == '+234':
                phone_number = f"{phone_country_code}{raw_phone[1:]}"
            else:
                phone_number = f"{phone_country_code}{raw_phone}"
        else:
            phone_number = ''

        # Validation (matching TCGC_BACKEND /imgc/)
        errors = {}
        if not surname:
            errors['surname'] = 'Surname is required'
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not email or '@' not in email:
            errors['email'] = 'A valid email address is required'
        if not raw_phone:
            errors['phone_number'] = 'Phone number is required'
        if not gender:
            errors['gender'] = 'Please select your gender'
        if not age_range:
            errors['age_range'] = 'Please select your age range'
        if not designation:
            errors['designation'] = 'Please select your designation'
        if not city:
            errors['city'] = 'City is required'
        if not country:
            errors['country'] = 'Country is required'
        if not attendance_mode:
            errors['attendance_mode'] = 'Please select your mode of attendance'

        # Duplicate registration prevention (check email & last 10 digits of phone number)
        existing_reg = None
        if not errors.get('email') and email:
            existing_reg = ConferenceRegistration.objects.filter(email__iexact=email).first()

        if not existing_reg and not errors.get('phone_number') and phone_number:
            clean_digits = ''.join(c for c in phone_number if c.isdigit())
            if len(clean_digits) >= 10:
                last_10 = clean_digits[-10:]
                existing_reg = ConferenceRegistration.objects.filter(phone_number__endswith=last_10).first()
            else:
                existing_reg = ConferenceRegistration.objects.filter(phone_number__iexact=phone_number).first()

        if existing_reg:
            if not existing_reg.registration_code:
                existing_reg.registration_code = _generate_imgc_code(
                    existing_reg.attendance_mode, existing_reg.feeding_subscription
                )
                existing_reg.save(update_fields=['registration_code'])
            dup_msg = (
                f"You have already registered for IMGC 2026! "
                f"Your registration code is {existing_reg.registration_code}. "
                f"Duplicate registrations with the same email or phone number are not permitted."
            )
            errors['duplicate'] = dup_msg
            if email and existing_reg.email.lower() == email.lower():
                errors['email'] = f"An attendee is already registered with this email ({existing_reg.registration_code})."
            else:
                errors['phone_number'] = f"An attendee is already registered with this phone number ({existing_reg.registration_code})."

        # Validate feeding subscription according to attendance mode
        if attendance_mode == 'camping':
            if feeding_subscription not in ['lunch_dinner', 'lunch_only', 'none']:
                feeding_subscription = 'lunch_dinner'
        elif attendance_mode == 'non_camping':
            if feeding_subscription not in ['lunch_dinner', 'lunch_only', 'none']:
                feeding_subscription = 'none'
        else:  # online
            feeding_subscription = 'none'

        feeding_days = request.POST.get('feeding_days', '').strip()
        if feeding_subscription == 'lunch_only':
            if not feeding_days or feeding_days.lower() in ('all', 'all days', 'all_days'):
                feeding_days = 'All Days'
        elif feeding_subscription == 'lunch_dinner':
            feeding_days = 'All Days'
        else:
            feeding_days = ''

        if errors:
            first_err_msg = errors.get('duplicate') or next(iter(errors.values()), 'Please check your input and try again.')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'status': 'error',
                    'success': False,
                    'message': first_err_msg,
                    'errors': errors,
                    'existing_code': existing_reg.registration_code if existing_reg else None,
                    'redirect_url': (
                        reverse('registration_confirmation', kwargs={'registration_code': existing_reg.registration_code})
                        if existing_reg else None
                    ),
                }, status=400)
            return render(request, 'registration.html', {
                'active_page': 'events',
                'errors': errors,
                'form_data': request.POST,
                'existing_code': existing_reg.registration_code if existing_reg else None,
                'camping_phone': CAMPING_DISPATCH_PHONE,
                'lunch_phone': LUNCH_DISPATCH_PHONE,
                'service_team_daily_cost': feeding_config.service_team_daily_cost,
            })

        # Compute dynamic feeding fee for TCGC Service Team (`church_worker` + `lunch_only`)
        calculated_amount = Decimal('0.00')
        if designation == 'church_worker' and feeding_subscription == 'lunch_only':
            if not feeding_days or feeding_days.strip().lower() in ('all', 'all days', 'all 5 days', 'all_days'):
                days_count = 5
            else:
                days_list = [d.strip() for d in feeding_days.split(',') if d.strip()]
                days_count = len(days_list) if days_list else 5
            calculated_amount = Decimal(days_count) * feeding_config.service_team_daily_cost

        # Generate unique IMGC code & determine WhatsApp dispatch requirements
        registration_code = _generate_imgc_code(attendance_mode, feeding_subscription)
        requires_dispatch = False
        target_phone = None

        if attendance_mode == 'camping':
            requires_dispatch = True
            target_phone = CAMPING_DISPATCH_PHONE
        elif feeding_subscription in ['lunch_dinner', 'lunch_only']:
            requires_dispatch = True
            target_phone = CAMPING_DISPATCH_PHONE

        # Get client IP & user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        reg_obj = ConferenceRegistration.objects.create(
            registration_code=registration_code,
            surname=surname,
            first_name=first_name,
            email=email,
            phone_country_code=phone_country_code,
            phone_number=phone_number,
            gender=gender,
            age_range=age_range,
            designation=designation,
            other_designation=other_designation,
            city=city,
            state=state,
            country=country,
            is_first_time=is_first_time,
            first_time_attending=is_first_time,
            attendance_mode=attendance_mode,
            feeding_subscription=feeding_subscription,
            feeding_days=feeding_days,
            amount_paid=calculated_amount,
            expectation=special_notes,
            special_notes=special_notes,
            requires_code_dispatch=requires_dispatch,
            dispatch_phone_target=target_phone,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Send automated confirmation email in background thread
        _send_imgc_confirmation_email(reg_obj)

        confirmation_url = reverse('registration_confirmation', kwargs={'registration_code': reg_obj.registration_code})

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'status': 'success',
                'success': True,
                'message': f'Registration complete! Your Registration Code is {reg_obj.registration_code}. Redirecting to your confirmation slip...',
                'registration_code': reg_obj.registration_code,
                'amount_to_pay': float(calculated_amount),
                'redirect_url': confirmation_url,
            })

        return redirect('registration_confirmation', registration_code=reg_obj.registration_code)

    return render(request, 'registration.html', {
        'active_page': 'events',
        'form_data': {},
        'errors': {},
        'camping_phone': CAMPING_DISPATCH_PHONE,
        'lunch_phone': LUNCH_DISPATCH_PHONE,
        'service_team_daily_cost': feeding_config.service_team_daily_cost,
    })


def registration_confirmation(request, registration_code):
    """
    IMGC 2026 Registration Confirmation Page with unique pass code,
    WhatsApp Desk 1 & Desk 2 dispatch links, Service Team fee breakdown, and printable slip.
    """
    feeding_config = IMGCFeedingConfig.get_config()
    reg = get_object_or_404(ConferenceRegistration, registration_code=registration_code)

    whatsapp_url = None
    whatsapp_url_alt = None
    if reg.requires_code_dispatch and reg.dispatch_phone_target:
        clean_phone = reg.dispatch_phone_target.replace('+', '').replace(' ', '').replace('-', '')
        clean_phone_alt = CAMPING_DISPATCH_PHONE_ALT.replace('+', '').replace(' ', '').replace('-', '')
        if reg.attendance_mode == 'camping':
            msg_text = (
                f"Hello TCGC Protocol & Registration Team,\n\n"
                f"My name is {reg.first_name} {reg.surname}.\n"
                f"I have registered for Image & Glory Conference 2026 (IMGC 2026) as a CAMPER.\n\n"
                f"📋 Registration Code: *{reg.registration_code}*\n"
                f"🍽️ Feeding Plan: *{reg.get_feeding_summary()}*\n"
                f"📞 Phone: {reg.phone_number}\n"
                f"📍 Location: {reg.city}, {reg.country}\n\n"
                f"Please verify my accommodation and feeding reservation. Thank you!"
            )
            encoded_msg = urllib.parse.quote(msg_text)
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            whatsapp_url_alt = f"https://wa.me/{clean_phone_alt}?text={encoded_msg}"
        else:
            plan_summary = reg.get_feeding_summary()
            fee_note = ""
            if reg.designation == 'church_worker' and reg.amount_paid and reg.amount_paid > 0:
                fee_note = f"\n💳 Amount to Pay: *₦{reg.amount_paid:,.2f}* ({reg.feeding_days or 'All 5 Days'})"
                if feeding_config.account_number:
                    fee_note += f"\n🏦 Transfer Account: {feeding_config.bank_name} - {feeding_config.account_number} ({feeding_config.account_name})"
            msg_text = (
                f"Hello TCGC Protocol & Registration Team,\n\n"
                f"My name is {reg.first_name} {reg.surname}.\n"
                f"I have registered for Image & Glory Conference 2026 (IMGC 2026) (TCGC Service Team / Day Attendee).\n\n"
                f"📋 Registration Code: *{reg.registration_code}*\n"
                f"🍽️ Meal Plan: *{plan_summary}*{fee_note}\n"
                f"📞 Phone: {reg.phone_number}\n\n"
                f"Please verify my meal ticket subscription. Thank you!"
            )
            encoded_msg = urllib.parse.quote(msg_text)
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            whatsapp_url_alt = f"https://wa.me/{clean_phone_alt}?text={encoded_msg}"

    return render(request, 'registration_confirmation.html', {
        'active_page': 'events',
        'reg': reg,
        'feeding_config': feeding_config,
        'whatsapp_url': whatsapp_url,
        'whatsapp_url_alt': whatsapp_url_alt,
        'camp_phone_1': CAMPING_DISPATCH_PHONE,
        'camp_phone_2': CAMPING_DISPATCH_PHONE_ALT,
    })


def video_streaming(request):
    youtube_live_info = get_youtube_live_info()
    return render(request, 'video_streaming.html', {
        'active_page': 'media',
        'youtube_live_info': youtube_live_info,
        'youtube_live_json': json.dumps(youtube_live_info),
    })


def audio_streaming(request):
    return render(request, 'audio_streaming.html', {'active_page': 'media'})


def ministries(request):
    return render(request, 'ministries.html', {'active_page': 'about'})


def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Thank you for subscribing to The CityGate Church updates!'
                })
            messages.success(request, 'Thank you for subscribing to The CityGate Church updates!')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address.'}, status=400)
    return redirect(request.META.get('HTTP_REFERER', 'home'))
