import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_opportunity_assigned_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='assigned_agent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_opportunities',
                to='api.agentprofile',
            ),
        ),
    ]
