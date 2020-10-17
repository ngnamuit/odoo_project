#### Steps to setup candex on production 
1. Install integrate module
2. Setup cron job to run fb integration:
 - Set up cron to run for both comment and like action: 
    - Model: `Model-social.integrate`
    - Action To Do:	`Execute Python Code`
    - Python Code: `model.get_all_feeds_from_fb_page`
 - For running specific cron: 
```
 - Set up cron to run for comment: Model-social.integrate, model.get_actions(`[post_id]`, 'comment')
 - Set up cron to run for like: model.get_actions(`[1960711184230057]`, 'like')
```