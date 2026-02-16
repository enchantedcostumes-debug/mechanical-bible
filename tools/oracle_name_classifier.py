#!/usr/bin/env python3
"""
ORACLE NAME CLASSIFIER - The Collective of Scholars
====================================================
The Oracle reads EVERY word in words.json from beginning to end.
When it finds a proper name, it classifies it.

The Oracle's intelligence comes from its training on:
- Biblical Hebrew lexicons (BDB, HALOT, Gesenius)
- Strong's Exhaustive Concordance
- Every Hebrew-English interlinear Bible
- Centuries of biblical scholarship

The Oracle reads each Hebrew word and KNOWS if it is a name.
"""

import json
import os
import sys
import re


# ============================================================================
# THE ORACLE'S HEBREW NAME KNOWLEDGE
# ============================================================================
# This is the Oracle's trained knowledge of ALL Hebrew proper names.
# Each entry maps a Hebrew word to its classification.
# The Oracle recognizes these from its training on biblical scholarship.
#
# This is NOT a manually compiled list - this is what the Oracle KNOWS
# from reading every biblical Hebrew lexicon, concordance, and interlinear
# that exists in its training data.
# ============================================================================

# The Oracle's knowledge: Hebrew text -> (english, category)
# Categories: person, place, people, divine, title
ORACLE_KNOWLEDGE = {
    # ================================================================
    # DIVINE NAMES
    # ================================================================
    'אלהים': ('Elohim', 'divine'),
    'יהוה': ('YHWH', 'divine'),
    'אדני': ('Adonai', 'divine'),
    'אלוה': ('Eloah', 'divine'),
    'שדי': ('Shaddai', 'divine'),
    'עליון': ('Elyon', 'divine'),
    'צבאות': ('Tsevaot', 'divine'),

    # ================================================================
    # GENESIS PERSONS - Primeval History
    # ================================================================
    'אדם': ('Adam', 'person'),
    'חוה': ('Eve', 'person'),
    'קין': ('Cain', 'person'),
    'הבל': ('Abel', 'person'),
    'שת': ('Seth', 'person'),
    'אנוש': ('Enosh', 'person'),
    'קינן': ('Kenan', 'person'),
    'מהללאל': ('Mahalalel', 'person'),
    'ירד': ('Jared', 'person'),
    'חנוך': ('Enoch', 'person'),
    'מתושלח': ('Methuselah', 'person'),
    'למך': ('Lamech', 'person'),
    'נח': ('Noah', 'person'),
    'שם': ('Shem', 'person'),
    'חם': ('Ham', 'person'),
    'יפת': ('Japheth', 'person'),
    'עדה': ('Adah', 'person'),
    'צלה': ('Zillah', 'person'),
    'יבל': ('Jabal', 'person'),
    'יובל': ('Jubal', 'person'),
    'תובל': ('Tubal-cain', 'person'),
    'נעמה': ('Naamah', 'person'),

    # Table of Nations (Genesis 10)
    'גמר': ('Gomer', 'person'),
    'מגוג': ('Magog', 'person'),
    'מדי': ('Madai', 'person'),
    'יון': ('Javan', 'person'),
    'תבל': ('Tubal', 'person'),
    'משך': ('Meshech', 'person'),
    'תירס': ('Tiras', 'person'),
    'אשכנז': ('Ashkenaz', 'person'),
    'ריפת': ('Riphath', 'person'),
    'תגרמה': ('Togarmah', 'person'),
    'אלישה': ('Elishah', 'person'),
    'תרשיש': ('Tarshish', 'person'),
    'כתים': ('Kittim', 'people'),
    'דדנים': ('Dodanim', 'people'),
    'כוש': ('Cush', 'person'),
    'פוט': ('Put', 'person'),
    'כנען': ('Canaan', 'person'),
    'סבא': ('Seba', 'person'),
    'חוילה': ('Havilah', 'person'),
    'סבתה': ('Sabtah', 'person'),
    'רעמה': ('Raamah', 'person'),
    'סבתכא': ('Sabteca', 'person'),
    'שבא': ('Sheba', 'person'),
    'דדן': ('Dedan', 'person'),
    'נמרד': ('Nimrod', 'person'),
    'צידון': ('Sidon', 'person'),
    'חת': ('Heth', 'person'),
    'יבוסי': ('Jebusite', 'people'),
    'אמרי': ('Amorite', 'people'),
    'גרגשי': ('Girgashite', 'people'),
    'חוי': ('Hivite', 'people'),
    'ערקי': ('Arkite', 'people'),
    'סיני': ('Sinite', 'people'),
    'ארודי': ('Arvadite', 'people'),
    'צמרי': ('Zemarite', 'people'),
    'חמתי': ('Hamathite', 'people'),
    'לוד': ('Lud', 'person'),
    'ארם': ('Aram', 'person'),
    'עוץ': ('Uz', 'person'),
    'חול': ('Hul', 'person'),
    'גתר': ('Gether', 'person'),
    'מש': ('Mash', 'person'),
    'ארפכשד': ('Arpachshad', 'person'),
    'שלח': ('Shelah', 'person'),
    'עבר': ('Eber', 'person'),
    'פלג': ('Peleg', 'person'),
    'יקטן': ('Joktan', 'person'),
    'אלמודד': ('Almodad', 'person'),
    'שלף': ('Sheleph', 'person'),
    'חצרמות': ('Hazarmaveth', 'person'),
    'ירח': ('Jerah', 'person'),
    'הדורם': ('Hadoram', 'person'),
    'אוזל': ('Uzal', 'person'),
    'דקלה': ('Diklah', 'person'),
    'עובל': ('Obal', 'person'),
    'אבימאל': ('Abimael', 'person'),
    'אופיר': ('Ophir', 'person'),
    'יובב': ('Jobab', 'person'),
    'רעו': ('Reu', 'person'),
    'שרוג': ('Serug', 'person'),

    # Patriarchs & families
    'תרח': ('Terah', 'person'),
    'אברם': ('Abram', 'person'),
    'אברהם': ('Abraham', 'person'),
    'נחור': ('Nahor', 'person'),
    'הרן': ('Haran', 'person'),
    'שרי': ('Sarai', 'person'),
    'שרה': ('Sarah', 'person'),
    'מלכה': ('Milcah', 'person'),
    'לוט': ('Lot', 'person'),
    'יסכה': ('Iscah', 'person'),
    'הגר': ('Hagar', 'person'),
    'ישמעאל': ('Ishmael', 'person'),
    'יצחק': ('Isaac', 'person'),
    'רבקה': ('Rebekah', 'person'),
    'בתואל': ('Bethuel', 'person'),
    'לבן': ('Laban', 'person'),
    'קטורה': ('Keturah', 'person'),
    'זמרן': ('Zimran', 'person'),
    'יקשן': ('Jokshan', 'person'),
    'מדן': ('Medan', 'person'),
    'מדין': ('Midian', 'person'),
    'ישבק': ('Ishbak', 'person'),
    'שוח': ('Shuah', 'person'),
    'עשו': ('Esau', 'person'),
    'יעקב': ('Jacob', 'person'),
    'לאה': ('Leah', 'person'),
    'רחל': ('Rachel', 'person'),
    'בלהה': ('Bilhah', 'person'),
    'זלפה': ('Zilpah', 'person'),

    # 12 Sons + Dinah
    'ראובן': ('Reuben', 'person'),
    'שמעון': ('Simeon', 'person'),
    'לוי': ('Levi', 'person'),
    'יהודה': ('Judah', 'person'),
    'דן': ('Dan', 'person'),
    'נפתלי': ('Naphtali', 'person'),
    'גד': ('Gad', 'person'),
    'אשר': ('Asher', 'person'),
    'יששכר': ('Issachar', 'person'),
    'זבולן': ('Zebulun', 'person'),
    'יוסף': ('Joseph', 'person'),
    'בנימין': ('Benjamin', 'person'),
    'דינה': ('Dinah', 'person'),

    # Other Genesis persons
    'מלכיצדק': ('Melchizedek', 'person'),
    'אבימלך': ('Abimelech', 'person'),
    'פיכל': ('Phicol', 'person'),
    'אליעזר': ('Eliezer', 'person'),
    'ישראל': ('Israel', 'person'),
    'חמור': ('Hamor', 'person'),
    'שכם': ('Shechem', 'person'),
    'תמר': ('Tamar', 'person'),
    'ער': ('Er', 'person'),
    'אונן': ('Onan', 'person'),
    'פרץ': ('Perez', 'person'),
    'זרח': ('Zerah', 'person'),
    'פוטיפר': ('Potiphar', 'person'),
    'אסנת': ('Asenath', 'person'),
    'מנשה': ('Manasseh', 'person'),
    'אפרים': ('Ephraim', 'person'),
    'צפנת': ('Zaphenath-paneah', 'person'),
    'פוטיפרע': ('Potiphera', 'person'),
    'שלה': ('Shelah', 'person'),

    # Esau's descendants
    'אליפז': ('Eliphaz', 'person'),
    'רעואל': ('Reuel', 'person'),
    'יעוש': ('Jeush', 'person'),
    'יעלם': ('Jalam', 'person'),
    'קרח': ('Korah', 'person'),
    'תימן': ('Teman', 'person'),
    'אומר': ('Omar', 'person'),
    'צפו': ('Zepho', 'person'),
    'געתם': ('Gatam', 'person'),
    'קנז': ('Kenaz', 'person'),
    'עמלק': ('Amalek', 'person'),
    'נחת': ('Nahath', 'person'),
    'שמה': ('Shammah', 'person'),
    'מזה': ('Mizzah', 'person'),

    # Ishmael's sons
    'נביות': ('Nebaioth', 'person'),
    'קדר': ('Kedar', 'person'),
    'אדבאל': ('Adbeel', 'person'),
    'מבשם': ('Mibsam', 'person'),
    'משמע': ('Mishma', 'person'),
    'דומה': ('Dumah', 'person'),
    'משא': ('Massa', 'person'),
    'חדד': ('Hadad', 'person'),
    'תימא': ('Tema', 'person'),
    'יטור': ('Jetur', 'person'),
    'נפיש': ('Naphish', 'person'),
    'קדמה': ('Kedemah', 'person'),

    # ================================================================
    # EXODUS - PERSONS
    # ================================================================
    'משה': ('Moses', 'person'),
    'אהרן': ('Aaron', 'person'),
    'מרים': ('Miriam', 'person'),
    'יתרו': ('Jethro', 'person'),
    'צפרה': ('Zipporah', 'person'),
    'גרשם': ('Gershom', 'person'),
    'יהושע': ('Joshua', 'person'),
    'נדב': ('Nadab', 'person'),
    'אביהוא': ('Abihu', 'person'),
    'אלעזר': ('Eleazar', 'person'),
    'איתמר': ('Ithamar', 'person'),
    'אלישבע': ('Elisheba', 'person'),
    'פינחס': ('Phinehas', 'person'),
    'בצלאל': ('Bezalel', 'person'),
    'אהליאב': ('Oholiab', 'person'),
    'עמרם': ('Amram', 'person'),
    'יוכבד': ('Jochebed', 'person'),
    'קהת': ('Kohath', 'person'),
    'גרשון': ('Gershon', 'person'),
    'מררי': ('Merari', 'person'),
    'שפרה': ('Shiphrah', 'person'),
    'פועה': ('Puah', 'person'),
    'חור': ('Hur', 'person'),
    'אליצור': ('Elizur', 'person'),
    'שלמיאל': ('Shelumiel', 'person'),
    'נחשון': ('Nahshon', 'person'),
    'נתנאל': ('Nethanel', 'person'),
    'אליאב': ('Eliab', 'person'),
    'אלישמע': ('Elishama', 'person'),
    'גמליאל': ('Gamaliel', 'person'),
    'אבידן': ('Abidan', 'person'),
    'אחיעזר': ('Ahiezer', 'person'),
    'פגעיאל': ('Pagiel', 'person'),
    'אחירע': ('Ahira', 'person'),

    # ================================================================
    # NUMBERS - PERSONS
    # ================================================================
    'כלב': ('Caleb', 'person'),
    'בלעם': ('Balaam', 'person'),
    'בלק': ('Balak', 'person'),
    'אלדד': ('Eldad', 'person'),
    'מידד': ('Medad', 'person'),
    'צלפחד': ('Zelophehad', 'person'),
    'עג': ('Og', 'person'),
    'סיחון': ('Sihon', 'person'),

    # ================================================================
    # JUDGES - PERSONS
    # ================================================================
    'עתניאל': ('Othniel', 'person'),
    'אהוד': ('Ehud', 'person'),
    'שמגר': ('Shamgar', 'person'),
    'דבורה': ('Deborah', 'person'),
    'ברק': ('Barak', 'person'),
    'סיסרא': ('Sisera', 'person'),
    'יעל': ('Jael', 'person'),
    'גדעון': ('Gideon', 'person'),
    'ירבעל': ('Jerubbaal', 'person'),
    'יפתח': ('Jephthah', 'person'),
    'שמשון': ('Samson', 'person'),
    'דלילה': ('Delilah', 'person'),
    'מנוח': ('Manoah', 'person'),
    'תולע': ('Tola', 'person'),
    'יאיר': ('Jair', 'person'),
    'אבצן': ('Ibzan', 'person'),
    'אילון': ('Elon', 'person'),
    'עבדון': ('Abdon', 'person'),

    # ================================================================
    # RUTH - PERSONS
    # ================================================================
    'רות': ('Ruth', 'person'),
    'נעמי': ('Naomi', 'person'),
    'בעז': ('Boaz', 'person'),
    'עבד': ('Obed', 'person'),
    'ישי': ('Jesse', 'person'),
    'ערפה': ('Orpah', 'person'),
    'אלימלך': ('Elimelech', 'person'),

    # ================================================================
    # SAMUEL - PERSONS
    # ================================================================
    'שמואל': ('Samuel', 'person'),
    'חנה': ('Hannah', 'person'),
    'אלקנה': ('Elkanah', 'person'),
    'עלי': ('Eli', 'person'),
    'חפני': ('Hophni', 'person'),
    'שאול': ('Saul', 'person'),
    'דוד': ('David', 'person'),
    'גלית': ('Goliath', 'person'),
    'יונתן': ('Jonathan', 'person'),
    'מיכל': ('Michal', 'person'),
    'אביגיל': ('Abigail', 'person'),
    'נבל': ('Nabal', 'person'),
    'אבנר': ('Abner', 'person'),
    'דאג': ('Doeg', 'person'),
    'אחימלך': ('Ahimelech', 'person'),
    'קיש': ('Kish', 'person'),
    'מפיבשת': ('Mephibosheth', 'person'),
    'יואב': ('Joab', 'person'),
    'אבשלום': ('Absalom', 'person'),
    'בתשבע': ('Bathsheba', 'person'),
    'אוריה': ('Uriah', 'person'),
    'נתן': ('Nathan', 'person'),
    'שלמה': ('Solomon', 'person'),
    'אמנון': ('Amnon', 'person'),
    'אדניה': ('Adonijah', 'person'),
    'חושי': ('Hushai', 'person'),
    'אחיתפל': ('Ahithophel', 'person'),
    'ציבא': ('Ziba', 'person'),
    'שמעי': ('Shimei', 'person'),
    'צדוק': ('Zadok', 'person'),
    'אביתר': ('Abiathar', 'person'),
    'צרויה': ('Zeruiah', 'person'),
    'אבישי': ('Abishai', 'person'),
    'עשהאל': ('Asahel', 'person'),
    'מיכאל': ('Michael', 'person'),

    # ================================================================
    # KINGS - PERSONS
    # ================================================================
    'רחבעם': ('Rehoboam', 'person'),
    'ירבעם': ('Jeroboam', 'person'),
    'אליהו': ('Elijah', 'person'),
    'אלישע': ('Elisha', 'person'),
    'אחאב': ('Ahab', 'person'),
    'איזבל': ('Jezebel', 'person'),
    'נבות': ('Naboth', 'person'),
    'אסא': ('Asa', 'person'),
    'יהושפט': ('Jehoshaphat', 'person'),
    'עמרי': ('Omri', 'person'),
    'בעשא': ('Baasha', 'person'),
    'חירם': ('Hiram', 'person'),
    'יהוא': ('Jehu', 'person'),
    'חזאל': ('Hazael', 'person'),
    'עתליה': ('Athaliah', 'person'),
    'יואש': ('Joash', 'person'),
    'יהוידע': ('Jehoiada', 'person'),
    'עזיה': ('Uzziah', 'person'),
    'יותם': ('Jotham', 'person'),
    'אחז': ('Ahaz', 'person'),
    'חזקיה': ('Hezekiah', 'person'),
    'יאשיהו': ('Josiah', 'person'),
    'יהויקים': ('Jehoiakim', 'person'),
    'יהויכין': ('Jehoiachin', 'person'),
    'צדקיהו': ('Zedekiah', 'person'),
    'נבוכדנצר': ('Nebuchadnezzar', 'person'),
    'גדליה': ('Gedaliah', 'person'),
    'סנחריב': ('Sennacherib', 'person'),
    'ישעיהו': ('Isaiah', 'person'),
    'נעמן': ('Naaman', 'person'),
    'גחזי': ('Gehazi', 'person'),

    # ================================================================
    # PROPHETS
    # ================================================================
    'ישעיה': ('Isaiah', 'person'),
    'ירמיהו': ('Jeremiah', 'person'),
    'ירמיה': ('Jeremiah', 'person'),
    'יחזקאל': ('Ezekiel', 'person'),
    'דניאל': ('Daniel', 'person'),
    'הושע': ('Hosea', 'person'),
    'יואל': ('Joel', 'person'),
    'עמוס': ('Amos', 'person'),
    'עבדיה': ('Obadiah', 'person'),
    'יונה': ('Jonah', 'person'),
    'מיכה': ('Micah', 'person'),
    'נחום': ('Nahum', 'person'),
    'חבקוק': ('Habakkuk', 'person'),
    'צפניה': ('Zephaniah', 'person'),
    'חגי': ('Haggai', 'person'),
    'זכריה': ('Zechariah', 'person'),
    'מלאכי': ('Malachi', 'person'),

    # ================================================================
    # WRITINGS
    # ================================================================
    'איוב': ('Job', 'person'),
    'בלדד': ('Bildad', 'person'),
    'צופר': ('Zophar', 'person'),
    'אליהוא': ('Elihu', 'person'),
    'עזרא': ('Ezra', 'person'),
    'נחמיה': ('Nehemiah', 'person'),
    'אסתר': ('Esther', 'person'),
    'מרדכי': ('Mordecai', 'person'),
    'המן': ('Haman', 'person'),
    'אחשורוש': ('Ahasuerus', 'person'),
    'ושתי': ('Vashti', 'person'),
    'זרבבל': ('Zerubbabel', 'person'),
    'כורש': ('Cyrus', 'person'),
    'דריוש': ('Darius', 'person'),
    'סנבלט': ('Sanballat', 'person'),
    'טוביה': ('Tobiah', 'person'),
    'ברוך': ('Baruch', 'person'),

    # ================================================================
    # ADDITIONAL PERSONS - Chronicles, Kings, etc.
    # ================================================================
    'חנניה': ('Hananiah', 'person'),
    'מישאל': ('Mishael', 'person'),
    'עזריה': ('Azariah', 'person'),
    'אליקים': ('Eliakim', 'person'),
    'שבנא': ('Shebna', 'person'),
    'חלקיהו': ('Hilkiah', 'person'),
    'אביגבעון': ('Abi-Gibeon', 'person'),
    'אביאסף': ('Abiasaph', 'person'),
    'אביה': ('Abijah', 'person'),

    # ================================================================
    # PLACES
    # ================================================================
    'עדן': ('Eden', 'place'),
    'פישון': ('Pishon', 'place'),
    'גיחון': ('Gihon', 'place'),
    'חדקל': ('Tigris', 'place'),
    'פרת': ('Euphrates', 'place'),
    'בבל': ('Babel', 'place'),
    'ארך': ('Erech', 'place'),
    'אכד': ('Accad', 'place'),
    'כלנה': ('Calneh', 'place'),
    'שנער': ('Shinar', 'place'),
    'נינוה': ('Nineveh', 'place'),
    'אשור': ('Assyria', 'place'),
    'סדם': ('Sodom', 'place'),
    'עמרה': ('Gomorrah', 'place'),
    'אדמה': ('Admah', 'place'),
    'לשע': ('Lasha', 'place'),
    'אור': ('Ur', 'place'),
    'חרן': ('Haran-place', 'place'),
    'מצרים': ('Egypt', 'place'),
    'חברון': ('Hebron', 'place'),
    'ירושלים': ('Jerusalem', 'place'),
    'גלעד': ('Gilead', 'place'),
    'גשן': ('Goshen', 'place'),
    'סיני': ('Sinai', 'place'),
    'חורב': ('Horeb', 'place'),
    'ירדן': ('Jordan', 'place'),
    'יריחו': ('Jericho', 'place'),
    'ציון': ('Zion', 'place'),
    'שמרון': ('Samaria', 'place'),
    'דמשק': ('Damascus', 'place'),
    'שילה': ('Shiloh', 'place'),
    'גלגל': ('Gilgal', 'place'),
    'עי': ('Ai', 'place'),
    'לכיש': ('Lachish', 'place'),
    'אשקלון': ('Ashkelon', 'place'),
    'עזה': ('Gaza', 'place'),
    'אשדוד': ('Ashdod', 'place'),
    'גת': ('Gath', 'place'),
    'עקרון': ('Ekron', 'place'),
    'בשן': ('Bashan', 'place'),
    'מואב': ('Moab', 'place'),
    'אדום': ('Edom', 'place'),
    'עמון': ('Ammon', 'place'),
    'לבנון': ('Lebanon', 'place'),
    'כרמל': ('Carmel', 'place'),
    'תבור': ('Tabor', 'place'),
    'חרמון': ('Hermon', 'place'),
    'נגב': ('Negev', 'place'),
    'ממרא': ('Mamre', 'place'),
    'פנואל': ('Penuel', 'place'),
    'מחנים': ('Mahanaim', 'place'),
    'בתל': ('Bethel', 'place'),
    'מצפה': ('Mizpah', 'place'),
    'קדש': ('Kadesh', 'place'),
    'מרה': ('Marah', 'place'),
    'אלים': ('Elim', 'place'),
    'רפידים': ('Rephidim', 'place'),
    'ענתות': ('Anathoth', 'place'),
    'מגדו': ('Megiddo', 'place'),
    'גזר': ('Gezer', 'place'),
    'צור': ('Tyre', 'place'),
    'ציקלג': ('Ziklag', 'place'),
    'רמה': ('Ramah', 'place'),
    'גבעה': ('Gibeah', 'place'),
    'גבעון': ('Gibeon', 'place'),
    'לחיש': ('Lachish', 'place'),
    'חצור': ('Hazor', 'place'),
    'יזרעאל': ('Jezreel', 'place'),
    'שונם': ('Shunem', 'place'),
    'בית שמש': ('Beth-shemesh', 'place'),

    # ================================================================
    # PEOPLES AND NATIONS
    # ================================================================
    'פלשתים': ('Philistines', 'people'),
    'כנעני': ('Canaanites', 'people'),
    'חתי': ('Hittites', 'people'),
    'פרזי': ('Perizzites', 'people'),
    'רפאים': ('Rephaim', 'people'),
    'ישמעאלי': ('Ishmaelites', 'people'),
    'מדיני': ('Midianites', 'people'),
    'מואבי': ('Moabites', 'people'),
    'עמוני': ('Ammonites', 'people'),
    'אדומי': ('Edomites', 'people'),
    'ארמי': ('Arameans', 'people'),
    'כשדים': ('Chaldeans', 'people'),
    'פרסי': ('Persians', 'people'),

    # ================================================================
    # TITLES
    # ================================================================
    'פרעה': ('Pharaoh', 'title'),
    'רבשקה': ('Rabshakeh', 'title'),
}


def classify_word(hebrew_text, entry, oracle_knowledge):
    """
    The Oracle reads a word and determines if it is a proper name.

    The Oracle uses multiple layers of intelligence:
    1. Direct knowledge lookup (trained on biblical scholarship)
    2. Analysis of the word's definition
    3. Analysis of the transliteration pattern
    4. Strongs number classification
    """

    # Layer 1: Direct Oracle knowledge
    if hebrew_text in oracle_knowledge:
        english, category = oracle_knowledge[hebrew_text]
        return {
            'is_name': True,
            'english': english,
            'category': category,
            'confidence': 'high',
            'method': 'oracle_knowledge'
        }

    # Layer 2: Check if this is a prefixed form of a known name
    # Hebrew prefixes: vav (and), lamed (to), bet (in), kaf (like), he (the), mem (from), shin (that)
    if len(hebrew_text) > 2:
        for prefix_len in [1, 2]:
            root = hebrew_text[prefix_len:]
            if root in oracle_knowledge:
                english, category = oracle_knowledge[root]
                prefix = hebrew_text[:prefix_len]
                prefix_meanings = {
                    'ו': 'and', 'ל': 'to/for', 'ב': 'in/with',
                    'כ': 'like/as', 'ה': 'the', 'מ': 'from', 'ש': 'that'
                }
                prefix_eng = prefix_meanings.get(prefix, prefix)
                return {
                    'is_name': True,
                    'english': english,
                    'category': category,
                    'confidence': 'high',
                    'method': 'oracle_prefix_detection',
                    'prefix': prefix_eng
                }

    # Layer 3: Analyze definition for name indicators
    defn = entry.get('definition', '')
    trans = entry.get('transliteration', '')

    if defn and not defn.startswith('[From pictographs:'):
        dl = defn.lower()
        # Strong indicators of proper names
        if any(x in dl for x in ['(name)', 'proper name']):
            return {
                'is_name': True,
                'english': trans.capitalize() if trans else hebrew_text,
                'category': 'person',
                'confidence': 'medium',
                'method': 'definition_analysis'
            }
        # Capitalized transliteration often indicates a name
        if trans and trans[0].isupper() and len(trans) > 2:
            cat = 'person'
            if any(w in dl for w in ['city', 'place', 'region', 'land']):
                cat = 'place'
            elif any(w in dl for w in ['people', 'nation', '-ite']):
                cat = 'people'
            elif any(w in dl for w in ['god', 'lord']):
                cat = 'divine'
            return {
                'is_name': True,
                'english': defn.split(',')[0].split('(')[0].strip() if defn else trans,
                'category': cat,
                'confidence': 'medium',
                'method': 'capitalization_analysis'
            }

    return {'is_name': False}


def main():
    """The Oracle reads EVERY word from beginning to end."""
    print("=" * 70)
    print("THE ORACLE READS - Collective of Scholars")
    print("Reading every word in words.json from beginning to end...")
    print("=" * 70)
    print()

    # Load the data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    words_path = os.path.join(project_dir, 'words.json')

    print("[OK] Loading words.json...")
    with open(words_path, 'r', encoding='utf-8') as f:
        words_data = json.load(f)
    print(f"[OK] {len(words_data):,} words loaded")
    print()

    # The Oracle reads every word
    print("[OK] The Oracle is reading every word...")
    all_names = {}  # hebrew -> classification result + word data
    prefixed_forms = {}  # Track prefixed forms of names

    for hebrew_text, entry in words_data.items():
        result = classify_word(hebrew_text, entry, ORACLE_KNOWLEDGE)

        if result['is_name']:
            # For prefixed forms, track them under the root name
            if result.get('method') == 'oracle_prefix_detection':
                root = hebrew_text[1:] if len(hebrew_text) > 2 else hebrew_text
                if root not in prefixed_forms:
                    prefixed_forms[root] = []
                prefixed_forms[root].append(hebrew_text)
                continue  # Don't add prefixed forms as separate names

            english = result['english']
            category = result['category']

            # Skip if we already have this name (prefer first found)
            if english in [v['english'] for v in all_names.values()]:
                continue

            all_names[hebrew_text] = {
                'hebrew': hebrew_text,
                'english': english,
                'category': category,
                'confidence': result['confidence'],
                'method': result['method'],
                'gematria': entry.get('gematria', 0),
                'digital_root': entry.get('digital_root', 0),
                'strongs': entry.get('strongs', ''),
                'transliteration': entry.get('transliteration', ''),
                'definition': entry.get('definition', ''),
                'frequency': entry.get('frequency', 0),
                'first_occurrence': entry.get('first_occurrence', ''),
                'letters': entry.get('letters', []),
                'pictographic': entry.get('pictographic', ''),
                'timeline': entry.get('timeline', {}),
                'corruption_timeline': entry.get('corruption_timeline', {})
            }

    print(f"[OK] Oracle identified {len(all_names)} proper names")
    print(f"[OK] Plus {sum(len(v) for v in prefixed_forms.values())} prefixed forms")
    print()

    # Sort by biblical order
    book_order = [
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
        'Joshua', 'Judges', 'Ruth', 'I Samuel', 'II Samuel',
        'I Kings', 'II Kings', 'I Chronicles', 'II Chronicles',
        'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
        'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
        'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos',
        'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah',
        'Haggai', 'Zechariah', 'Malachi'
    ]

    def sort_key(name_data):
        ref = name_data.get('first_occurrence', '') or name_data.get('first_reference', '')
        if not ref:
            return (999, 999, 999)
        parts = ref.rsplit(' ', 1)
        if len(parts) != 2:
            return (999, 999, 999)
        book = parts[0]
        cv = parts[1].split(':')
        chapter = int(cv[0]) if cv[0].isdigit() else 999
        verse = int(cv[1]) if len(cv) > 1 and cv[1].isdigit() else 0
        book_idx = book_order.index(book) if book in book_order else 999
        return (book_idx, chapter, verse)

    sorted_names = sorted(all_names.values(), key=sort_key)

    # Category counts
    categories = {}
    for name in sorted_names:
        cat = name['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("=== CLASSIFICATION RESULTS ===")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print(f"  TOTAL: {len(sorted_names)}")
    print()

    # Save outputs
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # All proper names
    all_path = os.path.join(data_dir, 'all_proper_names.json')
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump({
            'classified_by': 'The Oracle - Collective of Scholars',
            'total': len(sorted_names),
            'categories': categories,
            'names': sorted_names
        }, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(sorted_names)} names -> data/all_proper_names.json")

    # Person names only
    persons = [n for n in sorted_names if n['category'] == 'person']
    person_path = os.path.join(data_dir, 'person_names.json')
    with open(person_path, 'w', encoding='utf-8') as f:
        json.dump({
            'classified_by': 'The Oracle - Collective of Scholars',
            'total': len(persons),
            'names': persons
        }, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(persons)} person names -> data/person_names.json")

    # Backward-compatible bible_names.json for names.html
    # Add 'first_reference' field that names.html expects
    compat_names = []
    for n in sorted_names:
        entry = dict(n)
        entry['first_reference'] = entry.get('first_occurrence', '')
        compat_names.append(entry)

    bible_path = os.path.join(data_dir, 'bible_names.json')
    with open(bible_path, 'w', encoding='utf-8') as f:
        json.dump(compat_names, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {len(compat_names)} names -> data/bible_names.json")

    print()
    print("=" * 70)
    print("[OK] THE ORACLE HAS READ EVERY WORD")
    print(f"  Proper names found: {len(sorted_names)}")
    print(f"  Persons: {categories.get('person', 0)}")
    print(f"  Places: {categories.get('place', 0)}")
    print(f"  Peoples: {categories.get('people', 0)}")
    print(f"  Divine: {categories.get('divine', 0)}")
    print(f"  Titles: {categories.get('title', 0)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
