import random

PROFESSIONS = ["Shifokor","Jarroh","Hamshira","Farmatsevt","Muhandis","Mexanik","Elektrik","Dasturchi","Kiberxavfsizlik mutaxassisi","Biolog","Kimyogar","Fizik","Astronom","Fermer","Agronom","Veterinar","Psixolog","Psixiatr","O'qituvchi","Tarixchi","Harbiy","Snayper","Qutqaruvchi","O't o'chiruvchi","Politsiyachi","Uchuvchi","Kapitan","Navigator","Pazanda","Nonvoy","Santexnik","Quruvchi","Arxitektor","Geolog","Seismolog","Meteorolog","Ekolog","Bog'bon","Ovchi","Baliqchi","Radio muhandis","Elektronika ustasi","Tikuvchi","Dizayner","Rassom","Musiqachi","Aktrisa","Jurnalist","Yurist","Sudya","Diplomat","Tarjimon","Logist","Haydovchi","Traktorchi","Dron operatori","SMM mutaxassisi","Data analyst","AI mutaxassisi","Laborant","Dentist","Massajchi"]
HEALTH_STATUSES = ["Mutlaqo sog'lom","Yuqori qon bosimi","Diabet 1-tur","Diabet 2-tur","Astma","Ko'zi xiralashgan","Ko'r","Quloq eshitmaydi","Allergiya changga","Allergiya dori vositasiga","Miya chayqalishi izi","Yengil depressiya","Anemiya","Suyak mo'rtligi","Bel og'rig'i","Tizza jarohati","Qon ivish muammosi","Migren","Semizlik","Ozginlik","Immunitet kuchli","Homilador 3 oy","Homilador 7 oy","Yurak stimulyatori bor","Yurak sog'lom","Qalqonsimon bez muammosi","Epilepsiya","Uyqusizlik","Teri kasalligi","Saraton remissiya","Bir qo'li protez","Bir oyog'i protez","Surunkali bronxit","Gipermetropiya","Miyopiya","Vitamin yetishmovchiligi","Panik hujumlar","Travmadan keyingi stress","Laktoza intoleransi","Gluten intoleransi"]
HOBBIES = ["Bog'dorchilik","Ovchilik","Baliq ovlash","Shaxmat","Yugurish","Suzish","Kitob o'qish","Dasturlash","Robot yig'ish","Duradgorlik","Mebel ta'mirlash","Avto ta'mirlash","Pazandachilik","Non yopish","Tikuvchilik","To'qish","Rasm chizish","Gitara chalish","Pianino chalish","Yulduz kuzatish","Qush kuzatish","Meditatsiya","Yoga","Birinchi yordam","Qutqaruv kursi","Qurol tozalash","Kamondan otish","Karta o'yini","Storytelling","Xarita o'qish","Kompas","Til o'rganish","Jamoani boshqarish","Tog' yurishi","Velosiped","Video montaj","Hamradio","Elektronika lehimlash","Fermentatsiya","Asalarichilik"]
LUGGAGE_ITEMS = ["Birinchi yordam to'plami","Generator","Urug'lar to'plami","Qurol va o'q-dori","Suv filtri","Konserva qutisi","Quritilgan ovqat","Gaz plita","Benzin kanistri","Quyosh paneli","Qalin adyol","Issiq kiyimlar","Batareyalar","Radio","Satellit telefon","Noutbuk","Planshet","Toolbox","Payvandlash apparati","Balta","Arra","Kichik bolta","Arqon 50m","Kompas","GPS","Yong'in o'chirgich","Gaz niqobi","Himoya kostyumi","Tibbiy kitob","Botanika kitobi","Xaritalar","Kartoshka urug'i","Inkubator","Qahva doni","Shokolad","Gitara","Shaxmat doskasi","3D printer","Dron","Ventilyator"]
TRAITS = ["Kuchli lider","Ishonchli","Paranoid","Janjalkash","Optimist","Pessimist","Tez qaror qiladi","Sekin lekin aniq","Qattiqqo'l","Mehribon","Muloqotchi","Yakkalanishni xush ko'radi","Hazilkash","Sovuqqon","Hissiyotga beriluvchan","Mas'uliyatli","Tartibsiz","Perfeksionist","Tejamkor","Saxiy","Xavfsevar","Ehtiyotkor","Tahlilchi","Ijodkor","Mojarochi","Mediator","Sabrsiz","Sabrli","Manipulyativ","Jamoaviy"]
PHOBIAS = ["Tor joylardan qo'rqadi","Qorong'ulikdan qo'rqadi","Qondan qo'rqadi","Balandlikdan qo'rqadi","Suvdan qo'rqadi","Yolg'izlikdan qo'rqadi","Olomondan qo'rqadi","Yong'indan qo'rqadi","Hasharotlardan qo'rqadi","Ilonlardan qo'rqadi","Sichqondan qo'rqadi","Shovqindan qo'rqadi","Yopiq eshikdan qo'rqadi","Ignadan qo'rqadi","Kasallikdan qo'rqadi","O'limdan qo'rqadi","Samolyotdan qo'rqadi","Chuqurlikdan qo'rqadi","Elektrdan qo'rqadi","Sovuqdan qo'rqadi","Yashindan qo'rqadi","Robotlardan qo'rqadi","Begonalardan qo'rqadi","Itlardan qo'rqadi","Muvaffaqiyatsizlikdan qo'rqadi"]
SPECIAL_ACTIONS = ["🔄 Karta almashtirish","🔍 Razvedka","🛡️ Immunitet","🗣️ Extra vaqt","📢 Fosh qilish","🔄 Ovoz bekor"]


def generate_card() -> dict:
    return {
        "profession": random.choice(PROFESSIONS),
        "age": random.randint(18, 65),
        "gender": random.choice(["Erkak", "Ayol"]),
        "health": random.choice(HEALTH_STATUSES),
        "hobby": random.choice(HOBBIES),
        "luggage": random.choice(LUGGAGE_ITEMS),
        "trait": random.choice(TRAITS),
        "phobia": random.choice(PHOBIAS),
        "special_action": random.choice(SPECIAL_ACTIONS),
    }
