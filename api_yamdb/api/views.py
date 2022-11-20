from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from reviews.models import Category, Genre, Review, Title, User
from reviews.token_generator import confirmation_code
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentsSerializer,
                          GenreSerializer, ReadOnlyTitleSerializer,
                          ReviewSerializer, TitleSerializer,
                          UserCreateSerializer, UserSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация и получение confirmation_code"""

    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
        user_confirmation_code = confirmation_code.make_token(user)
        user.confirmation_code = user_confirmation_code
        user.is_active = True
        user.save()
        mail_subject = 'Confirm your email account.'
        message = f'user: {user}, confirmation_code: {user_confirmation_code}'
        user.email_user(mail_subject, message)

        return Response(serializer.data, status=200)

    return Response(serializer.errors, status=400)


class UserViewSet(viewsets.ModelViewSet):
    """Передает объекты модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['patch', 'get'], detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me', url_name='me',
    )
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            data = request.data

            if 'role' in data:
                data._mutable = True
                data.pop('role')
                data._mutable = False

            serializer = self.get_serializer(
                instance, data=data, partial=True
            )
            serializer.is_valid()
            serializer.save()

        return Response(serializer.data)


class CategoryViewSet(CreateListDestroyViewSet):
    """Передает объекты модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = IsAdminOrReadOnly,
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug')


class GenreViewSet(CreateListDestroyViewSet):
    """Передает объекты модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = IsAdminOrReadOnly,
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug')


class TitleViewSet(viewsets.ModelViewSet):
    """Передает объекты модели Title."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = IsAdminOrReadOnly,
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        queryset = Title.objects.annotate(
            rating=Avg('reviews__score')
        )

        return queryset

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):

            return ReadOnlyTitleSerializer

        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Передает объекты модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Передает объекты модели Comments."""

    serializer_class = CommentsSerializer
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )

        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)
