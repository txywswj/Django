# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class PostItem(scrapy.Item):
    table_name='posts'
    '''保存视频的ITEM'''
    pid = Field()
    title = Field()
    thumbnail = Field()
    preview = Field()
    video = Field()
    video_format = Field()
    category = Field()
    play_counts = Field()
    like_counts = Field()
    description = Field()
    created_at = Field()


class CommentItem(scrapy.Item):
    table_name='comments'
    pid = Field()
    cid = Field()
    content = Field()
    created_at = Field()

    like_counts = Field()
    commentid = Field()
    uname = Field()
    avatar = Field()
    reply=Field()


class ComposerItem(scrapy.Item):
    table_name='composers'
    cid = Field()
    banner = Field()
    avatar = Field()  # 头像
    verified = Field()
    name = Field()
    intro = Field()
    like_counts = Field()
    fans_counts = Field()
    follow_counts = Field()  # 关注的 ren


class CopyrightItem(scrapy.Item):
    table_name='copyrights'
    pcid = Field()
    pid = Field()
    cid = Field()
    roles = Field()
