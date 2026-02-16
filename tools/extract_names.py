"""
Extract ALL biblical proper names from words.json using training knowledge.
Keys in words.json are Hebrew characters. We look up by Hebrew text.
Outputs: data/bible_names.json
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# =============================================================================
# MASTER LIST OF BIBLICAL PERSON NAMES
# Format: (hebrew_chars, english_name, first_reference)
# Hebrew characters are the actual keys used in words.json
# Ordered approximately by first appearance in the Hebrew Bible
# =============================================================================

BIBLE_NAMES = [
    # --- GENESIS: Creation to Patriarchs ---
    ("\u05D0\u05D3\u05DD", "Adam", "Genesis 1:26"),
    ("\u05D7\u05D5\u05D4", "Eve (Chavvah)", "Genesis 3:20"),
    ("\u05E7\u05D9\u05DF", "Cain (Qayin)", "Genesis 4:1"),
    ("\u05D4\u05D1\u05DC", "Abel (Hevel)", "Genesis 4:2"),
    ("\u05D7\u05E0\u05D5\u05DA", "Enoch (son of Cain)", "Genesis 4:17"),
    ("\u05E2\u05D9\u05E8\u05D3", "Irad", "Genesis 4:18"),
    ("\u05DE\u05D7\u05D5\u05D9\u05D0\u05DC", "Mehujael", "Genesis 4:18"),
    ("\u05DE\u05EA\u05D5\u05E9\u05D0\u05DC", "Methushael", "Genesis 4:18"),
    ("\u05DC\u05DE\u05DA", "Lamech", "Genesis 4:18"),
    ("\u05E2\u05D3\u05D4", "Adah (wife of Lamech)", "Genesis 4:19"),
    ("\u05E6\u05DC\u05D4", "Zillah", "Genesis 4:19"),
    ("\u05D9\u05D1\u05DC", "Jabal", "Genesis 4:20"),
    ("\u05D9\u05D5\u05D1\u05DC", "Jubal", "Genesis 4:21"),
    ("\u05EA\u05D5\u05D1\u05DC\u05E7\u05D9\u05DF", "Tubal-cain", "Genesis 4:22"),
    ("\u05E0\u05E2\u05DE\u05D4", "Naamah", "Genesis 4:22"),
    ("\u05E9\u05EA", "Seth (Sheth)", "Genesis 4:25"),
    ("\u05D0\u05E0\u05D5\u05E9", "Enosh", "Genesis 4:26"),
    ("\u05E7\u05D9\u05E0\u05DF", "Kenan", "Genesis 5:9"),
    ("\u05DE\u05D4\u05DC\u05DC\u05D0\u05DC", "Mahalalel", "Genesis 5:12"),
    ("\u05D9\u05E8\u05D3", "Jared", "Genesis 5:15"),
    ("\u05D7\u05E0\u05D5\u05DA", "Enoch (son of Jared)", "Genesis 5:18"),
    ("\u05DE\u05EA\u05D5\u05E9\u05DC\u05D7", "Methuselah", "Genesis 5:21"),
    ("\u05DC\u05DE\u05DA", "Lamech (father of Noah)", "Genesis 5:25"),
    ("\u05E0\u05D7", "Noah", "Genesis 5:29"),
    ("\u05E9\u05DD", "Shem", "Genesis 5:32"),
    ("\u05D7\u05DD", "Ham", "Genesis 5:32"),
    ("\u05D9\u05E4\u05EA", "Japheth", "Genesis 5:32"),
    # Table of Nations (Genesis 10)
    ("\u05D2\u05DE\u05E8", "Gomer (son of Japheth)", "Genesis 10:2"),
    ("\u05DE\u05D2\u05D5\u05D2", "Magog", "Genesis 10:2"),
    ("\u05DE\u05D3\u05D9", "Madai", "Genesis 10:2"),
    ("\u05D9\u05D5\u05DF", "Javan", "Genesis 10:2"),
    ("\u05EA\u05D5\u05D1\u05DC", "Tubal", "Genesis 10:2"),
    ("\u05DE\u05E9\u05DA", "Meshech", "Genesis 10:2"),
    ("\u05EA\u05D9\u05E8\u05E1", "Tiras", "Genesis 10:2"),
    ("\u05DB\u05D5\u05E9", "Cush", "Genesis 10:6"),
    ("\u05DE\u05E6\u05E8\u05D9\u05DD", "Mizraim (Egypt)", "Genesis 10:6"),
    ("\u05E4\u05D5\u05D8", "Put", "Genesis 10:6"),
    ("\u05DB\u05E0\u05E2\u05DF", "Canaan", "Genesis 10:6"),
    ("\u05E0\u05DE\u05E8\u05D3", "Nimrod", "Genesis 10:8"),
    ("\u05D0\u05E9\u05D5\u05E8", "Asshur", "Genesis 10:11"),
    ("\u05D0\u05E8\u05E4\u05DB\u05E9\u05D3", "Arpachshad", "Genesis 10:22"),
    ("\u05DC\u05D5\u05D3", "Lud", "Genesis 10:22"),
    ("\u05D0\u05E8\u05DD", "Aram", "Genesis 10:22"),
    ("\u05E2\u05D1\u05E8", "Eber", "Genesis 10:24"),
    ("\u05E4\u05DC\u05D2", "Peleg", "Genesis 10:25"),
    ("\u05D9\u05E7\u05D8\u05DF", "Joktan", "Genesis 10:25"),
    # Shem genealogy (Genesis 11)
    ("\u05E8\u05E2\u05D5", "Reu", "Genesis 11:18"),
    ("\u05E9\u05E8\u05D5\u05D2", "Serug", "Genesis 11:20"),
    ("\u05E0\u05D7\u05D5\u05E8", "Nahor", "Genesis 11:22"),
    ("\u05EA\u05E8\u05D7", "Terah", "Genesis 11:24"),
    ("\u05D0\u05D1\u05E8\u05DD", "Abram", "Genesis 11:26"),
    ("\u05D4\u05E8\u05DF", "Haran", "Genesis 11:26"),
    ("\u05E9\u05E8\u05D9", "Sarai", "Genesis 11:29"),
    ("\u05DE\u05DC\u05DB\u05D4", "Milcah", "Genesis 11:29"),
    ("\u05DC\u05D5\u05D8", "Lot", "Genesis 11:27"),
    # Patriarchal narratives
    ("\u05E4\u05E8\u05E2\u05D4", "Pharaoh", "Genesis 12:15"),
    ("\u05DE\u05DC\u05DB\u05D9\u05E6\u05D3\u05E7", "Melchizedek", "Genesis 14:18"),
    ("\u05D4\u05D2\u05E8", "Hagar", "Genesis 16:1"),
    ("\u05D9\u05E9\u05DE\u05E2\u05D0\u05DC", "Ishmael", "Genesis 16:11"),
    ("\u05D0\u05D1\u05E8\u05D4\u05DD", "Abraham", "Genesis 17:5"),
    ("\u05E9\u05E8\u05D4", "Sarah", "Genesis 17:15"),
    ("\u05D9\u05E6\u05D7\u05E7", "Isaac", "Genesis 17:19"),
    ("\u05D0\u05D1\u05D9\u05DE\u05DC\u05DA", "Abimelech", "Genesis 20:2"),
    ("\u05D1\u05EA\u05D5\u05D0\u05DC", "Bethuel", "Genesis 22:22"),
    ("\u05E8\u05D1\u05E7\u05D4", "Rebekah", "Genesis 22:23"),
    ("\u05DC\u05D1\u05DF", "Laban", "Genesis 24:29"),
    ("\u05E2\u05E9\u05D5", "Esau", "Genesis 25:25"),
    ("\u05D9\u05E2\u05E7\u05D1", "Jacob", "Genesis 25:26"),
    ("\u05E8\u05D7\u05DC", "Rachel", "Genesis 29:6"),
    ("\u05DC\u05D0\u05D4", "Leah", "Genesis 29:16"),
    ("\u05D6\u05DC\u05E4\u05D4", "Zilpah", "Genesis 29:24"),
    ("\u05D1\u05DC\u05D4\u05D4", "Bilhah", "Genesis 29:29"),
    ("\u05E8\u05D0\u05D5\u05D1\u05DF", "Reuben", "Genesis 29:32"),
    ("\u05E9\u05DE\u05E2\u05D5\u05DF", "Simeon", "Genesis 29:33"),
    ("\u05DC\u05D5\u05D9", "Levi", "Genesis 29:34"),
    ("\u05D9\u05D4\u05D5\u05D3\u05D4", "Judah", "Genesis 29:35"),
    ("\u05D3\u05DF", "Dan", "Genesis 30:6"),
    ("\u05E0\u05E4\u05EA\u05DC\u05D9", "Naphtali", "Genesis 30:8"),
    ("\u05D2\u05D3", "Gad", "Genesis 30:11"),
    ("\u05D0\u05E9\u05E8", "Asher", "Genesis 30:13"),
    ("\u05D9\u05E9\u05E9\u05DB\u05E8", "Issachar", "Genesis 30:18"),
    ("\u05D6\u05D1\u05D5\u05DC\u05DF", "Zebulun", "Genesis 30:20"),
    ("\u05D3\u05D9\u05E0\u05D4", "Dinah", "Genesis 30:21"),
    ("\u05D9\u05D5\u05E1\u05E3", "Joseph", "Genesis 30:24"),
    ("\u05D1\u05E0\u05D9\u05DE\u05D9\u05DF", "Benjamin", "Genesis 35:18"),
    ("\u05E2\u05E8", "Er", "Genesis 38:3"),
    ("\u05D0\u05D5\u05E0\u05DF", "Onan", "Genesis 38:4"),
    ("\u05E9\u05DC\u05D4", "Shelah (son of Judah)", "Genesis 38:5"),
    ("\u05EA\u05DE\u05E8", "Tamar", "Genesis 38:6"),
    ("\u05E4\u05E8\u05E5", "Perez", "Genesis 38:29"),
    ("\u05D6\u05E8\u05D7", "Zerah (son of Judah)", "Genesis 38:30"),
    ("\u05E4\u05D5\u05D8\u05D9\u05E4\u05E8", "Potiphar", "Genesis 39:1"),
    ("\u05DE\u05E0\u05E9\u05D4", "Manasseh", "Genesis 41:51"),
    ("\u05D0\u05E4\u05E8\u05D9\u05DD", "Ephraim", "Genesis 41:52"),
    # --- EXODUS ---
    ("\u05DE\u05E9\u05D4", "Moses", "Exodus 2:10"),
    ("\u05E6\u05E4\u05E8\u05D4", "Zipporah", "Exodus 2:21"),
    ("\u05D2\u05E8\u05E9\u05DD", "Gershom", "Exodus 2:22"),
    ("\u05D9\u05EA\u05E8\u05D5", "Jethro", "Exodus 3:1"),
    ("\u05D0\u05D4\u05E8\u05DF", "Aaron", "Exodus 4:14"),
    ("\u05DE\u05E8\u05D9\u05DD", "Miriam", "Exodus 15:20"),
    ("\u05D9\u05D4\u05D5\u05E9\u05E2", "Joshua", "Exodus 17:9"),
    ("\u05E7\u05D4\u05EA", "Kohath", "Exodus 6:16"),
    ("\u05D2\u05E8\u05E9\u05D5\u05DF", "Gershon", "Exodus 6:16"),
    ("\u05DE\u05E8\u05E8\u05D9", "Merari", "Exodus 6:16"),
    ("\u05E7\u05E8\u05D7", "Korah", "Exodus 6:21"),
    ("\u05E0\u05D3\u05D1", "Nadab", "Exodus 6:23"),
    ("\u05D0\u05D1\u05D9\u05D4\u05D5\u05D0", "Abihu", "Exodus 6:23"),
    ("\u05D0\u05DC\u05E2\u05D6\u05E8", "Eleazar", "Exodus 6:23"),
    ("\u05D0\u05D9\u05EA\u05DE\u05E8", "Ithamar", "Exodus 6:23"),
    ("\u05D1\u05E6\u05DC\u05D0\u05DC", "Bezalel", "Exodus 31:2"),
    ("\u05D0\u05D4\u05DC\u05D9\u05D0\u05D1", "Oholiab", "Exodus 31:6"),
    # --- NUMBERS ---
    ("\u05DB\u05DC\u05D1", "Caleb", "Numbers 13:6"),
    ("\u05D1\u05DC\u05E2\u05DD", "Balaam", "Numbers 22:5"),
    ("\u05D1\u05DC\u05E7", "Balak", "Numbers 22:2"),
    ("\u05E4\u05D9\u05E0\u05D7\u05E1", "Phinehas", "Numbers 25:7"),
    # --- JOSHUA ---
    ("\u05E2\u05DB\u05DF", "Achan", "Joshua 7:1"),
    ("\u05E8\u05D7\u05D1", "Rahab", "Joshua 2:1"),
    # --- JUDGES ---
    ("\u05E2\u05EA\u05E0\u05D9\u05D0\u05DC", "Othniel", "Judges 3:9"),
    ("\u05D0\u05D4\u05D5\u05D3", "Ehud", "Judges 3:15"),
    ("\u05E9\u05DE\u05D2\u05E8", "Shamgar", "Judges 3:31"),
    ("\u05D3\u05D1\u05E8\u05D4", "Deborah", "Judges 4:4"),
    ("\u05D1\u05E8\u05E7", "Barak", "Judges 4:6"),
    ("\u05E1\u05D9\u05E1\u05E8\u05D0", "Sisera", "Judges 4:2"),
    ("\u05D9\u05E2\u05DC", "Jael", "Judges 4:17"),
    ("\u05D2\u05D3\u05E2\u05D5\u05DF", "Gideon", "Judges 6:11"),
    ("\u05EA\u05D5\u05DC\u05E2", "Tola", "Judges 10:1"),
    ("\u05D9\u05D0\u05D9\u05E8", "Jair", "Judges 10:3"),
    ("\u05D9\u05E4\u05EA\u05D7", "Jephthah", "Judges 11:1"),
    ("\u05D0\u05D1\u05E6\u05DF", "Ibzan", "Judges 12:8"),
    ("\u05D0\u05D9\u05DC\u05D5\u05DF", "Elon", "Judges 12:11"),
    ("\u05E2\u05D1\u05D3\u05D5\u05DF", "Abdon", "Judges 12:13"),
    ("\u05E9\u05DE\u05E9\u05D5\u05DF", "Samson", "Judges 13:24"),
    ("\u05D3\u05DC\u05D9\u05DC\u05D4", "Delilah", "Judges 16:4"),
    # --- RUTH ---
    ("\u05D0\u05DC\u05D9\u05DE\u05DC\u05DA", "Elimelech", "Ruth 1:2"),
    ("\u05E0\u05E2\u05DE\u05D9", "Naomi", "Ruth 1:2"),
    ("\u05E2\u05E8\u05E4\u05D4", "Orpah", "Ruth 1:4"),
    ("\u05E8\u05D5\u05EA", "Ruth", "Ruth 1:4"),
    ("\u05D1\u05E2\u05D6", "Boaz", "Ruth 2:1"),
    # --- 1 SAMUEL ---
    ("\u05E2\u05DC\u05D9", "Eli", "1 Samuel 1:3"),
    ("\u05D7\u05E0\u05D4", "Hannah", "1 Samuel 1:2"),
    ("\u05E9\u05DE\u05D5\u05D0\u05DC", "Samuel", "1 Samuel 1:20"),
    ("\u05E9\u05D0\u05D5\u05DC", "Saul", "1 Samuel 9:2"),
    ("\u05D9\u05D5\u05E0\u05EA\u05DF", "Jonathan", "1 Samuel 13:2"),
    ("\u05DE\u05D9\u05DB\u05DC", "Michal", "1 Samuel 14:49"),
    ("\u05D0\u05D1\u05E0\u05E8", "Abner", "1 Samuel 14:50"),
    ("\u05D9\u05E9\u05D9", "Jesse", "1 Samuel 16:1"),
    ("\u05D3\u05D5\u05D3", "David", "1 Samuel 16:13"),
    ("\u05D2\u05DC\u05D9\u05EA", "Goliath", "1 Samuel 17:4"),
    ("\u05D0\u05D7\u05D9\u05DE\u05DC\u05DA", "Ahimelech", "1 Samuel 21:1"),
    ("\u05E0\u05D1\u05DC", "Nabal", "1 Samuel 25:3"),
    ("\u05D0\u05D1\u05D9\u05D2\u05DC", "Abigail", "1 Samuel 25:3"),
    # --- 2 SAMUEL ---
    ("\u05D9\u05D5\u05D0\u05D1", "Joab", "2 Samuel 2:13"),
    ("\u05D0\u05DE\u05E0\u05D5\u05DF", "Amnon", "2 Samuel 3:2"),
    ("\u05D0\u05D1\u05E9\u05DC\u05D5\u05DD", "Absalom", "2 Samuel 3:3"),
    ("\u05DE\u05E4\u05D9\u05D1\u05E9\u05EA", "Mephibosheth", "2 Samuel 4:4"),
    ("\u05E0\u05EA\u05DF", "Nathan", "2 Samuel 7:2"),
    ("\u05D0\u05D5\u05E8\u05D9\u05D4", "Uriah", "2 Samuel 11:3"),
    ("\u05D1\u05EA\u05E9\u05D1\u05E2", "Bathsheba", "2 Samuel 11:3"),
    # --- 1 KINGS ---
    ("\u05E9\u05DC\u05DE\u05D4", "Solomon", "1 Kings 1:11"),
    ("\u05D7\u05D9\u05E8\u05DD", "Hiram", "1 Kings 5:1"),
    ("\u05E9\u05D1\u05D0", "Queen of Sheba", "1 Kings 10:1"),
    ("\u05D9\u05E8\u05D1\u05E2\u05DD", "Jeroboam", "1 Kings 11:26"),
    ("\u05E8\u05D7\u05D1\u05E2\u05DD", "Rehoboam", "1 Kings 11:43"),
    ("\u05D0\u05D7\u05D0\u05D1", "Ahab", "1 Kings 16:28"),
    ("\u05D0\u05D9\u05D6\u05D1\u05DC", "Jezebel", "1 Kings 16:31"),
    ("\u05D0\u05DC\u05D9\u05D4\u05D5", "Elijah", "1 Kings 17:1"),
    ("\u05D0\u05DC\u05D9\u05E9\u05E2", "Elisha", "1 Kings 19:16"),
    ("\u05E0\u05D1\u05D5\u05EA", "Naboth", "1 Kings 21:1"),
    ("\u05D9\u05D4\u05D5\u05E9\u05E4\u05D8", "Jehoshaphat", "1 Kings 15:24"),
    # --- 2 KINGS ---
    ("\u05E0\u05E2\u05DE\u05DF", "Naaman", "2 Kings 5:1"),
    ("\u05D9\u05D5\u05D0\u05E9", "Joash", "2 Kings 11:2"),
    ("\u05E2\u05D6\u05D9\u05D4\u05D5", "Uzziah", "2 Kings 15:13"),
    ("\u05D7\u05D6\u05E7\u05D9\u05D4\u05D5", "Hezekiah", "2 Kings 18:1"),
    ("\u05DE\u05E0\u05E9\u05D4", "Manasseh (king)", "2 Kings 21:1"),
    ("\u05D9\u05D0\u05E9\u05D9\u05D4\u05D5", "Josiah", "2 Kings 22:1"),
    ("\u05E6\u05D3\u05E7\u05D9\u05D4\u05D5", "Zedekiah", "2 Kings 24:17"),
    # --- EZRA / NEHEMIAH ---
    ("\u05D6\u05E8\u05D1\u05D1\u05DC", "Zerubbabel", "Ezra 2:2"),
    ("\u05E2\u05D6\u05E8\u05D0", "Ezra", "Ezra 7:1"),
    ("\u05E0\u05D7\u05DE\u05D9\u05D4", "Nehemiah", "Nehemiah 1:1"),
    # --- ESTHER ---
    ("\u05D0\u05D7\u05E9\u05D5\u05E8\u05D5\u05E9", "Ahasuerus", "Esther 1:1"),
    ("\u05D5\u05E9\u05EA\u05D9", "Vashti", "Esther 1:9"),
    ("\u05DE\u05E8\u05D3\u05DB\u05D9", "Mordecai", "Esther 2:5"),
    ("\u05D0\u05E1\u05EA\u05E8", "Esther", "Esther 2:7"),
    ("\u05D4\u05DE\u05DF", "Haman", "Esther 3:1"),
    # --- JOB ---
    ("\u05D0\u05D9\u05D5\u05D1", "Job", "Job 1:1"),
    ("\u05D0\u05DC\u05D9\u05E4\u05D6", "Eliphaz", "Job 2:11"),
    ("\u05D1\u05DC\u05D3\u05D3", "Bildad", "Job 2:11"),
    ("\u05E6\u05D5\u05E4\u05E8", "Zophar", "Job 2:11"),
    ("\u05D0\u05DC\u05D9\u05D4\u05D5\u05D0", "Elihu", "Job 32:2"),
    # --- PSALMS ---
    ("\u05D0\u05E1\u05E3", "Asaph", "1 Chronicles 6:39"),
    # --- PROPHETS ---
    ("\u05D9\u05E9\u05E2\u05D9\u05D4\u05D5", "Isaiah", "Isaiah 1:1"),
    ("\u05D0\u05D7\u05D6", "Ahaz", "Isaiah 7:1"),
    ("\u05DB\u05D5\u05E8\u05E9", "Cyrus", "Isaiah 44:28"),
    ("\u05D9\u05E8\u05DE\u05D9\u05D4\u05D5", "Jeremiah", "Jeremiah 1:1"),
    ("\u05D1\u05E8\u05D5\u05DA", "Baruch", "Jeremiah 32:12"),
    ("\u05E0\u05D1\u05D5\u05DB\u05D3\u05E0\u05E6\u05E8", "Nebuchadnezzar", "Jeremiah 21:2"),
    ("\u05D2\u05D3\u05DC\u05D9\u05D4\u05D5", "Gedaliah", "Jeremiah 39:14"),
    ("\u05D9\u05D7\u05D6\u05E7\u05D0\u05DC", "Ezekiel", "Ezekiel 1:3"),
    ("\u05D3\u05E0\u05D9\u05D0\u05DC", "Daniel", "Daniel 1:6"),
    ("\u05E9\u05D3\u05E8\u05DA", "Shadrach", "Daniel 1:7"),
    ("\u05DE\u05D9\u05E9\u05DA", "Meshach", "Daniel 1:7"),
    ("\u05E2\u05D1\u05D3\u05E0\u05D2\u05D5", "Abednego", "Daniel 1:7"),
    ("\u05D1\u05DC\u05E9\u05D0\u05E6\u05E8", "Belshazzar", "Daniel 5:1"),
    ("\u05D3\u05E8\u05D9\u05D5\u05E9", "Darius", "Daniel 5:31"),
    ("\u05D4\u05D5\u05E9\u05E2", "Hosea", "Hosea 1:1"),
    ("\u05D2\u05DE\u05E8", "Gomer (wife of Hosea)", "Hosea 1:3"),
    ("\u05D9\u05D5\u05D0\u05DC", "Joel", "Joel 1:1"),
    ("\u05E2\u05DE\u05D5\u05E1", "Amos", "Amos 1:1"),
    ("\u05E2\u05D1\u05D3\u05D9\u05D4", "Obadiah", "Obadiah 1:1"),
    ("\u05D9\u05D5\u05E0\u05D4", "Jonah", "Jonah 1:1"),
    ("\u05DE\u05D9\u05DB\u05D4", "Micah", "Micah 1:1"),
    ("\u05E0\u05D7\u05D5\u05DD", "Nahum", "Nahum 1:1"),
    ("\u05D7\u05D1\u05E7\u05D5\u05E7", "Habakkuk", "Habakkuk 1:1"),
    ("\u05E6\u05E4\u05E0\u05D9\u05D4", "Zephaniah", "Zephaniah 1:1"),
    ("\u05D7\u05D2\u05D9", "Haggai", "Haggai 1:1"),
    ("\u05D6\u05DB\u05E8\u05D9\u05D4", "Zechariah", "Zechariah 1:1"),
    ("\u05DE\u05DC\u05D0\u05DB\u05D9", "Malachi", "Malachi 1:1"),
    # --- KEY DIVINE/SACRED NAMES ---
    ("\u05D9\u05D4\u05D5\u05D4", "YHWH (LORD)", "Genesis 2:4"),
    ("\u05D0\u05DC\u05D4\u05D9\u05DD", "Elohim (God)", "Genesis 1:1"),
    ("\u05D9\u05E9\u05E8\u05D0\u05DC", "Israel", "Genesis 32:28"),
]


def book_order(ref):
    """Return a sort key based on biblical book order and chapter:verse."""
    BOOK_ORDER = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth",
        "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
        "1 Chronicles", "2 Chronicles",
        "Ezra", "Nehemiah", "Esther",
        "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
        "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah",
        "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi"
    ]
    parts = ref.rsplit(" ", 1)
    book = parts[0]
    cv = parts[1] if len(parts) > 1 else "1:1"

    book_idx = 999
    for i, b in enumerate(BOOK_ORDER):
        if b.lower() == book.lower():
            book_idx = i
            break

    chapter = 0
    verse = 0
    if ":" in cv:
        try:
            chapter = int(cv.split(":")[0])
            verse = int(cv.split(":")[1])
        except ValueError:
            pass
    else:
        try:
            chapter = int(cv)
        except ValueError:
            pass

    return (book_idx, chapter, verse)


def main():
    words_path = os.path.join(ROOT_DIR, "words.json")
    output_path = os.path.join(ROOT_DIR, "data", "bible_names.json")

    print("[INFO] Loading words.json...")
    if not os.path.exists(words_path):
        print("[FAIL] words.json not found at", words_path)
        sys.exit(1)

    with open(words_path, "r", encoding="utf-8") as f:
        words_data = json.load(f)

    print(f"[OK] Loaded {len(words_data)} word entries")

    # Process each name - look up by Hebrew characters (the actual key)
    results = []
    found = 0
    not_found = 0

    for hebrew_chars, english, ref in BIBLE_NAMES:
        entry = words_data.get(hebrew_chars)

        if entry and isinstance(entry, dict):
            found += 1
            name_record = {
                "english": english,
                "hebrew": entry.get("hebrew", hebrew_chars),
                "transliteration": entry.get("transliteration", ""),
                "gematria": entry.get("gematria", 0),
                "digital_root": entry.get("digital_root", 0),
                "first_occurrence": ref,  # Use OUR reference for proper sorting
                "first_occurrence_word": entry.get("first_occurrence", ""),
                "frequency": entry.get("frequency", 0),
                "strongs": entry.get("strongs", ""),
                "letters": entry.get("letters", []),
                "pictographic": entry.get("pictographic", ""),
                "definition": entry.get("definition", ""),
                "timeline": entry.get("timeline", {}),
                "corruption_timeline": entry.get("corruption_timeline", {}),
                "lookup_key": hebrew_chars,
            }
            results.append(name_record)
        else:
            not_found += 1
            # Still include with what we know
            results.append({
                "english": english,
                "hebrew": hebrew_chars,
                "transliteration": "",
                "gematria": 0,
                "digital_root": 0,
                "first_occurrence": ref,
                "frequency": 0,
                "strongs": "",
                "letters": [],
                "pictographic": "",
                "definition": "",
                "timeline": {},
                "corruption_timeline": {},
                "lookup_key": hebrew_chars,
                "_not_found": True,
            })

    # Sort by biblical order
    results.sort(key=lambda x: book_order(x["first_occurrence"]))

    # Assign sequential order number
    for i, r in enumerate(results):
        r["order"] = i + 1

    # Summary
    print(f"[OK] Processed {len(results)} names: {found} found in words.json, {not_found} not found")
    if not_found > 0:
        print("[WARN] Names not found in words.json:")
        for r in results:
            if r.get("_not_found"):
                print(f"  - {r['english']} (hebrew: {r['hebrew']})")

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Clean _not_found flag before writing
    for r in results:
        r.pop("_not_found", None)

    output = {
        "meta": {
            "title": "Biblical Names - Ordered by First Appearance",
            "total_names": len(results),
            "found_in_words_json": found,
            "not_found": not_found,
            "source": "Training knowledge matched against words.json (58,400 entries)",
            "scope": "Old Testament / Hebrew Bible (Masoretic Text)",
        },
        "names": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] Output written to {output_path}")
    print(f"[OK] File size: {os.path.getsize(output_path):,} bytes")

    # Show Genesis 5 patriarchs gematria sequence
    print("\n--- Genesis 5 Patriarchs Gematria Sequence ---")
    gen5_names = ["Adam", "Seth (Sheth)", "Enosh", "Kenan", "Mahalalel",
                  "Jared", "Enoch (son of Jared)", "Methuselah",
                  "Lamech (father of Noah)", "Noah"]
    for name_str in gen5_names:
        for r in results:
            if r["english"] == name_str:
                print(f"  {r['english']}: {r['hebrew']} = {r['gematria']} (dr={r['digital_root']}) - {r['pictographic'][:80]}")
                break

    # Show the name meaning sequence
    print("\n--- Name Meaning Sequence (Pictographic) ---")
    for r in results[:30]:
        defn = r.get("definition", "")[:60]
        print(f"  {r['order']}. {r['english']}: {r['hebrew']} = {defn}")


if __name__ == "__main__":
    main()
