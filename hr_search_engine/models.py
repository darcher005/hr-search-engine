from django.db import models


class Products(models.Model):
    code = models.CharField(max_length=30)

    def _get_full_name(self):  # 注意此处，很重要，通过加入full_name这一属性，完成了与JS的数据对接
        return self.name

    full_name = property(_get_full_name)
