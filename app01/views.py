from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01 import models
import json


# Create your views here.

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
        response['a_list'] = a_list

        # 帖子推荐列表，推荐8个帖子，推荐8个要改
        recommends = models.Topic.objects.filter(recommend=True)
        # 推荐列表
        r_list = []

        for t in recommends:
            dic = {'t_id': t.id, 't_title': t.t_title, 't_introduce': t.t_introduce, 't_photo': t.t_photo}
            r_list.append(dic)
        # 把列表装进response
        response['r_list'] = r_list

        response['uid'] = request.session['uid']

        return render(request, 'home.html', response)


def all_tie(request, kid, reply_limit, time_limit):
    if request.method == 'GET':
        kinds = models.Kind.objects.filter()
        if kid == 0 and reply_limit == 0 and time_limit == 0:
            # 默认时间排序把帖子传过去
            topics = models.Topic.objects.filter()
        else:
            topics = models.Topic.objects.filter()
            # 筛选分类
            topics.filter(t_kind=kid)

            # 筛选回复数量
            tmp = []
            for topic in topics:
                # 查看每个帖子的回复数量
                count = len(models.Reply.objects.filter(r_tid=topic.id))
                if reply_limit == 0:
                    pass
                elif reply_limit == 1:  # 1是大于100
                    if count < 100:
                        continue
                elif reply_limit == 2:  # 2是30-100
                    if count < 30 or count > 100:
                        continue
                elif reply_limit == 3:  # 3是小于30
                    if count > 30:
                        continue
                tmp.append(topic)
            topics = tmp

            # 筛选发布时间
            tmp = []
            for topic in topics:
                if time_limit == 0: # 0是全部时间
                    pass
                elif time_limit == 1:   # 1是1个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == 2:   # 2是3个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == 3:   # 3是6个月内
                    # 如果在限制之前，就筛掉
                    pass
                elif time_limit == 4:   # 4是1年内
                    # 如果在限制之前，就筛掉
                    pass
                tmp.append(topic)
            topics = tmp

        response = {
            'topics': topics,
            'kinds': kinds,
        }
        return render(request, 'all.html', response)

    elif request.method == 'POST':
        # 搜索接收一个字段，查询标题或者简介里有关键字的帖子
        keys = request.POST.get('keys')
        # 按关键字查询标题里含有关键字的
        topics = models.Topic.objects.filter(t_title__icontains=keys)
        return render(request, 'all.html', {'topics': topics})


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


def publish(request):
    if request.method == 'GET':
        name = []
        for kind in models.Kind.objects.filter():
            name.append(kind.k_name)
        response = {
            'kindnames': name
        }
        return render(request, 'publish.html', response)
    elif request.method == 'POST':
        # session获取uid
        uid = request.session['uid']
        # 提交发布的文章
        t_name = request.POST.get('t_name')
        t_introduce = request.POST.get('t_introduce')
        t_content = request.POST.get('t_content')
        t_kind = request.POST.get('t_kind')

        obj = models.Topic.objects.create(t_name=t_name, t_introduce=t_introduce,
                                          t_content=t_content, t_kind=t_kind, t_uid=uid)
        t_id = obj.id
        # 存帖子图片
        t_photo = request.FILES.get('t_photo', None)
        t_photo_path = 'static/img/t_photo/' + t_id + '_', t_photo.name
        if t_photo:
            # 保存文件
            import os
            f = open(os.path.join(t_photo_path), 'wb')
            for line in t_photo.chunks():
                f.write(line)
            f.close()

        # 吧图片路径存入数据库
        obj.save(t_photo=t_photo_path)

        return redirect('/single/' + t_id)


def single(request, tid):
    if request.method == 'GET':
        # 帖子内容
        # 时间类别作者，标题，正文，图片path
        topic = models.Topic.objects.get(id=tid)

        t_time = topic.create_time
        t_kind = topic.t_kind
        t_title = topic.t_title
        t_content = topic.t_content
        t_photo = topic.t_photo
        t_uid = topic.t_uid
        t_introduce = topic.t_introduce
        uid = request.session['uid']

        response = {
            't_uid': t_uid,
            't_time': t_time,
            't_kind': t_kind,
            't_title': t_title,
            't_content': t_content,
            't_photo': t_photo,
            't_introduce': t_introduce,
            'uid': uid,
        }

        # 留言内容
        # 留言者，留言时间，留言内容
        replys = models.Reply.objects.filter(r_tid=tid)
        reply_list = []
        for reply in replys:
            single_reply = {
                'r_uid': reply.r_uid,
                'r_time': reply.r_time,
                'r_content':reply.r_content,
            }
            reply_list.append(single_reply)
        response['reply_list'] = reply_list

        return render(request, 'single.html', response)
    elif request.method == 'POST':
        # 进行回复
        pass
