from rest_framework import serializers
from .models import Task, AcceptTask, TaskReview, Keyword, Bidder, NewBidder, Support, Shop, TaskImages
from users.models import User, Profile
from django.utils import timezone
from users.serializers import CustomUserSerializer, MyUserSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings

class KeywordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["name"]



class TaskHistorySerializer(serializers.ModelSerializer):
    date_posted = serializers.SerializerMethodField("format_date_posted")
    class Meta:
        model = Task
        fields = ["id", "type", "name", "date_posted"]

    def format_date_posted(self, obj):
        return obj.date_posted.strftime('%d-%m-%Y')

    



class PostNewBidderSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField("get_bidder_username")
    class Meta:
        model = NewBidder
        fields = ["message"]


class GetNewBidderSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewBidder
        fields = ["message"]

    # def get_bidder_username(self, obj):
    #     return obj.user.username


class GetBidderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_bidder_username")
    phone_number = serializers.SerializerMethodField("get_bidder_phone_number")
    bidder_detail_url = serializers.SerializerMethodField("get_task_bidder_details")

    class Meta:
        model = Bidder
        fields = ["user", "message", "price", "phone_number", "bidder_detail_url"]

    def get_bidder_username(self, obj):
        return obj.user.username
    
    def get_bidder_phone_number(self, obj):
        return obj.user.profile.phone_number
    
    def get_task_bidder_details(self, obj):
        if settings.DEBUG:
            return f"http://127.0.0.1:8000/tasks/{obj.task.id}/bidders/{obj.user.email}/details"
        else:
            return f"https://runit-78od.onrender.com/tasks/{obj.task.id}/bidders/{obj.user.email}/details"
    


class PostBidderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bidder
        fields = ["message", "price"]


class BidderDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_bidder_username")
    phone_number = serializers.SerializerMethodField("get_bidder_phone_number")
    user = CustomUserSerializer()
    user_profile = serializers.SerializerMethodField("get_user_profile")
    # profile_details = ProfileSerializer()


    class Meta:
        model = Bidder
        fields = ["user", "price", "phone_number", "message", "user", "user_profile"]


    def get_bidder_username(self, obj):
        return obj.user.username
    
    def get_bidder_phone_number(self, obj):
        return obj.user.profile.phone_number
    

    def get_user_profile(self, obj):
        print(obj.user.email)
        user = get_object_or_404(User, email=obj.user.email)
        user_profile = get_object_or_404(Profile, user=user)
        serializer = ProfileSerializer(user_profile)
        return serializer.data
    
    
    

    


        
    

# class CreateTaskBidSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=100)
#     message = serializers.CharField(max_length=300)

 
#     def validate(self, attrs):
#         user = attrs.get("username")
#         if not User.objects.get(username=user):
#             raise ValueError({"Response": "No user found"})
#         return attrs
    

#     def create(self, validated_data):
#         username = validated_data["username"]
#         message = validated_data["message"]
#         user=User.objects.get(username=username)
#         if user:
#             comment=Bidder.objects.create(user=user, message=message)
#             payload={
#                 "username":comment.user__username,
#                 "message": message
#             }
#         return payload



class CreateShopTaskSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField("get_name_of_sender")
    # url = serializers.HyperlinkedIdentityField(view_name='task-detail', lookup_field='id')
    # receiver_name = serializers.SerializerMethodField("get_name_of_receiver")
    # keywords = KeywordsSerializer()
    keywords = serializers.SerializerMethodField("get_actual_keyword")
    # task_bidders = serializers.SerializerMethodField("get_task_bidders")
    is_active = serializers.ReadOnlyField()
    completed = serializers.ReadOnlyField()
    paid = serializers.ReadOnlyField()
    category = serializers.StringRelatedField()
    shop = serializers.StringRelatedField()
    class Meta:
        model = Task
        fields = ["id", "name", "description", "category", "image", "bidding_amount", "sender_name", "shop", "keywords", "is_active",  "completed", "paid"]


    def get_name_of_sender(self, obj):
        shop_name = obj.shop.name
        return shop_name
    
    def get_actual_keyword(self, obj):
        return KeywordsSerializer(obj.keywords.all(), many=True).data


class TaskImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskImages
        fields = ["task", "image"]


class DirectTaskSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField("get_name_of_sender")
    keywords = serializers.SerializerMethodField("get_actual_keyword")
    is_active = serializers.ReadOnlyField()
    completed = serializers.ReadOnlyField()
    paid = serializers.ReadOnlyField()
    category = serializers.StringRelatedField()
    images = TaskImageSerializer(many=True, read_only=True)
    task_url = serializers.HyperlinkedIdentityField(
        view_name="task-detail",
        lookup_field = "id"
    )
    messenger = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    

    class Meta:
        model = Task
        fields = ["id", "task_url", "name", "description", "type", "tip", "pick_up", "deliver_to", "category", "image", "bidding_amount", "sender_name", "keywords", "is_active", "picked_up",  "completed", "paid", "messenger", "images"]

    
    def create(self, validated_data):
        # Retrieve the request context if available
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
        
        return super().create(validated_data)
 

    def get_name_of_sender(self, task_sender):
        username = task_sender.sender.username
        return username
    
    def get_actual_keyword(self, obj):
        return KeywordsSerializer(obj.keywords.all(), many=True).data
    
    def get_task_bidders(self, obj):
        return GetBidderSerializer(obj.task_bidders.all(), many=True).data

    
    def get_name_of_receiver(self, task_receiver):
        username = task_receiver.receiver.username
        return  username


def validate_image_size(image):
    """Validate that the image size is less than or equal to 1 MB."""
    max_size_mb = 1
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if image.size > max_size_bytes:
        raise serializers.ValidationError(f"Image size should not exceed {max_size_mb} MB.")


class AddImageToTaskSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, validators=[validate_image_size])
    
    class Meta:
        model = Task
        fields = ["image"]




class TaskSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField("get_name_of_sender")
    # url = serializers.HyperlinkedIdentityField(view_name='task-detail', lookup_field='id')
    # receiver_name = serializers.SerializerMethodField("get_name_of_receiver")
    # keywords = KeywordsSerializer()
    keywords = serializers.SerializerMethodField("get_actual_keyword")
    # task_bidders = serializers.SerializerMethodField("get_task_bidders")
    is_active = serializers.ReadOnlyField()
    completed = serializers.ReadOnlyField()
    paid = serializers.ReadOnlyField()
    category = serializers.StringRelatedField()
    images = TaskImageSerializer(many=True, read_only=True)
    # uploaded_images = serializers.ListField(
    #     child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False), write_only=True)
    # uploaded_images = serializers.ListField(
    #     child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
    #     write_only=True,
    #     required=False,  # Make the field optional
    #     allow_null=True, # Allow the field to be null
    #     default=[]      # Provide a default empty list if the field is not provided
    # )
    task_url = serializers.HyperlinkedIdentityField(
        view_name="task-detail",
        lookup_field = "id"
    )
    
    class Meta:
        model = Task
        fields = ["id", "task_url", "name", "description", "type", "tip", "pick_up", "deliver_to", "category", "image", "bidding_amount", "sender_name", "keywords", "is_active", "picked_up",  "completed", "paid", "images"]
 

    # def create(self, validated_data):
    #     if uploaded_images:
    #         uploaded_images = validated_data.pop("uploaded_images")
    #         task = Task.objects.create(**validated_data)
    #         for image in uploaded_images:
    #             TaskImages.objects.create(task=task, image=image)
    #     else:
    #         task = Task.objects.create(**validated_data)
    #     return task


    def get_name_of_sender(self, task_sender):
        username = task_sender.sender.username
        return username
    
    def get_actual_keyword(self, obj):
        return KeywordsSerializer(obj.keywords.all(), many=True).data
    
    # def get_task_bidders(self, obj):
    #     return GetBidderSerializer(obj.task_bidders.all(), many=True).data

    
    # def get_name_of_receiver(self, task_receiver):
    #     username = task_receiver.receiver.username
    #     return  username'''


class ShopTaskSerializer(serializers.ModelSerializer):
    more_details = serializers.SerializerMethodField("get_detail_of_tasks")
    class Meta:
        model = Task
        fields = ["id", "name", "more_details"]

    
    def get_detail_of_tasks(self, obj):
        return f"http://127.0.0.1:800/tasks/{obj.id}"

    
   
    

class ShopSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField("get_brief_info_of_tasks")
    subscribers = serializers.SerializerMethodField("get_subscribers_details")
    class Meta:
        model = Shop
        fields = ["name", "slug", "description", "location", "tasks", "subscribers", "rating"]

    def get_brief_info_of_tasks(self, obj:Shop):
        return ShopTaskSerializer(obj.tasks.all(), many=True).data
    
    def get_subscribers_details(self, obj):
        data = {}
        for subscriber in obj.subscribers.all():
            updated_dict = {"name": subscriber.username, "email": subscriber.email}
            data.update(updated_dict)
        return data



class TaskDetailSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField("get_name_of_sender")
    # url = serializers.HyperlinkedIdentityField(view_name='task-detail', lookup_field='id')
    # receiver_name = serializers.SerializerMethodField("get_name_of_receiver")
    # keywords = KeywordsSerializer()
    keywords = serializers.SerializerMethodField("get_actual_keyword")
    task_bidders = serializers.SerializerMethodField("get_task_bidder_details")
    task_url  = serializers.SerializerMethodField("generate_task_url")
    # task_bidders = serializers.SerializerMethodField("get_task_bidders")
    is_active = serializers.ReadOnlyField()
    completed = serializers.ReadOnlyField()
    paid = serializers.ReadOnlyField()
    status = serializers.SerializerMethodField("get_status")

    class Meta:
        model = Task
        fields = ["id", "name", "description", "image", "bidding_amount",  "sender", "sender_name", "keywords", "is_active", "task_bidders",  "completed", "paid", "task_url", "status"]


    def get_name_of_sender(self, task_sender):
        username = task_sender.sender.username
        return username
    
    def get_status(self, obj):
        current_time = timezone.now()
        time_difference = current_time - obj.date_updated
        time_difference_minutes = time_difference.total_seconds() // (60*60*24)
        return f"Posted {time_difference_minutes} days ago"
    
    def get_actual_keyword(self, obj):
        return KeywordsSerializer(obj.keywords.all(), many=True).data
    
    def get_task_bidder_details(self, obj):
        all_bidders = obj.task_bidders.all()
        for bidder in all_bidders:
            return bidder.user.username
        
    def generate_task_url(self, obj):
        return f"http://127.0.0.1:8000/tasks/{obj.id}"
    
    
    
    # def get_task_bidders(self, obj):
    #     return obj.task_bidders.all()
        # return GetBidderSerializer(obj.task_bidders.all(), many=True).data

    
    # def get_name_of_receiver(self, task_receiver):
    #     username = task_receiver.receiver.username
    #     return  username'''



class AcceptTaskSerializer(serializers.ModelSerializer):
    # receiver_name = serializers.SerializerMethodField("get_name_of_receiver")
    class Meta:
        model = AcceptTask

        fields = ["task", "receiver", "time_picked", "receiver_amount"]

    # def get_name_of_receiver(self, accepttask_receiver):
    #     username = accepttask_receiver.receiver.username
    #     return username


class TaskReviewSerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField("get_task_name")
    errander = serializers.SerializerMethodField("get_errander_name")
    class Meta:
        model = TaskReview

        fields = ['task', 'errander', 'errandee', 'comment', 'date_created']

    
    def get_task_name(self, obj:TaskReview):
        return obj.task.name
    
    def get_errander_name(self, obj):
        return obj.errander.username



class TaskRequestSerializer(serializers.ModelSerializer):
    '''
    This is to return a brief history of all tasks you have
    requested for on RUNAM...i.e you were the sender
    '''
    more_details = serializers.SerializerMethodField("generate_detail_link")
    bidding_amount = serializers.SerializerMethodField("add_naira_sign_to_bidding_amount")

    class Meta:
        model = Task
        fields = ["name", "more_details", "bidding_amount", "date_updated", "completed"]

    def generate_detail_link(self, obj):
        link = f"http://127.0.0.1:8000/tasks/{obj.id}"
        return link


    def add_naira_sign_to_bidding_amount(self, obj):
        sign =	u'\u20a6'
        new = f"{sign}{obj.bidding_amount}"
        return new
    


class MyTaskErrandSerializer(serializers.ModelSerializer):
    '''
    This is to return all tasks that a user has carried on
    i.e he was the messenger 
    '''
    class Meta:
        model = Task
        fields = ["name", "more_details", "bidding_amount", "date_updated", "completed"]

    def generate_detail_link(self, obj):
        link = f"http://127.0.0.1:8000/tasks/{obj.id}"
        return link


    def add_naira_sign_to_bidding_amount(self, obj):
        sign =	u'\u20a6'
        new = f"{sign}{obj.bidding_amount}"
        return new
    


class MyTotalEarningsSerializer(serializers.ModelSerializer):
    receiver_amount = serializers.SerializerMethodField("add_naira_sign_to_bidding_amount")
    class Meta:
        model = AcceptTask
        fields = ["receiver_amount"]

    def add_naira_sign_to_bidding_amount(self, obj):
        sign =	u'\u20a6'
        new = f"{sign}{obj.receiver_amount}"
        return new




    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)



class TaskSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ["category", "message", "date_created"]