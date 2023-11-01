from django.http import HttpResponseForbidden

from app.models import AllowedIpModel


class WhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        remote_ip = request.META.get('REMOTE_ADDR')
        print(remote_ip)
        allowed_ips = [elem.ip for elem in AllowedIpModel.objects.all()]
        print(allowed_ips)
        if remote_ip not in allowed_ips:
            return HttpResponseForbidden("Access Denied")

        response = self.get_response(request)
        return response
