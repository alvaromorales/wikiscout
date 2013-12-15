import re
import sys
import json

import mrjob.util
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob

from start import infobox
from start import sentence

class MRExtractor(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def configure_options(self):
        super(MRExtractor, self).configure_options()
        self.add_file_option('--attributes')

    def mapper_init(self):
        f = open(self.options.attributes)
        top_attributes = {}
        for l in f:
            template_attrs = json.loads(l.strip())            
            top_attributes[template_attrs['template']] = set([a['attribute'] for a in template_attrs['attributes']])
            
        self.top_attributes = top_attributes

    def mapper(self, key, joined_article):
        title = joined_article['wikiTitle']
        en_article = joined_article['en']
        simple_article = joined_article['simple']

        if 'infobox' not in en_article:
            return
        
        article_infobox = infobox.parse(en_article['infobox']['name'], en_article['infobox']['description'])

        if article_infobox is None:
            return
        
        infobox_type = infobox.normalize_template(article_infobox.name)

        if infobox_type not in self.top_attributes:
            return

        matching_attributes = {}
        
        for attribute, value in infobox.get_items(article_infobox):
            if attribute in self.top_attributes[infobox_type] and attribute not in infobox.ignore_attributes:
                matching_attributes[attribute] = value

        simple_sentences = sentence.get(simple_article['paragraphs'])
        candidate_sentences = {}

        for attribute,value in matching_attributes.items():
            attribute_matches = []
            if not infobox.validate_value(value):
                continue

            for s in simple_sentences:
                if sentence.has_value(s,value):
                    attribute_matches.append({'sentence':s,'value':value,'wikiTitle':title})

            if attribute not in candidate_sentences:
                candidate_sentences[attribute] = []
            
            map(lambda c: candidate_sentences[attribute].append(c), attribute_matches)

        for attribute,candidates in candidate_sentences.items():
            yield (attribute,infobox_type), candidates

    def reducer_attributes(self, attribute_infobox, candidates):
        attribute, infobox_type = attribute_infobox

        candidate_sentences = {
            'attribute' : attribute,
            'sentences' : []
            }
        
        for candidate_group in candidates:
            for c in candidate_group:
                candidate_sentences['sentences'].append(c)

        if len(candidate_sentences['sentences']) > 0:
            yield infobox_type, candidate_sentences
    
    def mapper_infobox_type(self,infobox_type,candidates):
        yield infobox_type,candidates

    def reducer_infobox_type(self,infobox_type,candidates):
        infobox_type_candidates = {
            'infobox_type': infobox_type,
            'attributes' : {}
            }
        
        for c in candidates:
            infobox_type_candidates['attributes'][c['attribute']] = c['sentences']

        yield None, infobox_type_candidates
        
    def steps(self):
        return [
            self.mr(mapper_init=self.mapper_init,
                    mapper=self.mapper,
                    reducer=self.reducer_attributes),
            self.mr(mapper=self.mapper_infobox_type,
                    reducer=self.reducer_infobox_type)
        ]

if __name__ == '__main__':
    MRExtractor.run()
