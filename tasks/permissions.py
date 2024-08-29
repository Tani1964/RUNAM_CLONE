from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
# class HasPhoneNumberPermission(BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.profile.phone_number:
#             return Response
#         # Check if the user has a phone number in their profile
#         return request.user.profile.phone_number is not None
    


# class HasPhoneNumberPermission(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user.profile.phone_number)


class HasPhoneNumberPermission(BasePermission):
    message = "You must complete your profile to create, view or accept tasks, click on this link: http://127.0.0.1:8000/users/profile/"
    def has_permission(self, request, view):
        
        check = bool(request.user.profile.phone_number)
        if check == False:
            raise PermissionDenied(detail=self.message)
        return bool(request.user.profile.phone_number)
    
        


class IsTaskMessenger(BasePermission):
    """
    Custom permission to allow only the messenger of a task to perform changes.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the messenger of the task.
        """
        # Check if the request method is safe (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # For non-safe methods (PUT, PATCH, DELETE), check if the user is the messenger
        if obj.messenger == request.user:
            return True
        
        # Raise a PermissionDenied exception with a custom message
        raise PermissionDenied(detail="You do not have permission to modify this task.")



# permissions.py

# from rest_framework.permissions import BasePermission
# from rest_framework import status
# from rest_framework.exceptions import PermissionDenied


# class HasPhoneNumberPermission(BasePermission):
#     message = "User must have a phone number in their profile to create tasks."

#     def has_permission(self, request, view):
#         if request.user.profile.phone_number is None:
#             raise PermissionDenied(detail=self.message)
#         return True
