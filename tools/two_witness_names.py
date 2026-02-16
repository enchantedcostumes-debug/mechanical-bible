"""
TWO-WITNESS VERIFICATION: Compare our bible_names.json against Hitchcock's Bible Names Dictionary.

Witness 1: Our mechanical Bible extraction (2,338 names)
Witness 2: Hitchcock's Bible Names Dictionary (1869, public domain, ~2,500 OT names)

This is the biblical standard: "By the mouth of two or three witnesses shall
every word be established." - 2 Corinthians 13:1
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)

# Load our data
with open(os.path.join(REPO_DIR, 'data', 'bible_names.json'), 'r', encoding='utf-8') as f:
    our_data = json.load(f)

our_names = {}
for n in our_data['names']:
    key = n['english'].lower().strip()
    our_names[key] = n

# Hitchcock's Bible Names Dictionary - OT names only
# Source: https://ccel.org/h/hitchcock/bible_names/bible_names.txt
# Filtered to remove obvious NT-only names (Apostles, Greek cities, etc.)
HITCHCOCK_OT = [
    "Aaron","Abaddon","Abagtha","Abana","Abarim","Abba","Abda","Abdeel","Abdi",
    "Abdiel","Abdon","Abel","Abi","Abiah","Abi-albon","Abiasaph","Abiathar","Abib",
    "Abidah","Abidan","Abiel","Abiezer","Abigail","Abihail","Abihu","Abihud","Abijah",
    "Abijam","Abimael","Abimelech","Abinadab","Abinoam","Abiram","Abishag","Abishai",
    "Abishalom","Abishua","Abishur","Abital","Abitub","Abner","Abram","Abraham",
    "Absalom","Accad","Achan","Achbor","Achish","Achmetha","Achor","Achsah","Achshaph",
    "Achzib","Adadah","Adah","Adaiah","Adaliah","Adam","Adamah","Adami","Adar","Adbeel",
    "Addi","Addon","Adiel","Adin","Adithaim","Adlai","Admah","Admatha","Adna","Adnah",
    "Adoni-bezek","Adonijah","Adonikam","Adoniram","Adoni-zedek","Adoraim","Adoram",
    "Adrammelech","Adriel","Adullam","Adummim","Agag","Agee","Agur","Ahab","Aharah",
    "Aharhel","Ahasbai","Ahasuerus","Ahava","Ahaz","Ahaziah","Ahi","Ahiah","Ahiam",
    "Ahian","Ahiezer","Ahihud","Ahijah","Ahikam","Ahilud","Ahimaaz","Ahiman",
    "Ahimelech","Ahimoth","Ahinadab","Ahinoam","Ahio","Ahira","Ahiram","Ahisamach",
    "Ahishahur","Ahishar","Ahithophel","Ahitub","Ahlab","Ahlai","Ahoah","Aholah",
    "Aholiab","Aholibah","Aholibamah","Ahumai","Ahuzam","Ahuzzah","Ai","Aiah","Aiath",
    "Ain","Ajalon","Akkub","Alammelech","Alemeth","Alian","Allon","Almodad","Almon",
    "Alvah","Amad","Amal","Amalek","Amana","Amariah","Amasa","Amasai","Amashai","Ami",
    "Amaziah","Amittai","Ammah","Ammi","Ammiel","Ammihud","Ammi-nadab","Ammishaddai",
    "Ammizabad","Ammon","Amnon","Amok","Amon","Amos","Amoz","Amram","Amraphel","Amzi",
    "Anab","Anah","Anaharath","Anak","Anamim","Anammelech","Anani","Anathoth","Anem",
    "Aner","Aniam","Anim","Anub","Aphek","Aphekah","Aphik","Aphiah","Appaim","Ar","Ara",
    "Arab","Arad","Arah","Aram","Aran","Ararat","Araunah","Arba","Ard","Ardon","Areli",
    "Ariel","Arioch","Arnon","Aroer","Arpad","Arphaxad","Arumah","Asa","Asahel","Asaiah",
    "Asaph","Asareel","Asenath","Ashan","Ashbel","Ashdod","Asher","Ashima","Ashkenaz",
    "Ashnah","Ashriel","Ashtaroth","Ashtoreth","Ashur","Asiel","Askelon","Asnapper",
    "Asriel","Assir","Asshurim","Atad","Atarah","Ataroth","Ater","Athach","Athaiah",
    "Athaliah","Athlai","Attai","Ava","Aven","Avim","Avith","Azaliah","Azaniah",
    "Azareel","Azariah","Azaz","Azazel","Azaziah","Azekah","Azgad","Azmaveth","Azmon",
    "Azriel","Azrikam","Azubah","Azur","Azzan","Azzur","Baal","Baalah","Baalath",
    "Baal-berith","Baal-gad","Baal-hamon","Baal-hermon","Baali","Baalim","Baalis",
    "Baal-meon","Baal-peor","Baal-perazim","Baal-shalisha","Baal-tamar","Baal-zebub",
    "Baal-zephon","Baanah","Baara","Baaseiah","Baasha","Babel","Baca","Bahurim","Bajith",
    "Balaam","Baladan","Balak","Bamah","Barachel","Barak","Baruch","Barzillai","Bashan",
    "Bashemath","Bathsheba","Bealiah","Bealoth","Bebai","Becher","Bechorath","Bedad",
    "Bedaiah","Bedan","Beeliada","Beer","Beera","Beeri","Beeroth","Beersheba","Behemoth",
    "Belah","Belial","Belshazzar","Belteshazzar","Ben","Benaiah","Ben-ammi","Beneberak",
    "Benhadad","Benhail","Benhanan","Benjamin","Beno","Benoni","Benzoheth","Beon","Beor",
    "Bera","Berachah","Berachiah","Beraiah","Bered","Beri","Beriah","Berith",
    "Berodach-baladan","Berothai","Besai","Besodeiah","Besor","Betah","Beten","Beth-aven",
    "Beth-barah","Beth-car","Beth-dagon","Beth-el","Bether","Beth-ezal","Beth-gader",
    "Beth-gamul","Beth-haccerem","Beth-haran","Beth-horon","Beth-lehem","Beth-peor",
    "Beth-rapha","Bethshan","Beth-shean","Beth-shemesh","Bethuel","Beth-zur","Betonim",
    "Beulah","Bezai","Bezaleel","Bezek","Bezer","Bichri","Bidkar","Bigthan","Bigvai",
    "Bildad","Bileam","Bilgah","Bilhah","Bilhan","Bilshan","Binea","Binnui","Birsha",
    "Bishlam","Bithiah","Bithron","Boaz","Bocheru","Bochim","Bohan","Bozez","Bozrah",
    "Bukki","Bukkiah","Bul","Bunah","Bunni","Buz","Buzi","Cabbon","Cabul","Cain",
    "Cainan","Calah","Calcol","Caleb","Calneh","Calno","Camon","Canaan","Carmel","Carmi",
    "Carshena","Casiphia","Casluhim","Chebar","Chedorlaomer","Chelal","Chelub","Chelluh",
    "Chelubai","Chemosh","Chenaanah","Chenani","Chenaniah","Chephirah","Cheran","Cherith",
    "Chesed","Chesil","Chesulloth","Chidon","Chiliab","Chilion","Chilmad","Chimham",
    "Chisleu","Chislon","Chun","Chushan-rishathaim","Coz","Cozbi","Cush","Cushan","Cushi",
    "Dabbasheth","Daberath","Dagon","Dalaiah","Dalphon","Damascus","Dan","Dannah","Darah",
    "Darda","Darius","Darkon","Dathan","David","Debir","Deborah","Dedan","Dekar","Delaiah",
    "Delilah","Deuel","Diblaim","Diblath","Dibon","Dibri","Diklah","Dilean","Dimon",
    "Dimonah","Dinah","Dinhabah","Dishan","Dishon","Dodai","Dodanim","Dodavah","Dodo",
    "Doeg","Dophkah","Dor","Dothan","Dumah","Dura","Ebal","Ebed","Ebed-melech",
    "Eben-ezer","Eber","Ebiasaph","Ebronah","Ed","Eden","Eder","Edom","Edrei","Eglah",
    "Eglaim","Eglon","Ehud","Eker","Ekron","Eladah","Elah","Elam","Elasah","Elath",
    "Eldaah","Eldad","Elead","Elealeh","Eleazar","Elhanan","Eli","Eliab","Eliada","Eliah",
    "Eliahba","Eliakim","Eliam","Eliasaph","Eliashib","Eliathah","Elidad","Eliel",
    "Elienai","Eliezer","Elihoreph","Elihu","Elijah","Elika","Elim","Elimelech",
    "Elioenai","Eliphal","Eliphalet","Eliphaz","Elisha","Elishah","Elishama","Elishaphat",
    "Elisheba","Elishua","Elkanah","Ellasar","Elnaam","Elnathan","Elon","Elpaal","Elpalet",
    "Eltekeh","Eltolad","Elul","Eluzai","Elzabad","Elzaphan","Enam","Enan","En-dor",
    "En-gedi","En-hakkore","En-mishpat","Enoch","Enos","Ephah","Epher","Ephraim",
    "Ephratah","Ephrath","Ephron","Er","Eran","Erech","Eri","Esau","Esek","Esh-baal",
    "Esh-ban","Eshcol","Eshean","Eshek","Eshtaol","Eshtemoa","Esther","Etam","Etham",
    "Ethan","Ethbaal","Ether","Ethnan","Ethni","Eve","Evi","Evil-merodach","Ezbon",
    "Ezekiel","Ezel","Ezem","Ezer","Ezion-geber","Ezra","Ezri","Gaal","Gaash","Gabbai",
    "Gabriel","Gad","Gaddi","Gaddiel","Galal","Galeed","Gallim","Gamaliel","Gamul","Gareb",
    "Gatam","Gath","Gaza","Gazer","Gazez","Gazzam","Geba","Gebal","Geber","Gebim",
    "Gedaliah","Geder","Gederah","Gederoth","Gederothaim","Gehazi","Geliloth","Gemalli",
    "Gemariah","Genubath","Gera","Gerar","Gerizim","Gershom","Gershon","Geshur","Gether",
    "Geuel","Gezer","Giah","Gibbar","Gibbethon","Gibeah","Gibeon","Giddel","Gideon",
    "Gideoni","Gihon","Gilalai","Gilboa","Gilead","Gilgal","Giloh","Gimzo","Ginath",
    "Gispa","Gob","Gog","Golan","Goliath","Gomer","Gomorrah","Goshen","Gozan","Gudgodah",
    "Guni","Gur","Habakkuk","Habazinaiah","Habor","Hachaliah","Hachilah","Hachmoni",
    "Hadad","Hadadezer","Hadadrimmon","Hadar","Hadarezer","Hadashah","Hadassah","Hadid",
    "Hadlai","Hadoram","Hadrach","Hagab","Hagabah","Hagar","Haggai","Haggi","Haggiah",
    "Haggith","Hakkatan","Hakkoz","Hakupha","Halah","Halak","Halhul","Hali","Ham","Haman",
    "Hamath","Hammedatha","Hammelech","Hammon","Hamon-gog","Hamor","Hamul","Hamutal",
    "Hanameel","Hanan","Hananeel","Hanani","Hananiah","Hanes","Hannah","Hannathon",
    "Hanniel","Hanoch","Hanun","Hara","Haradah","Haran","Harbonah","Hareph","Harhas",
    "Harhaiah","Harhur","Harim","Harnepher","Harod","Harosheth","Harsha","Harum",
    "Harumaph","Haruz","Hasadiah","Hashabiah","Hashabnah","Hashabniah","Hashem","Hashub",
    "Hashubah","Hashum","Hashupha","Hasrah","Hatach","Hathath","Hatita","Hattil","Hattipha",
    "Hattush","Hauran","Havilah","Hazael","Hazaiah","Hazarmaveth","Hazelelponi","Hazeroth",
    "Hazo","Hazor","Heber","Hebron","Hegai","Helam","Helbah","Helbon","Heldai","Heleb",
    "Helek","Helem","Heleph","Helez","Helkai","Helon","Heman","Hen","Hena","Henadad",
    "Henoch","Hepher","Hephzibah","Heres","Heresh","Hermon","Heshbon","Heshmon","Heth",
    "Hethlon","Hezekiah","Hezir","Hezrai","Hezron","Hiddai","Hiddekel","Hiel","Hilkiah",
    "Hillel","Hinnom","Hirah","Hiram","Hobab","Hobah","Hod","Hodaiah","Hodaviah","Hodesh",
    "Hodiah","Hodijah","Hoglah","Hoham","Holon","Homam","Hophin","Hor","Horam","Horeb",
    "Horem","Hori","Hormah","Horonaim","Hosah","Hosea","Hoshea","Hoshaiah","Hoshama",
    "Hotham","Hothir","Hukkok","Hul","Huldah","Hupham","Huppim","Hur","Huram","Huri",
    "Hushah","Hushai","Hushim","Ibhar","Ibleam","Ibneiah","Ibniah","Ibri","Ibzan",
    "Ichabod","Idalah","Idbash","Iddo","Igal","Igdaliah","Ijon","Ikkesh","Imlah","Immer",
    "Imnah","Imrah","Imri","Iphedeiah","Ir","Ira","Irad","Iram","Iri","Irijah","Irpeel",
    "Isaac","Iscah","Ishbak","Ishbi-benob","Ishbosheth","Ishi","Ishiah","Ishma","Ishmael",
    "Ishmaiah","Ishmerai","Ishod","Israel","Issachar","Isui","Ithai","Ithamar","Ithiel",
    "Ithmah","Ithran","Ithream","Izhar","Izrahiah","Izri","Jaakan","Jaakobah","Jaala",
    "Jaalam","Jaanai","Jaasiel","Jaazaniah","Jaaziel","Jabal","Jabbok","Jabesh","Jabez",
    "Jabin","Jabneh","Jabneel","Jachan","Jachin","Jacob","Jada","Jaddua","Jael","Jagur",
    "Jahath","Jahaz","Jahaziel","Jahdiel","Jahdo","Jahleel","Jahmai","Jahzeel","Jair",
    "Jakim","Jalon","Jamin","Jamlech","Janoah","Janum","Japhia","Japhlet","Japho","Jarah",
    "Jareb","Jared","Jaresiah","Jarib","Jarmuth","Jashen","Jashobeam","Jashub","Jasiel",
    "Jathniel","Jattir","Javan","Jazer","Jaziz","Jearim","Jebus","Jecamiah","Jecoliah",
    "Jeconiah","Jedaiah","Jediael","Jedidah","Jedidiah","Jeduthun","Jegar-sahadutha",
    "Jehaziel","Jehdeiah","Jehiah","Jehiskiah","Jehoadah","Jehoaddan","Jehoahaz","Jehoash",
    "Jehohanan","Jehoiachin","Jehoiada","Jehoiakim","Jehoiarib","Jehonadab","Jehonathan",
    "Jehoram","Jehoshaphat","Jehosheba","Jehoshua","Jehozabad","Jehozadak","Jehu",
    "Jehubbah","Jehucal","Jehud","Jehudi","Jehudijah","Jekabzeel","Jekamean","Jekamiah",
    "Jekuthiel","Jemima","Jemuel","Jephunneh","Jerah","Jerahmeel","Jered","Jeremai",
    "Jeremiah","Jeremoth","Jeriah","Jericho","Jeriel","Jerimoth","Jerioth","Jeroboam",
    "Jeroham","Jerubbaal","Jerubbesheth","Jeruel","Jerusalem","Jerusha","Jesaiah",
    "Jeshebeab","Jesher","Jeshimon","Jeshua","Jesimiel","Jesse","Jether","Jetheth",
    "Jethlah","Jethro","Jetur","Jeuel","Jeush","Jezaniah","Jezebel","Jezer","Jeziel",
    "Jezreel","Jibsam","Jidlaph","Jimnah","Joab","Joah","Joahaz","Joash","Job","Jobab",
    "Jochebed","Joed","Joel","Joezer","Jogbehah","Jogli","Joha","Johanan","Joiarib",
    "Jokdeam","Jokim","Jokmeam","Jokneam","Jokshan","Joktan","Jonah","Jonathan","Joppa",
    "Jorah","Jorai","Joram","Jordan","Joseph","Joshah","Joshaviah","Joshbekesha","Joshua",
    "Josiah","Josibiah","Josiphiah","Jotham","Jozabad","Jozachar","Jubal","Judah","Judith",
    "Juttah","Kabzeel","Kadesh","Kadmiel","Kallai","Kanah","Kareah","Karkor","Kartah",
    "Kedar","Kedemah","Kedemoth","Keilah","Kelaiah","Kelitah","Kemuel","Kenan","Kenaz",
    "Keren-happuch","Kerioth","Keros","Keturah","Kezia","Kibzaim","Kidron","Kinah","Kir",
    "Kirjath","Kirjath-arba","Kirjath-jearim","Kish","Kishi","Kishion","Kishon","Kithlish",
    "Kitron","Kittim","Koa","Kohath","Korah","Laban","Lachish","Lael","Lahad","Lahmam",
    "Lahmi","Laish","Lamech","Lapidoth","Leah","Lehabim","Lehi","Lemuel","Leshem","Levi",
    "Libnah","Libni","Lo-ammi","Lod","Lo-ruhamah","Lot","Lotan","Lud","Ludim","Luhith",
    "Luz","Maachah","Maadai","Maadiah","Maaseiah","Maaz","Machbenah","Machbanai","Machi",
    "Machir","Machpelah","Madai","Madmannah","Madon","Magbish","Magdiel","Magog",
    "Magpiash","Mahalah","Mahalath","Mahali","Mahanaim","Maharai","Mahath","Mahazioth",
    "Mahlah","Mahli","Mahlon","Makkedah","Malachi","Malcham","Malchiah","Malchiel",
    "Mallothi","Malluch","Mamre","Manasseh","Manoah","Maon","Mara","Marah","Mareshah",
    "Maroth","Marsena","Mash","Masrekah","Massa","Matred","Matri","Mattan","Mattaniah",
    "Mebunnai","Medad","Medan","Medeba","Megiddo","Megiddon","Mehetabel","Mehida","Mehir",
    "Mehujael","Mehuman","Melatiah","Melchizedek","Melech","Menahem","Mephaath",
    "Mephibosheth","Merab","Meraioth","Merari","Mered","Meremoth","Meres","Meribah",
    "Meribbaal","Merodach-baladan","Merom","Meroz","Mesha","Meshach","Meshech",
    "Meshelemiah","Meshullam","Methusael","Methuselah","Meunim","Mezahab","Mibhar",
    "Mibsam","Mibzar","Micah","Micaiah","Michael","Michal","Midian","Migdol","Migron",
    "Mijamin","Mikloth","Milcah","Milcom","Millo","Minni","Minnith","Miriam","Mishael",
    "Mishal","Misham","Mishma","Mishmannah","Mispar","Mithredath","Mizar","Mizpah",
    "Mizraim","Mizzah","Moab","Moladah","Molech","Molid","Mordecai","Moreh","Moriah",
    "Moserah","Moses","Muppim","Mushi","Naam","Naamah","Naaman","Naarah","Naarai",
    "Naashon","Nabal","Naboth","Nachon","Nahor","Nadab","Nahaliel","Nahallal","Naham",
    "Nahamani","Naharai","Nahash","Nahath","Nahbi","Nahshon","Nahum","Naioth","Naomi",
    "Naphish","Naphtali","Nathan","Neariah","Nebaioth","Neballat","Nebat","Nebo",
    "Nebuchadnezzar","Necho","Nedabiah","Nehemiah","Nehum","Nehushta","Nehushtan","Neiel",
    "Nekoda","Nemuel","Nepheg","Ner","Neriah","Nethaneel","Nethaniah","Neziah","Nezib",
    "Nibhaz","Nibshan","Nimrah","Nimrod","Nimshi","Nineveh","Nisroch","Noadiah","Noah",
    "Nob","Nobah","Nod","Nodab","Nogah","Non","Nun","Obadiah","Obal","Obed","Obed-edom",
    "Obil","Oboth","Ocran","Oded","Og","Ohad","Ohel","Omar","Omri","On","Onam","Onan",
    "Ono","Ophel","Ophir","Ophni","Ophrah","Oreb","Ornan","Orpah","Othni","Othniel",
    "Ozem","Ozni","Paarai","Padon","Pagiel","Pahath-Moab","Pai","Palal","Pallu","Palti",
    "Paltiel","Parah","Paran","Parmashta","Parnach","Parosh","Parshandatha","Paruah",
    "Pasach","Paseah","Pashur","Pathros","Pedahzur","Pedaiah","Pekah","Pekahiah","Pekod",
    "Pelaiah","Pelaliah","Pelatiah","Peleg","Peniel","Peninnah","Penuel","Peor","Peresh",
    "Perez","Perida","Perizzites","Persia","Peulthai","Pharaoh","Pharez","Phichol",
    "Phinehas","Phurah","Pinon","Piram","Pirathon","Pisgah","Pithom","Pithon","Pochereth",
    "Potiphar","Potipherah","Puah","Pul","Punon","Putiel","Raamah","Raamiah","Rabbah",
    "Raddai","Raguel","Rahab","Raham","Rakkath","Rakkon","Ram","Ramah","Ramath","Ramiah",
    "Ramoth","Raphah","Raphu","Reaiah","Reba","Rebekah","Rechab","Reelaiah","Regem",
    "Rehabiah","Rehob","Rehoboam","Rehoboth","Rehum","Rei","Rekem","Remaliah","Rephael",
    "Rephaiah","Rephidim","Resen","Reu","Reuben","Reuel","Reumah","Rezeph","Rezin","Rezon",
    "Ribai","Riblah","Rimmon","Rinnah","Riphath","Rissah","Rizpah","Rogelim","Rohgah",
    "Rosh","Ruth","Sabtah","Sabtechah","Sacar","Salah","Salathiel","Salcah","Salem",
    "Sallai","Sallu","Salma","Salmon","Samaria","Samlah","Samson","Samuel","Sanballat",
    "Sansannah","Saph","Sarah","Sarai","Sargon","Sarid","Satan","Saul","Seba","Secacah",
    "Sechu","Segub","Seir","Sela","Seled","Semachiah","Senaah","Seneh","Senir",
    "Sennacherib","Seorim","Sephar","Sepharad","Sepharvaim","Serah","Seraiah","Sered",
    "Serug","Seth","Sethur","Shaalbim","Shaaraim","Shaashgaz","Shabbethai","Shadrach",
    "Shage","Shalem","Shallum","Shalmai","Shalmaneser","Shamariah","Shamed","Shamer",
    "Shamgar","Shamhuth","Shamir","Shammah","Shammai","Shammoth","Shammuah","Shamsherai",
    "Shapham","Shaphan","Shaphat","Sharai","Sharar","Sharezer","Sharon","Shashai","Shashak",
    "Shaul","Shealtiel","Sheariah","Shear-jashub","Sheba","Shebaniah","Sheber","Shebna",
    "Shebuel","Shecaniah","Shechem","Shedeur","Shehariah","Shelah","Shelemiah","Sheleph",
    "Shelesh","Shelomi","Shelomith","Shelumiel","Shem","Shema","Shemaiah","Shemariah",
    "Shemeber","Shemer","Shemida","Shemiramoth","Shemuel","Shenazar","Shephatiah","Shephi",
    "Sherah","Sherebiah","Sheshach","Sheshai","Sheshan","Sheshbazzar","Shethar","Sheva",
    "Shilhi","Shilhim","Shillem","Shiloh","Shilshah","Shimeah","Shimeath","Shimei",
    "Shimeon","Shimma","Shimon","Shimrath","Shimshai","Shimri","Shimrith","Shimron",
    "Shinab","Shinar","Shiphi","Shiphrah","Shisha","Shishak","Shitrai","Shittim","Shiza",
    "Shoa","Shobab","Shobach","Shobai","Shobal","Shobek","Shoham","Shomer","Shophach",
    "Shua","Shuah","Shual","Shubael","Shuham","Shunem","Shuni","Shur","Shushan",
    "Shuthelah","Sibbechai","Sibmah","Sichem","Siddim","Sidon","Sihon","Simeon","Sin",
    "Sinai","Sippai","Sisera","Sitnah","So","Socoh","Sodi","Sodom","Solomon","Sophereth",
    "Sorek","Sotai","Suah","Succoth","Susi","Tabbaoth","Tabbath","Tabeel","Taberah",
    "Tabor","Tabrimon","Tadmor","Tahan","Tahath","Tahpenes","Tahrea","Talmai","Tamar",
    "Tammuz","Tanhumeth","Taphath","Tappuah","Tarah","Tarea","Tarshish","Tartak","Tartan",
    "Tatnai","Tebah","Tebaliah","Tehinnah","Tekoa","Telah","Telassar","Telem","Tema",
    "Teman","Terah","Thebez","Tibbath","Tibni","Tidal","Tiglath-pileser","Tikvah","Tilon",
    "Timnah","Timnath","Tiphsah","Tirhakah","Tiria","Tirzah","Tob","Tobiah","Tobijah",
    "Tochen","Togarmah","Tohu","Toi","Tola","Tolad","Tophel","Tophet","Tubal","Tubal-cain",
    "Ucal","Uel","Ulai","Ulam","Ulla","Ummah","Unni","Ur","Uri","Uriah","Uriel","Uthai",
    "Uz","Uzai","Uzal","Uzzah","Uzzi","Uzziah","Uzziel","Vajezatha","Vaniah","Vashni",
    "Vashti","Vophsi","Zaavan","Zabad","Zabbai","Zabdi","Zaccai","Zaccur","Zachariah",
    "Zadok","Zaham","Zair","Zalaph","Zalmon","Zalmonah","Zalmunna","Zanoah",
    "Zaphnath-paaneah","Zarah","Zared","Zarephath","Zaretan","Zatthu","Zaza","Zebadiah",
    "Zebah","Zebina","Zeboiim","Zebudah","Zebul","Zebulun","Zechariah","Zedad","Zedekiah",
    "Zeeb","Zelah","Zelek","Zelophehad","Zemaraim","Zemira","Zenan","Zephaniah","Zephath",
    "Zepho","Zephon","Zer","Zerah","Zerahiah","Zeredah","Zeresh","Zereth","Zeror","Zeruah",
    "Zerubbabel","Zeruiah","Zethar","Zia","Ziba","Zibeon","Zibiah","Zichri","Zidon","Ziha",
    "Ziklag","Zillah","Zilpah","Zilthai","Zimmah","Zimran","Zin","Zion","Zior","Ziph",
    "Ziphron","Zippor","Zipporah","Zithri","Ziz","Ziza","Zoan","Zoar","Zobah","Zobebah",
    "Zohar","Zoheleth","Zoheth","Zophah","Zophar","Zophim","Zorah","Zuar","Zuph","Zur",
    "Zuriel","Zurishaddai","Zuzims",
]

hitchcock_set = set(n.lower() for n in HITCHCOCK_OT)

print("=" * 70)
print("TWO-WITNESS VERIFICATION: Bible Names")
print("=" * 70)
print(f"Witness 1 (Our extraction): {len(our_names)} names")
print(f"Witness 2 (Hitchcock Dict): {len(hitchcock_set)} names")
print()

# Cross-reference
overlap = our_names.keys() & hitchcock_set
in_hitchcock_not_ours = hitchcock_set - our_names.keys()
in_ours_not_hitchcock = our_names.keys() - hitchcock_set

print(f"OVERLAP (both witnesses agree): {len(overlap)}")
print(f"In Hitchcock but NOT in ours: {len(in_hitchcock_not_ours)}")
print(f"In ours but NOT in Hitchcock: {len(in_ours_not_hitchcock)}")
print()

# Agreement rate
agreement = len(overlap) / len(hitchcock_set) * 100
print(f"AGREEMENT RATE: {agreement:.1f}% of Hitchcock names found in our data")
print()

# Missing from ours - these might be real gaps
print("=== IN HITCHCOCK BUT NOT IN OURS (potential gaps) ===")
missing_sorted = sorted(in_hitchcock_not_ours)
for i, name in enumerate(missing_sorted):
    print(f"  {i+1}. {name}")
print(f"Total: {len(missing_sorted)}")
print()

# Extra in ours - mechanical translation finds more
print(f"=== IN OURS BUT NOT IN HITCHCOCK (first 30 of {len(in_ours_not_hitchcock)}) ===")
extra_sorted = sorted(in_ours_not_hitchcock)
for name in extra_sorted[:30]:
    entry = our_names[name]
    print(f"  {name} ({entry.get('hebrew','')}) - {entry.get('first_occurrence','')} [{entry.get('category','')}]")
print(f"  ... and {len(extra_sorted) - 30} more")
print()

print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"Total verified names (in both): {len(overlap)}")
print(f"Agreement rate: {agreement:.1f}%")
print(f"Names unique to our extraction: {len(in_ours_not_hitchcock)}")
print(f"  (Expected - mechanical translation preserves more names)")
print(f"Names in Hitchcock we missed: {len(in_hitchcock_not_ours)}")
print(f"  (May be spelling variants or compound names)")
print()

if agreement >= 70:
    print("[OK] TWO-WITNESS VERIFICATION: PASSED")
    print("Both witnesses substantially agree on the biblical name corpus.")
else:
    print("[WARN] TWO-WITNESS VERIFICATION: NEEDS REVIEW")
    print("Significant disagreement between witnesses.")
