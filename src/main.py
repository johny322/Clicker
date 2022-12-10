import json
import logging
import os
import time
import traceback
from io import BytesIO
from sys import exit
from typing import List, Dict

import keyboard
import plyer
import win32clipboard
from PIL import Image

SETTINGS_PATH = 'settings.json'

error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
event_logger = logging.getLogger('event_logger')
event_logger.setLevel(logging.DEBUG)


def setup_loggers():
    """
        Установка логгеров для вывода в консоль и записи в файл
    """

    log_error_file_name = 'error.log'
    log_event_file_name = 'event.log'
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    strfmt = '[%(asctime)s] [%(levelname)-8s] --- %(message)s (%(filename)s:%(funcName)s:%(lineno)s)'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)

    error_log_path = os.path.join(log_dir, log_error_file_name)
    error_file_handler = logging.FileHandler(error_log_path)
    error_file_handler.setFormatter(formatter)

    error_logger.addHandler(error_file_handler)
    error_logger.addHandler(stdout_handler)

    event_log_path = os.path.join(log_dir, log_event_file_name)
    event_file_handler = logging.FileHandler(event_log_path)
    event_file_handler.setFormatter(formatter)
    event_logger.addHandler(event_file_handler)

    event_logger.addHandler(stdout_handler)


class Binder:

    def __init__(self):
        self.start_data = ''
        self.settings = self._get_settings()

    @staticmethod
    def _send_notification(message, title):
        plyer.notification.notify(
            message=message,
            app_name='clicker',
            app_icon='binder.ico',
            title=title,
        )

    def _processing_critical_error(self, exception):
        error_logger.error(exception, exc_info=True)
        self._send_notification(
            message='Неизвестная ошибка',
            title='Ошибка'
        )
        input('Для завершения нажмите ENTER')
        exit()

    def _get_settings(self):
        data = {}
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self._send_notification(
                message='Файл с настройками не найден\n'
                        'Перейдите в программу для завершения',
                title='Ошибка'
            )
            input('Для завершения нажмите ENTER')
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            self._processing_critical_error(e)
        return data

    def get_clipboard_data(self):
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except TypeError:
            event_logger.warning('can`t get start clipboard data')
        except Exception as e:
            error_logger.error(e, exc_info=True)
        else:
            self.start_data = data
        finally:
            win32clipboard.CloseClipboard()

    def set_start_clipboard_data(self):
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            if self.start_data:
                win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, self.start_data)
        except TypeError:
            event_logger.warning('can`t set start clipboard data')
        except Exception as e:
            error_logger.error(e, exc_info=True)
        finally:
            win32clipboard.CloseClipboard()

    @staticmethod
    def send_to_clipboard(clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()

    def set_clipboard_photo_data(self, photo_path):
        image = Image.open(photo_path)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]

        output.close()

        self.send_to_clipboard(win32clipboard.CF_DIB, data)

    def _add_hotkey(self, photo_path, shortcut):
        event_logger.info(f'get shortcut: {shortcut}')
        need_enter = self.settings.get('need_enter')
        sleep_time = self.settings.get('sleep_time') or 1
        self.get_clipboard_data()
        self.set_clipboard_photo_data(photo_path)
        time.sleep(0.2)
        hotkey = 'ctrl+v'
        keyboard.send(hotkey)
        event_logger.info(f'send {hotkey}')
        if need_enter:
            time.sleep(sleep_time)
            hotkey = 'enter'
            keyboard.send(hotkey)
            event_logger.info(f'send {hotkey}')
        self.set_start_clipboard_data()

    def _prepare_to_work(self):
        shortcuts: List[Dict[str]] = self.settings.get('shortcuts')
        no_photo_path_count = 0
        for shortcut_data in shortcuts:
            shortcut = shortcut_data['shortcut']
            photo_path = shortcut_data['photo_path']
            if not os.path.exists(photo_path):
                event_logger.warning(f'no {photo_path}')
                # self._send_notification(
                #     message=f'Отсутствует файл {photo_path}',
                #     title='Уведомление'
                # )
                no_photo_path_count += 1
                continue
            event_logger.info(f'add {photo_path} to {shortcut}')

            keyboard.add_hotkey(shortcut, self._add_hotkey, args=(photo_path, shortcut))
        if no_photo_path_count == len(shortcuts):
            event_logger.warning(f'no any photo_path')
            self._send_notification(
                message=f'Отсутствуют файлы с фотографиями',
                title='Уведомление'
            )
            input('Для завершения нажмите ENTER')
            exit()

    def start(self):
        event_logger.info(f'Программа запущена')
        self._send_notification(
            message='Программа запущена',
            title='Старт'
        )
        try:
            self._prepare_to_work()
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            self._processing_critical_error(e)
        while True:
            pass


def main():
    setup_loggers()
    try:
        b = Binder()
        b.start()
    except Exception as e:
        error_logger.error(e, exc_info=True)
        input('Критическая ошибка\n'
              'Для завершения нажмите ENTER')


if __name__ == '__main__':
    main()
