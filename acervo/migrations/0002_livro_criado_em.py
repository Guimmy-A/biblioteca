import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acervo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='livro',
            name='criado_em',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddIndex(
            model_name='livro',
            index=models.Index(fields=['criado_em'], name='livro_criado_em_idx'),
        ),
    ]
