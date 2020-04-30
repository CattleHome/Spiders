# coding=utf-8
import requests
import re
import csv
from lxml import etree

# 字体大小
font_size = 14

#   css的处理表头
header_css = {
    'Host': 's3plus.meituan.net',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    "Cookie": "_lxsdk_cuid=1713f073ef6c8-094ffe6dbe22e6-f313f6d-1fa400-1713f073ef6c8; _lxsdk=1713f073ef6c8-094ffe6dbe22e6-f313f6d-1fa400-1713f073ef6c8; _hc.v=7e3974e0-0277-41e5-7872-e42ae6898ea6.1585900372; s_ViewType=10; _dp.ac.v=fb964315-a2fe-48d0-b154-349659e35ff0; ua=dpuser_2815203639; ctu=8677991d86fd67e60aa4f9b3e8dc2c2bc04ff8de5ed2cfa7703709aa8f9c2fb6; fspop=test; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dper=ad1841136c2da38d3f0cfd236199e8e2bfd6e8694465f01cbf3684e4ac41509142d8ee0cc7e740545efdcde0f424851a3ea96370fd10ed6d876a0f2d8a6529f6c54c2d2b02279b228fa96cc3e043d8de885dc33f3c6885e50e8f0229465a397a; ll=7fd06e815b796be3df069dec7836c3df; uamo=13229853738; cy=1; cye=shanghai; dplet=f10182f268d5572a26c5771c012935ca; _lxsdk_s=1717c24fc8e-d52-1d3-9c6%7C%7C229"

}
#   svg的处理表头
header_svg = {
    'accept-encoding': 'gzip, deflate',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'

}

#   正常请求网页处理的表头
header_pinlun = {
    "Cookie": "_lxsdk_cuid=1713f073ef6c8-094ffe6dbe22e6-f313f6d-1fa400-1713f073ef6c8; _lxsdk=1713f073ef6c8-094ffe6dbe22e6-f313f6d-1fa400-1713f073ef6c8; _hc.v=7e3974e0-0277-41e5-7872-e42ae6898ea6.1585900372; s_ViewType=10; _dp.ac.v=fb964315-a2fe-48d0-b154-349659e35ff0; ctu=8677991d86fd67e60aa4f9b3e8dc2c2bc04ff8de5ed2cfa7703709aa8f9c2fb6; t_lxid=171864b9c68f-08c1c93adf0563-5313f6f-1fa400-171864b9c69c8-tid; ll=7fd06e815b796be3df069dec7836c3df; uamo=13229853738; fspop=test; cy=2; cye=beijing; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1587955973; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1587955973; thirdtoken=7248e98e-572b-45af-a91e-ee82a1d1e668; _thirdu.c=dc225bbbe150c481c49d3101ba0b08bb; dper=53e35f4a85e2e6153ec9b2c63ca8205ad64713190cbcb99507ce25f9d0b4c87ab9ffa0838f4acede941d053b8a6a27c929cdc9d2fccc264108231dd32acdd39e6c62e99ad8492b60b2a6cd53d988655b617723d321583155c1c18ef4b57c2585; ua=dpuser_5783949249; dplet=59be271fca1145fbf3196542570179ac; _lxsdk_s=171be66eda4-e5e-41-5c7%7C%7C804",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "Host": "www.dianping.com",
    'Accept-Encoding': 'gzip',
    "Referer": "http://www.dianping.com/shop/93478681/review_all/p2",
    "Upgrade-Insecure-Requests": "1"
}



class review_all_url(object):
    '''
    有review_all更多评论的URL
    url = 'http://www.dianping.com/shop/k9oYRvTyiMk4HEdQ/review_all/p2'
    '''

    def __init__(self):
        self.file_comment = open('dzdp_comment.csv', 'w', encoding='utf-8', newline='')
        self.csv_write = csv.writer(self.file_comment)
        self.csv_write.writerow(
            ('昵称', '星级', '口味', '环境', '服务', '性价比', '人均', '评论', '喜欢的菜', '评论时间', '店铺名称', '商家回复时间', '商家评论'))

        self.file_shop = open('dzdp_shop.csv', 'w', encoding='utf-8', newline='')
        self.csv_shop = csv.writer(self.file_shop)
        self.csv_shop.writerow(("店铺名", "评论数", "人均", "口味分", "环境分", "服务分", "地址", "电话"))

    def get_css_link(self, url):
        ''' 获取css链接 '''
        # 获取网页源码
        html_origin = requests.get(url, headers=header_pinlun).text
        # 正则表达式匹配css链接
        css_link = re.search('<link rel="stylesheet" type="text/css" href="(//s3plus.meituan.net.*?.css)">',
                             html_origin,
                             re.S)

        css_link_detail = css_link.group(1)

        css_link = 'http:' + str(css_link_detail)
        html_css = requests.get(css_link, headers=header_css).text
        print("css_link ： ", css_link)

        return html_origin, html_css

    def get_svg_link(sell, html_css, front_two_alp_addr):
        # 获取的svg链接
        alp = front_two_alp_addr
        # 根据class的值选择svg

        search = '\[class\^=\"' + alp + '\"\]\{.*?background-image: url\((//.*?svg)\)'
        background_image_links = re.search(search, html_css, re.S)

        background_image_links_detail = background_image_links.group(1)

        print("svg", background_image_links_detail)

        #
        background_image_link_addr = 'http:' + str(background_image_links_detail)

        return background_image_link_addr  # 地址对应此链接

    def get_front_two_alp_addr(self, html_origin, class_name):
        '''获取地址的隐藏字体的class_name　前三个字母,有时候只有两个字母'''

        # front_three_alp = re.search('<span class="' + class_name + '">.*?<span class="(\w\w).*?"></span>', html_origin,re.S)

        # 拿到的是bb class之后的所有
        front_three_alp = re.search('<div class="' + class_name + '">.*?<bb class="(\w\w\w).*?"></bb>', html_origin,
                                    re.S)

        front_three_alp_detail = front_three_alp.group(1)
        print("addr 前两个字母", front_three_alp_detail)
        return front_three_alp_detail

    def get_font_css(self, html_css, front_alp_addr):
        '''获取html_css里面有关地址的(class_name,x,y)'''

        font_css = re.findall('\.({0}.*?)'.format(front_alp_addr) + '{background:-(\d+).0px -(\d+).0px;}', html_css,
                              re.S)
        # print('addr_css')
        print("所有的坐标", font_css)

        return font_css

    #   第一种加密
    def get_font_dict_by_offset_old(self, addr_svg_link, addr_css):
        '''获取坐标偏移的文字字典'''
        # print('svg的url:', addr_svg_link)
        svg_html = requests.get(addr_svg_link, headers=header_svg).text
        # print("addrs上的svg", svg_html)

        font_finded = {}

        #   所有的addr坐标  [('rcrrr', '0', '62'), ('rcul7', '126', '164'),...]
        all_addr_css = addr_css
        #   获取网页上所有要和y进行对比的坐标
        y_list_M0 = re.findall('d="M0 (\d+)', svg_html)
        # print("svg上的y", y_list_M0)

        if y_list_M0:
            #   获得所有的字体
            font_finded = re.findall('<textPath.*?>(.*?)<', svg_html)
            # print("svg上的字体：", font_finded)

            #   把字体弄成列表的形式，结合索引将其算出
            font_list = []

            # all_addr_css ：css上地址的各个字坐标和前缀 [('rcrrr', '0', '62'), ('rcul7', '126', '164')。。。】
            # print("所有的address_css", all_addr_css)
            for addr_css_name_x_y in all_addr_css:
                #  y_list_M0：svg上的y
                for y in y_list_M0:

                    #   例子：号 ，background: -378.0px -240.0px; 对比的是y坐标 240 < 255，每个网址不一样。
                    if int(addr_css_name_x_y[2]) < int(y):
                        #   拿到id的值
                        id_href_y = re.findall('<path id="(\d+)" d="M0 {} .*?/>'.format(y), svg_html)
                        #   background: -378.0px -240.0px; 号 。x坐标/字体大小
                        offset_x = int((int(addr_css_name_x_y[1]) / int(font_size)))
                        #   字体的位置
                        offset_y = int(id_href_y[0]) - 1
                        font_list.append((addr_css_name_x_y[0], font_finded[offset_y][offset_x]))
                        break

            return font_list

    def get_result_font_addr(self, html_origin, font_list, phone):

        for font in font_list:
            html_origin = html_origin.replace('<bb class="' + font[0] + '"></bb>', font[1])
        html = etree.HTML(html_origin)
        shops = html.xpath('//div[@class="review-shop-wrap"]')
        for shop in shops:
            shop_name = shop.xpath('div[@class="shop-info clearfix"]/h1/text()')[0]
            reviews = shop.xpath('div[@class="rank-info"]/span[@class="reviews"]/text()')[0]
            prices = shop.xpath('div[@class="rank-info"]/span[@class="price"]/text()')[0].split('：')[-1]
            score_tastes = shop.xpath('div[@class="rank-info"]/span[@class="score"]/span[1]/text()')[0].split('：')[-1]
            score_environments = shop.xpath('div[@class="rank-info"]/span[@class="score"]/span[2]/text()')[0].split('：')[-1]
            score_services = shop.xpath('div[@class="rank-info"]/span[@class="score"]/span[3]/text()')[0].split('：')[-1]
            address = shop.xpath('div[@class="address-info"]/text()')[0].replace('\n', '').split(':')[-1]
            address=''.join(address.split())
            phones=phone.split(': ')[-1]
            # print(shop_name)
            # print(reviews)
            # print(prices)
            # print(score_tastes)
            # print(score_environments)
            # print(score_services)
            # print(address)

            self.csv_shop.writerow((shop_name, reviews, prices, score_tastes, score_environments, score_services, address, phones))
        print("店铺信息保存成功！！")

        # 替换成功提取地址
        # result_font = re.findall('<div class="' + head_span_class_name + '">(.*?)</div>', html_origin, re.S)
        # addrs = result_font[0].replace('\n', '').replace('&nbsp;', '').replace(' ', '')

        # return addrs

    def get_front_two_alp_phone(self, html_origin, class_name):
        front_three_alp = re.search('<div class="' + class_name + '">.*?<cc class="(\w\w\w).*?"></cc>', html_origin,
                                    re.S)
        front_three_alp_detail = front_three_alp.group(1)
        return front_three_alp_detail

    def get_result_font_comment(self, html_origin, font_list):
        print("字体列表:", font_list)
        for font in font_list:
            html_origin = html_origin.replace('<svgmtsi class="' + font[0] + '"></svgmtsi>', font[1])
        html = etree.HTML(html_origin)
        infos = html.xpath('//div[@class="reviews-items"]/ul/li/div[@class="main-review"]')
        for info in infos:
            # 用户昵称
            names = info.xpath('div[@class="dper-info"]/a/text()')[0].strip().replace('\n', '')
            # 星星
            stars = info.xpath('div[@class="review-rank"]/span/@class')[0].split(' ')[1]
            if stars == "sml-str50":
                stars = "5"
            elif stars == "sml-str45":
                stars = "4.5"
            elif stars == "sml-str40":
                stars = "4"
            elif stars == "sml-str35":
                stars = '3.5'
            elif stars == "sml-str30":
                stars = "3"
            elif stars == "sml-str25":
                stars = "2.5"
            elif stars == "sml-str20":
                stars = "2"
            elif stars == "sml-str15":
                stars = "1.5"
            elif stars == "sml-str10":
                stars = "1"
            elif stars == "sml-str5":
                stars = "0.5"
            else:
                stars = "0"

            # 口味分
            tastes = info.xpath('div[@class="review-rank"]/span[2]/span[1]/text()')[0].strip().replace('\n', '')
            tastes = tastes.split('：')[-1]

            # 环境分
            environments = info.xpath('div[@class="review-rank"]/span[2]/span[2]/text()')[0].strip().replace('\n', '')
            environments = environments.split('：')[-1]

            # 服务分
            services = info.xpath('div[@class="review-rank"]/span[2]/span[3]/text()')[0].strip().replace('\n', '')
            services = services.split('：')[-1]

            # 性价比
            effectives = info.xpath('div[@class="review-rank"]/span[2]/span[4]/text()')[0].strip().replace('\n', '')
            effectives = effectives.split('：')[-1]

            if info.xpath('div[@class="review-rank"]/span[2]/span[5]'):
                # 人均价格
                averages = info.xpath('div[@class="review-rank"]/span[2]/span[5]/text()')[0].strip().replace('\n', '')
                averages = averages.split('：')[-1]
            else:
                averages = ''

            # 用户第一次评论
            contents = info.xpath('div[@class="review-words Hide"]/text()')[0].strip().replace('\n', '')
            if info.xpath('div[@class="review-recommend"]'):
                # 用户喜欢的菜
                like_dishs = info.xpath('div[@class="review-recommend"]/a/text()')
            else:
                like_dishs = ""

            # 用户评论时间
            times = info.xpath('div[@class="misc-info clearfix"]/span[@class="time"]/text()')[0].strip().replace('\n',
                                                                                                                 '')
            # 用户选择的餐厅
            shops = info.xpath('div[@class="misc-info clearfix"]/span[@class="shop"]/text()')[0].strip().replace('\n',
                                                                                                                 '')

            if info.xpath('div[@class="shop-reply"]'):
                # 商家回应时间
                shop_recontents_times = info.xpath('div[@class="shop-reply"]/div[@class="hd clearfix"]/span/text()')[
                    0].strip().replace('\n', '')
                # 商家回应信息
                shop_re_contents = info.xpath('div[@class="shop-reply"]/p/text()')[0].strip().replace('\n', '')

            else:
                shop_recontents_times = ''
                shop_re_contents = ''

            self.csv_write.writerow((names, stars, tastes, environments, services, effectives, averages, contents,
                                     str(like_dishs), times, shops, shop_recontents_times, shop_re_contents))

        # for i in result_font:
        #     x=i.replace('&#x20;',' ').replace(';','').replace('&#x0A','').replace('\n','').strip()
        #     sel=re.sub('<img class=.*?alt=""/>','',x)
        #     print(sel)

        print("评论信息保存成功!!!")

    # 3.2获得class_name 对应的文字  //第二种加密方法－new－无M0
    def get_font_dict_by_offset_new(self, svg_link_num, food_kind_css):
        '''获取坐标偏移的文字字典'''

        svg_html = requests.get(svg_link_num, headers=header_svg).text

        font_finded = {}

        y_list = re.findall('<text x=.*?y="(\d+)"', svg_html)

        y_list_new = []
        for i in enumerate(y_list):
            y_list_new.append(i)

        if y_list:
            font_finded = re.findall('<text .*?>(.*?)<', svg_html)
            offset_x = []
            offset_y = []
            font_list = []
            for food_css_name_x_y in food_kind_css:
                for y in y_list:
                    if int(food_css_name_x_y[2]) < int(y):
                        offset_x = int((int(food_css_name_x_y[1]) / int(font_size)))
                        for one_y in y_list_new:
                            if int(one_y[1]) == int(y):
                                offset_y = one_y[0]
                                font_list.append((food_css_name_x_y[0], font_finded[offset_y][offset_x]))
                        break

            return font_list

    def get_result_font_phone(self, html_origin, font_list, head_span_class_name):

        for font in font_list:
            html_origin = html_origin.replace('<cc class="' + font[0] + '"></cc>', font[1])
        # 替换成功提取地址
        result_font = re.findall('<div class="' + head_span_class_name + '">(.*?)</div>', html_origin, re.S)
        phone = result_font[0].replace('\n', '').replace('&nbsp;', ' ').strip()

        return phone

    def get_front_two_alp_pinglun(self, html_origin, class_name):
        search = '<div class="' + class_name + '">.*?<svgmtsi class="(\w\w\w).*?"></svgmtsi>'
        front_three_alp = re.search(search, html_origin, re.S)
        front_three_alp_detail = front_three_alp.group(1)

        return front_three_alp_detail

    def main(self):
        # **********************2020-4-29**********************
        # 目前电话、地址和评论都是第二种解密方式

        #   需要有review_all 更多评论的URL
        url = 'http://www.dianping.com/shop/93478681/review_all'
        #  获取css样式文件
        html_origin, html_css = self.get_css_link(url)

        #   拿到电话的前两个字母
        front_two_alp_phone = self.get_front_two_alp_phone(html_origin, class_name='phone-info')
        #   拿到电话的svg连接
        phone_svg_link = self.get_svg_link(html_css, front_two_alp_phone)
        #   获取获取html_css有关地址的（background,x,y)
        font_css_phone = self.get_font_css(html_css, front_two_alp_phone)
        #   第二种解密方式
        font_list = self.get_font_dict_by_offset_new(phone_svg_link, font_css_phone)
        phone_font = self.get_result_font_phone(html_origin, font_list, head_span_class_name='phone-info')

        # 　获取地址的前两个字母 地址的class=addr,传入addr
        front_two_alp_addr = self.get_front_two_alp_addr(html_origin, class_name='address-info')
        #  获取地址对应的svg链接
        addr_svg_link = self.get_svg_link(html_css, front_two_alp_addr)
        #  获取html_css有关地址的（background,x,y)
        font_css_addr = self.get_font_css(html_css, front_two_alp_addr)
        #   第一种解密方式
        font_list = self.get_font_dict_by_offset_new(addr_svg_link, font_css_addr)
        # 获取地址　　/** 将电话传入
        self.get_result_font_addr(html_origin, font_list, phone_font)

        #   拿到评论的前两个字母，有时候是三个字母

        front_two_alp_phone = self.get_front_two_alp_pinglun(html_origin, class_name='review-words Hide')
        #   拿到评论的svg连接
        pinglun_svg_link = self.get_svg_link(html_css, front_two_alp_phone)
        #   获取获取html_css有关地址的（background,x,y)
        font_css_comment = self.get_font_css(html_css, front_two_alp_phone)
        #   第二种解密方式
        font_list = self.get_font_dict_by_offset_new(pinglun_svg_link, font_css_comment)
        self.get_result_font_comment(html_origin, font_list)


if __name__ == '__main__':
    rau = review_all_url()
    rau.main()
