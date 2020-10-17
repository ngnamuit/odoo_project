import logging
import requests
import ast
from odoo import api, fields, models, registry, _
_logger = logging.getLogger(__name__)
FB_CONF = {
    'app_name': 'app.smartstore',
    'app_id': '1471296016504912',
    'app_token': 'EAAFZCeNVXZBLgBAGjJVm4ZC1LX8jtWDvWX79ZCZCPwFs4gb3IiJzh3JSu5EJl4N7vZAGNxhYLIONVe4EFjn7BrUszY3lsZAjFcYZAzVAZBcZCyfGkQMyT52wb1byd0nz0QiL9OcSUIjSTCXZBIYrfOlrnGMsUq64TL1GYZAE0xZAb3EmWb9q9rPv3XXD5',
}

FB_API_URL = 'https://graph.facebook.com'

def get_facebook_config(self):
    icp    = self.env['ir.config_parameter'].sudo()
    config = icp.get_param("facebook_config".upper(), default={})
    return FB_CONF

class SocialIntegrate(models.Model):
    _name = 'social.integrate'

    name = fields.Char('Name')


    def create_lead_contact_and_activities(self, vals={}):
        #region for create or update contact
        contact = self.env['res.partner'].search([('fid', '=', vals['fid'])])
        if not contact:
            contact_vals = {
                'name'      : vals.get('full_name'),
                'first_name': vals.get('first_name'),
                'last_name' : vals.get('last_name'),
                'fid'       : vals.get('fid'),
                'type'      : 'contact',
            }
            contact = self.env['res.partner'].create(contact_vals)
        logging.info(f"[GET_ACTIONS]- Contact: {contact.id}")
        #endregion

        #region for lead
        lead = self.env['crm.lead'].search([
            ('post_id', '=', str(vals['post_id'])),
            ('fid', '=', vals['fid'])
        ])
        if not lead:
            lead_vals = {
                'first_name' : vals.get('first_name'),
                'last_name'  : vals.get('last_name'),
                'fid'        : vals['fid'],
                'post_id'    : vals['post_id'],
                'contact_id' : contact.id,
                'link_ref'   : vals['post_url'],
                'lifecycle_stage': 'subscriber',
            }
            lead = self.env['crm.lead'].create(lead_vals)
        logging.info(f"[GET_ACTIONS]- Lead: {lead.id}")
        #endregion

        #region for activity
        activity_vals = {
            'platform'  : 'facebook',
            'source'    : vals['post_url'],
            'type'      : vals['type'].lower(),
            'contact_id': contact.id,
            'lead_id'   : lead.id,
            'content'   : vals.get('content'),
            'fid'       : vals['fid'],
            'post_id'   : vals['post_id'],
        }
        activity = self.env['crm.lead.activities'].create(activity_vals)
        logging.info(f"[GET_ACTIONS]- Lead Activity: {activity.id}")
        #endregion

        return True

    def get_api_url(self, post_id, type):
        if type=='like':
            short_link = 'reactions'
        elif type == 'comment':
            short_link = 'comments'
        elif type == 'feeds':
            return f'{FB_API_URL}/{FB_CONF["app_id"]}/feed?access_token={FB_CONF["app_token"]}'
        else:
            raise Exception(f'Can not found type = {type} on get_api_url function')
        api_url = f'{FB_API_URL}/{FB_CONF["app_id"]}_{post_id}/{short_link}?access_token={FB_CONF["app_token"]}'
        return api_url

    @api.model
    def get_actions(self, post_ids, type='like'):
        logging.info(f"[START] get_actions function with post_ids: {post_ids}")
        for post_id in post_ids:
            logging.info(f"[GET_ACTIONS]- Processing post_id={post_id} ")
            api_url = self.get_api_url(post_id, type)
            post_url = f'https://www.facebook.com/{FB_CONF["app_name"]}/posts/{post_id}'
            response = requests.get(api_url)
            if response.status_code == 200:
                r = response.json()
                datas = r.get('data', {})
                if datas: # I like to write this code although It's not alive, Will be better haha
                    for row in datas:
                        # 1. type == comment -> act_type = 'comment', user =
                        # 2. type == like -> act_type in (haha, like, .... )
                        act_type  = 'comment' if type == 'comment' else row.get('type')
                        act_type  = act_type.lower()

                        # define some variables to put into vals
                        user      = row.get('from', {})  # this field will have when type is comment
                        fid       = user.get('id') or row.get('id')
                        full_name = user.get('name') or row.get('name')
                        first_name= full_name.split(' ')[0]
                        last_name = full_name[len(first_name) + 1:]
                        message   = row.get('message')

                        # check record if it is existing, do nothing else store it as a activity
                        fb_act = self.env['crm.lead.activities'].search([
                            ('post_id', '=', post_id),
                            ('fid', '=', fid),  # row['id']: "facebook-user-id"
                            ('type', '=', act_type),
                            ('content', '=', message)
                        ])
                        if not fb_act:
                            vals = {
                                'full_name'  : full_name,
                                'first_name' : first_name,
                                'last_name'  : last_name,
                                'fid'        : str(fid),
                                'type'       : act_type,
                                'post_id'    : str(post_id),
                                'post_url'   : post_url,
                                'content'    : message
                            }
                            self.create_lead_contact_and_activities(vals)
                        else:
                            logging.info(f"[GET_ACTIONS]- FID: {fid} and Post_ID: {post_id} is created alr")
                else:
                    logging.info(f"[GET_ACTIONS]- Can not found data {response}")
            else:
                logging.info(f"[GET_ACTIONS]- FAILS w reposone {response}")
        logging.info("[DONE] get_actions function ")

    @api.model
    def get_all_feeds_from_fb_page(self):
        api_url = self.get_api_url(post_id=None, type='feeds')
        response = requests.get(api_url)
        if response.status_code == 200:
            r = response.json()
            datas = r.get('data', {})
            for page_post in datas:
                post_id = page_post.get('id', '').split('_')[-1]

                # log and go to next feed
                if not post_id:
                    logging.info(f"[GET FEEDS FROM FB's PAGE]- Can not found w page_post: {page_post}")
                    continue

                # 1. Run like action
                self.get_actions(post_ids=[post_id], type='like')
                # 2. Run like action
                self.get_actions(post_ids=[post_id], type='comment')
        else:
            logging.info(f"[GET FEEDS FROM FB's PAGE]- Can not found data {response}")