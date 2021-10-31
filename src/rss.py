from typing import List

from lxml import etree
from podgen import Podcast, Episode
from podgen.util import formatRFC2822

from base import Message
from pocket_casts import PocketCasts
from requests_xml import XML

CLOSING_CHANNEL_TAG = "</channel>"

name = "פודקאסט פלייליסט"
description = """ערוץ עידכוני הפרקים של יוליה שנרר. כאן תמצאו המלצות על פרקים מפודקאסטים שונים. אין סדר או העדפה מסוימים, מה שנשמע מעניין באותו שבוע.

ניתן לחפש בערוץ בעזרת האשתגים: #שיווק #כלכלה ועוד... 

דברו איתי כאן:
https://www.linkedin.com/in/yuliashnerer"""
website = "https://t.me/podcastsrec"
image_url = "https://github.com/bityob/podcasts-list-to-rss/raw/main/assets/podcast-image.jpg"


class RssGenerator:
    def __init__(self, messages: List[Message]):
        self.p = Podcast(
            name=name,
            description=description,
            website=website,
            explicit=False,
            image=image_url,
        )
        self.messages = messages

    def create_rss(self):
        """
        Need to take the original xml item string and change only those fields:
        * pubDate - use telegram Message date
        * description - prepand the orignal text with the Message text
        """

        # Rss with only basic fields
        rss_string = str(self.p)

        for message in self.messages:
            try:
                print(f"Message id={message.id}...")

                url = next(url for url in [message.url] + message.urls if PocketCasts.is_valid_url(url))

                print(f"Found url={url}")

                connector = PocketCasts(url)

                print(f"title={connector.item_title}")
                item = str(connector.item)
                        
                # Replace item fields

                # Replace publish date
                xml_item = XML(xml=item)
                xml_item.lxml.find("pubDate").text = formatRFC2822(message.date)
                print(f"after={xml_item.lxml.find('pubDate').text}")

                # Prepand text to description
                original_text = xml_item.lxml.find("description").text
                message_text = message.text.replace("\n", "<br>")
                new_text = f"{message_text}<br><br><br>#######<br><br><br>{original_text}"

                xml_item.lxml.find("description").text = new_text
                
                try:
                    itunes_summary = xml_item.lxml.find("itunes:summary", namespaces=xml_item.lxml.nsmap)
                    if itunes_summary is not None:
                        itunes_summary.text = new_text
                except:
                    pass
                
                try:
                    content_encoded = xml_item.lxml.find("content:encoded", namespaces=xml_item.lxml.nsmap)
                    if content_encoded is not None:
                        content_encoded.text = new_text
                except:
                    pass

                # Must use the `lxml` and not the `xml`, because we change it 
                xml_string = etree.tostring(xml_item.lxml, encoding='utf8').decode('utf8')

                
                rss_string = rss_string.replace(CLOSING_CHANNEL_TAG, f"{xml_string}{CLOSING_CHANNEL_TAG}")
            except Exception as ex:
                import pdb; pdb.set_trace()
                print(f"Failed with message id={message.id}, error={ex}, text={message.text}")

        return rss_string
