.. image:: art.jpeg


Japanese NLP
============
:Date: 2012-01-16
:Version: 1
:Authors: pulkit[at]jaist.ac.jp

.. contents::

Requirements
------------

- Third Party Dependencies

  - Cabocha Japanese Morphological parser http://sourceforge.net/projects/cabocha/

- Python Dependencies

  - ``Python 2.6.*`` or above


``Links``
---------

- All code at jProcessing Repo GitHub_

.. _GitHub: https://github.com/kevincobain2000/jProcessing

- Web_ and HomePage_

.. _Web: http://www.jaist.ac.jp/~s1010205/jnlp

.. _HomePage: http://www.jaist.ac.jp/~s1010205/

- PyPi_ Python Package

.. _PyPi: 
 

``Install``
-----------

In ``Terminal`` ::

  >>>bash$ python setup.py install

History
-------

- ``0.1`` 
        + Morphologically Tokenize Japanese Sentence
        + Kanji / Hiragana / Katakana to Romaji Converter
        + Edict Dictionary Search - borrowed
        + Edict Examples Search - incomplete
        + Sentence Similarity between two JP Sentences
        + Run Cabocha(ISO--8859-1 configured) in Python. 
        + Longest Common String between Sentences
        + Kanji to Katakana Pronunciation
        + Hiragana, Katakana Chart Parser


Libraries and Modules
=====================

Tokenize ``jTokenize.py``
-------------------------
In ``Python`` ::

  >>>from jNlp.jTokenize import jTokenize
  >>>input_sentence = u'私は彼を５日前、つまりこの前の金曜日に駅で見かけた'
  >>>list_of_tokens = jTokenize(input_sentence)
  >>>print list_of_tokens
  >>>print '--'.join(list_of_tokens).encode('utf-8')

Returns ::

  ...[u'\u79c1', u'\u306f', u'\u5f7c', u'\u3092', u'\uff15'...]
  ...私--は--彼--を--５--日--前--、--つまり--この--前--の--金曜日--に--駅--で--見かけ--た

Katakana Pronunciation:

::

  >>>print '--'.join(jReads(input_sentence)).encode('utf-8')
  ...ワタシ--ハ--カレ--ヲ--ゴ--ニチ--マエ--、--ツマリ--コノ--マエ--ノ--キンヨウビ--ニ--エキ--デ--ミカケ--タ


Cabocha ``jCabocha.py``
-----------------------

Run Cabocha_ with original ``EUCJP`` or ``IS0-8859-1`` configured encoding, with ``utf8`` python

.. _Cabocha: http://code.google.com/p/cabocha/

- If cobocha is configured as ``utf8`` then see this http://nltk.googlecode.com/svn/trunk/doc/book-jp/ch12.html#cabocha

In ``Python`` ::

>>>from jNlp.jCabocha import JCabocha
>>>cabocha = JCabocha()
>>>print cabocha.xmlstring(input_sentence).encode('utf-8')

Output:

::

  <sentence>
   <chunk id="0" link="8" rel="D" score="0.971639" head="0" func="1">
    <tok id="0" read="ワタシ" base="私" pos="名詞-代名詞-一般" ctype="" cform="" ne="O">私</tok>
    <tok id="1" read="ハ" base="は" pos="助詞-係助詞" ctype="" cform="" ne="O">は</tok>
   </chunk>
   <chunk id="1" link="2" rel="D" score="0.488672" head="2" func="3">
    <tok id="2" read="カレ" base="彼" pos="名詞-代名詞-一般" ctype="" cform="" ne="O">彼</tok>
    <tok id="3" read="ヲ" base="を" pos="助詞-格助詞-一般" ctype="" cform="" ne="O">を</tok>
   </chunk>
   <chunk id="2" link="8" rel="D" score="2.25834" head="6" func="6">
    <tok id="4" read="ゴ" base="５" pos="名詞-数" ctype="" cform="" ne="B-DATE">５</tok>
    <tok id="5" read="ニチ" base="日" pos="名詞-接尾-助数詞" ctype="" cform="" ne="I-DATE">日</tok>
    <tok id="6" read="マエ" base="前" pos="名詞-副詞可能" ctype="" cform="" ne="I-DATE">前</tok>
    <tok id="7" read="、" base="、" pos="記号-読点" ctype="" cform="" ne="O">、</tok>
   </chunk>

Similarily ::

>>>print cabocha.lattice(input_sentence).encode('utf-8') #will print lattice
>>>print cabocha.corpus(input_sentence).encode('utf-8') #will print corpus view


Kanji / Katakana /Hiragana to Tokenized Romaji ``jConvert.py``
--------------------------------------------------------------

Uses ``data/katakanaChart.txt`` and parses the chart. See katakanaChart_.

Usage ::

>>>input_sentence = u'気象庁が２１日午前４時４８分、発表した天気概況によると、'
>>>print ' '.join(tokenizedRomaji(input_sentence))
>>>print tokenizedRomaji(input_sentence)

Output ::

...kisyoutyou ga ni ichi nichi gozen yon ji yon hachi hun  hapyou si ta tenki gaikyou ni yoru to
...[u'kisyoutyou', u'ga', u'ni', u'ichi', u'nichi', u'gozen',...]

 
**katakanaChart.txt**


.. _katakanaChart:

- katakanaChartFile_ and hiraganaChartFile_

.. _katakanaChartFile: https://raw.github.com/kevincobain2000/jProcessing/master/src/jNlp/data/katakanaChart.txt

.. _hiraganaChartFile: https://raw.github.com/kevincobain2000/jProcessing/master/src/jNlp/data/hiraganaChart.txt


Longest Common String Japanese ``jProcessing.py``
-------------------------------------------------

On English Strings ::

>>> from jNlp.jProcessing import long_substr
>>> a = 'Once upon a time in Italy'
>>> b = 'Thre was a time in America'
>>> print long_substr(a, b)

Output ::

...a time in

On Japanese Strings ::

>>> a = u'これでアナタも冷え知らず'
>>> b = u'これでア冷え知らずナタも'
>>> print long_substr(a, b).encode('utf-8')

Output ::

...冷え知らず

Similarity between two sentences ``jProcessing.py``
---------------------------------------------------
Uses MinHash by checking the overlap http://en.wikipedia.org/wiki/MinHash

:English Strings:

>>> from jNlp.jProcessing import Similarities
>>> s = Similarities()
>>> a = 'There was'
>>> b = 'There is'
>>> print s.minhash(a,b)
...0.444444444444

:Japanese Strings:

>>> from jNlp.jProcessing import *
>>> a = u'これは何ですか？'
>>> b = u'これはわからないです'
>>> print s.minhash(' '.join(jTokenize(a)), ' '.join(jTokenize(b)))
...0.210526315789


Edict Japanese Dictionary Search with Example sentences
=======================================================

Edict dictionary and example sentences parser.
----------------------------------------------

This package uses the EDICT_ and KANJIDIC_ dictionary files.
These files are the property of the
Electronic Dictionary Research and Development Group_ , and
are used in conformance with the Group's licence_ .

.. _EDICT: http://www.csse.monash.edu.au/~jwb/edict.html
.. _KANJIDIC: http://www.csse.monash.edu.au/~jwb/kanjidic.html
.. _Group: http://www.edrdg.org/
.. _licence: http://www.edrdg.org/edrdg/licence.html

Edict Parser By **Paul Goins**, see ``edict_search.py``
Edict Example sentences Parse by query, **Pulkit Kathuria**, see ``edict_examples.py``
Edict examples pickle files are provided but latest example files can be downloaded from the links provided.

Charset
-------
Two files

- ``utf8`` Charset example file if not using ``src/jNlp/data/edict_examples``

  To convert ``EUCJP/ISO-8859-1`` to ``utf8`` ::
       
    iconv -f EUCJP -t UTF-8 path/to/edict_examples > path/to/save_with_utf-8
      
- ``ISO-8859-1`` edict_dictionary file

Outputs example sentences for a query in Japanese only for ambiguous words.


Links
-----

**Latest** Dictionary files can be downloaded here_

.. _here: http://www.csse.monash.edu.au/~jwb/edict.html

``edict_search.py``
-------------------
:author: Paul Goins `License included` linkToOriginal_:

.. _linkToOriginal: http://repo.or.cz/w/jbparse.git/blame/8e42831ca5f721c0320b27d7d83cb553d6e9c68f:/jbparse/edict.py

For all entries of sense definitions

>>> from jNlp.edict_search import *
>>> query = u'認める'
>>> edict_path = 'src/jNlp/data/edict-yy-mm-dd'
>>> kp = Parser(edict_path)
>>> for i, entry in enumerate(kp.search(query)):
...     print entry.to_string().encode('utf-8')


``edict_examples.py``
---------------------
:`Note`: Only outputs the examples sentences for ambiguous words (if word has one or more senses)

:author: Pulkit Kathuria

>>> from jNlp.edict_examples import *
>>> query = u'認める'
>>> edict_path = 'src/jNlp/data/edict-yy-mm-dd'
>>> edict_examples_path = 'src/jNlp/data/edict_examples'
>>> search_with_example(edict_path, edict_examples_path, query)

Output ::

  認める

  Sense (1) to recognize;
    EX:01 我々は彼の才能を*認*めている。We appreciate his talent.

  Sense (2) to observe;
    EX:01 ｘ線写真で異状が*認*められます。We have detected an abnormality on your x-ray.

  Sense (3) to admit;
    EX:01 母は私の計画をよいと*認*めた。Mother approved my plan.
    EX:02 母は決して私の結婚を*認*めないだろう。Mother will never approve of my marriage.
    EX:03 父は決して私の結婚を*認*めないだろう。Father will never approve of my marriage.
    EX:04 彼は女性の喫煙をいいものだと*認*めない。He doesn't approve of women smoking.
    ...



Contacts
========

  - ContactForm_
  - BugReport_
  
  .. _ContactForm: http://www.jaist.ac.jp/~s1010205/styled-2/index.html
  .. _BugReport: http://www.jaist.ac.jp/~s1010205/styled/index.html

  :Author: `pulkit[at]jaist.ac.jp` [change ``at`` with ``@``]




