from rest_framework import status, viewsets, mixins
from django.shortcuts import get_object_or_404
from rest_framework import pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser, Follow
from .serializers import UserSerializer, PasswordChangeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(['post'], detail=False, permission_classes=[IsAuthenticated])
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
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = request.user.follower.all()
        authors = []
        for follow in subscriptions:
            authors.append(follow.author)
        serializer = UserSerializer(authors, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])    
def subscribe(request, id):
    if request.method == 'GET':
        author = get_object_or_404(CustomUser, id=id)
        if request.user != author:
            if Follow.objects.filter(user=request.user,
                                     author=author
            ).count() == 0:
                Follow.objects.create(user=request.user,
                                      author=author)
                author = get_object_or_404(CustomUser, id=id)
                serializer = UserSerializer(author, context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Вы уже подписаны на этого автора!'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': 'Нельзя подписаться на самого себя!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        author=get_object_or_404(CustomUser, id=id)
        if Follow.objects.filter(user=request.user,
                                 author=author
        ).count() > 0:        
            Follow.objects.filter(
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы уже отписаны от этого автора!'},
                        status=status.HTTP_400_BAD_REQUEST)
