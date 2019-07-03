from django.db import models


# Create your models here.

# 用户表
class User(models.Model):
    uid = models.CharField(verbose_name='电话/用户号', max_length=16, unique=True)
    password = models.CharField(verbose_name='密码', max_length=16)
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)


# 帖子表
class Topic(models.Model):
    # t_id = models.CharField(verbose_name='帖子id', max_length=16)
    t_uid = models.CharField(verbose_name='帖子所属用户id', max_length=16)
    t_kind = models.CharField(verbose_name='类别', max_length=32)
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)
    t_photo = models.CharField(verbose_name='帖子图片', max_length=128, null=True)
    t_content = models.CharField(verbose_name='帖子正文', max_length=3000)
    t_title = models.CharField(verbose_name='帖子标题', max_length=64)
    t_introduce = models.CharField(verbose_name='帖子简介', max_length=256)
    recommend = models.BooleanField(verbose_name='是否推荐', default=False)


# 回复表
class Reply(models.Model):
    r_tid = models.CharField(verbose_name='帖子id', max_length=16)
    r_uid = models.CharField(verbose_name='发表者id', max_length=16)
    r_photo = models.CharField(verbose_name='回复的图片', max_length=128, null=True)
    r_time = models.DateField(verbose_name='留言时间', auto_now_add=True)
    r_content = models.CharField(verbose_name='回复内容', max_length=256)


# 分类表
class Kind(models.Model):
    # k_id = models.CharField(verbose_name='分类id', max_length=16)
    k_name = models.CharField(verbose_name='分类名称', max_length=16)


# 公告表
class Announcement(models.Model):
    # a_id = models.CharField(verbose_name='公告id', max_length=16)
    a_title = models.CharField(verbose_name='公告标题', max_length=64)
    a_content = models.CharField(verbose_name='公告内容', max_length=3000, null=True)
