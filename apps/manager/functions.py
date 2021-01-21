from .models import ElectricityBill


def private_file_auth_function(private_file):
    user = private_file.request.user
    if user.is_staff or user.is_superuser:
        return True
    else:
        try:
            profile = user.profile
            return ElectricityBill.objects.filter(
                project__profile=profile,
                private_file=private_file.relative_name.replace('/private/', ''),
            )
        except:
            return False
