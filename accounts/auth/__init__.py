class MembershipStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            if not request.user.is_current_member:
                request.user.sync_membership_status()
        return response
