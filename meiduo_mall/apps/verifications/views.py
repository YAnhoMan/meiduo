import logging
import random

from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.apps.verifications import constants
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.
from meiduo_mall.utils.captcha.captcha import captcha

logger = logging.getLogger('Django')


class SMSCodeView(APIView):

    def get(self, request, mobile):
        # 1.生成验证码
        # 2.创建redis连接对象
        # 3.存储验证码
        # 4.利用容联云发送验证码
        # 5.返回状态

        #  获取redis对象
        redis_conn = get_redis_connection('verify_codes')

        #  60秒内不允许重发发送短信
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        # 图片验证码验证
        image_code = request.query_params.get('text')
        image_code_id = request.query_params.get('image_code_id')

        if image_code_id:

            real_image_code = redis_conn.get("image_code_%s" % image_code_id)

            if real_image_code:
                # 如果能够取出来值，删除redis中缓存的内容
                real_image_code = real_image_code.decode()
                redis_conn.delete("image_code_%s" % image_code_id)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if image_code.lower() != real_image_code.lower():
                # 验证码输入错误
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if send_flag:
            return Response({'message': '发送短信太过频繁'}, status=status.HTTP_400_BAD_REQUEST)


        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        print(sms_code)
        logger.debug(sms_code)

        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行
        pl.execute()

        send_sms_code.delay(mobile, sms_code)

        return Response({'message': 'OK'})


class ImageCode(APIView):
    """获取图片验证码"""
    def get(self,request,image_code_id):
        name,text,image = captcha.generate_captcha()
        redis_conn = get_redis_connection("verify_codes")
        try:
            redis_conn.setex("image_code_%s" % image_code_id, 300 , text.lower())
        except Exception:
            return Response({"message":"图片验证码储存出错"})

        return HttpResponse(image, content_type='img/png')


