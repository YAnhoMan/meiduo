from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData


# Create your models here.

class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 定义生成验证邮箱链接的方法

    def generate_verify_email_url(self):
        serializer = TJWSSerializer(
            settings.SECRET_KEY,
            expires_in=3600 * 24)

        data = {'user_id': self.id, 'email': self.email}

        token = serializer.dumps(data).decode()

        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """
        验证邮箱的token
        """
        serializer = TJWSSerializer(
            settings.SECRET_KEY,
            expires_in=3600 * 24)

        try:
            data = serializer.loads(token)
        except BadData:
            return None

        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user