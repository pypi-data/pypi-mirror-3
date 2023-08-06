#!/usr/bin/python
# -*- coding=utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        stem_verb
# Purpose:     Arabic lexical analyser, provides feature for stemming arabic word as verb
#
# Author:      Taha Zerrouki (taha.zerrouki[at]gmail.com)
#
# Created:     31-10-2011
# Copyright:   (c) Taha Zerrouki 2011
# Licence:     GPL
#-------------------------------------------------------------------------------
import re
import tashaphyne.stemming
import pyarabic.araby as araby

import libqutrub.triverbtable
import stem_verb_const 
import libqutrub.classverb   
import arabicdictionary 
import wordfreqdictionaryclass
#import dictionaries.verb_dictionary 



class verbStemmer:
	"""
        Arabic verb stemmer
	"""

	def __init__(self,debug=False):
		# create a stemmer object for stemming enclitics and procletics
		self.compStemmer=tashaphyne.stemming.ArabicLightStemmer();

		# configure the stemmer object
		self.compStemmer.set_infix_letters(stem_verb_const.COMP_INFIX_LETTERS);
		self.compStemmer.set_prefix_letters(stem_verb_const.COMP_PREFIX_LETTERS);
		self.compStemmer.set_suffix_letters(stem_verb_const.COMP_SUFFIX_LETTERS);
		self.compStemmer.set_max_prefix_length(stem_verb_const.COMP_MAX_PREFIX);
		self.compStemmer.set_max_suffix_length(stem_verb_const.COMP_MAX_SUFFIX);
		self.compStemmer.set_min_stem_length(stem_verb_const.COMP_MIN_STEM);
		self.compStemmer.set_prefix_list(stem_verb_const.COMP_PREFIX_LIST);
		self.compStemmer.set_suffix_list(stem_verb_const.COMP_SUFFIX_LIST);


		# create a stemmer object for stemming conjugated verb
		self.conjStemmer=tashaphyne.stemming.ArabicLightStemmer();

		# configure the stemmer object
		self.conjStemmer.set_infix_letters(stem_verb_const.CONJ_INFIX_LETTERS);
		self.conjStemmer.set_prefix_letters(stem_verb_const.CONJ_PREFIX_LETTERS);
		self.conjStemmer.set_suffix_letters(stem_verb_const.CONJ_SUFFIX_LETTERS);
		self.conjStemmer.set_max_prefix_length(stem_verb_const.CONJ_MAX_PREFIX);
		self.conjStemmer.set_max_suffix_length(stem_verb_const.CONJ_MAX_SUFFIX);
		self.conjStemmer.set_min_stem_length(stem_verb_const.CONJ_MIN_STEM);
		self.conjStemmer.set_prefix_list(stem_verb_const.CONJ_PREFIX_LIST);
		self.conjStemmer.set_suffix_list(stem_verb_const.CONJ_SUFFIX_LIST);
		print 'stem_verb_const.CONJ_PREFIX_LETTERS', stem_verb_const.CONJ_PREFIX_LETTERS.encode('utf8');
		# To show statistics about verbs
		statistics={0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0, 20:0,
		}
		#create index for dictionary to accelerate verb search
		VERB_DICTIONARY_INDEX={
		u'id':0,
		u'vocalized':1,
		u'unvocalized':2,
		u'root':3,
		u'normalized':4,
		u'stamped':5,
		u'future_type':6,
		u'triliteral':7,
		u'transitive':8,
		u'double_trans':9,
		u'think_trans':10,
		u'unthink_trans':11,
		u'reflexive_trans':12,
		u'past':13,
		u'future':14,
		u'imperative':15,
		u'passive':16,
		u'future_moode':17,
		u'confirmed':18,
			}
		self.TriVerbTable_INDEX={};
		self.Table_affix_INDEX={};
		self.VERB_DICTIONARY_STAMP={
        }
		self.create_index_affix()
		self.debug=debug;

		
		self.verbDictionary=arabicdictionary.arabicDictionary("verbs", VERB_DICTIONARY_INDEX)
		#self.triVerbDictionary=arabicdictionary.arabicDictionary("verbs", VERB_DICTIONARY_INDEX)
		
		#word frequency dictionary
		self.wordfreq= wordfreqdictionaryclass.wordfreqDictionary('wordfreq', wordfreqdictionaryclass.wordfreq_DICTIONARY_INDEX);

	def stemming_verb(self,verb):
		list_found=[];
		display_conj_result=False;
		detailed_result=[];
		verb=verb.strip();
		verb_list=[verb];
		if verb.startswith(araby.ALEF_MADDA):
			verb_list.append(araby.ALEF_HAMZA_ABOVE + araby.ALEF_HAMZA_ABOVE+verb[1:])
			verb_list.append(araby.HAMZA+araby.ALEF+verb[1:])

		for verb in verb_list:

			list_seg_comp=self.compStemmer.segment(verb);
			for seg in list_seg_comp:
				procletic=verb[:seg[0]];
				stem=verb[seg[0]:seg[1]]
				encletic=verb[seg[1]:]
				secondsuffix=u'';
				# حالة الفعل المتعدي لمفعولين
				if stem_verb_const.TableDoubleTransitiveSuffix.has_key(encletic ):
					firstsuffix=stem_verb_const.TableDoubleTransitiveSuffix[encletic]['first'];
					secondsuffix=stem_verb_const.TableDoubleTransitiveSuffix[encletic]['second'];
					encletic=firstsuffix;


				affix=u'-'.join([procletic,encletic])
				if self.debug: print "\t", "-".join([procletic,stem,encletic]).encode("utf8") ;
				# ajusting verbs variant
				list_stem=[stem];
				if encletic!="":
					transitive=True;
					if stem.endswith(araby.TEH + araby.MEEM + araby.WAW):
						list_stem.append(stem[:-1]);
					elif stem.endswith(araby.WAW):
						list_stem.append(stem+ araby.ALEF);
					elif stem.endswith( araby.ALEF):
						list_stem.append(stem[:-1]+ araby.ALEF_MAKSURA);

				else: transitive=False;
				if verb.startswith(araby.ALEF_MADDA):
					# االبداية بألف مد
					list_stem.append(araby.ALEF_HAMZA_ABOVE + araby.ALEF_HAMZA_ABOVE+verb[1:])
					list_stem.append(araby.HAMZA+ araby.ALEF+verb[1:])

		# stem reduced verb : level two
				result=[];
				for verb2 in list_stem:
					#segment the coinjugated verb
					list_seg_conj=self.conjStemmer.segment(verb2);
					if self.debug: print len(list_seg_conj), self.conjStemmer.get_affix_list()#.encode('utf8');
					if self.debug: print self.conjStemmer.get_prefix_list(), self.conjStemmer.get_prefix_letters()#.encode('utf8');

					# verify affix compatibility
					list_seg_conj=self.verify_affix(verb2,list_seg_conj, stem_verb_const.VERBAL_CONJUGATION_AFFIX);
					# verify procletics and enclitecs
					# verify length pof stem
					list_seg_conj2=[];
					for seg_conj in list_seg_conj:
						if (seg_conj[1]- seg_conj[0])<=6 :
							prefix_conj=verb2[:seg_conj[0]];
							stem_conj=verb2[seg_conj[0]:seg_conj[1]]
							suffix_conj=verb2[seg_conj[1]:]
							affix_conj=prefix_conj+'-'+suffix_conj;


						# verify compatibility between procletics and afix
							if (self.is_compatible_proaffix_affix(procletic, encletic, affix_conj)):
								# verify the existing of a verb stamp in the dictionary
								if self.verbDictionary.existsAsStamp(stem_conj):
									list_seg_conj2.append(seg_conj)

					list_seg_conj=list_seg_conj2;

					list_correct_conj=[];

					for seg_conj in list_seg_conj:
						prefix_conj=verb2[:seg_conj[0]];
						stem_conj=verb2[seg_conj[0]:seg_conj[1]]
						suffix_conj=verb2[seg_conj[1]:]
						affix_conj='-'.join([prefix_conj,suffix_conj])

							
						# search the verb in the dictionary by stamp
						# if the verb exists in dictionary,
						# The transitivity is consedered
						# if is trilateral return its forms and Tashkeel
						# if not return forms without tashkeel, because the conjugator can vocalized it,
						# we can return the tashkeel if we don't need the conjugation step						
						infverb_dict=self.getInfinitiveVerbByStem(stem_conj, transitive);


						for item in infverb_dict:
							#The haraka from is given from the dict

							inf_verb=item['verb'];
							haraka=item['haraka'];
							unstemed_verb=verb2;

							# conjugation step

							# ToDo, conjugate the verb with affix,
							# if exists one verb which match, return it
							# تصريف الفعل مع الزوائد
							# إذا توافق التصريف مع الكلمة الناتجة
							# تعرض النتيجة
							onelist_correct_conj=[];
							onelist_correct_conj=self.generate_possible_conjug(inf_verb,unstemed_verb,affix_conj,haraka,procletic,encletic);

							if len(onelist_correct_conj)>0:
								list_correct_conj+=onelist_correct_conj;
					for conj in list_correct_conj:
						if display_conj_result:print "\t\t","\t".join([conj['verb'], conj['vocalized'], conj['tense'],conj['pronoun']]).encode('utf8')
						result.append(conj['verb'])
						detailed_result.append({
						'word':verb,
						'procletic':procletic,
						'encletic':encletic,
						'prefix':prefix_conj,
						'suffix':suffix_conj,
						'stem':stem_conj,
						'original':conj['verb'],
						'vocalized':self.vocalize(conj['vocalized'],procletic,encletic),
						'tags':u':'.join((conj['tense'],conj['pronoun'])+stem_verb_const.COMP_PREFIX_LIST_TAGS[procletic]['tags']+stem_verb_const.COMP_SUFFIX_LIST_TAGS[encletic]['tags']),
						'type':'Verb',
						'root':'',
						'template':'',
						'freq':self.wordfreq.getFreq(conj['verb'],'verb'),
						});

	##				result+=detect_arabic_verb(verb2,transitive,prefix_conj,suffix_conj,debug);
				list_found+=result;

		list_found=set(list_found);
		return detailed_result

	def create_index_affix(self):
		""" create index from the affix dictionary
		to accelerate the search in the dictionary for verbs
		"""

		for key in stem_verb_const.Table_affix.keys():
			self.Table_affix_INDEX[key]={'tenses':[],'pronouns':[]};
			for item in stem_verb_const.Table_affix[key]:
				self.Table_affix_INDEX[key]['tenses'].append(item[0])
				self.Table_affix_INDEX[key]['pronouns'].append(item[1])

	
	def verify_affix(self,word,list_seg,affix_list):

		list_segTemp=set(list_seg);
		# empty the list_seg
		list_seg=set();
		#look up in a affix list
		for s in list_segTemp:
			affix=affix='-'.join([word[:s[0]],word[s[1]:]]);
			if affix in affix_list:
				list_seg.add(s);
		return list_seg;





	def getInfinitiveVerbByStem(self,verb, transitive):
		# a solution by using verbs stamps
		liste=[];
		
		verbIdList=self.verbDictionary.lookupByStamp(verb);
		#print 'len list verb id', len(verbIdList), len(set(verbIdList));

		if len(verbIdList):
			for id in verbIdList:
				verb_tuple=self.verbDictionary.getEntryById(id);
				liste.append({'verb':verb_tuple['vocalized'],'transitive':verb_tuple['transitive'],'haraka':verb_tuple['future_type']});

		# #lookup in triverb dict
		# verbIdList=self.triVerbDictionary.lookupByStamp(verb);
		# print 'len list triverb id', len(verbIdList), len(set(verbIdList));
		
		# if len(verbIdList):
			# for id in verbIdList:
				# verb_tuple=self.triVerbDictionary.getEntryById(id);
				# liste.append({'verb':verb_tuple['vocalized'],'transitive':verb_tuple['transitive'],'haraka':verb_tuple['future_type']});

		# if the verb in dictionary is vi and the stemmed verb is vt, don't accepot
		listetemp=liste;
		liste=[]
		for item in listetemp:
			##        print item['transitive'].encode("utf8"),transitive
			if item['transitive']==u'y' or  not transitive:
				liste.append(item);

		return liste;

	#----------------------------
	# generate possible conjugation
	# This function uses Qutrub conjugator
	#----------------------------
	def generate_possible_conjug(self,infinitive_verb,unstemed_verb ,affix,future_type=araby.FATHA,externPrefix="-",externSuffix="-"):
	##    future_type=FATHA;
		transitive=True;
		list_correct_conj=[];
		if infinitive_verb=="" or unstemed_verb=="" or affix=="":
			return set();
		verb=infinitive_verb;
		future_type=libqutrub.ar_verb.get_future_type_entree(future_type);
		#print u"\t".join([verb, future_type]).encode('utf8');
		vb=libqutrub.classverb.verbclass(verb,transitive,future_type);
		# الألف ليست جزءا من السابقة، لأنها تستعمل لمنع الابتداء بساكن
		# وتصريف الفعل في الامر يولده
		if affix.startswith(araby.ALEF):affix=affix[1:]
		if stem_verb_const.Table_affix.has_key(affix):
			for pair in stem_verb_const.Table_affix[affix]:
				tense=pair[0]
				#print "-0--",tense.encode("utf8")#,unstemed_verb.encode("utf8");
				
				pronoun=pair[1]
	##                print "-----",
				if self.is_compatible_proaffix_tense(externPrefix,externSuffix,tense,pronoun):
					#print "-1--",tense.encode("utf8")
					result=vb.conjugate_all_tenses([tense,]);
					conj_vocalized=vb.conj_display.tab_conjug[tense][pronoun];
					#strip all marks and shadda
					#if conj_vocalized=="":
					#	print u":".join([verb,tense,pronoun,future_type]).encode('utf8');
					conj_nm=araby.stripTashkeel(conj_vocalized);
					#print "-----",conj_vocalized.encode("utf8"),verb.encode("utf8"),unstemed_verb.encode("utf8");
	##                conj_nm=conj_vocalised;
					if conj_nm==unstemed_verb:
						list_correct_conj.append({'verb':infinitive_verb,'tense':tense,'pronoun':pronoun,'vocalized':conj_vocalized,'unvocalized':conj_nm});
						#print u'\t'.join([infinitive_verb,tense, pronoun,conj_vocalized]).encode('utf8');
		return list_correct_conj;

	def is_compatible_proaffix_affix(self,procletic, encletic, affix):
		"""
		Verify if proaffixes (sytaxic affixes) are compatable with affixes ( conjugation) 
		@param procletic: first level prefix.
		@type procletic: unicode.
		@param encletic: first level suffix.
		@type encletic: unicode.
		@param affix: second level affix.
		@type affix: unicode.
		@return: compatible.
		@rtype: True/False.
		"""	
		if procletic==u'' and encletic==u'':  return True;

		else:

			procletic_compatible=False;
			if procletic==u'' :

				procletic_compatible=True
			elif stem_verb_const.ExternalPrefixTable.has_key(procletic):
	##			print "-1"
				if affix=='-':
	##				print '-1.1';
					procletic_compatible=True;
				elif stem_verb_const.Table_affix.has_key(affix):
					i=0;
					len_Table_affix=len(stem_verb_const.Table_affix[affix])
					while i < len_Table_affix and not procletic_compatible :

						#the tense
	##					print Table_affix[affix][i][0].encode('utf8')
						if stem_verb_const.Table_affix[affix][i][0] in stem_verb_const.ExternalPrefixTable[procletic]:
							procletic_compatible=True;
						i+=1;

				else :
					procletic_compatible=False;

			if procletic_compatible:
	##			print '-2.1';
				if encletic==u'' :
					return True;
				elif not (stem_verb_const.ExternalSuffixTable.has_key(encletic)):
					return False;
				elif stem_verb_const.ExternalSuffixTable.has_key(encletic):
					if affix=='-':
						return True;
					elif stem_verb_const.Table_affix.has_key(affix):
						i=0;
						length=len(stem_verb_const.Table_affix[affix])
						while i < length:
							#the pronoun
							if stem_verb_const.Table_affix[affix][i][1] in stem_verb_const.ExternalSuffixTable[encletic]:
								return True;
							i+=1;
						# not found
						return False;
					else:
						return False;
				else:
					return False;
			else:

				return False;

		return False;


	def is_compatible_proaffix_tense(self,procletic, encletic, tense, pronoun):

		if procletic==u'' and encletic==u'':  return True;
		else:
			procletic_compatible=False;
			if procletic==u'' :
				procletic_compatible=True
			elif stem_verb_const.ExternalPrefixTable.has_key(procletic) and tense in stem_verb_const.ExternalPrefixTable[procletic]:
					procletic_compatible=True;
			else:
				return False;

			if procletic_compatible:
				if encletic==u'' :
					return True;
				elif not (stem_verb_const.ExternalSuffixTable.has_key(encletic)):
					return False;
				elif stem_verb_const.ExternalSuffixTable.has_key(encletic) and pronoun in stem_verb_const.ExternalSuffixTable[encletic]:
							return True;
				else:
					return False;
			else:
				return False;
		return False;


	def vocalize(self, verb, proclitic,enclitic):
		"""
		Join the  verb and its affixes, and get the vocalized form
		@param verb: verb found in dictionary.
		@type verb: unicode.
		@param proclitic: first level prefix.
		@type proclitic: unicode.
		@param enclitic: first level suffix.
		@type enclitic: unicode.		
		@return: vocalized word.
		@rtype: unicode.
		"""	
		enclitic_voc=stem_verb_const.COMP_SUFFIX_LIST_TAGS[enclitic]["vocalized"][0];
		proclitic_voc=stem_verb_const.COMP_PREFIX_LIST_TAGS[proclitic]["vocalized"][0];
		#suffix_voc=suffix;#CONJ_SUFFIX_LIST_TAGS[suffix]["vocalized"][0];
		# لمعالجة حالة ألف التفريق
		if verb.endswith(araby.WAW+ araby.ALEF) and enclitic!=u"":
			verb=verb[:-1];
		return ''.join([ proclitic_voc,verb ,enclitic_voc]);


	def set_debug(self,debug):
		"""
		Set the debug attribute to allow printing internal analysis results.
		@param debug: the debug value.
		@type debug: True/False.
		"""
		self.debug=debug;

#Class test
if __name__ == '__main__':
	#ToDo: use the full dictionary of arramooz
	wordlist=[u'يضرب', u"استقلّ", u'استقل', ]
	verbstemmer=verbStemmer();
	verbstemmer.set_debug(True);
	for word in wordlist:
		verbstemmer.conjStemmer.segment(word);
		print verbstemmer.conjStemmer.get_affix_list();
	for word in wordlist:
		result=verbstemmer.stemming_verb(word);
		for analyzed in  result:
			print repr(analyzed);
			print u'\n'.join(analyzed.keys());
			for key in analyzed.keys():
				print u'\t'.join([key,unicode(analyzed[key])]).encode('utf8')
			print;
			print;