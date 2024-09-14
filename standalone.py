import pytesseract
import pyautogui
import cv2
import numpy as np
import re
import keyboard
import time
from dotenv import load_dotenv
import os
import scripts as script
import pygetwindow as gw
from datetime import datetime
from main import product,sell_price, scan_region,okRegion,threshold_price,minBuyPrice,scrollCords,resale_image,resale_price, resale_count


def start():
    search_button_coords = None
    counter = {}
    just_counter = 0
    check_server_connecting = 0
    check_pda = 0
    lastBuyed = None
    updateButtonCords=None
    checkScroll = script.checkScrollInLots()
    if checkScroll:
        return #если скролл есть, то перезапускаемся
    script.open_pda(product=product)
    while True:
        total_purchases = sum(counter.values())
        if total_purchases >= resale_count:
            priceByPercent=max(round(lastBuyed * 1.10), threshold_price+1)
            script.startResale(itemImage=resale_image, sell_price=priceByPercent)
            return  # Выход из функции после вызова функции, если это необходимо
        check_server_connecting += 1
        current_price = 0

        if check_server_connecting >= 150:
            need_to_connect = True
            while need_to_connect is True:
                need_to_connect = script.reconnecting()
            if need_to_connect is False:
                check_server_connecting = 0
        else:
            check_pda += 1
            if keyboard.is_pressed('f7'):
                script.stop(counter, sell_price)
                break
            if check_pda >= 50:
                need_pda = True
                while need_pda is True:
                    need_pda = script.reopen_pda(product=product)
                if need_pda is False:
                    check_pda = 0
            screenshot = script.capture_screen(scan_region)
            lots_info = script.find_and_recognize_lots(screenshot)
            lots = script.transformLots(lots_info)

            lot_coordinates = script.find_lots_coordinates(screenshot)

            print(f"Найдено лотов: {len(lots)}")
            isOkOnScreen = script.check_image_on_screen('screens/ok.png', okRegion)
            if not isOkOnScreen:
                if search_button_coords is None:
                    # TODO Передать в search_button_coords координаты клика
                    script.check_image_on_screen('screens/search.png',
                                                 need_to_click=True,
                                                 returnCords=True,
                                                 region="up",
                                                 double=True)
                else:
                    pass
                    #TODO клик по координатам, а не по кнопке
                if len(lots) < 1:  # Если найдено 1 или меньше лотов
                    # Перемещаем мышь в указанные координаты
                    pyautogui.moveTo(scrollCords)
                    time.sleep(0.1)  # Небольшая задержка
                    # Прокручиваем страницу вниз
                    pyautogui.scroll(-300)  # Прокрутка вниз на 300 пикселей
                    time.sleep(0.1)  # Задержка перед следующей итерацией
                    continue  # Переходим к следующей итерации цикла

                if lot_coordinates:  # Проверка на наличие координат
                    # Сортируем координаты по y
                    sorted_coordinates = sorted(lot_coordinates, key=lambda coord: coord[1])

                    for index, lot in enumerate(lots):
                        if lot <= threshold_price and lot > minBuyPrice:
                            x, y, w, h = sorted_coordinates[0]  # Кликаем на лот с наименьшей y
                            click_x = x + scan_region[0] + w // 2
                            click_y = y + scan_region[1] + h // 2
                            # print(f"Найден лот с ценой {lot}")
                            # # Первый клик на лот
                            # print(f'Клик на лот: {lot} по координатам ({click_x}, {click_y})')
                            pyautogui.moveTo(click_x, click_y,0.1)
                            time.sleep(0.1)
                            pyautogui.click(click_x, click_y)
                            time.sleep(0.1)
                            # Второй клик на покупку
                            second_click_y = click_y + 35
                            # print(f'Второй клик на координатах ({click_x + 10}, {second_click_y})')
                            pyautogui.moveTo(click_x, second_click_y,0.1)
                            time.sleep(0.1)
                            pyautogui.click(click_x, second_click_y)
                            just_counter += 1
                            current_price = lot
                            lastBuyed = lot
                            break
                else:
                    print('Координаты не найдены для данного лота')


                time.sleep(0.1)
                if script.check_image_on_screen('screens/success_buy.png', need_to_click=False, region="center"):
                    if current_price not in counter:
                        counter[current_price] = 1
                    else:
                        counter[current_price] += 1
                    keyboard.send('escape')
                elif script.check_image_on_screen('screens/error_buy.png', need_to_click=False, region="center"):
                    keyboard.send('escape')