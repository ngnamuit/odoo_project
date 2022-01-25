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

    project_type = fields.Selection([
        ('project', 'Project'),
        ('daily_work', 'Daily_work')
    ], string='project_type')


    @api.model
    def create(self, vals):
        context = self._context or {}
        project_type = 'project'
        if context.get('is_daily_work'):
            project_type = 'daily_work'
        vals.update({'project_type': project_type})
        return super(ProjectProject, self).create(vals)

    def write(self, vals):
        return super(ProjectProject, self).write(vals)


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _domain_project_id(self):
        context = self._context or {}
        if context.get('is_daily_work'):
            return [('project_type', '=', 'daily_work')]
        return [('project_type', '!=', 'daily_work')]


    project_id = fields.Many2one('project.project', "Project", help="Project to make billable", required=True, domain=lambda self: self._domain_project_id())
    is_daily_task = fields.Boolean(string='Is Daily Tasks')


    @api.model
    def create(self, vals):
        context = self._context or {}
        if context.get('is_daily_work'):
            is_daily_task = True
            vals.update({'is_daily_task': is_daily_task})
        return super(ProjectTask, self).create(vals)


class ProjectStage(models.Model):
    _inherit = "project.task.type"


    def _domain_project_ids(self):
        context = self._context or {}
        if context.get('is_daily_work'):
            return [('project_type', '=', 'daily_work')]
        return [('project_type', '!=', 'daily_work')]

    project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id',
                                   string='Projects', domain=lambda self: self._domain_project_ids())
    is_daily_task = fields.Boolean(string='Is Daily Tasks')

    @api.model
    def create(self, vals):
        context = self._context or {}
        if context.get('is_daily_work'):
            is_daily_task = True
            vals.update({'is_daily_task': is_daily_task})
        return super(ProjectStage, self).create(vals)