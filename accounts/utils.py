

def detectUser(user):
    if user.role == 1:
        redirectUrl = 'accounts:vendorDashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'accounts:custDashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl
