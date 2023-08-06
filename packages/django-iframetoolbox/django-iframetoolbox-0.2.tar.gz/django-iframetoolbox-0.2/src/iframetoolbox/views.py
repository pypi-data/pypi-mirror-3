from django.shortcuts import render_to_response


def iframe_fix(request):
    return render_to_response('iframe/cookie_page.html')
