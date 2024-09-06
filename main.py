import pytesseract
import pyautogui
import cv2
import numpy as np
import re
import keyboard
import time
# Укажите путь к Tesseract, если он не добавлен в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Координаты области экрана для сканирования (x, y, ширина, высота)
scan_region = (1253, 360, 110, 300)  # Пример координат
threshold_price = 26000  # Пороговая цена для покупки
updateButtonCords = (1333, 350)
image_path = './ok.png'

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


def check_image_on_screen(image_path, region=None, need_to_click=True):
    # Захват экрана
    screenshot = pyautogui.screenshot(region=region)  # Указываем область
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
            if region:
                center_x += region[0]
                center_y += region[1]
            print(f'Найдено изображение в координатах: ({center_x}, {center_y})')
            # Нажимаем на центр изображения
            if need_to_click:
                pyautogui.click(center_x, center_y)  # Клик по центру изображения
            return True

    print('Изображение не найдено.')
    return False

def main():
    while True:
        if check_image_on_screen('disconnect_error.png', need_to_click=False):
            keyboard.send('escape')
            time.sleep(5)
            do_login = check_image_on_screen('login_button.png', need_to_click=True)

            if do_login:
                time.sleep(15)
                keyboard.send('p')
            else:
                quit()
        else:

            if keyboard.is_pressed('f2'):
                print("Скрипт остановлен.")
                break

            screenshot = capture_screen(scan_region)
            lots_info = find_and_recognize_lots(screenshot)
            lots = transformLots(lots_info)
            region = (862, 530, 200, 200)  # (x, y, width, height)
            lot_coordinates = find_lots_coordinates(screenshot)

            print(f"Найдено лотов: {len(lots)}")
            isOkOnScreen = check_image_on_screen(image_path, region)
            if not isOkOnScreen:
                if len(lots) <= 1:  # Если найдено 1 или меньше лотов
                    # Перемещаем мышь в указанные координаты
                    pyautogui.moveTo(1385, 433)
                    time.sleep(0.1)  # Небольшая задержка
                    # Прокручиваем страницу вниз
                    pyautogui.scroll(-300)  # Прокрутка вниз на 300 пикселей
                    time.sleep(0.1)  # Задержка перед следующей итерацией
                    # continue  # Переходим к следующей итерации цикла

                if lot_coordinates:  # Проверка на наличие координат
                    # Сортируем координаты по y
                    sorted_coordinates = sorted(lot_coordinates, key=lambda coord: coord[1])

                    for index, lot in enumerate(lots):
                        if lot <= threshold_price and lot > 20000:
                            x, y, w, h = sorted_coordinates[0]  # Кликаем на лот с наименьшей y
                            click_x = x + scan_region[0] + w // 2
                            click_y = y + scan_region[1] + h // 2
                            print(f"Найден лот с ценой {lot}")
                            # Первый клик на лот
                            print(f'Клик на лот: {lot} по координатам ({click_x}, {click_y})')
                            pyautogui.moveTo(click_x, click_y,0.1)
                            time.sleep(0.2)
                            pyautogui.click(click_x, click_y)
                            time.sleep(0.1)
                            # Второй клик на покупку
                            second_click_y = click_y + 35
                            print(f'Второй клик на координатах ({click_x + 10}, {second_click_y})')
                            pyautogui.moveTo(click_x, second_click_y,0.1)
                            time.sleep(0.1)
                            pyautogui.click(click_x, second_click_y)
                            time.sleep(0.1)
                            break
                else:
                    print('Координаты не найдены для данного лота')

                pyautogui.click(updateButtonCords)
                time.sleep(0.1)

if __name__ == "__main__":
    main()
