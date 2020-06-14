import cv2
# VK_API
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id

# ПАРСИНГ
import requests
import lxml.html

# Silenium для скриншота веб страницы
import os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Значения города по умолчанию
hist_city = "волгоград"


def CalcImageHash(FileName):
    image = cv2.imread(FileName)  # Прочитаем картинку
    resized = cv2.resize(image, (8, 8), interpolation=cv2.INTER_AREA)  # Уменьшим картинку
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)  # Переведем в черно-белый формат
    avg = gray_image.mean()  # Среднее значение пикселя
    ret, threshold_image = cv2.threshold(gray_image, avg, 255, 0)  # Бинаризация по порогу

    # Рассчитаем хэш
    _hash = ""
    for x in range(8):
        for y in range(8):
            val = threshold_image[x, y]
            if val == 255:
                _hash = _hash + "1"
            else:
                _hash = _hash + "0"

    return _hash

def CompareHash(hash1, hash2):
    l = len(hash1)
    i = 0
    count = 0
    while i < l:
        if hash1[i] != hash2[i]:
            count = count + 1
        i = i + 1
    return count


# Открываем обзглавенный браузер с разрешение 700х600, делаем скриншот, обрезаем скриншот, сохраняем
def screen(city):
    chrome_options = Options()  #
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--window-size=700x600")
    executable_path = os.path.dirname(os.path.abspath(__file__)) + '\chromedriver.exe'
    driver = webdriver.Chrome(options=chrome_options, executable_path=executable_path)
    if (translate(city) == 'moskva') or (translate(city) == 'moscow'):
        print("Я В МОСКВЕ!!!!!", translate(city))
        driver.get(
            "https://yandex.ru/pogoda/moscow")

    else:
        driver.get(
            "https://yandex.ru/pogoda/" + translate(city))
    if (translate(city) == "nizhni-novgorod") or (translate(city) == "nizhni novgorod"):
        driver.get(
            "https://yandex.ru/pogoda/nizhny-novgorod")

    print(translate(city))
    driver.get_screenshot_as_file('IMG\original.png')
    driver.quit()
    image = Image.open('IMG\original.png')
    cropped = image.crop((25, 103, 452, 404))
    cropped.save('IMG\cropped.png')


# Авторизация
vk_session = VkApi(token='8151a8ad2b82f8a4c0fdebfddbd427b1fda9b116fd35bd7f601b672c8c597a88e6557096f81444fe94742')
long_poll = VkBotLongPoll(vk_session, '161386911')
vk = vk_session.get_api()
upload = VkUpload(vk)


# Транслитерация
def translate(text):
    cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    latin = 'a|b|v|g|d|e||zh|z|i||k|l|m|n|o|p|r|s|t|u|f|kh|tc|ch|sh|shch||y||e|iu|ia|A|B|V|G|D|E|E|Zh|Z|I|I|K|L|M|N|O|P|R|S|T|U|F|Kh|Tc|Ch|Sh|Shch||Y||E|Iu|Ia'.split(
        '|')
    return text.translate({ord(k): v for k, v in zip(cyrillic, latin)})


# Загрузка фото
def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


# Функция отправления фотографий пользователям
def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attachment
    )


def picture(city):
    screen(city)
    NT = 'IMG\eror.png'
    crop = 'IMG\cropped.png'
    hash_eror = CalcImageHash(NT)
    hash_img = CalcImageHash(crop)
    tmp = CompareHash(hash_eror, hash_img)
    print('ХЭШ: ', tmp)
    if tmp < 5:
        send_photo(vk,peer_id, *upload_photo(upload, 'IMG\A404.png'))
    else:
        send_photo(vk, peer_id, *upload_photo(upload, 'IMG\cropped.png'))


# Получение погоды с сайта
def parse(url):
    api = requests.get(url)
    tree = lxml.html.document_fromstring(api.text)
    sost = tree.xpath('/html/body/div[7]/div[2]/main/div[1]/div[2]/div/div/div[2]/div[1]/text()')
    textGradus = tree.xpath('/html/body/div[7]/div[2]/main/div[1]/div[2]/div/div/div[1]/div[3]/text()')
    textGradus_ = str(textGradus)
    tmp = textGradus_[5:len(textGradus_) - 8]
    textGradus = tmp
    textGradus_ = str(sost)
    tmp = textGradus_[2:len(textGradus_) - 2]
    sost = tmp
    res = str(s.capitalize()) + "\nТемпература сейчас: " + str(textGradus) + "\nПрогноз на день: " + str(sost)
    if (len(str(textGradus)) < 1):
        return "Город не найден"
    print(res)
    hist = str(res)
    return res


# Функция отправки текстовой погоды
def send(s):
    if (s.lower() == "нижний новгород"):
        http = "https://sinoptik.com.ru/погода-нижний-новгород"
        pref = parse(http)
    else:
        http = "https://sinoptik.com.ru/погода-" + s.lower()
        pref = parse(http)

    print(pref)
    return pref


# Основной цикл, прслушивать диалог с user пока не будет полученно сообщение
for event in long_poll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        message = event.obj['message']

        peer_id = message['peer_id']
        text = message['text']
        str(text)
        s = text.lower()
        if (s == 'пиво'):
            vk.messages.send(
                peer_id=peer_id,
                message="В этом городе всегда тепло и хорошо....",
                random_id=get_random_id(),
            )
            continue
        if s != 'погода' or s == 'gjujlf' or s == 'пгода' or s == 'пгда':
            vk.messages.send(
                peer_id=peer_id,
                message=send(s),
                random_id=get_random_id(),
            )
            picture(s)
            hist_city = s
            continue

        if s == 'погода' or s == 'gjujlf' or s == 'пагода' or s == 'пгода' or s == 'пгда':
            vk.messages.send(
                peer_id=peer_id,
                message=send(hist_city),
                random_id=get_random_id(),
            )
            picture(hist_city)
        else:
            if (len(hist_city) > 5):
                vk.messages.send(
                    peer_id=peer_id,
                    message="Данные введены некоректно!",
                    random_id=get_random_id(),
                )
            else:
                vk.messages.send(
                    peer_id=peer_id,
                    message='Введите "Погода" для успешного начала работы бота, для смены города введите его название: Москва, Санкт-Петербург....',
                    random_id=get_random_id(),
                )
