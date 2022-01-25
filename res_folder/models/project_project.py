# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    folder_id = fields.Many2one('res.folder', 'Folder')


class ProjectTask(models.Model):
    _inherit = "project.task"

    folder_parent_id =fields.Many2one('res.folder', 'Parent Folder', related='project_id.folder_id')
    file_ids = fields.One2many('res.file', 'task_id', string="Files")
