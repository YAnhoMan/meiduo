from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.sms.yuntongxun import constants
from celery_tasks.main import celery_app


@celery_app.task(name='')
def send_sms_code(mobile, sms_code):
    """

    :param mobile: 手机号
    :param sms_code: 短信验证码
    """
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                            constants.SEND_SMS_TEMPLATE_ID)
