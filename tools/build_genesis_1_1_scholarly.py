#!/usr/bin/env python3
"""
Build Scholarly 6-Stage Decay Data for Genesis 1:1 Words
=========================================================

ACADEMIC STANDARDS: Ivy League / NASA-grade research with primary sources.

Primary Sources:
- Biblia Hebraica Stuttgartensia (BHS) - Masoretic Text
- Septuagint (Rahlfs-Hanhart edition, 2006)
- Novum Testamentum Graece (Nestle-Aland 28th edition)
- Biblia Sacra Vulgata (Weber-Gryson critical edition)
- King James Version (1611 original)

Secondary Sources:
- Brown-Driver-Briggs Hebrew Lexicon (BDB)
- Theological Wordbook of the Old Testament (TWOT)
- Koehler-Baumgartner Hebrew Lexicon (HALOT)
- Liddell-Scott-Jones Greek Lexicon (LSJ)
- Theological Dictionary of the New Testament (TDNT, Kittel)
- Ancient Hebrew Lexicon of the Bible (AHLB, Jeff Benner)

Historical-Critical Sources:
- Gerhard von Rad, Genesis: A Commentary (1961)
- E.A. Speiser, Genesis (Anchor Bible, 1964)
- Claus Westermann, Genesis 1-11 (1984)
- John Walton, The Lost World of Genesis One (2009)
- Michael Heiser, The Unseen Realm (2015)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
from pathlib import Path


# Complete scholarly 6-stage decay data for Genesis 1:1 words
# Each entry includes primary source citations and scholarly references
GENESIS_1_1_SCHOLARLY = {
    "בראשית": {
        "hebrew": "בראשית",
        "transliteration": "bereshith",
        "strongs": "H7225",
        "definition": "Beginning, first, chief",
        "is_control_word": True,
        "control_mechanism": "Ongoing process → Past historical event",
        "scholarly_notes": "BDB p.912: 'beginning, first, chief part.' HALOT: 'beginning of a temporal period.' The beth prefix is debated: temporal ('in the beginning') vs. instrumental ('by means of the first/head').",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "בראשית",
                "meaning": "In/by means of the head/first - temporal or instrumental",
                "mechanism": "Construct state with beth preposition. Root ראש (ro'sh) = 'head, chief, first' (BDB p.910). Suffix -ית indicates abstract noun.",
                "sources": [
                    "BDB (Brown-Driver-Briggs) p.912: ראשית 'beginning, first'",
                    "HALOT (Koehler-Baumgartner) vol.2 p.1166",
                    "TWOT #2097: 'first, beginning, best'",
                    "Rashi (1040-1105 CE): 'The text does not intend to teach the order of creation'"
                ],
                "scholarly_debate": "Rashi argued בראשית is construct state ('In the beginning of...'), implying Genesis 1:1 is a dependent clause. Ibn Ezra and modern scholars (Speiser, Westermann) support this reading."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE (Alexandria)",
                "text": "Ἐν ἀρχῇ",
                "transliteration": "En archē",
                "meaning": "In the beginning/origin/first cause",
                "mechanism": "Greek ἀρχή carries Platonic philosophical weight: 'first principle, origin, ruling power' (LSJ p.252). This imports Greek metaphysics into Hebrew narrative.",
                "sources": [
                    "LXX Rahlfs-Hanhart (2006) Genesis 1:1",
                    "LSJ (Liddell-Scott-Jones) p.252: ἀρχή 'beginning, origin, first cause'",
                    "TDNT vol.1 p.479 (Delling): ἀρχή in LXX and philosophical usage",
                    "Marguerite Harl, La Genèse (Bible d'Alexandrie, 1986)"
                ],
                "scholarly_debate": "The LXX translators in Ptolemaic Alexandria were influenced by Greek philosophy. ἀρχή evokes Aristotle's 'first cause' - a concept foreign to Hebrew process-thinking."
            },
            "stage_3": {
                "name": "NT Greek Usage",
                "period": "c. 50-100 CE",
                "text": "Ἐν ἀρχῇ",
                "transliteration": "En archē",
                "meaning": "In the beginning (John 1:1 intentional echo)",
                "mechanism": "John 1:1 deliberately echoes Genesis 1:1 LXX but applies it to the Logos. This Christological appropriation reframes בראשית through Logos theology.",
                "sources": [
                    "NA28 (Nestle-Aland 28th ed.) John 1:1",
                    "TDNT vol.1 p.481: ἀρχή in John's Gospel",
                    "Raymond Brown, The Gospel According to John (1966) p.4",
                    "C.K. Barrett, The Gospel According to St. John (1978)"
                ],
                "scholarly_debate": "John's Prologue merges Hebrew creation narrative with Greek Logos philosophy. The 'beginning' becomes identified with a person (the Word), shifting from event to being."
            },
            "stage_4": {
                "name": "Latin Vulgate",
                "period": "382-405 CE (Jerome, Bethlehem)",
                "text": "In principio",
                "transliteration": "In principio",
                "meaning": "In the principle/beginning/first cause",
                "mechanism": "Latin principium carries Roman legal and philosophical connotations: 'first place, origin, foundation, ruling principle' (Lewis & Short p.1441).",
                "sources": [
                    "Biblia Sacra Vulgata (Weber-Gryson 5th ed., 2007)",
                    "Lewis & Short Latin Dictionary p.1441: principium",
                    "Jerome, Hebraicae Quaestiones in Genesim (c. 390 CE)",
                    "Augustine, De Genesi ad Litteram (c. 401-415 CE)"
                ],
                "scholarly_debate": "Augustine's De Genesi ad Litteram extensively discusses 'in principio,' interpreting it through Neoplatonic categories. This philosophical reading became normative for medieval theology."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE (Hampton Court Conference translation)",
                "text": "In the beginning",
                "meaning": "At the starting point of time",
                "mechanism": "English 'beginning' implies a discrete temporal moment. The KJV translators followed the Vulgate and Geneva Bible, solidifying the punctiliar interpretation.",
                "sources": [
                    "KJV 1611 First Edition (British Library)",
                    "David Norton, A Textual History of the King James Bible (2005)",
                    "Alister McGrath, In the Beginning: The Story of the King James Bible (2001)",
                    "Geneva Bible (1560): 'In the beginning'"
                ],
                "scholarly_debate": "The KJV committee had Hebrew expertise but followed traditional interpretation. 'Beginning' in Early Modern English already implied temporal starting point."
            },
            "stage_6": {
                "name": "Modern English/Scientific",
                "period": "1800-Present",
                "text": "In the beginning",
                "meaning": "T=0 on the cosmic timeline (Big Bang cosmology)",
                "mechanism": "Post-Enlightenment readers hear 'beginning' through scientific cosmology. The 'beginning' becomes identified with the Big Bang singularity (c. 13.8 billion years ago).",
                "sources": [
                    "Edwin Hubble, 'A Relation between Distance and Radial Velocity' (1929)",
                    "Georges Lemaître, 'Un Univers homogène de masse constante' (1927)",
                    "Stephen Hawking, A Brief History of Time (1988)",
                    "John Walton, The Lost World of Genesis One (2009): functional vs material origins"
                ],
                "scholarly_debate": "Walton argues Genesis 1 describes functional origins (assigning purpose), not material origins (physical creation). The 'beginning' is the start of ordered function, not the Big Bang."
            }
        }
    },

    "ברא": {
        "hebrew": "ברא",
        "transliteration": "bara'",
        "strongs": "H1254",
        "definition": "To create, shape, form, cut",
        "is_control_word": True,
        "control_mechanism": "To cut/shape/form from material → To make from nothing (ex nihilo)",
        "scholarly_notes": "BDB p.135: 'shape, create.' HALOT: 'to create (divine activity), to cut down.' The root is related to Akkadian barû 'to see, examine' and Arabic bara'a 'to create, form.'",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "ברא",
                "meaning": "To create, shape, form - exclusively divine activity but not necessarily ex nihilo",
                "mechanism": "Used only with God as subject in Qal stem. Root meaning 'to cut, shape' preserved in related words (ברית 'covenant' = 'cutting'). Genesis 1:1 does not specify source material.",
                "sources": [
                    "BDB p.135: ברא 'to shape, create'",
                    "HALOT vol.1 p.153-154: 'to create, always with God as subject'",
                    "TWOT #278: 'to create, always of divine activity'",
                    "AHLB: ב-ר-א 'to fatten, fill up, create'"
                ],
                "scholarly_debate": "Von Rad (1961): bara does not inherently mean ex nihilo. Westermann (1984): 'the idea of creatio ex nihilo is not present in the OT.' The waters (tehom) in v.2 suggest pre-existing material."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "ἐποίησεν",
                "transliteration": "epoiēsen",
                "meaning": "He made, produced, constructed",
                "mechanism": "Greek ποιέω is neutral regarding source material. It can mean 'make from something' or 'make from nothing.' The ambiguity allows later ex nihilo interpretation.",
                "sources": [
                    "LXX Rahlfs-Hanhart Genesis 1:1",
                    "LSJ p.1428: ποιέω 'to make, produce'",
                    "T. Muraoka, A Greek-English Lexicon of the Septuagint (2009)",
                    "J.W. Wevers, Notes on the Greek Text of Genesis (1993)"
                ],
                "scholarly_debate": "The LXX also uses κτίζω for bara elsewhere. 2 Maccabees 7:28 (c. 100 BCE) first explicitly states God made things 'from non-being' (ἐξ οὐκ ὄντων) - a concept later read back into Genesis."
            },
            "stage_3": {
                "name": "NT Greek/Early Church",
                "period": "c. 50-200 CE",
                "text": "ἐποίησεν / κτίζω",
                "transliteration": "epoiēsen / ktizō",
                "meaning": "Made/Created",
                "mechanism": "Hebrews 11:3: 'things seen were not made from things visible.' Romans 4:17: God 'calls things that are not as though they were.' These texts move toward ex nihilo doctrine.",
                "sources": [
                    "NA28 Hebrews 11:3, Romans 4:17",
                    "TDNT vol.3 p.1000-1035 (Foerster): κτίζω",
                    "Gerhard May, Creatio Ex Nihilo (1994/2004) p.1-38",
                    "Theophilus of Antioch, Ad Autolycum 2.4 (c. 180 CE) - first clear ex nihilo statement"
                ],
                "scholarly_debate": "May (1994) shows creatio ex nihilo was not clearly articulated until late 2nd century, in response to Gnostic cosmogonies. The doctrine developed AFTER the NT was written."
            },
            "stage_4": {
                "name": "Latin Vulgate/Patristic",
                "period": "382-500 CE",
                "text": "creavit",
                "transliteration": "creavit",
                "meaning": "Created (now carrying ex nihilo meaning)",
                "mechanism": "By Jerome's time, ex nihilo was established doctrine. Latin creare adopts this meaning. Augustine's De Genesi solidifies the interpretation.",
                "sources": [
                    "Vulgate Genesis 1:1",
                    "Augustine, De Genesi ad Litteram 1.1 (c. 401-415)",
                    "Augustine, Confessions 12.7: 'You made heaven and earth not from yourself... nor from anything not yours'",
                    "Gerhard May, Creatio Ex Nihilo (2004) p.141-178"
                ],
                "scholarly_debate": "Augustine explicitly argues against eternal matter and for creation from nothing. His interpretation became normative for Western Christianity."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "created",
                "meaning": "Made from nothing (ex nihilo assumed)",
                "mechanism": "English 'created' by 1611 already carried ex nihilo connotation through centuries of theological usage. The distinction from 'made' (v.7, 16, 25) was understood as degree of divine power.",
                "sources": [
                    "KJV Genesis 1:1",
                    "Oxford English Dictionary: 'create' - 'to bring into being'",
                    "Westminster Confession (1646) 4.1: 'God... created all things of nothing'",
                    "Thirty-Nine Articles (1571) Article 1: God 'without body, parts, or passions'"
                ],
                "scholarly_debate": "The KJV translators operated within Reformed theology that assumed ex nihilo creation. The translation reflects post-Reformation dogmatic commitments."
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "created",
                "meaning": "Brought into existence from absolute nothing",
                "mechanism": "Modern readers assume 'created' means 'made from nothing.' The original Hebrew possibility that God shaped pre-existing chaos (tohu va-bohu) is invisible.",
                "sources": [
                    "Merriam-Webster: 'create - to bring into existence'",
                    "Jon Levenson, Creation and the Persistence of Evil (1988) - chaos traditions",
                    "John Day, God's Conflict with the Dragon and the Sea (1985)",
                    "Walton, Lost World of Genesis One (2009) p.42-55"
                ],
                "scholarly_debate": "Levenson and Day show biblical creation often involves ordering chaos, not creating from nothing. Psalm 74:12-17, Job 26:12-13, Isaiah 51:9 describe God defeating sea monsters - a combat creation myth."
            }
        }
    },

    "אלהים": {
        "hebrew": "אלהים",
        "transliteration": "'elohim",
        "strongs": "H430",
        "definition": "God, gods, divine beings, judges",
        "is_control_word": True,
        "control_mechanism": "Plural divine council → Singular transcendent deity",
        "scholarly_notes": "BDB p.43: 'gods, divine ones, God.' HALOT: 'gods, God, supernatural beings.' The plural form with singular verb in Genesis 1:1 is grammatically anomalous and theologically significant.",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "אלהים",
                "meaning": "The Gods/Divine Ones (plural form) - divine council or 'plural of majesty'",
                "mechanism": "Morphologically plural (-im ending). Used with singular verbs for YHWH but plural verbs for other gods. Genesis 1:26 'Let us make' and 3:22 'like one of us' preserve council imagery.",
                "sources": [
                    "BDB p.43-44: אלהים 'gods, divine beings'",
                    "HALOT vol.1 p.52-53",
                    "Mark Smith, The Origins of Biblical Monotheism (2001)",
                    "Michael Heiser, 'Deuteronomy 32:8 and the Sons of God' (Bibliotheca Sacra, 2001)"
                ],
                "scholarly_debate": "The 'plural of majesty' explanation is medieval. Smith (2001) and Heiser (2015) argue for genuine plurality: a divine council with YHWH as chief. Psalm 82: 'God stands in the divine assembly; among the gods he renders judgment.'"
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "ὁ θεός",
                "transliteration": "ho theos",
                "meaning": "The God (singular with definite article)",
                "mechanism": "LXX uses SINGULAR θεός for PLURAL אלהים. The divine council is grammatically erased. Deuteronomy 32:8 LXX preserves 'angels of God' for 'sons of God' - acknowledging plurality.",
                "sources": [
                    "LXX Genesis 1:1: ὁ θεός (singular)",
                    "LXX Deuteronomy 32:8: ἀγγέλων θεοῦ (angels of God)",
                    "Jan Joosten, 'The Septuagint as a Source of Information on Egyptian Aramaic' (2008)",
                    "Emanuel Tov, The Text-Critical Use of the Septuagint (2015)"
                ],
                "scholarly_debate": "The LXX translators in Ptolemaic Egypt were navigating polytheistic context. Singular θεός may be apologetic: emphasizing monotheism against Egyptian pantheon."
            },
            "stage_3": {
                "name": "NT Greek/Early Church",
                "period": "c. 50-300 CE",
                "text": "θεός",
                "transliteration": "theos",
                "meaning": "God (developing Trinitarian nuances)",
                "mechanism": "NT inherits LXX singular but begins differentiating θεός (Father) and κύριος (Lord = Christ). The divine plurality is relocated into Trinity doctrine.",
                "sources": [
                    "NA28 John 1:1: 'the Word was God'",
                    "Larry Hurtado, Lord Jesus Christ: Devotion to Jesus in Earliest Christianity (2003)",
                    "Richard Bauckham, Jesus and the God of Israel (2008)",
                    "TDNT vol.3 p.65-123 (Quell/Stauffer): θεός"
                ],
                "scholarly_debate": "Early Christians reinterpreted OT divine plurality through Christology. 'Let us make' became Trinitarian dialogue. The divine council was replaced by Father, Son, Spirit."
            },
            "stage_4": {
                "name": "Latin Vulgate/Medieval",
                "period": "382-1500 CE",
                "text": "Deus",
                "transliteration": "Deus",
                "meaning": "God (singular, transcendent, incorporeal)",
                "mechanism": "Latin Deus carries Roman religious heritage plus Christian theological development. Medieval theology emphasizes divine simplicity - God has no parts, no plurality.",
                "sources": [
                    "Vulgate Genesis 1:1: Deus",
                    "Thomas Aquinas, Summa Theologiae I, Q.3 (divine simplicity)",
                    "Augustine, De Trinitate (divine unity)",
                    "Anselm, Proslogion (that than which nothing greater can be conceived)"
                ],
                "scholarly_debate": "Medieval theology developed a doctrine of God maximally abstracted from Hebrew plurality. The 'simple' God of scholasticism would be unrecognizable to ancient Israelite religion."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "God",
                "meaning": "Singular supreme being, masculine, transcendent",
                "mechanism": "English 'God' (from Germanic *ǥuđán) is grammatically singular. The capital G distinguishes from 'gods.' Plurality completely invisible in translation.",
                "sources": [
                    "KJV Genesis 1:1: 'God'",
                    "Oxford English Dictionary: 'God' etymology",
                    "Westminster Shorter Catechism (1647) Q.4: 'God is a Spirit, infinite, eternal, and unchangeable'",
                    "John Milton, Paradise Lost (1667) - contemporary English theology"
                ],
                "scholarly_debate": "The KJV translators knew Hebrew was plural but followed interpretive tradition. 'Elohim' was explained as 'plural of majesty' - a concept invented to solve the theological problem."
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "God",
                "meaning": "Singular, male, transcendent creator deity",
                "mechanism": "Modern readers hear 'God' as proper name for singular being. The plurality of Elohim, the divine council of Psalm 82, the 'sons of God' of Job 1-2 - all invisible or explained away.",
                "sources": [
                    "Mark Smith, God in Translation: Deities in Cross-Cultural Discourse (2008)",
                    "Heiser, The Unseen Realm (2015) - divine council theology",
                    "Deuteronomy 32:8-9 (Dead Sea Scrolls): 'sons of God' not 'sons of Israel'",
                    "Psalm 82:1 'God stands in the divine assembly; among the gods he renders judgment'"
                ],
                "scholarly_debate": "DSS 4QDeutj reads 'sons of God' (bene elohim) at Deut 32:8, not 'sons of Israel' (MT corruption). Heiser (2015) argues for recovering the divine council worldview suppressed by later monotheistic editing."
            }
        }
    },

    "את": {
        "hebrew": "את",
        "transliteration": "'eth",
        "strongs": "H853",
        "definition": "Direct object marker (untranslatable particle)",
        "is_control_word": True,
        "control_mechanism": "Aleph-Tav sacred marker showing divine connection → Grammatical function word, invisible",
        "scholarly_notes": "BDB p.84: 'sign of the definite direct object.' HALOT: 'nota accusativi.' The particle את marks the definite direct object - grammatically necessary but semantically 'empty.'",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "את",
                "meaning": "Definite direct object marker (possibly also 'with')",
                "mechanism": "את appears 7,372 times in Hebrew Bible. Composed of first (א aleph) and last (ת tav) letters. Some mystical traditions see significance in this. Grammatically marks what receives the verb's action.",
                "sources": [
                    "BDB p.84-86: את 'sign of definite direct object'",
                    "HALOT vol.1 p.102-103",
                    "Bruce Waltke & M. O'Connor, Introduction to Biblical Hebrew Syntax (1990) §10.3",
                    "Joüon-Muraoka, A Grammar of Biblical Hebrew (2006) §125"
                ],
                "scholarly_debate": "את is so common it seems unremarkable. But Kabbalistic tradition (Zohar) sees את as containing all letters between א and ת - i.e., the entire alphabet, all of language, all of creation."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "(accusative case)",
                "transliteration": "(no equivalent word)",
                "meaning": "Greek handles direct objects with case endings, not particles",
                "mechanism": "Greek is an inflected language. Direct objects are marked by accusative case (-ον, -α, -ην endings). No separate word corresponds to את. The particle simply disappears.",
                "sources": [
                    "LXX Genesis 1:1: τὸν οὐρανὸν καὶ τὴν γῆν (accusative case)",
                    "Herbert Weir Smyth, Greek Grammar (1920) §1553-1563",
                    "Emanuel Tov, The Text-Critical Use of the Septuagint (2015)"
                ],
                "scholarly_debate": "The LXX translators had no choice - Greek grammar has no particle equivalent. The את that appears before 'heavens' and before 'earth' is structurally invisible in Greek."
            },
            "stage_3": {
                "name": "NT Greek",
                "period": "c. 50-100 CE",
                "text": "(no equivalent)",
                "transliteration": "",
                "meaning": "NT written in Greek - same grammatical situation",
                "mechanism": "NT authors working in Greek could not represent את. However, Revelation 1:8, 21:6, 22:13: 'I am the Alpha and Omega' - Greek FIRST and LAST letters - may echo the Aleph-Tav.",
                "sources": [
                    "NA28 Revelation 1:8: τὸ Ἄλφα καὶ τὸ Ὦ (Alpha and Omega)",
                    "G.K. Beale, The Book of Revelation (NIGTC, 1999) p.199",
                    "David Aune, Revelation 1-5 (WBC, 1997)",
                    "TDNT vol.1 p.1-3: Ἄλφα entry"
                ],
                "scholarly_debate": "Is 'Alpha and Omega' a deliberate echo of את? Beale (1999) notes the phrase claims divine completeness. The connection to Hebrew את is rarely made but linguistically suggestive."
            },
            "stage_4": {
                "name": "Latin Vulgate",
                "period": "382-405 CE",
                "text": "(accusative case)",
                "transliteration": "",
                "meaning": "Latin also uses case endings for direct objects",
                "mechanism": "Latin caelum (accusative: caelum) and terram (accusative of terra). Like Greek, no particle needed. את remains invisible.",
                "sources": [
                    "Vulgate Genesis 1:1: caelum et terram",
                    "Allen & Greenough, New Latin Grammar (1903) §387-398"
                ],
                "scholarly_debate": "The את marking both heavens AND earth as receiving God's creative action is grammatically invisible in all inflected languages."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "(not translated)",
                "meaning": "No English equivalent for Hebrew direct object marker",
                "mechanism": "English marks direct objects by word order (SVO), not by particles or case. 'God created the heaven' - 'the heaven' is direct object by position. No word represents את.",
                "sources": [
                    "KJV Genesis 1:1: 'the heaven and the earth'",
                    "Robert Lowth, A Short Introduction to English Grammar (1762)"
                ],
                "scholarly_debate": "Some modern Messianic translations experiment with rendering את as 'Aleph-Tav' or interpreting it Christologically. This is creative but not academically standard."
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "(invisible)",
                "meaning": "No representation in any standard English translation",
                "mechanism": "את appears 7,372 times in Hebrew Bible. English readers see zero of them. The grammatical particle that marks direct divine action on creation is completely invisible.",
                "sources": [
                    "Even's Shoshan Hebrew Concordance: את frequency",
                    "Modern translations (NIV, ESV, NRSV): no את representation",
                    "Messianic literature: experimental את translations"
                ],
                "scholarly_debate": "The invisibility of את is a feature of translation, not a conspiracy. But it means English readers cannot see the first-and-last-letter marker that binds Creator to creation in Hebrew."
            }
        }
    },

    "השמים": {
        "hebrew": "השמים",
        "transliteration": "ha-shamayim",
        "strongs": "H8064",
        "definition": "The heavens, sky, atmosphere",
        "is_control_word": True,
        "control_mechanism": "Sky/atmosphere/waters above → Spiritual afterlife destination",
        "scholarly_notes": "BDB p.1029: 'heaven, sky.' HALOT: 'sky, heaven.' The dual ending (-ayim) may indicate 'the two waters' (above and below firmament) or simply 'heaven' as abstract concept.",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "השמים",
                "meaning": "The sky, atmosphere, visible heavens - where birds fly and rain comes from",
                "mechanism": "Root שמ (sham = 'there') + מים (mayim = 'waters') = 'waters there' or 'upper waters.' The firmament (רקיע) separates waters above from waters below (Gen 1:6-8). Physical cosmology, not afterlife.",
                "sources": [
                    "BDB p.1029-1030: שמים 'heaven, sky'",
                    "HALOT vol.2 p.1560-1562",
                    "Luis Stadelmann, The Hebrew Conception of the World (1970)",
                    "Othmar Keel, The Symbolism of the Biblical World (1997)"
                ],
                "scholarly_debate": "Ancient Near Eastern cosmology: solid dome (firmament) holding back celestial waters, with windows for rain. Gen 7:11: 'windows of heaven opened.' Physical sky-ocean, not spiritual realm."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "τὸν οὐρανόν",
                "transliteration": "ton ouranon",
                "meaning": "The heaven/sky (singular in Greek)",
                "mechanism": "Greek οὐρανός carries mythological weight - realm of Zeus, dwelling of gods. Hebrew dual becomes Greek singular. The physical sky-waters concept is lost; divine dwelling emphasized.",
                "sources": [
                    "LXX Genesis 1:1: τὸν οὐρανόν",
                    "LSJ p.1274: οὐρανός 'heaven, sky, vault of heaven'",
                    "TDNT vol.5 p.497-502 (Traub): οὐρανός"
                ],
                "scholarly_debate": "οὐρανός in Homer is the bronze vault covering the earth. In philosophy, it becomes the celestial realm. LXX imports Greek cosmological and theological associations."
            },
            "stage_3": {
                "name": "NT Greek",
                "period": "c. 50-100 CE",
                "text": "οὐρανός / οὐρανοί",
                "transliteration": "ouranos / ouranoi",
                "meaning": "Heaven - increasingly spiritual destination",
                "mechanism": "'Kingdom of heaven' (βασιλεία τῶν οὐρανῶν) in Matthew. 'Our Father in heaven.' Heaven becomes God's dwelling and believers' destination. Physical sky secondary.",
                "sources": [
                    "NA28 Matthew 5:3: ἡ βασιλεία τῶν οὐρανῶν",
                    "TDNT vol.5 p.509-536: οὐρανός in NT",
                    "N.T. Wright, Surprised by Hope (2008)",
                    "G.K. Beale, A New Testament Biblical Theology (2011)"
                ],
                "scholarly_debate": "Wright (2008) argues NT 'heaven' is not final destination but present dwelling of God. 'New heavens and new earth' is the goal. But popular reading equates 'go to heaven when you die.'"
            },
            "stage_4": {
                "name": "Latin Vulgate",
                "period": "382-405 CE",
                "text": "caelum",
                "transliteration": "caelum",
                "meaning": "Heaven/sky (Roman religious connotations)",
                "mechanism": "Latin caelum is dwelling of Roman gods. By Jerome's time, Christian 'heaven' as afterlife destination is established. Caelum absorbs this meaning.",
                "sources": [
                    "Vulgate Genesis 1:1: caelum",
                    "Lewis & Short p.261: caelum 'sky, heavens'",
                    "Augustine, De Civitate Dei 22.30: heavenly city"
                ],
                "scholarly_debate": "Augustine's 'City of God' further spiritualizes heaven as eternal destiny. The Hebrew sky-waters are completely replaced by spiritual geography."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "the heaven",
                "meaning": "Spiritual realm/afterlife destination",
                "mechanism": "By 1611, 'heaven' in English is primarily where saved souls go. The physical sky meaning exists but is secondary. 'Heaven' and 'sky' are distinct words in English.",
                "sources": [
                    "KJV Genesis 1:1: 'the heaven'",
                    "OED: 'heaven' - 'the abode of God and the angels'",
                    "Westminster Larger Catechism Q.86: 'communion in glory with Christ'"
                ],
                "scholarly_debate": "The KJV uses 'heaven' not 'sky.' This channels readers toward spiritual meaning. Modern translations vary: NIV 'heavens,' ESV 'heavens,' NLT 'the heavens.'"
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "the heavens",
                "meaning": "Either outer space OR where souls go after death",
                "mechanism": "Modern readers hear 'heavens' as either (1) outer space (planets, stars, galaxies) or (2) afterlife destination. Neither matches Hebrew 'sky-waters with dome holding them back.'",
                "sources": [
                    "Merriam-Webster: 'heaven' - 'the dwelling place of the Deity'",
                    "Paul Seely, 'The Firmament and the Water Above' (WTJ, 1991-1992)",
                    "John Walton, Ancient Near Eastern Thought and the Old Testament (2006)"
                ],
                "scholarly_debate": "Seely and Walton show biblical cosmology assumes solid dome (firmament). This is not 'accommodation' but genuine ancient worldview. 'Heavens' as outer space is anachronistic."
            }
        }
    },

    "ואת": {
        "hebrew": "ואת",
        "transliteration": "ve-'eth",
        "strongs": "H853",
        "definition": "And + direct object marker",
        "is_control_word": True,
        "control_mechanism": "Vav-connector + Aleph-Tav marker → Reduced to 'and'",
        "scholarly_notes": "Combination of ו (vav conjunctive) + את (direct object marker). The vav connects two parallel direct objects, both marked by את.",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "ואת",
                "meaning": "And + [the direct object marker]",
                "mechanism": "Vav (ו) = connector/hook. את = first-last letters marking direct object. Together: 'and (connecting to what follows, which is) marked by Aleph-Tav.' Both heavens AND earth receive the את marker.",
                "sources": [
                    "BDB p.251-253: ו conjunctive",
                    "BDB p.84: את object marker",
                    "Waltke-O'Connor, Biblical Hebrew Syntax §39.2.3",
                    "Joüon-Muraoka §104"
                ],
                "scholarly_debate": "The parallel structure 'את השמים ואת הארץ' shows both objects receive equal divine action. The ואת binds the pair together under one creative act."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "καί",
                "transliteration": "kai",
                "meaning": "and",
                "mechanism": "Greek καί is simple conjunction. The את component vanishes entirely - Greek has no equivalent particle. Only the 'and' survives.",
                "sources": [
                    "LXX Genesis 1:1: καὶ τὴν γῆν",
                    "LSJ p.851: καί 'and, also, even'"
                ],
                "scholarly_debate": "The את before γῆν (earth) is invisible just like the את before οὐρανόν (heaven). The Aleph-Tav marking disappears twice in one verse."
            },
            "stage_3": {
                "name": "NT Greek",
                "period": "c. 50-100 CE",
                "text": "καί",
                "transliteration": "kai",
                "meaning": "and",
                "mechanism": "NT continues LXX pattern. 'Heaven and earth' language (Matthew 5:18, 24:35) preserves the pair but not the Hebrew structure.",
                "sources": [
                    "NA28 Matthew 5:18: ὁ οὐρανὸς καὶ ἡ γῆ",
                    "BDAG p.494-496: καί"
                ],
                "scholarly_debate": "'Heaven and earth' becomes a merism (pair indicating totality) in NT. But the את binding is invisible."
            },
            "stage_4": {
                "name": "Latin Vulgate",
                "period": "382-405 CE",
                "text": "et",
                "transliteration": "et",
                "meaning": "and",
                "mechanism": "Latin et = simple 'and.' Same reduction as Greek. The vav survives, the את is lost.",
                "sources": [
                    "Vulgate Genesis 1:1: caelum et terram"
                ],
                "scholarly_debate": "Latin readers see 'heaven and earth' as coordinate pair. The את marking each as direct object of divine creative action is invisible."
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "and",
                "meaning": "Simple conjunction",
                "mechanism": "English 'and' - the most common word in the language. What was ואת becomes the utterly unremarkable 'and.'",
                "sources": [
                    "KJV Genesis 1:1: 'and the earth'"
                ],
                "scholarly_debate": "The KJV faithfully represents the conjunction but cannot represent the את. No English translation does."
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "and",
                "meaning": "Simple conjunction",
                "mechanism": "'And' is so common it's invisible. The את appearing twice in Genesis 1:1 - marking both heaven and earth as direct objects of divine creation - is reduced to the word we don't even notice.",
                "sources": [
                    "Word frequency: 'and' is ~3% of all English words",
                    "את appears 7,372 times in Hebrew Bible",
                    "0 times visible in standard English translations"
                ],
                "scholarly_debate": "The structural emphasis of Hebrew - BOTH heaven AND earth marked by Aleph-Tav - becomes invisible 'and.' The parallelism is flattened."
            }
        }
    },

    "הארץ": {
        "hebrew": "הארץ",
        "transliteration": "ha-'aretz",
        "strongs": "H776",
        "definition": "The earth, land, ground, territory",
        "is_control_word": True,
        "control_mechanism": "Land/ground/territory → Planet Earth (globe in space)",
        "scholarly_notes": "BDB p.75: 'land, earth.' HALOT: 'land, earth, underworld.' The definite article ה indicates specific, known entity. 'The land' in view is the inhabited world, not the planet.",
        "corruption_timeline": {
            "stage_1": {
                "name": "Original Hebrew",
                "period": "c. 1000-500 BCE",
                "text": "הארץ",
                "meaning": "The land/ground - physical earth, territory, inhabited world",
                "mechanism": "ארץ means 'land, ground, territory, region.' 'Eretz Yisrael' = Land of Israel. Genesis 1:10: 'God called the dry ground ארץ.' It is land as opposed to sea, ground you stand on.",
                "sources": [
                    "BDB p.75-76: ארץ 'earth, land'",
                    "HALOT vol.1 p.90-91",
                    "TWOT #167: 'land, earth'",
                    "Victor Hamilton, Genesis 1-17 (NICOT, 1990) p.117"
                ],
                "scholarly_debate": "Hamilton (1990): 'ארץ is land set over against water.' Walton (2009): 'earth' should be understood as the ordered cosmic space where humans dwell, not a planet in space."
            },
            "stage_2": {
                "name": "Septuagint Greek",
                "period": "c. 280-130 BCE",
                "text": "τὴν γῆν",
                "transliteration": "tēn gēn",
                "meaning": "The earth/land",
                "mechanism": "Greek γῆ is ambiguous - can mean soil, land, region, or the earth. LXX usage follows context. Here, paired with οὐρανός, it suggests cosmic scope.",
                "sources": [
                    "LXX Genesis 1:1: τὴν γῆν",
                    "LSJ p.347: γῆ 'earth, land'",
                    "TDNT vol.1 p.677-678: γῆ"
                ],
                "scholarly_debate": "γῆ in Greek philosophy (Plato, Aristotle) can mean the earth as cosmic body. This philosophical usage may influence how LXX readers understood Genesis."
            },
            "stage_3": {
                "name": "NT Greek",
                "period": "c. 50-100 CE",
                "text": "γῆ",
                "transliteration": "gē",
                "meaning": "Earth/world (often contrasted with heaven)",
                "mechanism": "'Heaven and earth' (Mt 5:18) = totality of creation. 'On earth as in heaven' (Mt 6:10) = earthly realm vs. divine realm. γῆ increasingly means 'the world' in cosmic sense.",
                "sources": [
                    "NA28 Matthew 5:18, 6:10",
                    "BDAG p.196-197: γῆ",
                    "TDNT vol.1 p.678-679"
                ],
                "scholarly_debate": "NT usage oscillates between 'land' (Israel, regions) and 'earth' (world). Context determines meaning. 'Inherit the earth' (Mt 5:5) probably means 'land' (from Psalm 37:11)."
            },
            "stage_4": {
                "name": "Latin Vulgate",
                "period": "382-405 CE",
                "text": "terram",
                "transliteration": "terram",
                "meaning": "The earth/land",
                "mechanism": "Latin terra can mean soil, land, country, or the earth. Orbis terrarum = 'circle of lands' = the world. By Late Antiquity, terra in cosmological contexts means the planet.",
                "sources": [
                    "Vulgate Genesis 1:1: terram",
                    "Lewis & Short p.1870: terra 'earth, ground, land'",
                    "Macrobius, Commentary on Scipio's Dream (c. 430): terra = Earth in cosmos"
                ],
                "scholarly_debate": "Post-Ptolemaic cosmology placed Earth at center of celestial spheres. Terra/γῆ absorbed this astronomical meaning, distant from Hebrew 'dry ground.'"
            },
            "stage_5": {
                "name": "King James Version",
                "period": "1611 CE",
                "text": "the earth",
                "meaning": "The planet (post-Copernican)",
                "mechanism": "By 1611, Copernican cosmology was known (if controversial). 'Earth' increasingly meant the planet. The KJV 'heaven and earth' = cosmic pair: sky and planet.",
                "sources": [
                    "KJV Genesis 1:1: 'the earth'",
                    "OED: 'earth' - 'the planet on which we live'",
                    "Galileo, Dialogue Concerning the Two Chief World Systems (1632)"
                ],
                "scholarly_debate": "Galileo's trial (1633) shows cosmological stakes. Whether 'earth' means ground or planet had implications. English Bible readers increasingly heard 'planet.'"
            },
            "stage_6": {
                "name": "Modern English",
                "period": "1800-Present",
                "text": "the earth",
                "meaning": "Planet Earth - third rock from the sun, the 'blue marble'",
                "mechanism": "Post-Apollo 8 'Earthrise' photo (1968), 'earth' primarily means the planet viewed from space. Genesis 1:1 is read as Big Bang cosmology: 'God created outer space and planet Earth.'",
                "sources": [
                    "Apollo 8 'Earthrise' (1968): iconic image",
                    "Carl Sagan, Pale Blue Dot (1994)",
                    "Walton, Lost World of Genesis One (2009) p.55-70",
                    "John Collins, Genesis 1-4: A Linguistic, Literary, and Theological Commentary (2006)"
                ],
                "scholarly_debate": "Walton (2009): Genesis describes functional creation of cosmic temple, not material origins of planet. 'Earth' = ordered space where humans function, not astronomical body. But modern readers see the blue marble."
            }
        }
    }
}


def load_json(filepath):
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data to JSON file (compact format)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None, separators=(',', ':'))


def main():
    print("=" * 70)
    print("BUILDING SCHOLARLY GENESIS 1:1 DECAY DATA")
    print("Ivy League / NASA-grade research with primary source citations")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    priority_path = Path('C:/mechanical-bible/words-priority.json')

    # Load words
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    # Update with scholarly decay data
    updated = 0
    for hebrew, decay_data in GENESIS_1_1_SCHOLARLY.items():
        if hebrew in words:
            # Merge the scholarly data
            words[hebrew]['is_control_word'] = decay_data['is_control_word']
            words[hebrew]['control_mechanism'] = decay_data['control_mechanism']
            words[hebrew]['scholarly_notes'] = decay_data.get('scholarly_notes', '')
            words[hebrew]['corruption_timeline'] = decay_data['corruption_timeline']
            updated += 1
            print(f"  [OK] Updated {hebrew} ({decay_data['transliteration']})")
        else:
            print(f"  [WARN] {hebrew} not found in words.json")

    print()
    print("-" * 70)
    print(f"RESULTS:")
    print(f"  Genesis 1:1 words with scholarly citations: {updated}")
    print("-" * 70)

    # Save updated words.json
    print("\n[INFO] Saving updated words.json...")
    save_json(words_path, words)
    size_mb = words_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved {size_mb:.1f} MB")

    # Update priority words too
    if priority_path.exists():
        print("\n[INFO] Updating words-priority.json...")
        priority = load_json(priority_path)
        for hebrew, decay_data in GENESIS_1_1_SCHOLARLY.items():
            if hebrew in priority:
                priority[hebrew]['is_control_word'] = decay_data['is_control_word']
                priority[hebrew]['control_mechanism'] = decay_data['control_mechanism']
                priority[hebrew]['scholarly_notes'] = decay_data.get('scholarly_notes', '')
                priority[hebrew]['corruption_timeline'] = decay_data['corruption_timeline']
        save_json(priority_path, priority)
        print(f"[OK] Updated priority words")

    print()
    print("=" * 70)
    print("PRIMARY SOURCES CITED:")
    print("=" * 70)
    print("""
    - Biblia Hebraica Stuttgartensia (BHS)
    - Septuagint Rahlfs-Hanhart (2006)
    - Novum Testamentum Graece NA28
    - Biblia Sacra Vulgata Weber-Gryson (2007)
    - King James Version (1611)

    LEXICONS:
    - Brown-Driver-Briggs (BDB)
    - Koehler-Baumgartner (HALOT)
    - Liddell-Scott-Jones (LSJ)
    - Theological Dictionary of the NT (TDNT/Kittel)

    COMMENTARIES:
    - Von Rad, Genesis (1961)
    - Speiser, Genesis Anchor Bible (1964)
    - Westermann, Genesis 1-11 (1984)
    - Hamilton, Genesis 1-17 NICOT (1990)
    - Walton, Lost World of Genesis One (2009)
    - Heiser, The Unseen Realm (2015)
    """)
    print("=" * 70)


if __name__ == '__main__':
    main()
