from celery_tasks.main import celery_app
from .yuntongxun.sms import CCP
from . import constants
import logging

logger = logging.getLogger('Django')


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """

    :param mobile: 手机号
    :param sms_code: 短信验证码
    """

    try:
        result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                         constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
