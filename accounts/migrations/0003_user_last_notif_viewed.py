from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_assigned_telescopes'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_notif_viewed',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Last time user viewed their notifications. Used to compute unseen count.'
            ),
        ),
    ]
