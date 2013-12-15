import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob

class MRArticleJoiner(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol       

    def mapper(self, key, article):
        if 'wikiTitle' in article and 'lang' in article:
            title = article['wikiTitle']
            lang = article['lang']
        
            yield title, (article,lang)

    def reducer(self, title, articles_lang):
        articles = []
        for a in articles_lang:
            articles.append(a)

        if len(articles) == 2:
            join_result = {
                'wikiTitle': title,
                'en': None,
                'simple': None
                }
            
            for (article,lang) in articles:
                join_result[lang] = article
                
            yield None, join_result

if __name__ == '__main__':
    MRArticleJoiner.run()
