from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow
from .serializers import (PasswordChangeSerializer, SubscribedUserSerializer,
                          SubscriptionWriteSerializer, UserCreateSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset_subscribed = User.objects.annotate_subscribed_flag(
            self.request.user
        )
        queryset_recipes_count = User.objects.annotate_recipes_count()
        return queryset_subscribed | queryset_recipes_count

    def create(self, request):
        creation_serializer = UserCreateSerializer(
            data=request.data
        )
        if creation_serializer.is_valid():
            user = creation_serializer.save()
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(creation_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(['post'], detail=False, permission_classes=[AllowAny])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
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

    @action(
        ['get', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if request.method == 'GET':
            serializer = SubscriptionWriteSerializer(
                data={'author': author.id, 'user': request.user.id}
            )
            if serializer.is_valid():
                serializer.save()
                subscribed_serializer = SubscribedUserSerializer(
                    author,
                    context={'request': request}
                )
                return Response(subscribed_serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Follow.objects.filter(
                    user=request.user,
                    author=author
            ).delete() != 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Вы уже отписаны от этого автора!'},
                            status=status.HTTP_400_BAD_REQUEST)
