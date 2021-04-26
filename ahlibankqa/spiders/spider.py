import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import AhlibankqaItem
from itemloaders.processors import TakeFirst


class AhlibankqaSpider(scrapy.Spider):
	name = 'ahlibankqa'
	start_urls = ['https://www.ahlibank.com.qa/subwide.aspx?pageid=724']

	def parse(self, response):
		post_links = response.xpath('//div[@class="img"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="loadMore"]/a/@href').getall()
		print(next_page)
		if next_page:
			yield FormRequest.from_response(response, formdata={
				'__EVENTTARGET': 'ctl00$cpMainContent$BICMSZone1$ctl00$ctl00$btnMore'}, callback=self.parse, method='POST')

	def parse_post(self, response):
		title = response.xpath('//div[@class="newsDetailsContent"]/h2/text()[normalize-space()]').get()
		description = response.xpath('//div[@class="newsDetailsContent"]//text()[normalize-space() and not(ancestor::h2 | ancestor::div[@class="newsDate"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="newsDate"]/text()').get()

		item = ItemLoader(item=AhlibankqaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
