from rest_framework import serializers, viewsets, permissions
from rest_framework.generics import CreateAPIView
from .models import Note
from django.contrib.auth.models import User

class NoteSerializer(serializers.HyperlinkedModelSerializer):

  def create(self, validated_data):
    # import pdb; pdb.set_trace()
    user = self.context['request'].user

    note = Note.objects.create(user=user, **validated_data)
    return note

  class Meta:
    model = Note
    fields = ('title', 'content')

class NoteViewSet(viewsets.ModelViewSet):
  serializer_class = NoteSerializer
  queryset = Note.objects.all()

  def get_queryset(self):
    user = self.request.user

    if user.is_anonymous:
      return Note.objects.none()
    else:
      return Note.objects.filter(user=user)

class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  def create(self, validated_data):

    user = User.objects.create(username=validated_data['username'])
    user.set_password(validated_data['password'])

    return user

  class Meta:
    model = User
    fields = ('username', 'password')

class CreateUserView(CreateAPIView):
  model = User
  permissions_classes = [ permissions.AllowAny ]
  serializer_class = UserSerializer