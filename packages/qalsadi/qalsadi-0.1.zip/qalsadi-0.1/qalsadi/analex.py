#!/usr/bin/python
# -*- coding=utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        analex
# Purpose:     Arabic lexical analyser, provides feature to stem arabic words as noun, verb, stopword 
#
# Author:      Taha Zerrouki (taha.zerrouki[at]gmail.com)
#
# Created:     31-10-2011
# Copyright:   (c) Taha Zerrouki 2011
# Licence:     GPL
#-------------------------------------------------------------------------------
import re
import pyarabic.araby as araby  # basic arabic text functions
import stem_noun		# noun stemming 
import stem_verb		# verb stemming
import stem_unknown		# unknown word stemming
import stem_pounct_const # pounctaution constants 
import stopwords #s topwords list
import naftawayh.wordtag
import wordfreqdictionaryclass
class analex :
	"""
		Arabic text morphological analyzer.
		Provides routins  to alanyze text.
		Can treat text as verbs or as nouns.
	"""


	def __init__(self):
		"""
		Create Analex instance.
		"""
		#print "len stop words",len(stopwords.STOPWORDS);
		self.nounstemmer=stem_noun.nounStemmer(); # to stem nouns
		self.verbstemmer=stem_verb.verbStemmer(); # to stem verbs
		self.unknownstemmer=stem_unknown.unknownStemmer(); # to stem unknown		
		self.tagger=naftawayh.wordtag.WordTagger();
		self.debug=False; # to allow to print internal data
		self.limit=10000; # limit words in the text
		
		# the words contain arabic letters and harakat.
		# the unicode considers arabic harakats as marks not letters,
		# then we add harakat to the regluar expression to tokenize
		marks=u"".join(araby.TASHKEEL)# contains [FATHA,DAMMA,KASRA,SUKUN,DAMMATAN,KASRATAN,FATHATAN,SHADDA])
		# used to tokenize arabic text
		self.token_pat=re.compile(u"([\w%s]+)"%marks,re.UNICODE);				
		# allow partial vocalization support, 
		#~The text is analyzed as partial or fully vocalized.
		self.partial_vocalization_support=True;
		
		#word frequency dictionary
		self.wordfreq= wordfreqdictionaryclass.wordfreqDictionary('wordfreq', wordfreqdictionaryclass.wordfreq_DICTIONARY_INDEX);


	def text_treat(self,text):
		""" deprecated: treat text to eliminate pountuation.
		@param text: input text;
		@type text: unicode;
		@return : treated text.
		@rtype: unicode.
		"""
		return text;


	def tokenize(self,text=u""):
		"""
		Tokenize text into words
		@param text: the input text.
		@type text: unicode.
		@return: list of words.
		@rtype: list.
		"""
		if text==u'':
			return [];
		else:
			mylist= self.token_pat.split(text)
			for i in range(len(mylist)):
				mylist[i]=re.sub("\s",'',mylist[i]);
			while u'' in mylist: mylist.remove(u'');
			#print u"'".join(mylist).encode('utf8');
			return mylist;


	def text_tokenize(self,text):
		"""
		Tokenize text into words, after treatement.
		@param text: the input text.
		@type text: unicode.
		@return: list of words.
		@rtype: list.
		"""	
		text=self.text_treat(text);
		list_word=self.tokenize(text);
		return list_word;

	def set_debug(self,debug):
		"""
		Set the debug attribute to allow printing internal analysis results.
		@param debug: the debug value.
		@type debug: True/False.
		"""
		self.debug=debug;
		self.nounstemmer.set_debug(debug); # to set debug on noun stemming
		self.verbstemmer.set_debug(debug); # to set debug on verb stemming

	def set_limit(self,limit):
		"""
		Set the number of word treated in text.
		@param limit: the word number limit.
		@type limit: integer.
		"""
		self.limit=limit;


	def check_text(self,text, mode='all'):
		"""
		Analyze text morphologically
		@param text: the input text.
		@type text: unicode.
		@param mode: the mode of analysis as 'verbs', 'nouns', or 'all'.
		@type mode: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""
		list_word=self.text_tokenize(text);
		resulted_text=u""
		resulted_data=[];
		checkedWords={};
		if mode=='all':
			for word in list_word [:self.limit]:
				if checkedWords.has_key(word):
					resulted_data.append(checkedWords[word]);
				else:
					one_data_list=self.check_word(word);
					resulted_data.append(one_data_list);
					checkedWords[word]=one_data_list;
		elif mode=='nouns':
			for word in list_word[:self.limit] :
				one_data_list=self.check_word_as_noun(word);
				resulted_data.append(one_data_list);
		elif mode=='verbs':
			for word in list_word[:self.limit] :
				one_data_list=self.check_word_as_verb(word);
				resulted_data.append(one_data_list);
		return resulted_data;


	def check_text_as_nouns(self,text):
		"""
		Analyze text morphologically as nouns
		@param text: the input text.
		@type text: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""
		return self.check_text(text,"nouns");


	def check_text_as_verbs(self,text):
		"""
		Analyze text morphologically as verbs
		@param text: the input text.
		@type text: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""	
		return self.check_text(text,"verbs");


	def check_word(self,word):
		"""
		Analyze one word morphologically as verbs
		@param word: the input word.
		@type word: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""	
		word=araby.stripTatweel(word);
		word_vocalised=word;
		word_nm=araby.stripTashkeel(word);
		resulted_text=u"";
		resulted_data=[];
		
		# if word is a pounctuation
		resulted_data+=self.check_word_as_pounct(word_nm);

		# if word is stopword
		resulted_data+=self.check_word_as_stopword(word_nm);

		# Todo: if the word is a stop word we have  some problems,
		# the stop word can also be another normal word (verb or noun),
		# we must consider it in future works
		if len(resulted_data)==0:

			#TodDo guessing word type

			#if word is verb
			rabti=len(resulted_data)
			if self.tagger.is_verb(word_nm):
				resulted_data+=self.check_word_as_verb(word_nm);
				print "is verb", rabti,len(resulted_data);
			#if word is noun
			if self.tagger.is_noun(word_nm):			
				resulted_data+=self.check_word_as_noun(word_nm);
			
			#check if the word is nomralized and sollution are equivalent
			resulted_data=self.check_normalized(word_vocalised,resulted_data)
			#check if the word is shadda like
			resulted_data=self.check_shadda(word_vocalised,resulted_data)

			#check if the word is vocalized like results			
			if self.partial_vocalization_support:
				resulted_data=self.check_partial_vocalized(word_vocalised,resulted_data);

		if len(resulted_data)==0:
			#check the word as unkonwn
			resulted_data+=self.check_word_as_unknown(word_nm);
		if len(resulted_data)==0:
			resulted_data.append({
			'word':word,
			'procletic':'',
			'encletic':'',
			'prefix':'',
			'suffix':'',
			'stem':'',
			'original':'',
			'vocalized':'',
			'tags':u'',
			'type':'unknown',
			'root':'',
			'template':'',
			'freq':self.wordfreq.getFreq(word, 'unknown'),
			});
		return resulted_data;


	def check_normalized(self, word_vocalised,resulted_data):
		"""
		If the entred word is like the found word in dictionary, to treat some normalized cases, 
		the analyzer return the vocalized like words;
		ُIf the word is ذئب, the normalized form is ذءب, which can give from dictionary ذئبـ ذؤب.
		this function filter normalized resulted word according the given word, and give ذئب.
		@param word_vocalised: the input word.
		@type word_vocalised: unicode.
		@param resulted_data: the founded resulat from dictionary.
		@type resulted_data: list of dict.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""
		#print word_vocalised.encode('utf8');
		filtred_data=[];
		inputword=araby.stripTashkeel(word_vocalised)
		for item in  resulted_data:
			if item.has_key('vocalized') :
				outputword=araby.stripTashkeel(item['vocalized'])
				if inputword==outputword:
					#item['tags']+=':a';
					filtred_data.append(item);
		return  filtred_data;


	def check_shadda(self, word_vocalised,resulted_data):
		"""
		if the entred word is like the found word in dictionary, to treat some normalized cases, 
		the analyzer return the vocalized like words.
		This function treat the Shadda case.
		@param word_vocalised: the input word.
		@type word_vocalised: unicode.
		@param resulted_data: the founded resulat from dictionary.
		@type resulted_data: list of dict.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""
		#print word_vocalised.encode('utf8');
		filtred_data=[];
		for item in  resulted_data:
			if item.has_key('vocalized')  and araby.shaddalike(word_vocalised, item['vocalized']):
				#item['tags']+=':a';
				filtred_data.append(item);
		return  filtred_data;		


	def check_partial_vocalized(self, word_vocalised,resulted_data):
		"""
		if the entred word is vocalized fully or partially, 
		the analyzer return the vocalized like words;
		This function treat the partial vocalized case.
		@param word_vocalised: the input word.
		@type word_vocalised: unicode.
		@param resulted_data: the founded resulat from dictionary.
		@type resulted_data: list of dict.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.		
		"""
		#print word_vocalised.encode('utf8');
		filtred_data=[];
		if not araby.isVocalized(word_vocalised):
			return resulted_data;
		else:
			#compare the vocalized output with the vocalized input
			#print ' is vocalized';
			for item in  resulted_data:
				if item.has_key('vocalized') and araby.vocalizedlike(word_vocalised,item['vocalized']):
					item['tags']+=':v';
					filtred_data.append(item);
			return  filtred_data;


	def check_word_as_stopword(self,word):
		"""
		Check if the word is a stopword, 
		@param word: the input word.
		@type word: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.		
		"""	
		detailed_result=[]
		if stopwords.STOPWORDS.has_key(word):
			detailed_result.append({
			'word':word,
			'procletic':stopwords.STOPWORDS[word]['procletic'],
			'encletic':stopwords.STOPWORDS[word]['encletic'],
			'prefix':'',
			'suffix':'',
			'stem':stopwords.STOPWORDS[word]['stem'],
			'original':stopwords.STOPWORDS[word]['original'],
			'vocalized':stopwords.STOPWORDS[word]['vocalized'],
			'tags':stopwords.STOPWORDS[word]['tags'],
			'type':'STOPWORD',
			'root':'',
			'template':'',
			'freq':self.wordfreq.getFreq(stopwords.STOPWORDS[word]['vocalized'], 'stopword'),			
			});
		return detailed_result
		


	def check_word_as_pounct(self,word):
		"""
		Check if the word is a pounctuation, 
		@param word: the input word.
		@type word: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.		
		"""		
		detailed_result=[]
		if word.isnumeric():
			detailed_result.append({
			'word':word,
			'procletic':'',
			'encletic':'',
			'prefix':'',
			'suffix':'',
			'stem':'',
			'original':'',
			'vocalized':'',
			'tags':self.get_number_tags(word),
			'type':'NUMBER',
			'root':'',
			'template':'',
			'freq':0,			
			});	
		if stem_pounct_const.POUNCTUATION.has_key(word):

			detailed_result.append({
			'word':word,
			'procletic':'',
			'encletic':'',
			'prefix':'',
			'suffix':'',
			'stem':'',
			'original':'',
			'vocalized':'',
			'tags':stem_pounct_const.POUNCTUATION[word]['tags'],
			'type':'POUNCT',
			'root':'',
			'template':'',
			'freq':0,			
			});
		return detailed_result;


	def check_word_as_verb(self,verb):
		"""
		Analyze the word as verb.
		@param verb: the input word.
		@type verb: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.		
		"""	
		detailed_result=self.verbstemmer.stemming_verb(verb)
		return detailed_result;


	def check_word_as_noun(self,noun):
		"""
		Analyze the word as noun.
		@param noun: the input word.
		@type noun: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""

		detailed_result=self.nounstemmer.stemming_noun(noun)
		return detailed_result;


	def check_word_as_unknown(self,noun):
		"""
		Analyze the word as unknown.
		@param noun: the input word.
		@type noun: unicode.
		@return: list of dictionaries of analyzed words with tags.
		@rtype: list.
		"""

		detailed_result=self.unknownstemmer.stemming_noun(noun)
		return detailed_result;

	def context_analyze(self,result):
		"""
		Deprecated: Analyze the context.
		@param result: analysis result.
		@type result: list of dict.
		@return: filtred relust according to context.
		@rtype: list.
		"""	
		detailed_result=result;
		return detailed_result;
	def get_number_tags(self, word):
		"""
		Check the numbers and return tags.
		@param word: the input word.
		@type word: unicode.
		@return: tags.
		@rtype: text.
		"""	
		return u"عدد";

