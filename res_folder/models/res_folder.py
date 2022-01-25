# -*- coding: utf-8 -*-
import base64
import logging
from odoo import api, fields, models, tools, _
from ..models.google_storage_service import Storage as StorageSvc
_logger = logging.getLogger(__name__)


class ResFolder(models.Model):
    _name = "res.folder"
    _description = "Res Folder"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('res.folder', 'Parent Folder', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('res.folder', 'parent_id', 'Child Folders')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for folder in self:
            if folder.parent_id:
                folder.complete_name = '%s / %s' % (folder.parent_id.complete_name, folder.name)
            else:
                folder.complete_name = folder.name


def create_local_file(data, file_name):
    local_path = '/tmp/odoo/' + file_name
    with open(local_path, 'wb') as temp_file:
        if isinstance(data, str):
            data = base64.b64decode(data)
        temp_file.write(data)
    return local_path


class ResFile(models.Model):
    _name = "res.file"

    name = fields.Char('Name')
    folder_id = fields.Many2one('res.folder')
    url = fields.Char('Url')
    url_backup = fields.Char('Url Backup')
    file = fields.Binary('File', help="File to check and/or import, raw binary (not base64)")  # https://www.facebook.com/groups/odoo.community/permalink/2562206483863638/?comment_id=2562219827195637
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')
    task_id = fields.Many2one('project.task', 'Task')

    #region CRUD
    @api.model
    def create(self, values):
        data_file = values.get('file')
        if data_file:
            # create local path
            file_name = values.get('file_name')
            local_file = create_local_file(data_file, file_name)

            # create remote path
            folder_id = values.get('folder_id')
            folder = self.env['res.folder'].browse(folder_id)
            remote_file = folder.complete_name + '/' + file_name

            # upload google storage and update record
            folder_name, public_url = StorageSvc.upload(local_file, remote_file)
            #StorageSvc.make_blob_public(remote_file)
            values.update({'url': public_url, 'file': False})
        res = super(ResFile, self).create(values)
        return res

    def write(self, values):
        for rec in self:
            data_file = values.get('file')
            if data_file:
                # create local path
                file_name = values.get('file_name') or rec.file_name
                local_file = create_local_file(data_file, file_name)

                # create remote path
                folder_id = values.get('folder_id') or rec.folder_id
                remote_file = folder_id.complete_name + '/' + file_name

                # upload google storage and update record
                folder_name, public_url = StorageSvc.upload(local_file, remote_file)
                #StorageSvc.make_public(remote_file)
                values.update({'url': public_url, 'file': False})

                #region to delete old url
                delete_url = rec.url

                # old blood_name need to delete
                delete_remote_name = (rec.folder_id.complete_name + '/' if rec.folder_id else '') + rec.file_name

                rec.delete_url_from_google_storage(delete_url, delete_remote_name)
                #endregion
        res = super(ResFile, self).write(values)
        return res

    def unlink(self):
        for rec in self:
            delete_remote_name = (rec.folder_id.complete_name + '/' if rec.folder_id else '') + rec.file_name
            delete_url = rec.url
            if delete_remote_name and delete_url:
                rec.delete_url_from_google_storage(delete_url, delete_remote_name)
        return super(ResFile, self).unlink()
    #endregion CRUD

    def delete_url_from_google_storage(self, delete_url, delete_remote_name):
        _logger.info('DELETE URL RUNNING: .......... ')
        self.ensure_one()
        try:
            if delete_url:
                files = self.search([('url', '=', delete_url)])
                if len(files) > 1:
                    _logger.info('Url is used by some other records')
                else:
                    StorageSvc.delete_blob(delete_remote_name)
        except Exception as e:
            _logger.info('DELETE URL RUNNING: ERROR {0} .......... '.format(e))
        _logger.info('DELETE URL RUNNING: .......... DONE')
