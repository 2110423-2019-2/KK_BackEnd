from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import *


invalid_input = Response(
    {'message': 'Cannot create user, please recheck input fields'},
    status=status.HTTP_400_BAD_REQUEST,
)


def check_arguments(request, args):
    # check for missing arguments
    missing = []
    for arg in args:
        if arg not in request.data:
            missing.append(arg)
    if missing:
        print(missing)
        response = {
            'Missing argument': '%s' % ', '.join(missing),
        }
        return 1, Response(response, status=status.HTTP_400_BAD_REQUEST)
    return 0,


def create_log(user, desc):
    Log.objects.create(user=user, desc=desc)


class UserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all()
    serializer_class = ExtendedUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = [IsAdminUser]

    def create(self, request):
        response = check_arguments(request, [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        ])
        if response[0] != 0:
            return response[1]

        username = request.data['username']
        password = request.data['password']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        phone_number = request.data['phone_number']
        try:
            User.objects.get(username=username)
            return Response(
                {'message': 'A user with identical username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            base_user = User.objects.create(username=username, password=password,
                                            first_name=first_name, last_name=last_name,
                                            email=email)
        try:
            base_user.full_clean()
            extended_user = ExtendedUser.objects.create(
                base_user=base_user, phone_number=phone_number)
            extended_user.full_clean()
        except ValidationError:
            base_user.delete()
            return invalid_input
        Token.objects.create(user=base_user)
        create_log(user=base_user,
                   desc="User %s has been created" % base_user.username)
        return Response(
            {
                'message': 'A user has been created',
                'result': ExtendedUserSerializer(extended_user, many=False).data,
            },
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        try:
            user = queryset.get(username=pk).extended
            serializer_class = ExtendedUserSerializer
            return Response(
                serializer_class(user, many=False).data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=['POST'], detail=True)
    def change_password(self, request, pk=None):
        response = check_arguments(request, ['password', ])
        if response[0] != 0:
            return response[1]

        queryset = User.objects.all()
        serializer_class = ExtendedUserSerializer
        username = pk
        password = request.data['password']

        try:
            user = queryset.get(username=username)
            user.set_password(password)
            user.save()
            return Response(
                {
                    'message': 'Password has been set',
                    'result': serializer_class(user.extended, many=False).data
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

    # TODO passwordRequestForm


class UserLogViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLogSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    authentication_classes = (TokenAuthentication,)

    def create(self, request):
        response = check_arguments(request, ['url'])
        if response[0] != 0:
            return response[1]

        url = request.data['url']
        user = request.user
        try:
            Document.objects.get(url=url)
            return Response(
                {'message': 'A document with the same url already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            try:
                document = Document.objects.create(user=user, url=url)
                document.full_clean()
                create_log(
                    user=user,
                    desc='User %s has been created' % user.username,
                )
                return Response(
                    {
                        'message': 'A user has been created',
                        'result': DocumentSerializer(document, many=False).data,
                    },
                    status=status.HTTP_200_OK
                )
            except:
                return Response(
                    {'message': 'invalid url'},
                    status.HTTP_400_BAD_REQUEST,
                )

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        try:
            document = queryset.get(username=pk).documents
            serializer_class = DocumentSerializer
            return Response(
                serializer_class(document, many=False).data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    authentication_classes = (TokenAuthentication,)

    @action(detail=True, methods=['POST'], )
    def rate_court(self, request, pk=None):
        response = check_arguments(request, ['score', 'review'])
        if response[0] != 0:
            return response[1]

        user = request.user
        court = Court.objects.get(id=pk)
        score = int(request.data['score'])
        review_text = request.data['review']

        try:
            review = Review.objects.get(user=user, court=court)
            review.score = score
            review.review = review_text
            review.save()
            review.full_clean()
            message = 'Review updated'
            create_log(
                user=user,
                desc='User %s has update the review for court %s'
                     % (user.username, court.name,)
            )
        except ValidationError:
            return invalid_input
        except:
            review = Review.objects.create(user=user, court=court,
                                           score=score, review=review_text, )
            message = 'Review created'
            create_log(
                user=user,
                desc='User %s has create a review for court %s'
                     % (user.username, court.name,)
            )
        return Response(
            {
                'message': message,
                'result': ReviewSerializer(review, many=False).data,
            },
            status=status.HTTP_200_OK
        )

    def create(self, request):
        response = check_arguments(request, ['name', 'price', 'desc'])
        if response[0] != 0:
            return response[1]

        user = request.user
        name = request.data['name']
        price = int(request.data['price'])
        desc = request.data['desc']
        try:
            Court.objects.get(name=name)
            return Response(
                {'message': 'A court with the same name already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            court = Court.objects.create(owner=user, price=price, name=name, desc=desc, )
            create_log(
                user=user,
                desc='User %s create court %s' % (user.username, name,))
            return Response(
                {
                    'message': 'A court has been created',
                    'result': CourtSerializer(court, many=False).data,
                },
                status=status.HTTP_200_OK
            )
