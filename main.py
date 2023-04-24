from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import subprocess
import wget
import zipfile
import json
import sys
import time

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QPropertyAnimation, QFile, QIODevice
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from scipy.spatial import distance

def hex_to_rgb(hex):
    """
    Transforme une valeur héxadécimal en une valeur rgb
    """
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)
    return tuple(rgb)


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex_to_rgb(hex):
    hex = hex[1:]
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)
    return tuple(rgb)


def closest_pantone(rgb):
    with open("results.json", "r") as file:
        pantone = json.load(file)
        min_dist = 2555555
        pantoneKeys = pantone.keys()
        rep = min(pantoneKeys)
        for color_pantone in pantoneKeys:
            dist = distance.euclidean(tuple(pantone[color_pantone]), rgb)
            if dist < min_dist:
                min_dist = dist
                rep = color_pantone
    return rep


def pantone_to_rgb(code_pantone):
    with open("results.json", "r") as file:
        pantone = json.load(file)
    if code_pantone in pantone.keys():
        return pantone[code_pantone]
    else:
        return tuple([window.sliderRed.value(), window.sliderGreen.value(), window.sliderBlue.value()])


def get_middle_grey():
    return 255 - (window.sliderRed.value() + window.sliderGreen.value() + window.sliderBlue.value()) / 3


def get_police_color(middleGrey: int):
    if middleGrey >= 128:
        return 0
    else:
        return 255


def label_color(color: int):
    window.labelRed.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.labelGreen.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.labelBlue.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.connectionStatus.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.labelHexa.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.labelPantone.setStyleSheet(
        f"color: rgb({color},{color},{color})")
    window.editHexa.setStyleSheet(
        f"color: rgb({color},{color},{color});\n"
        f"border: 0px;")
    window.editPantone.setStyleSheet(
        f"color: rgb({color},{color},{color});\n"
        f"border: 0px;")


def set_button_color(middleGrey: int):
    policeColor = get_police_color(middleGrey)
    label_color(abs(policeColor - 255))

    window.colorLaunch.setStyleSheet(
        f"background-color: rgb({middleGrey},{middleGrey},{middleGrey});"
        f"padding: 15px;"
        f"color: rgb({policeColor},{policeColor},{policeColor});"
        f"border-radius: 20px;")

    window.launchHyperyon.setStyleSheet(
        f"background-color: rgb({middleGrey},{middleGrey},{middleGrey});"
        f"padding: 15px;"
        f"color: rgb({policeColor},{policeColor},{policeColor});"
        f"border-radius: 20px;")

    window.quitHyperyon.setStyleSheet(
        f"background-color: rgb({middleGrey},{middleGrey},{middleGrey});"
        f"padding: 15px;"
        f"color: rgb({policeColor},{policeColor},{policeColor});"
        f"border-radius: 20px;")


def set_bg():
    window.setStyleSheet(
        f"background-color : rgb({window.sliderRed.value()},{window.sliderGreen.value()},{window.sliderBlue.value()})")
    set_button_color(get_middle_grey())


def change_bg_sliders():
    set_bg()
    window.valRed.setValue(window.sliderRed.value())
    window.valGreen.setValue(window.sliderGreen.value())
    window.valBlue.setValue(window.sliderBlue.value())
    window.editHexa.setText(rgb_to_hex(window.sliderRed.value(), window.sliderGreen.value(), window.sliderBlue.value()))
    window.editPantone.setText(
        closest_pantone((window.sliderRed.value(), window.sliderGreen.value(), window.sliderBlue.value())))


def change_bg_spinbox():
    set_bg()
    window.sliderRed.setValue(window.valRed.value())
    window.sliderGreen.setValue(window.valGreen.value())
    window.sliderBlue.setValue(window.valBlue.value())


def change_bg_hex():
    if len(window.editHexa.text()) == 7:
        hex = hex_to_rgb(window.editHexa.text())
        window.sliderRed.setValue(hex[0])
        window.sliderGreen.setValue(hex[1])
        window.sliderBlue.setValue(hex[2])


def change_bg_pantone():
    rgb = pantone_to_rgb(window.editPantone.text())
    window.sliderRed.setValue(rgb[0])
    window.sliderGreen.setValue(rgb[1])
    window.sliderBlue.setValue(rgb[2])


def get_rgb():
    return f"{window.valRed.value()}\n" \
           f"{window.valGreen.value()}\n" \
           f"{window.valBlue.value()}\n"



if __name__ == "__main__":

    try:
        driver = webdriver.Chrome()
    except:
        if os.path.exists("chromedriver.exe"):
            print("oui")
            os.remove("chromedriver.exe")

        print("pas la bonne version de chromedriver")
        output = subprocess.check_output(
            r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
            shell=True)
        version = output.decode('utf-8').strip()[8:]

        download_url = "https://chromedriver.storage.googleapis.com/" + version + "/chromedriver_win32.zip"

        latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

        with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
            zip_ref.extractall()

        os.remove(latest_driver_zip)

    driver.get(f"https://codebeautify.org/pantone-to-hex-converter")
    driver.find_element(By.ID, 'ez-accept-all').click()
    data = {}

    for i in range(1, 1342):
        driver.find_element(By.XPATH, f'//*[@id="pantoneList"]/option[{i}]').click()
        pantone = driver.find_element(By.XPATH, f'//*[@id="pantoneList"]/option[{i}]').get_attribute("value")
        hexa = driver.find_element(By.XPATH, f'//*[@id="h"]').get_attribute("value")
        data[pantone] = hex_to_rgb(hexa)

    print("scrapping terminé")
    with open("results.json", "w") as file:
        json.dump(data, file, indent=4)

    # fenêtre

    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    window = loader.load("fen.ui", None)
    window.show()

    window.setStyleSheet(
        f"background-color : rgb({0},{0},{0})")

    window.sliderRed.setMaximum(255)
    window.sliderGreen.setMaximum(255)
    window.sliderBlue.setMaximum(255)

    window.sliderRed.valueChanged.connect(change_bg_sliders)
    window.sliderGreen.valueChanged.connect(change_bg_sliders)
    window.sliderBlue.valueChanged.connect(change_bg_sliders)

    window.valRed.setMaximum(255)
    window.valGreen.setMaximum(255)
    window.valBlue.setMaximum(255)

    window.valRed.valueChanged.connect(change_bg_spinbox)
    window.valGreen.valueChanged.connect(change_bg_spinbox)
    window.valBlue.valueChanged.connect(change_bg_spinbox)
    window.editHexa.textChanged.connect(change_bg_hex)
    window.editPantone.returnPressed.connect(change_bg_pantone)

    window.labelRed.setStyleSheet(
        f"color: rgb(255,255,255)")
    window.labelGreen.setStyleSheet(
        f"color: rgb(255,255,255)")
    window.labelBlue.setStyleSheet(
        f"color: rgb(255,255,255)")

    app.exec()
