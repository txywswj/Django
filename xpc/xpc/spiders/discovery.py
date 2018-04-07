# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from xpc.items import PostItem, CommentItem, ComposerItem, CopyrightItem
import json

comment_api = 'http://www.xinpianchang.com/article/filmplay/ts-getCommentApi/id-%s/page-1'  # 当发生AJAX请求的时候，访问的地址
vip_map = {
    'yellow-v': 1,
    'blue-v': 2,
}


def convert_int(s):
    if isinstance(s, int):
        return s
    return int(s.replace(',','')) if s else 0


class DiscoverySpider(scrapy.Spider):
    name = 'discovery'  # 爬虫的名字
    allowed_domains = ['www.xinpianchang.com']
    root_url = 'http://www.xinpianchang.com'
    start_urls = ['http://www.xinpianchang.com/channel/index/sort-like']  # 爬去的主网页

    def parse(self, response):
        post_url = 'http://www.xinpianchang.com/a%sfrom=ArticleList'  # 每一个视频的具体网址
        post_list = response.xpath("//ul[@class='video-list']/li")  # 所有的视屏
        for post in post_list:#循环每一个视频
            post_id = post.xpath('./@data-articleid').extract_first()#获取视频的id
            thumbnail = post.xpath('./a/img/@_src').get()  # 缩略图的src
            request = Request(post_url % post_id, callback=self.parse_post)  # 根据每一个视频的地址创建一个新的request，
            request.meta['pid'] = post_id  # 传递数据 meta的作用是传递数据
            request.meta['thumbnail'] = thumbnail
            yield request

        next_page = response.xpath("//div[@class='page']/a[last()]/@href").extract_first()  # 下一页的地址
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_post(self, response):#视频函数
        post = PostItem()
        post['pid'] = response.meta['pid']#从请求中获取视频的id
        post['title'] = response.xpath('//div[@class="title-wrap"]/h3/text()').get()
        post['thumbnail'] = response.meta['thumbnail']
        post['video_format'] = ''
        post['preview'] = response.xpath('//div[@class="filmplay"]//img/@src').get()

        post['category'] = response.xpath('//span[@class="cate v-center"]/text()').get()#视频的分类
        post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()#视频的地址
        post['play_counts'] = convert_int(
            response.xpath('//i[contains(@class,"play-counts")]/@data-curplaycounts').get())#视频的播放次数，将其转换为整形
        post['like_counts'] = convert_int(response.xpath('//span[contains(@class,"like-counts")]/@data-counts').get())#视频的点赞次数，并讲其转换为整形
        post['description'] = response.xpath('//p[contains(@class,"desc")]/text()').get()#获取视频的描述
        post['created_at'] = response.xpath('//span[contains(@class,"update-time")]/i/text()').get()#视频的创建时间
        yield post
        creator_list = response.xpath('//div[contains(@class,"filmplay-creator")]/ul[@class="creator-list"]/li')#获取作者列表
        for creator in creator_list:
            user_page = creator.xpath('./a/@href').get()#获取作者的主页地址
            user_id = creator.xpath('./a/@data-userid').get()#获取作者的ID
            request = Request('%s%s' % (self.root_url, user_page), callback=self.parse_composer)#拼接路径，访问作者的主页
            request.meta['cid'] = user_id
            yield request
            cr = CopyrightItem()
            cr['pid'] = response.meta['pid']
            cr['cid'] = user_id
            cr['pcid'] = '%s_%s' % (cr['pid'], cr['cid'])#作者ID与视频ID相关联起来
            cr['roles'] = creator.xpath('./div[@class="creator-info"]/span/text()').get()#获取作者的职务
            yield cr

        request = Request(comment_api % post['pid'],
                          callback=self.parse_comment)
        request.meta['pid'] = post['pid']
        yield request

    def parse_comment(self, response):
        if response.text:
            pid = response.meta['pid']
            result = json.loads(response.text)#以json的格式加载数据
            next_page = result['data']['next_page_url']
            if next_page:
                request = Request(next_page, callback=self.parse_comment)
                request.meta['pid'] = pid
                yield request

            comments = result['data']['list']
            for c in comments:
                comment = CommentItem()
                comment['commentid'] = c['commentid']
                comment['pid'] = pid
                comment['cid'] = c['userInfo']['userid']
                comment['uname'] = c['userInfo']['username']
                comment['avatar'] = c['userInfo']['face']
                comment['created_at'] = int(c['addtime_int'])
                comment['content'] = c['content']
                comment['like_counts'] = convert_int(c['count_approve'])
                if c['reply']:
                    comment['reply'] = c['reply']['commentid'] or 0
                yield comment
                request = Request('%s/u%s' % (self.root_url, comment['cid']), callback=self.parse_composer)
                request.meta['cid'] = comment['cid']
                yield request



                # total_pages = response.xpath("//li[last()]/@data-totalpages").get()
                # pid = response.meta['pid']
                # cur_page = response.meta['cur_page']
                # if total_pages and total_pages.isdigit():
                #     total_pages = int(total_pages)
                #     if cur_page < total_pages:
                #         request = Request(comment_api % (pid, cur_page + 1), callback=self.parse_comment)
                #         request.meta['pid'] = pid
                #         request.meta['cur_page'] = cur_page + 1
                #         yield request
                # comments = response.xpath('//li')
                # for comment in comments:
                #     c = CommentItem()
                #     userid = comment.xpath('//span[@class="head-wrap"]/@data-userid').get()
                #     user_page = '%s%s' % (self.root_url, comment.xpath('./a[1]/@href').get())
                #     request = Request(user_page, callback=self.parse_composer)
                #     request.meta['cid'] = userid
                #     yield request
                #     c['content'] = comment.xpath('.//div[contains(@class,"comment-con")]/text()').get()
                #     c['create_time'] = comment.xpath('.//span[contains(@class,"send-time")]/text()').get()
                #     c['like_counts'] = comment.xpath('.//i[@class="counts"]/text()').get()
                #     c['pid'] = pid
                #     yield c

    def parse_composer(self, response):
        composer = ComposerItem()
        composer['cid'] = response.meta['cid']
        composer['name'] = response.xpath('//p[contains(@class, "creator-name")]/text()').get()
        composer['intro'] = response.xpath('//p[contains(@class, "creator-desc")]/text()').get()
        composer['banner'] = response.xpath('//div[@class="banner-wrap"]/@style').get()
        if composer['banner']:
            composer['banner'] = composer['banner'][21:-1]

        composer['verified'] = response.xpath('//span[@class="avator-wrap-s"]/span/@class').get()
        if composer['verified']:
            composer['verified'] = vip_map.get(composer['verified'].split(' ')[-1],0)
        composer['like_counts'] = convert_int(response.xpath('//span[contains(@class,"like-counts")]/text()').get())
        composer['follow_counts'] = convert_int(
            response.xpath('//span[contains(@class,"follow-wrap")]/span[last()]/text()').get())
        composer['fans_counts'] = convert_int(response.xpath('//span[contains(@class,"fans-counts")]/text()').get())
        composer['avatar'] = response.xpath('//span[@class="avator-wrap-s"]/img/@src').get()
        yield composer
