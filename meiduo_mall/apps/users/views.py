from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from goods.serializers import SKUSerializer
from users.models import User

from users import constants
from users.serializers import CreateUserSerializer, UserDetailSerializer, UserAddressSerializer, AddressTitleSerializer, \
    AddUserBrowsingHistorySerializer,ResetPasswordSerializer

from users.serializers import EmailSerializer


class UserView(CreateAPIView):
    """
    用户注册
    """

    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    """用户名数量"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """手机号数量"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserDetail(RetrieveAPIView):
    """
    用户个人信息
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    """
    邮箱验证
    """

    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class UserBrowsingHistoryView(CreateAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user_id = request.user.id

        redis_conn = get_redis_connection("history")
        history = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)
        skus = []
        # 为了保持查询出的顺序与用户的浏览历史保存顺序一致
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        s = SKUSerializer(skus, many=True)
        return Response(s.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """
    用户认证
    """

    def post(self, request, *args, **kwargs):
        # 调用父类的方法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)

        # 仿照drf jwt扩展对于用户登录的认证方式，判断用户是否认证登录成功
        # 如果用户登录认证成功，则合并购物车
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)
        return response


class ResetPassword(APIView):
    """修改密码  """""

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({'message': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = request.data

        print(data_dict)
        # {'old_password': '496736yl', 'password': '11111111', 'password2': '11111111'}

        serializer = ResetPasswordSerializer(data=data_dict)
        serializer.is_valid(raise_exception=True)
        # 1.对输入的旧密码进行判断
        # print('旧密码　１　%s'%user.password)
        # print('旧密码　２　%s' %data_dict.get('old_password'))
        old_password = data_dict.get('old_password')
        # print("old%s"%old_password)
        if not user.check_password(old_password):
            return Response({'message': '当前密码输入错误哦'}, status=status.HTTP_400_BAD_REQUEST)

        # 2.修改密码
        new_password = data_dict.get('password')
        print(new_password)
        user.set_password(new_password)
        user.save()

        # 响应
        return Response({'message': 'ok'}, status=status.HTTP_200_OK)
