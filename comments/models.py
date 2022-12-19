from django.db import models
from reports.models import Report
from users.models import User


class Comment(models.Model):
    send_date = models.DateTimeField(auto_now_add=True)
    report_id = models.ForeignKey(Report, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='getter')
    message = models.CharField(max_length=1000)
    comment_id = models.ForeignKey('Comment', null=True, on_delete=models.CASCADE)
