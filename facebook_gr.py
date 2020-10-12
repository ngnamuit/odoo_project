import facebook
import requests

access_token = 'EAAd7ijYZCOAcBABFXJFQFs3FHZAFQO4ln9lczTTWPtoRW4nZBTfKHDkCAUw6yfGf2Es6FotaL5umLP8bqqTzbQTvDXACZB2ns50CvJmYGriQDEJ60GSxrKm9GCqD1X5ZA9cRlyCNaktB9WiMmRhS5xqszZCMKfPGl4mA9CwZCmspNdycRid5GSi1T62Md2wTnn5zUGHB5mgMwZDZD'

graph = facebook.GraphAPI(access_token)
print(f"graph == {graph}")
graph.put_object("This is message for testing", "feed")


curl -i -X GET "https://graph.facebook.com/v7.0/102384894979771_102385854979675?fields=likes.summary(true)&access_token=EAAd7ijYZCOAcBABFXJFQFs3FHZAFQO4ln9lczTTWPtoRW4nZBTfKHDkCAUw6yfGf2Es6FotaL5umLP8bqqTzbQTvDXACZB2ns50CvJmYGriQDEJ60GSxrKm9GCqD1X5ZA9cRlyCNaktB9WiMmRhS5xqszZCMKfPGl4mA9CwZCmspNdycRid5GSi1T62Md2wTnn5zUGHB5mgMwZDZD"


curl -i -X GET "https://graph.facebook.com/1471296016504912_1960711184230057/reactions?access_token=EAAFZCeNVXZBLgBALaVFZBZCtoqoPGd2ycNgQ4RKvJTbgNogsl3k33bIcq9WGLOSjZCgHWA9TLdI1ykjvNET1XKFhFZAAmqgFZAGYOiNXOYJ5uo67h9X3jNbs0pRFl8Rkl1ZCjZBNYQkkmXGBmetWnbZCylFdqcdweNoZBZAZArumzgEPBjofqgmZAzidCjDysXEk48PCvHXVjFusdclwZDZD"
                                            # your_app_id  _    post_id/reactions?access_token=access_token



