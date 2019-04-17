import xadmin

from orders import models


class OrderAdmin(object):
    list_display = ['order_id', 'create_time', 'total_amount', 'pay_method', 'status']
    refresh_times = [3, 5]  # 可选以支持按多长时间(秒)刷新页面
    data_charts = {
        "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                         "order": ('create_time',)},
        "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }  # title 控制图标名称,x-field 控制x轴字段,y-field 控制y轴字段，可以是多个值,order 控制默认排序


xadmin.site.register(models.OrderInfo, OrderAdmin)
