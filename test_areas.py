import cv2
import numpy as np
import pyautogui

def draw_search_areas():
    screen_width, screen_height = pyautogui.size()

    # Создаем пустое изображение
    image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # Определяем зоны
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

    # Рисуем зоны на изображении
    colors = {
        "fullscreen": (200, 200, 200),  # light grey
        "up": (255, 0, 0),  # blue
        "down": (0, 255, 0),  # green
        "left": (0, 0, 255),  # red
        "right": (0, 165, 255),  # orange
        "center": (255, 0, 255),  # purple
    }

    for area, coords in areas.items():
        if coords is not None:
            cv2.rectangle(image, (coords[0], coords[1]), (coords[0] + coords[2], coords[1] + coords[3]), colors[area], 2)
            cv2.putText(image, area.capitalize(), (coords[0] + 10, coords[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Отображаем изображение
    cv2.imshow("Search Areas", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

draw_search_areas()