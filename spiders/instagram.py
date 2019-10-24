import scrapy
import json

class InstagramSpider(scrapy.Spider):
    name = "instagram"

    def start_requests(self):
        self.account = input("Account Name: ")
        url = "https://www.instagram.com/" + self.account + "/?__a=1"
        yield scrapy.Request(url=url)

    def parse(self, response):
        graphql = json.loads(response.text)
        user = graphql['graphql']['user']
        username = user['username']
        edges = user['edge_owner_to_timeline_media']['edges']
        bio = user['biography']
        user_id = user['id']
        follower = user['edge_followed_by']['count']
        following = user['edge_follow']['count']
        posts = user['edge_owner_to_timeline_media']['count']
        medias = []
        if not user['is_private']:
            for media in edges:
                caption_list = media['node']['edge_media_to_caption']["edges"]
                caption = ""
                for cap in caption_list:
                    caption = cap["node"]["text"]
                url = media["node"]["display_url"]

                medias.append({"url": url, "caption": caption})
        elif user['is_private']:
            medias.append({"AccountPrivate": 1})

        yield {'_id': username, 'accountId': user_id, 'biography': bio, 'follower': follower, 'following': following,
               'numberOfPosts': posts, 'medias': medias}
        for edge in edges:
            shortCode = edge['node']['shortcode']
            yield scrapy.Request("https://www.instagram.com/p/" + shortCode + "/?__a=1", callback=self.parseComment)

    def parseComment(self, response):
        graphql_comment = json.loads(response.text)
        short_code_media = graphql_comment['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']
        for userName in short_code_media:
            user_comment = userName['node']['owner']['username']
            yield scrapy.Request("https://www.instagram.com/" + user_comment + "/?__a=1")
