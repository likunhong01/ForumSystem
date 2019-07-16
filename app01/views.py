from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01 import models
import json


# Create your views here.

# 主页
def home(request):
    if request.method == 'GET':
        response = {}

        # top 10（公告）的处理，筛选10个也要改
        announcements = models.Announcement.objects.filter()
        # 把这10个公告封装成字典
        a_list = []
        for a in announcements:
            dic = {'a_id': a.id, 'a_title': a.a_title}
            a_list.append(dic)
        # 把列表装进回复字典里
        n = 10 if len(a_list) < 10 else len(a_list)

        response['a_list'] = a_list[::-1][0:n-1]

        # 帖子推荐列表，推荐8个帖子，推荐8个要改
        recommends = models.Topic.objects.filter(recommend=True)
        # 推荐列表
        r_list = []

        for t in recommends:
            dic = {'t_id': t.id, 't_title': t.t_title, 't_introduce': t.t_introduce, 't_photo': t.t_photo}
            r_list.append(dic)
        # 把列表装进response
        response['r_list'] = r_list

        # 把uid装进返回字典里
        response['uid'] = request.session['uid']

        # 把所有类别装入返回字典里
        kinds = models.Kind.objects.filter()
        response['kinds'] = kinds

        return render(request, 'home.html', response)


# 所有帖子
def all_tie(request, kid, reply_limit, time_limit):
    uid = request.session.get('uid')
    if request.method == 'GET':
        kinds = models.Kind.objects.filter()
        if kid == '0' and reply_limit == '0' and time_limit == '0':
            # 默认时间排序把帖子传过去
            topics = models.Topic.objects.filter()
        else:
            # request.path_info   # 获取当前url
            # from django.urls import reverse
            # reverse('all_tie', kwargs={'kid': '0', 'reply_limit': '0', 'time_limit': '0'})

            topics = models.Topic.objects.filter()

            # 筛选分类
            if kid != '0':
                topics = models.Topic.objects.filter(t_kind=kid)

            # 筛选回复数量
            tmp = []
            for topic in topics:
                # 查看每个帖子的回复数量
                count = len(models.Reply.objects.filter(r_tid=topic.id))
                # print(count)
                print(reply_limit)
                if reply_limit == '0':
                    pass
                elif reply_limit == '1':  # 1是大于100
                    print('到1了')
                    if count < 100:
                        print('到了')
                        continue
                elif reply_limit == '2':  # 2是30-100
                    if count < 30 or count > 100:
                        continue
                elif reply_limit == '3':  # 3是小于30
                    if count > 30:
                        continue
                tmp.append(topic)
            topics = tmp
            print(topics)

            # 筛选发布时间
            tmp = []
            for topic in topics:
                if time_limit == '0': # 0是全部时间
                    pass
                elif time_limit == '1':   # 1是1个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == '2':   # 2是3个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == '3':   # 3是6个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == '4':   # 4是1年内
                    # 如果在限制之前，就筛掉
                    pass
                tmp.append(topic)
            topics = tmp

        response = {
            'topics': topics,
            'kinds': kinds,
            'kid': kid,
            'time_limit': time_limit,
            'reply_limit': reply_limit,
            'uid': uid,
        }
        return render(request, 'all.html', response)

    elif request.method == 'POST':
        # 搜索接收一个字段，查询标题或者简介里有关键字的帖子
        keys = request.POST.get('keys')
        # 按关键字查询标题里含有关键字的
        topics = models.Topic.objects.filter(t_title__icontains=keys)

        kinds = models.Kind.objects.filter()
        return render(request, 'all.html', {'topics': topics, 'kinds': kinds, 'uid': uid})


# 登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        # 验证用户名密码是否正确，然后登陆存入session
        type = request.POST.get('type')
        response = {'msg': '', 'status': False}

        uid = request.POST.get('uid')
        pwd = request.POST.get('pwd')
        if type == 'login':
            if len(models.User.objects.filter(uid=uid, password=pwd)) != 0:
                # 登录成功
                response['status'] = True
                request.session['uid'] = uid
                return HttpResponse(json.dumps(response))
                pass
            else:
                # 登录失败
                response['msg'] = '用户名或者密码错误'
                return HttpResponse(json.dumps(response))
                pass
        elif type == 'register':
            models.User.objects.create(uid=uid, password=pwd)
            response['status'] = True
            request.session['uid'] = uid
            return HttpResponse(json.dumps(response))


# 注册
def register(request):
    if request.method == 'POST':
        # 判断是否已有
        uid = request.POST.get('uid')
        pwd = request.POST.get('pwd')
        if len(models.User.objects.filter(uid=uid)) != 0:
            # 已被创建，返回错误
            return render(request, 'login.html', {'message': '用户名已被创建'})
        else:
            # 插入数据
            user = {
                'uid': uid,
                'password': pwd,
            }
            models.User.objects.create(**user)
            return redirect('/home')


# 发布页
def publish(request):
    if request.method == 'GET':
        kinds = models.Kind.objects.filter()
        response = {
            'kinds': kinds
        }
        return render(request, 'publish.html', response)
    elif request.method == 'POST':
        # session获取uid
        uid = request.session['uid']
        # 提交发布的文章
        t_title = request.POST.get('t_title')
        t_introduce = request.POST.get('t_introduce')
        t_content = request.POST.get('t_content')
        t_kind = request.POST.get('t_kind')
        print(t_title, t_introduce)

        obj = models.Topic.objects.create(t_title=t_title, t_introduce=t_introduce,
                                          t_content=t_content, t_kind=t_kind, t_uid=uid)
        t_id = obj.id

        # 存帖子图片
        t_photo = request.FILES.get('t_photo', None)
        t_photo_path = 'static/img/t_photo/' + str(t_id) + '_' + t_photo.name

        if t_photo:
            # 保存文件
            import os
            f = open(os.path.join(t_photo_path), 'wb')
            for line in t_photo.chunks():
                f.write(line)
            f.close()

        # 吧图片路径存入数据库
        models.Topic.objects.filter(id=t_id).update(t_photo='/'+t_photo_path)

        return redirect('/single/' + str(t_id))


# 单个帖子页面
def single(request, tid):
    if request.method == 'GET':
        # 帖子内容
        # 时间类别作者，标题，正文，图片path
        try:
            topic = models.Topic.objects.get(id=tid)
        except Exception as e:
            return redirect('/home')

        t_time = topic.create_time
        t_kind = topic.t_kind
        t_title = topic.t_title
        t_content = topic.t_content
        t_photo = topic.t_photo
        t_uid = topic.t_uid
        t_introduce = topic.t_introduce
        uid = request.session['uid']
        admin_uid = request.session.get('admin_uid')

        response = {
            'tid': tid,
            't_uid': t_uid,
            't_time': t_time,
            't_kind': t_kind,
            't_title': t_title,
            't_content': t_content,
            't_photo': t_photo,
            't_introduce': t_introduce,
            'uid': uid,
            'admin_uid': admin_uid,
        }

        # 留言内容
        # 留言者，留言时间，留言内容
        replys = models.Reply.objects.filter(r_tid=tid)
        reply_list = []
        for reply in replys:
            single_reply = {
                'r_uid': reply.r_uid,
                'r_time': reply.r_time,
                'r_content': reply.r_content,
                'r_id': reply.id,
                'r_photo': reply.r_photo,
            }
            reply_list.append(single_reply)
        response['reply_list'] = reply_list

        return render(request, 'single.html', response)

    elif request.method == 'POST':
        # 判断是否登录
        uid = request.session.get('uid')

        # 删除回复，管理员才可以删除
        p_type = request.POST.get('type')
        print(p_type)
        if p_type == 'delete':
            response = {'msg': '', 'status': False}
            r_id = request.POST.get('r_id')
            models.Reply.objects.filter(id=r_id).delete()
            response['status'] = True
            return HttpResponse(json.dumps(response))

        if not uid:
            return redirect('/login')
        # 进行回复
        r_content = request.POST.get('r_content')

        # 提交数据库
        obj = models.Reply.objects.create(r_tid=tid,r_uid=uid,r_content=r_content)

        r_id = str(obj.id)
        r_photo = request.FILES.get('r_photo')
        r_photo_path = ''
        if r_photo:
            # 保存文件
            r_photo_path = 'static/img/r_photo/' + r_id + '_' + r_photo.name
            import os
            f = open(os.path.join(r_photo_path), 'wb')
            for line in r_photo.chunks():
                f.write(line)
            f.close()

        # 吧图片路径存入数据库
        models.Reply.objects.filter(id=r_id).update(r_photo='/'+r_photo_path)
        return redirect('/single/' + tid)


# 修改密码页面
def edit_pwd(request):
    if request.method == 'GET':
        uid = request.session.get('uid')
        return render(request, 'edit-pwd.html', {'uid': uid})

    if request.method == 'POST':
        uid = request.session.get('uid')
        old = request.POST.get('old_pwd')
        new1 = request.POST.get('new_pwd1')
        new2 = request.POST.get('new_pwd2')
        if new1 == new2 and len(models.User.objects.filter(uid=uid, password=old)) != 0:
            # 核对成功，修改密码
            models.User.objects.filter(uid=uid).update(password=new1)
        return redirect('/home')


# 管理员登录
def admin(request):
    if request.method == 'GET':
        return render(request, 'admin.html')
    elif request.method == 'POST':
        admin_uid = request.POST.get('admin_id')
        admin_pwd = request.POST.get('admin_pwd')

        response = {'msg': '', 'status': False}

        if admin_uid == 'guanliyuan' and admin_pwd == '123456':
            # 管理员登录成功
            response['status'] = True
            request.session['admin_uid'] = 'guanliyuan'
            return HttpResponse(json.dumps(response))
        else:
            response['msg'] = '用户名或者密码错误'
            return HttpResponse(json.dumps(response))


# 公告管理
def announcement(request):
    if not request.session.get('admin_uid'):
        return redirect('/my-admin')

    # 查询所有公告
    if request.method == 'GET':

        announcements = models.Announcement.objects.filter()
        response = {'announcements': announcements}
        return render(request, 'announcement.html', response)

    # 发公告，删公告
    elif request.method == 'POST':
        p_type = request.POST.get('type')
        response = {'msg': '', 'status': False}
        if p_type == 'delete':
            a_id = request.POST.get('a_id')
            models.Announcement.objects.filter(id=a_id).delete()
            response['status'] = True
        elif p_type == 'create':
            # 添加一条公告
            a_title = request.POST.get('a_title')
            a_content = request.POST.get('a_content')
            models.Announcement.objects.create(a_title=a_title, a_content=a_content)
            response['status'] = True
        return HttpResponse(json.dumps(response))


# 帖子管理：标题，简介，时间，
def topic_manage(request):
    if not request.session.get('admin_uid'):
        return redirect('/my-admin')

    if request.method == 'GET':
        topics = models.Topic.objects.filter()
        response = {
            'topics': topics,
        }
        return render(request, 'admin-home.html', response)
    elif request.method == 'POST':
        p_type = request.POST.get('type')
        response = {'msg': '', 'status': False}
        print(p_type)
        # 删除帖子
        if p_type == 'delete':
            t_id = request.POST.get('t_id')
            models.Topic.objects.filter(id=t_id).delete()
            response['status'] = True
        # 置顶（推荐）
        if p_type == 'zhiding':
            print('置顶')
            t_id = request.POST.get('t_id')
            models.Topic.objects.filter(id=t_id).update(recommend=True)
            response['status'] = True
        # 取消置顶（推荐）
        if p_type == 'qzhiding':
            t_id = request.POST.get('t_id')
            models.Topic.objects.filter(id=t_id).update(recommend=False)
            response['status'] = True
        return HttpResponse(json.dumps(response))


# 类别管理（板块管理）
def kind_manage(request):
    # 验证登录
    if not request.session.get('admin_uid'):
        return redirect('/my-admin')

    if request.method == 'GET':
        # get返回所有类别（板块）
        kinds = models.Kind.objects.filter()
        response = {
            'kinds': kinds,
        }
        return render(request, 'kind-manage.html', response)
    if request.method == 'POST':
        p_type = request.POST.get('type')
        response = {'msg': '', 'status': False}
        # 删除类别
        if p_type == 'delete':
            k_id = request.POST.get('k_id')
            models.Kind.objects.filter(id=k_id).delete()
            response['status'] = True

        # 添加类别
        if p_type == 'create':
            k_name = request.POST.get('k_name')
            models.Kind.objects.create(k_name=k_name)
            response['status'] = True

        return HttpResponse(json.dumps(response))


# 公告页面
def single_an(request, aid):
    if request.method == 'GET':
        try:
            an = models.Announcement.objects.get(id=aid)
        except Exception as e:
            return '/home'
        a_title = an.a_title
        a_content = an.a_content

        response = {
            'a_title': a_title,
            'a_content': a_content,
        }
        return render(request, 'single-an.html', response)
