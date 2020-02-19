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


def check_arguments(request_arr, args):
    # check for missing arguments
    missing = []
    for arg in args:
        if arg not in request_arr:
            missing.append(arg)
    if missing:
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
        response = check_arguments(request.data, [
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
        response = check_arguments(request.data, ['password', ])
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
        response = check_arguments(request.data, ['amount'])
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

    @action(methods=['GET'], detail=True)
    def courts(self, request, pk=None):
        user = User.objects.get(username=pk)

        court = Court.objects.filter(owner=user)
        serializer_class = CourtSerializer
        if len(court) == 0:
            return err_not_found
        return Response(
            serializer_class(court, many=True).data,
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
        response = check_arguments(request.data, ['url'])
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
    def book(self, request, pk=None):
        response = check_arguments(request.data, ['start', 'end'])
        if response[0] != 0:
            return response[1]

        start = request.data['start']
        end = request.data['end']
        user = request.user
        try:
            court = Court.objects.get(name=pk)
        except:
            return err_not_found
        if user.extended.credit < court.price:
            return Response(
                {'message': 'not enough credit'},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        if court.check_collision(start, end) != 0:
            return Response(
                {'message': 'court is not free'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if court.book(start, end) != 0:
            return Response(
                {'message': 'court could not be booked'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {'message': 'court has been booked'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['POST'], )
    def rate_court(self, request, pk=None):
        response = check_arguments(request.data, ['score', 'review'])
        if response[0] != 0:
            return response[1]

        user = request.user
        try:
            court = Court.objects.get(name=pk)
        except:
            return err_not_found
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
        response = check_arguments(request.data, ['url'])
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
        response = check_arguments(request.data, ['name', 'price', 'desc', 'lat', 'long', ])
        if response[0] != 0:
            return response[1]

        user = request.user
        name = request.data['name']
        price = int(request.data['price'])
        desc = request.data['desc']
        lat = float(request.data['lat'])
        long = float(request.data['long'])

        try:
            Court.objects.get(name=name)
            return Response(
                {'message': 'A court with the same name already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            court = Court.objects.create(owner=user, price=price, name=name,
                                         desc=desc, lat=lat, long=long, )
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
        queryset = Court.objects.all()

        name = request.GET.get('name', '')
        min_rating = float(request.GET.get('rating', 0))
        max_dist = float(request.GET.get('dist', 999))
        lat = float(request.GET.get('lat', 0))
        long = float(request.GET.get('long', 0))
        sort_by = request.GET.get('sort_by', 'name')

        if max_dist < 999 or sort_by == 'dist' or sort_by == '-dist':
            response = check_arguments(request.GET, ['lat', 'long', ])
            if response[0] != 0:
                return response[1]

        if not request.user.is_staff:
            queryset = Court.objects.exclude(
                owner__extended__ban_list__contains=request.user)

        if name != '':
            queryset = queryset.filter(name__contains=name)
        if min_rating > 0:
            queryset = [court for court in queryset if court.avg_score() >= min_rating]
        if max_dist < 999:
            queryset = [court for court in queryset if
                        (court.lat - lat) ** 2 + (court.long - long) ** 2 <= max_dist ** 2]

        reverse = False
        if sort_by[0] == '-':
            reverse = True
            sort_by = sort_by[1:]

        if sort_by == 'dist':
            sorted(queryset, key=lambda x: (x.lat - lat) ** 2 + (x.long - long) ** 2)
        elif sort_by == 'rating':
            sorted(queryset, key=lambda x: x.avg_rating(), reverse=True)
        elif sort_by == 'name':
            sorted(queryset, key=lambda x: x.name, reverse=reverse)

        serializer_class = CourtSerializer
        return Response(serializer_class(queryset, many=True).data,
                        status=status.HTTP_200_OK)
