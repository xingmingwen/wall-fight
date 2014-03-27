#encoding:utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import requests
import json
import os
import re
from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)
#==============================
TPL_PATH='static/template/'
JS_PATH='static/JS/'
CSS_PATH='static/CSS/'
#=============================
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(TPL_PATH + '/waterfall.html');
nt = ""
def get_next_nt():
    url = "http://www.meilishuo.com/guang/hot?frm=daeh"
    resp = requests.get(url)
    return re.findall("nt : '(\S+)'", resp.content)[0]

class AjaxHandler(tornado.web.RequestHandler):
    def get(self):
        global nt
        if not nt:
            nt = get_next_nt()
        page = self.get_argument('page')
        url =  'http://www.meilishuo.com/aj/getGoods/goods?frame={frame}&page={page}&view=1&word_name=hot&section=hot&price=all'
        url = url.format(frame=int(page)%8, page=int(page)/8)
        try:
            headers = {
                    'nt':nt,
                    'Referer':'http://www.meilishuo.com/guang/hot?frm=daeh'
            }
            htcontent = requests.get(url, headers=headers).json()
        except Exception, exp:
            nt = get_next_nt()
            headers = {
                    'nt':nt,
                    'Referer':'http://www.meilishuo.com/guang/hot?frm=daeh'
            }
            htcontent = requests.get(url, headers=headers).json()

        content = ""
        for item in htcontent['tInfo']:
            img_url = item['show_pic']
            link = 'http://www.meilishuo.com/share/item/%s' % item['twitter_id']
            likes = item['count_like']
            sold = item['sale_num']
            price = item['ginfo']['goods_price']
            #content += "<div class='box'><a href={link}><img src={img_url}></a></div>".format(img_url=img_url, link=link)
            kvs = dict(img_url=img_url, link=link, likes=likes, sold=sold, price=price)
            content += self.render_string(TPL_PATH + '/waterfall.box.html', **kvs)  
        self.write(content)
        self.finish()

def main():
    tornado.options.parse_command_line()
    settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))
    application = tornado.web.Application([
        (r"/next", AjaxHandler),
        (r"/", MainHandler),
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
