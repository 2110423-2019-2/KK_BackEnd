from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import *

err_invalid_input = Response(
    {'message': 'Cannot create user, please recheck input fields'},
    status=status.HTTP_400_BAD_REQUEST,
)
err_no_permission = Response(
    {'message': 'You do not have permission to perform this action'},
    status=status.HTTP_403_FORBIDDEN,
)
err_not_found = Response(
    {'message': 'Not found'},
    status=status.HTTP_404_NOT_FOUND,
)
err_not_allowed = Response(
    {'message': 'Operation Not Allowed'},
    status=status.HTTP_405_METHOD_NOT_ALLOWED
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

    def create(self, request):
        if not request.user.is_staff:
            return err_no_permission
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
            base_user = User.objects.create_user(username=username, password=password,
                                                 first_name=first_name, last_name=last_name,
                                                 email=email)
        try:
            base_user.full_clean()
            extended_user = ExtendedUser.objects.create(
                base_user=base_user, phone_number=phone_number)
            extended_user.full_clean()
        except ValidationError:
            base_user.delete()
            return err_invalid_input
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

    def list(self, request):
        if not request.user.is_staff:
            return err_no_permission
        queryset = ExtendedUser.objects.all()
        serializer_class = ExtendedUserSerializer
        return Response(serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        if pk != request.user.username and not request.user.is_staff:
            return err_no_permission
        queryset = User.objects.all()
        try:
            user = queryset.get(username=pk).extended
            serializer_class = ExtendedUserSerializer
            return Response(
                serializer_class(user, many=False).data,
                status=status.HTTP_200_OK
            )
        except:
            return err_not_found

    @action(methods=['POST'], detail=True)
    def change_password(self, request, pk=None):
        if pk != request.user.username and not request.user.is_staff:
            return err_no_permission
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
            return err_not_found

    @action(methods=['POST'], detail=True)
    def add_credit(self, request, pk=None):
        response = check_arguments(request, ['amount'])
        if response[0] != 0:
            return response[1]
        if not request.user.is_staff:
            return err_no_permission

        amount = int(request.data['amount'])
        if amount < 0:
            return Response(
                {'message': 'amount cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.get(username=pk)
        user.extended.credit += amount
        user.extended.save()
        create_log(user=user, desc='Admin %s add %d credit to user %s'
                                   % (request.user.username, amount, user.username))
        serializer_class = ExtendedUserSerializer
        return Response(
            {
                'message': 'credit added',
                'result': serializer_class(user.extended, many=False).data
            },
            status=status.HTTP_200_OK
        )

    # TODO passwordRequestForm


class LogViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLogSerializer

    def list(self, request):
        if request.user.is_staff:
            queryset = User.objects.all()
            serializer_class = UserLogSerializer
            return Response(serializer_class(queryset, many=True).data,
                            status=status.HTTP_200_OK, )
        try:
            queryset = request.user.logs
            serializer_class = LogSerializer
            return Response(serializer_class(queryset, many=True).data,
                            status=status.HTTP_200_OK, )
        except:
            return Response({'message': 'No log with your username is found'},
                            status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        if pk != request.user.username and not request.user.is_staff:
            return err_no_permission
        queryset = User.objects.get(username=pk).logs
        serializer_class = LogSerializer
        return Response(serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)

    def create(self):
        return err_not_allowed


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

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
            pass
        try:
            document = Document.objects.create(user=user, url=url)
            document.full_clean()
            create_log(
                user=user,
                desc='User %s has upload a document url: %s'
                     % (user.username, url,),
            )
            return Response(
                {
                    'message': 'The document has been uploaded',
                    'result': DocumentSerializer(document, many=False).data,
                },
                status=status.HTTP_200_OK
            )
        except:
            document.delete()
            return Response(
                {'message': 'invalid url'},
                status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, pk=None):
        if pk != request.user.username and not request.user.is_staff:
            return err_no_permission
        try:
            queryset = User.objects.all()
            document = queryset.get(username=pk).documents
            serializer_class = DocumentSerializer
            return Response(
                serializer_class(document, many=True).data,
                status=status.HTTP_200_OK
            )
        except:
            return err_not_found

    def list(self, request):
        if not request.user.is_staff:
            return err_no_permission
        queryset = User.objects.all()
        serializer_class = UserDocumentSerializer
        return Response(serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    @action(detail=True, methods=['POST'], )
    def rate_court(self, request, pk=None):
        response = check_arguments(request, ['score', 'review'])
        if response[0] != 0:
            return response[1]

        user = request.user
        court = Court.objects.get(name=pk)
        score = int(request.data['score'])
        review_text = request.data['review']

        if user == court.owner:
            return Response(
                {'message': 'You cannot rate your own court'},
                status=status.HTTP_403_FORBIDDEN
            )

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
            return err_invalid_input
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

    @action(detail=True, methods=['POST'], )
    def add_image(self, request, pk=None):
        try:
            court = Court.objects.get(name=pk)
        except:
            return err_not_found
        if request.user.username != court.owner and not request.user.is_staff:
            return err_no_permission
        response = check_arguments(request, ['url'])
        if response[0] != 0:
            return response[1]

        url = request.data['url']
        try:
            Image.objects.get(url=url)
            return Response(
                {'message': 'An image with the same url already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except:
            try:
                image = Image.objects.create(url=url, court=court)
                image.full_clean()
                create_log(user=request.user,
                           desc='User %s has upload an image url %s to court %s'
                                % (request.user.username, url, court.name,))
                serializer_class = ImageSerializer
                return Response(
                    {
                        'message': 'The image has been uploaded',
                        'result': serializer_class(image, many=False).data
                    },
                    status=status.HTTP_200_OK,
                )
            except:
                image.delete()
                return err_invalid_input

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

    def retrieve(self, request, pk=None):
        try:
            court = Court.objects.get(name=pk)
        except:
            return err_not_found
        try:
            court.owner.extended.ban_list.get(username=request.user.username)
            return err_no_permission
        except:
            pass
        if not request.user.is_staff:
            return err_no_permission
        serializer_class = CourtSerializer
        return Response(serializer_class(court, many=False).data,
                        status=status.HTTP_200_OK, )

    def list(self, request):
        if request.user.is_staff:
            queryset = Court.objects.all()
            serializer_class = CourtSerializer
            return Response(serializer_class(queryset, many=True).data,
                            status=status.HTTP_200_OK)

        queryset = Court.objects.exclude(
            owner__extended__ban_list__contains=request.user)
        serializer_class = CourtSerializer
        return Response(serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)
