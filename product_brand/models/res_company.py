from lxml import etree

from odoo import api, models, _, fields
from odoo.exceptions import AccessError, RedirectWarning, UserError
from odoo.tools import ustr


class ResCompany(models.Model):
    _inherit = "res.company"

    header = fields.Binary('Header')
    footer = fields.Binary('Footer')