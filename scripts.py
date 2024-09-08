import pytesseract
import pyautogui
import cv2
import numpy as np
import re
import keyboard
import time
from dotenv import load_dotenv
import os

# Получаем размеры экрана
screen_width, screen_height = pyautogui.size()

areas = {
    "fullscreen": None,
    "up": (0, 0, screen_width, int(screen_height * 0.5)),
    "down": (0, int(screen_height * 0.5), screen_width, screen_height),
    "left": (0, 0, int(screen_width * 0.5), screen_height),
    "right": (int(screen_width * 0.5), 0, screen_width, screen_height),
    "center": (
        int(screen_width * 0.2), int(screen_height * 0.2),
        int(screen_width * 0.6), int(screen_height * 0.6)),
}


def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def find_and_recognize_lots(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)

    return text

def transformLots(lots_info):
    arr = []
    if lots_info:
        for line in lots_info.splitlines():
            try:
                digits = ''.join(re.findall(r'\d+', line))
                result_number = int(digits[:-1])  # Убираем последнюю цифру
                arr.append(result_number)
            except ValueError:
                continue
    return arr


def find_lots_coordinates(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("Контуры не найдены")
        return []

    lot_coordinates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        lot_coordinates.append((x, y, w, h))

    return lot_coordinates


def check_image_on_screen(image_path, region=None, need_to_click=True, callback=None):
    """
    :param image_path: Путь до картинки
    :param region: Регион поиска
    :param need_to_click: Необходимо ли нажать
    :param callback:
    :return: True/False
    Регионы поиска - up, down, left, right, center, fullscreen
    """


    # Захват экрана
    if region is None or region not in areas:
        screenshot = pyautogui.screenshot()  # Полный экран
    else:
        screenshot = pyautogui.screenshot(region=areas[region])  # Указываем область
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Загружаем изображение, которое нужно найти
    target_image = cv2.imread(image_path)
    target_h, target_w = target_image.shape[:2]

    # Поиск изображения на экране
    result = cv2.matchTemplate(screenshot, target_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  # Порог для совпадения
    loc = np.where(result >= threshold)

    # Если найдено совпадение
    if loc[0].size > 0:
        # Получаем координаты центра найденного изображения
        for pt in zip(*loc[::-1]):  # Переводим координаты
            center_x = pt[0] + target_w // 2
            center_y = pt[1] + target_h // 2

            # Корректируем координаты относительно региона
            if region in areas and areas[region] is not None:
                x_offset, y_offset, _, _ = areas[region]
                center_x += x_offset
                center_y += y_offset

            print(f'Найдено изображение в координатах: ({center_x}, {center_y})')

            # Нажимаем на центр изображения
            if need_to_click:
                pyautogui.click(center_x, center_y)  # Клик по центру изображения
            # if callback is not None:
            #     callback(center_x, center_y)  # Вызываем коллбэк с координатами
            return True
    return False



def open_pda(product:str):
    print(f'ПДА не открыт, открываю')
    keyboard.send('p')
    time.sleep(1)
    if check_image_on_screen('screens/input_search.png', need_to_click=True):
        pyautogui.click()
        time.sleep(2)
        keyboard.write(text=product)
        time.sleep(0.5)
        check_image_on_screen('screens/search.png', need_to_click=True)
        time.sleep(0.5)
        check_image_on_screen('screens/filter_button.png', need_to_click=True)
        time.sleep(1)
        check_image_on_screen('screens/filter_button.png', need_to_click=True)
        time.sleep(0.5)

def connect_to_server(do_login=False):
    if do_login:
        check_image_on_screen('screens/login_button.png')
    else:
        pass

def calcProfit(session_buy, sell_price):
    total_cost = 0  # Суммарная затрата
    total_quantity = 0  # Общее количество товаров

    # Проход по всем покупкам
    for buy_price, quantity in session_buy.items():
        total_cost += buy_price * quantity  # Увеличение затрат на сумму покупки
        total_quantity += quantity  # Увеличение общего количества товаров

    # Суммарная выручка при продаже по sell_price
    total_revenue = total_quantity * sell_price

    # Средняя цена закупок
    average_buy_price = total_cost / total_quantity if total_quantity > 0 else 0

    # Профит в процентах
    profit_percentage = ((sell_price - average_buy_price) / average_buy_price) * 100 if average_buy_price > 0 else 0

    # Вывод результатов
    print(f"Суммарная затрата: {total_cost}")
    print(f"Суммарная выручка: {total_revenue}")
    print(f"Профит в %: {profit_percentage:.2f}%")
    print(f"Средняя цена закупок: {average_buy_price:.2f}")

def reconnecting():
    print(f'Проверка нахождения на сервере')
    if check_image_on_screen('screens/disconnect_error.png', need_to_click=False, region="down") or \
            check_image_on_screen('screens/relog_1.png', need_to_click=False, region="down"):
        keyboard.send('escape')
        time.sleep(5)
        connect_to_server(do_login=True)
        return True
    elif check_image_on_screen('screens/login_button.png', need_to_click=False, region="down"):
        connect_to_server(do_login=True)
        time.sleep(10)
        return True
    else:
        print(f'Персонаж на сервере')
        return False

def reopen_pda(product):
    if check_image_on_screen('screens/auction_type_2.png', need_to_click=False) is False:
        print('Хотелось бы открыть ПДА')
        open_pda(product=product)
        return True
    return False