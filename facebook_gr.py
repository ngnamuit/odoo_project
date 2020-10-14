import facebook
import requests

access_token = 'EAAd7ijYZCOAcBABFXJFQFs3FHZAFQO4ln9lczTTWPtoRW4nZBTfKHDkCAUw6yfGf2Es6FotaL5umLP8bqqTzbQTvDXACZB2ns50CvJmYGriQDEJ60GSxrKm9GCqD1X5ZA9cRlyCNaktB9WiMmRhS5xqszZCMKfPGl4mA9CwZCmspNdycRid5GSi1T62Md2wTnn5zUGHB5mgMwZDZD'

graph = facebook.GraphAPI(access_token)
print(f"graph == {graph}")
graph.put_object("This is message for testing", "feed")



"""
curl -i -X GET "https://graph.facebook.com/1471296016504912_1960711184230057/reactions?access_token=EAAFZCeNVXZBLgBAGAMldZAPZANcPWFumw0Hs85lOn31hHgjdeYquxZBcIvBnyIH5KGkMZBbeJIDnL3fnG51ieoH8Sp3lkm908WefGN4QO90Vs0cbOZAHAeEYbW4na2ZCVmpsS3UcjTrL3KsAbFBNP7zQ3ydz2dJeZAs0Scbdkt9AExSTjSTiwsfNa1DTFGdZBtjJKL1XcwYj1zYgZDZD"
                                            # your_app_id  _    post_id/reactions?access_token=access_token
                                            
link to get token without expired date: https://business.facebook.com/
token:                                            
                                            
"""



