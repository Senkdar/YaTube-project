# Generated by Django 2.2.16 on 2022-07-15 20:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='введите текст', verbose_name='текст')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='дата публикации')),
                ('author', models.ForeignKey(on_delete='cascade', related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('post', models.ForeignKey(on_delete='cascade', related_name='comments', to='posts.Post', verbose_name='комменнтарий')),
            ],
            options={
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
                'ordering': ['-created'],
            },
        ),
    ]