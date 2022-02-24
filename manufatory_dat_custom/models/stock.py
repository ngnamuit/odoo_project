from odoo import api, fields, models, _, SUPERUSER_ID
import pytz

VIE_TIMEZONE = pytz.timezone('Asia/Saigon')
FILETYPE_BASE64_MAGICWORD = {
    b'/': 'jpg',
    b'R': 'gif',
    b'i': 'png',
    b'P': 'svg+xml',
}

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def image_data_uri(self, base64_source):
        """This returns data URL scheme according RFC 2397
        (https://tools.ietf.org/html/rfc2397) for all kind of supported images
        (PNG, GIF, JPG and SVG), defaulting on PNG type if not mimetype detected.
        """
        return 'data:image/%s;base64,%s' % (
            FILETYPE_BASE64_MAGICWORD.get(base64_source[:1], 'png'),
            base64_source.decode(),
        )


    def to_SGT_datetime(self, dt):
        print("dt == %s"%(dt))
        return dt.astimezone(VIE_TIMEZONE)