import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号码格式错误')

        return value

    def validate_allow(self, value):
        """
        验证用户是否同意协议
        """
        if value != "true":
            raise serializers.ValidationError('请同意用户协议')

    def validate(self, attrs):
        """判断两次密码"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % attrs['mobile'])

        if not real_sms_code:
            raise serializers.ValidationError('无效的短信验证码')

        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """创建用户"""

        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)

        user.set_password(validated_data['password'])  # 自动设置密码属性

        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')

