class ActivityLogMiddleware:
    """Hook point for request-level logging; write actions are logged
    explicitly by views via apps.common.utils.log_activity()."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
