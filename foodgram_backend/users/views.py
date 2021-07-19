from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow
from .serializers import (PasswordChangeSerializer, SubscribedUserSerializer, SubscriptionSerializer,
                          UserSerializer)

user = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = user.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        try:
            new_user = user.objects.create_user(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                email=request.data['email'],
                username=request.data['username'],
                password=request.data['password']
            )
            serializer = UserSerializer(new_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(['post'], detail=False, permission_classes=[AllowAny])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            current_password = serializer.data['current_password']
            if not self.request.user.check_password(current_password):
                return Response(
                    {'current_password': 'Введенный пароль неправильный'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = request.user.follower.all().values_list('author')
        queryset = user.objects.filter(id__in=subscriptions)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribedUserSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribedUserSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


# TODO
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, id):
    author = get_object_or_404(user, id=id)
    if request.method == 'GET':
        if request.user != author:
            serializer = SubscriptionSerializer(user=request.user,
                                                author=author)
            if serializer.is_valid():
                serializer.save()
                serializer = SubscribedUserSerializer(
                    author,
                    context={'request': request}
                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        return Response({'errors': 'Нельзя подписаться на самого себя!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if Follow.objects.filter(
                user=request.user,
                author=author
        ).delete() != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы уже отписаны от этого автора!'},
                        status=status.HTTP_400_BAD_REQUEST)
