# -*- coding:utf-8 -*-
import time
import uuid
import os
import logging
import tempfile
try:
    import cStringIO as StringIO
except:
    import StringIO

from random import choice, randrange
from PIL import Image, ImageFont, ImageDraw
from werkzeug.contrib.cache import FileSystemCache


'''
@route('/admin/captcha')
class AdminCaptchaHandler(RequestHandler, CaptchaMixin):
    def get(self):
        self.captcha_send()

@route('/admin/login/')
class AdminLoginHandler(RequestHandler, CaptchaMixin):

    def get(self):
        if self.current_user:
            self.redirect('/admin/')
        else:
            self.render('admin/login.html')

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)

        if self.captcha_validate('captcha') and account and password:
            employee = self.db.query(Employee).filter_by(account=account).first()
            if employee and employee.validate_password(password):
                self.set_current_user(employee)
        self.redirect('/admin/')


html <img>:
    {% raw handler.captcha_html('captcha') %}

'''




settings = {
    'captcha_fgcolor': '#000000', # default:  '#000000' (color for characters and lines)
    'captcha_bgcolor': '#ffffff', # default:  '#ffffff' (color for background)
    'captcha_fonts': os.path.join(os.path.dirname(__file__), 'fonts'), # default:  None  (uses the directory of the captcha module)
    'captcha_minmaxvpos': (5, 15), # default:  (8, 15) (vertical position of characters)
    'captcha_minmaxrotations': (-30,31), # default:  (-30,31) (rotate characters)
    'captcha_minmaxheight': (30,45), # default:  (30,45) (font size)
    'captcha_minmaxkerning': (-2,1), # default:  (-2,1) (space between characters)
    'captcha_alphabet': "abdeghkmnqrt2346789AEFGHKMNRT", # default:  "abdeghkmnqrt2346789AEFGHKMNRT"
    'captcha_num_lines': 1, # default: 1
    'captcha_line_weight': 3, # default: 3
    'captcha_imagesize': (160,50), # default: (200,60)
}
cache = FileSystemCache(tempfile.gettempdir())


class CaptchaMixin(object):

    def captcha_html(handler, prefix=''):
        return '''
        <a href="#" onclick="this.firstChild.src='%s?captcha='+new Date().getTime(); return false;" title="点击刷新"><img src="%s?captcha=%s"></a>
        '''%(prefix, prefix, time.time())

    def captcha_validate(handler, param):
        value = handler.get_argument(param, '').lower()
        captcha_id = handler.get_cookie('captcha')
        logging.debug('check captcha: {captcha_id=%s, input=%s}'%(captcha_id, value))
        v = cache.get(captcha_id)
        if v:
            cache.delete(captcha_id)
            return value == v
        else:
            return False

    def captcha_send(handler):
        #generate the captcha code
        value = ''
        for i in range(choice((4,5))):
            value += choice(settings['captcha_alphabet'])
        value = value.lower()

        captcha_id = uuid.uuid4().hex
        cache.set(captcha_id, value, timeout=120)
        handler.set_cookie('captcha', captcha_id)

        #generate and send the captcha iamge
        data = _gen_image(value)
        f = StringIO.StringIO()
        data.save(f, "jpeg")
        data = f.getvalue()

        handler.set_header('Content-Type', 'image/jpeg')
        handler.set_header('Cache-Control', 'no-cache, no-store')
        handler.set_header('Pragma', 'no-cache')
        handler.set_header('Expires', 'now')
        handler.write(data)



def _gen_image(solution):
    cs = settings

    fontdir = cs['captcha_fonts']
    fontnames = [os.path.join(fontdir, x) for x in os.listdir(fontdir) ]
    imagesize = cs['captcha_imagesize']
    posnew = 7

    bgimage = Image.new('RGB',imagesize, cs['captcha_bgcolor'])

    # render characters
    for c in solution:
        fgimage = Image.new('RGB', imagesize, cs['captcha_fgcolor'])
        font = ImageFont.truetype(choice(fontnames), randrange(*cs['captcha_minmaxheight']))
        charimage = Image.new('L', font.getsize(' %s ' % c), '#000000')
        draw = ImageDraw.Draw(charimage)
        draw.text((0,0), ' %s' % c, font=font, fill='#ffffff')
        charimage = charimage.rotate(randrange(*cs['captcha_minmaxrotations']), expand=1,
                resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', imagesize)
        ypos = randrange(*cs['captcha_minmaxvpos'])
        maskimage.paste(charimage,
                (posnew, ypos,
                    charimage.size[0]+posnew,
                    charimage.size[1]+ypos)
                )
        bgimage = Image.composite(fgimage, bgimage, maskimage)
        posnew += charimage.size[0] + randrange(*cs['captcha_minmaxkerning'])

    # draw line(s)
    for dummy in range(cs['captcha_num_lines']):
        linex = choice( range(2, cs['captcha_minmaxheight'][1]) )
        minmaxliney = ( cs['captcha_minmaxvpos'][0], 
                cs['captcha_minmaxvpos'][1] + cs['captcha_minmaxheight'][0])
        linepoints = [linex, randrange(*minmaxliney)]
        while linex < posnew:
            linex += randrange(*cs['captcha_minmaxheight']) * 0.8
            linepoints.append(linex)
            linepoints.append(randrange(*minmaxliney))
        draw = ImageDraw.Draw(bgimage)
        draw.line(linepoints, width=cs['captcha_line_weight']
                , fill=cs['captcha_fgcolor'])

    return bgimage





