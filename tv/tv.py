# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import numbers
import os
import re
import sys
import time
import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from kairos import timing
from kairos import tools
from PIL import Image
from urllib.parse import unquote
import pyautogui
import pyperclip

CURRENT_DIR = os.path.curdir
TEXT = 'text'
CHECKBOX = 'checkbox'
SELECTBOX = 'selectbox'
DATE = 'date'
TIME = 'time'

WAIT_TIME_IMPLICIT_DEF = 30
PAGE_LOAD_TIMEOUT_DEF = 15
CHECK_IF_EXISTS_TIMEOUT_DEF = 15
DELAY_BREAK_MINI_DEF = 0.2
DELAY_BREAK_DEF = 0.5
DELAY_SUBMIT_ALERT_DEF = 3.5
DELAY_CLEAR_INACTIVE_ALERTS_DEF = 0
DELAY_CHANGE_SYMBOL_DEF = 0.2
DELAY_SCREENSHOT_DIALOG = 2
DELAY_SCREENSHOT = 1
DELAY_KEYSTROKE = 0.01
DELAY_WATCHLIST = 0.5
DELAY_TIMEFRAME = 0.5

ALERT_NUMBER = 0

MODIFIER_KEY = Keys.LEFT_CONTROL
OS = 'windows'
if sys.platform == 'os2':
    OS = 'macos'
    MODIFIER_KEY = Keys.COMMAND
elif os.name == 'posix':
    OS = 'linux'

css_selectors = dict(
    username='body > div.tv-main > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user > span.tv-header__dropdown-wrap.tv-dropdown-behavior__'
             'button > span.tv-header__dropdown-text.tv-header__dropdown-text--username.js-username.tv-header__dropdown-text--ellipsis.apply-overflow-tooltip.common-tooltip-fixed',
    signin='body > div.tv-main > div.tv-header > div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-header__dropdown-text > a',
    input_username='#signin-form > div.tv-control-error > div.tv-control-material-input__wrap > input',
    input_password='#signin-form > div.tv-signin-dialog__forget-wrap > div.tv-control-error > div.tv-control-material-input__wrap > input',
    btn_login='#signin-form > div.tv-signin-dialog__footer.tv-signin-dialog__footer--login > div:nth-child(2) > button',
    btn_timeframe='#header-toolbar-intervals > div:last-child',
    # options_timeframe='#__outside-render-0 > div > div > div > div > div > div > div',
    # options_timeframe='div[id^="__outside-render-"] div[class^="item"]',
    options_timeframe='div[class^="dropdown-"] div[class^="item"]',
    btn_watchlist_menu='body > div.js-rootresizer__contents > div.layout__area--right > div > div.widgetbar-tabs > div > div:nth-child(1) > div > div > div:nth-child(1)',
    btn_watchlist_menu_menu='input.wl-symbol-edit + a.button',
    options_watchlist='div.charts-popup-list > a.item.first',
    input_symbol='#header-toolbar-symbol-search > div > input',
    btn_alert_menu='div.widgetbar-widget-alerts_manage > div > div > a:last-child',
    item_clear_alerts='div.charts-popup-list > a.item:last-child',
    item_clear_inactive_alerts='div.charts-popup-list > a.item:nth-child(8)',
    item_restart_inactive_alerts='div.charts-popup-list > a.item:nth-child(6)',
    btn_dlg_clear_alerts_confirm='div.tv-dialog > div.tv-dialog__section--actions > div[data-name="yes"]',
    item_alerts='table.alert-list > tbody > tr.alert-item',
    btn_create_alert='#header-toolbar-alerts',
    dlg_create_alert_first_row_first_item='fieldset > div:nth-child(1) > span > div:nth-child(1)',
    options_dlg_create_alert_first_row_first_item='fieldset > div:nth-child(1) > span > div:nth-child(1) span.tv-control-select__option-wrap',
    exists_dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right > span > span',
    dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right > span',
    options_dlg_create_alert_first_row_second_item='div.js-condition-first-operand-placeholder div.tv-alert-dialog__group-item--right span.tv-control-select__option-wrap',
    dlg_create_alert_second_row='fieldset > div:nth-child(2) > span',
    options_dlg_create_alert_second_row='fieldset > div:nth-child(2) > span span.tv-control-select__option-wrap',
    inputs_and_selects_create_alert_3rd_row_and_above='div.js-condition-second-operand-placeholder select, div.js-condition-second-operand-placeholder input',
    dlg_create_alert_3rd_row_group_item='div.js-condition-second-operand-placeholder div.tv-alert-dialog__group-item',
    options_dlg_create_alert_3rd_row_group_item='span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    selected_dlg_create_alert_3rd_row_group_item='span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened > span > span > span:nth-child({0}) > span',
    checkbox_dlg_create_alert_frequency='div[data-title="{0}"]',
    clickable_dlg_create_alert_show_popup='div.tv-alert-dialog__fieldset-value-item:nth-child(1) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    clickable_dlg_create_alert_play_sound='div.tv-alert-dialog__fieldset-value-item:nth-child(2) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    dlg_create_alert_ringtone='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--left > span',
    options_dlg_create_alert_ringtone='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    dlg_create_alert_sound_duration='div.js-sound-settings > div.tv-alert-dialog__group-item.tv-alert-dialog__group-item--right > span',
    options_dlg_create_alert_sound_duration='div.js-sound-settings span.tv-control-select__dropdown.tv-dropdown-behavior__body.i-opened span.tv-control-select__option-wrap',
    clickable_dlg_create_alert_send_email='div.tv-alert-dialog__fieldset-value-item:nth-child(4) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    clickable_dlg_create_alert_send_email_to_sms='div.tv-alert-dialog__fieldset-value-item:nth-child(5) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    clickable_dlg_create_alert_send_sms='div.tv-alert-dialog__fieldset-value-item:nth-child(6) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    clickable_dlg_create_alert_send_push='div.tv-alert-dialog__fieldset-value-item:nth-child(7) > label:nth-child(1) > span:nth-child(1) > span:nth-child(3)',
    btn_dlg_create_alert_submit='div[data-name="submit"] > span.tv-button__loader',
    btn_alerts='div[data-name="alerts"]',
    btn_calendar='div[data-name="calendar"]',
    div_watchlist_item='div.symbol-list > div.symbol-list-item.success',
    signout='body > div.tv-main.tv-screener__standalone-main-container > div.tv-header K> div.tv-header__inner.tv-layout-width > div.tv-header__area.tv-header__area--right.tv-header__area--desktop > span.tv-dropdown-behavior.tv-header__dropdown.tv-header__dropdown--user.i-opened > '
            'span.tv-dropdown-behavior__body.tv-header__dropdown-body.tv-header__dropdown-body--fixwidth.i-opened > span:nth-child(13) > a',
    checkbox_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended input',
    clickable_dlg_create_alert_open_ended='div.tv-alert-dialog__fieldset-value-item--open-ended span.tv-control-checkbox__label',
    btn_dlg_screenshot='#header-toolbar-screenshot',
    dlg_screenshot_url='div[class^="copyForm"] > div > input',
    dlg_screenshot_close='div[class^="dialog"] > div > span[class^="close"]'
)

class_selectors = dict(
    form_create_alert='js-alert-form',
)

name_selectors = dict(
    checkbox_dlg_create_alert_show_popup='show-popup',
    checkbox_dlg_create_alert_play_sound='play-sound',
    checkbox_dlg_create_alert_send_email='send-email',
    checkbox_dlg_create_alert_email_to_sms='send-sms',
    checkbox_dlg_create_alert_send_sms='send-true-sms',
    checkbox_dlg_create_alert_send_push='send-push'
)

log = tools.log
log.setLevel(20)
config = tools.get_config(CURRENT_DIR)
log.setLevel(config.getint('logging', 'level'))

path_to_chromedriver = r"" + config.get('webdriver', 'path')
if os.path.exists(path_to_chromedriver):
    path_to_chromedriver = path_to_chromedriver.replace('.exe', '')
else:
    log.error("File " + path_to_chromedriver + " does not exist")
    log.exception(FileNotFoundError)
    exit(0)

screenshot_dir = ''
if config.has_option('logging', 'screenshot_path'):
    screenshot_dir = config.get('logging', 'screenshot_path')
    if screenshot_dir != '':
        screenshot_dir = os.path.join(CURRENT_DIR, screenshot_dir)
    if not os.path.exists(screenshot_dir):
        # noinspection PyBroadException
        try:
            os.mkdir(screenshot_dir)
        except Exception as screenshot_error:
            log.info('No screenshot directory specified or unable to create it.')
            screenshot_dir = ''

WAIT_TIME_IMPLICIT = config.getfloat('webdriver', 'wait_time_implicit')
PAGE_LOAD_TIMEOUT = config.getfloat('webdriver', 'page_load_timeout')
CHECK_IF_EXISTS_TIMEOUT = config.getfloat('webdriver', 'check_if_exists_timeout')
DELAY_BREAK_MINI = config.getfloat('delays', 'break_mini')
DELAY_BREAK = config.getfloat('delays', 'break')
DELAY_SUBMIT_ALERT = config.getfloat('delays', 'submit_alert')
DELAY_CHANGE_SYMBOL = config.getfloat('delays', 'change_symbol')
DELAY_CLEAR_INACTIVE_ALERTS = config.getfloat('delays', 'clear_inactive_alerts')
if config.has_option('delays', 'screenshot_dialog'):
    DELAY_SCREENSHOT_DIALOG = config.getfloat('delays', 'screenshot_dialog')
if config.has_option('delays', 'screenshot'):
    DELAY_SCREENSHOT = config.getfloat('delays', 'screenshot')
if config.has_option('delays', 'keystroke'):
    DELAY_KEYSTROKE = 0.05
EXACT_CONDITIONS = config.getboolean('tradingview', 'exact_conditions')

RESOLUTION = '1920,1080'
if config.has_option('webdriver', 'resolution'):
    RESOLUTION = config.get('webdriver', 'resolution').strip(' ')


def close_all_popups(browser):
    for h in browser.window_handles[1:]:
        browser.switch_to.window(h)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])


def element_exists_by_xpath(browser, xpath):
    try:
        log.debug(xpath + ': \n')
        browser.implicitly_wait(CHECK_IF_EXISTS_TIMEOUT)
        elements = browser.find_element_by_xpath(xpath)
        log.debug('\t' + str(elements))
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
    except NoSuchElementException:
        log.warning('No such element. XPATH=' + xpath)
        return False
    return True


def element_exists(browser, dom, css_selector, delay):
    result = False
    try:
        browser.implicitly_wait(delay)
        element = dom.find_element_by_css_selector(css_selector)
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
        result = type(element) is WebElement
    except NoSuchElementException:
        log.debug('No such element. CSS SELECTOR=' + css_selector)
    except Exception as element_exists_error:
        log.error(element_exists_error)
    finally:
        log.debug(str(result) + "(" + css_selector + ")")
        return result


def wait_and_click(browser, css_selector, delay=CHECK_IF_EXISTS_TIMEOUT):
    try:
        WebDriverWait(browser, delay).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()
    except Exception as e:
        log.exception(e)
        log_screenshot(browser)


def wait_and_click_by_xpath(browser, xpath, delay=CHECK_IF_EXISTS_TIMEOUT):
    try:
        WebDriverWait(browser, delay).until(
            ec.element_to_be_clickable((By.XPATH, xpath))).click()
    except Exception as e:
        log.exception(e)
        log_screenshot(browser)


def wait_and_click_by_text(browser, tag, search_text, css_class='', delay=CHECK_IF_EXISTS_TIMEOUT):
    if type(css_class) is str and len(css_class) > 0:
        xpath = '//{0}[contains(text(), "{1}") and @class="{2}"]'.format(tag, search_text, css_class)
    else:
        xpath = '//{0}[contains(text(), "{1}")]'.format(tag, search_text)
    try:
        WebDriverWait(browser, delay).until(
            ec.element_to_be_clickable((By.XPATH, xpath))).click()
    except Exception as e:
        log.exception(e)
        log_screenshot(browser)


def wait_and_get(browser, css, delay=CHECK_IF_EXISTS_TIMEOUT):
    try:
        element = WebDriverWait(browser, delay).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, css)))
        return element
    except Exception as e:
        log.exception(e)
        log_screenshot(browser)


def set_timeframe(browser, timeframe):
    log.info('Setting timeframe to ' + timeframe)
    wait_and_click(browser, css_selectors['btn_timeframe'])
    css = css_selectors['options_timeframe']
    el_options = browser.find_elements_by_css_selector(css)
    index = 0
    found = False
    while not found and index < len(el_options):
        if el_options[index].text == timeframe:
            el_options[index].click()
            found = True
        index += 1
    if not found:
        log.warning('Unable to set timeframe to ' + timeframe)
        raise ValueError

    if found:
        html = browser.find_element_by_tag_name('html')
        html.send_keys(MODIFIER_KEY + 's')
        time.sleep(DELAY_BREAK)

    return found


def get_interval(timeframe):
    """
    Get TV's short timeframe notation
    :param timeframe: String.
    :return: interval: Short timeframe notation if found, empty string otherwise.
    """
    match = re.search("(\\d+)\\s(\\w\\w\\w)", timeframe)
    interval = ""
    if match is None:
        log.warning("Cannot find match for timeframe '" + timeframe + "' with regex (\\d+)\\s(\\w\\w\\w). [0]")
    else:
        try:
            interval = match.group(1)
            unit = match.group(2)
            if unit == 'day':
                interval += 'D'
            elif unit == 'wee':
                interval += 'W'
            elif unit == 'mon':
                interval += 'M'
            elif unit == 'hou':
                interval += 'H'
            elif unit == 'min':
                interval += ''
        except Exception as interval_exception:
            log.warning("Cannot find match for timeframe '" + timeframe + "' with regex (\\d+)\\s(\\w\\w\\w). [1]")
            log.exception(interval_exception)
    return interval


def set_delays(chart):
    global WAIT_TIME_IMPLICIT
    global PAGE_LOAD_TIMEOUT
    global CHECK_IF_EXISTS_TIMEOUT
    global DELAY_BREAK_MINI
    global DELAY_BREAK
    global DELAY_SUBMIT_ALERT
    global DELAY_CLEAR_INACTIVE_ALERTS
    global DELAY_CHANGE_SYMBOL
    global DELAY_KEYSTROKE

    # set delays as defined within the chart with a fallback to the config file
    if 'wait_time_implicit' in chart and isinstance(chart['wait_time_implicit'], numbers.Real):
        WAIT_TIME_IMPLICIT = chart['wait_time_implicit']
    elif config.has_option('webdriver', 'wait_time_implicit'):
        WAIT_TIME_IMPLICIT = config.getfloat('webdriver', 'wait_time_implicit')

    if 'page_load_timeout' in chart and isinstance(chart['page_load_timeout'], numbers.Real):
        PAGE_LOAD_TIMEOUT = chart['page_load_timeout']
    elif config.has_option('webdriver', 'page_load_timeout'):
        PAGE_LOAD_TIMEOUT = config.getfloat('webdriver', 'page_load_timeout')

    if 'check_if_exists_timeout' in chart and isinstance(chart['check_if_exists_timeout'], numbers.Real):
        CHECK_IF_EXISTS_TIMEOUT = chart['check_if_exists_timeout']
    elif config.has_option('webdriver', 'check_if_exists_timeout'):
        CHECK_IF_EXISTS_TIMEOUT = config.getfloat('webdriver', 'check_if_exists_timeout')

    if 'delays' in chart and isinstance(chart['delays'], dict):
        delays = chart['delays']

        if 'change_symbol' in delays and isinstance(delays['change_symbol'], numbers.Real):
            DELAY_CHANGE_SYMBOL = delays['change_symbol']
        elif config.has_option('delays', 'change_symbol'):
            DELAY_CHANGE_SYMBOL = config.getfloat('delays', 'change_symbol')
        if 'submit_alert' in delays and isinstance(delays['submit_alert'], numbers.Real):
            DELAY_SUBMIT_ALERT = delays['submit_alert']
        elif config.has_option('delays', 'submit_alert'):
            DELAY_SUBMIT_ALERT = config.getfloat('delays', 'submit_alert')
        if 'break' in delays and isinstance(delays['break'], numbers.Real):
            DELAY_BREAK = delays['break']
        elif config.has_option('delays', 'break'):
            DELAY_BREAK = config.getfloat('delays', 'break')
        if 'break_mini' in delays and isinstance(delays['break_mini'], numbers.Real):
            DELAY_BREAK_MINI = delays['break_mini']
        elif config.has_option('delays', 'break_mini'):
            DELAY_BREAK_MINI = config.getfloat('delays', 'break_mini')
        if 'clear_inactive_alerts' in delays and isinstance(delays['clear_inactive_alerts'], numbers.Real):
            DELAY_CLEAR_INACTIVE_ALERTS = delays['clear_inactive_alerts']
        elif config.has_option('delays', 'clear_inactive_alerts'):
            DELAY_CLEAR_INACTIVE_ALERTS = config.getfloat('delays', 'clear_inactive_alerts')
        if 'keystroke' in delays and isinstance(delays['keystroke'], numbers.Real):
            DELAY_KEYSTROKE = delays['keystroke']
        elif config.has_option('delays', 'keystroke'):
            DELAY_KEYSTROKE = config.getfloat('delays', 'keystroke')


def open_chart(browser, chart, counter_alerts, total_alerts):
    """
    :param browser:
    :param chart:
    :param counter_alerts:
    :param total_alerts:
    :return:

    TODO:   remember original setting of opened chart, and place them back when finished
    """

    try:
        # load the chart
        close_all_popups(browser)
        log.info("Opening chart " + chart['url'])

        # set wait times defined in chart
        set_delays(chart)
        log.info("WAIT_TIME_IMPLICIT = " + str(WAIT_TIME_IMPLICIT))
        log.info("PAGE_LOAD_TIMEOUT = " + str(PAGE_LOAD_TIMEOUT))
        log.info("CHECK_IF_EXISTS_TIMEOUT = " + str(CHECK_IF_EXISTS_TIMEOUT))
        log.info("DELAY_BREAK_MINI = " + str(DELAY_BREAK_MINI))
        log.info("DELAY_BREAK = " + str(DELAY_BREAK))
        log.info("DELAY_SUBMIT_ALERT = " + str(DELAY_SUBMIT_ALERT))
        log.info("DELAY_CHANGE_SYMBOL = " + str(DELAY_CHANGE_SYMBOL))
        log.info("DELAY_CLEAR_INACTIVE_ALERTS = " + str(DELAY_CLEAR_INACTIVE_ALERTS))
        log.info("DELAY_KEYSTROKE = " + str(DELAY_KEYSTROKE))

        url = unquote(chart['url'])
        browser.execute_script("window.open('" + url + "');")
        for handle in browser.window_handles[1:]:
            browser.switch_to.window(handle)

        wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, css_selectors['btn_watchlist_menu'])
        time.sleep(DELAY_WATCHLIST)
        # scrape the symbols for each watchlist
        dict_watchlist = dict()
        for i in range(len(chart['watchlists'])):
            # open list of watchlists element
            watchlist = chart['watchlists'][i]
            log.info("Collecting symbols from watchlist " + watchlist)
            wait_and_click(browser, css_selectors['btn_watchlist_menu_menu'])

            # load watchlist
            watchlist_exists = False
            el_options = browser.find_elements_by_css_selector(css_selectors['options_watchlist'])
            for j in range(len(el_options)):
                if el_options[j].text == watchlist:
                    el_options[j].click()
                    watchlist_exists = True
                    log.debug('Watchlist \'' + watchlist + '\' found')
                    time.sleep(DELAY_WATCHLIST)
                    break

            if watchlist_exists:
                # extract symbols from watchlist
                symbols = dict()
                dict_symbols = browser.find_elements_by_css_selector(css_selectors['div_watchlist_item'])
                for j in range(len(dict_symbols)):
                    symbol = dict_symbols[j]
                    symbols[j] = symbol.get_attribute('data-symbol-full')
                    if len(symbols) >= config.getint('tradingview', 'max_symbols_per_watchlist'):
                        break
                log.debug(str(len(dict_symbols)) + ' names found for watchlist \'' + watchlist + '\'')
                dict_watchlist[chart['watchlists'][i]] = symbols

        # open alerts tab
        wait_and_click(browser, css_selectors['btn_alerts'])
        # set the time frame
        for i in range(len(chart['timeframes'])):
            timeframe = chart['timeframes'][i]
            interval = get_interval(timeframe)
            set_timeframe(browser, timeframe)
            time.sleep(DELAY_TIMEFRAME)

            # iterate over each symbol per watchlist
            # for j in range(len(chart['watchlists'])):
            for j in range(len(chart['watchlists'])):
                log.info("Opening watchlist " + chart['watchlists'][j])
                try:
                    symbols = dict_watchlist[chart['watchlists'][j]]
                except KeyError:
                    log.error(chart['watchlists'][j] + " doesn't exist")
                    break

                # open each symbol within the watchlist
                for k in range(len(symbols)):
                    symbol = symbols[k]
                    log.info(symbol)

                    # change symbol
                    try:
                        # might be useful for multi threading set the symbol by going to different url like this:
                        # https://www.tradingview.com/chart/?symbol=BINANCE%3AAGIBTC
                        input_symbol = browser.find_element_by_css_selector(css_selectors['input_symbol'])
                        send_keys(input_symbol, symbol)
                        input_symbol.send_keys(Keys.ENTER)
                        time.sleep(DELAY_CHANGE_SYMBOL)

                    except Exception as err:
                        log.debug('Unable to change to symbol at index ' + str(k) + ' in list of symbols:')
                        log.debug(str(symbols))
                        log.exception(err)

                    for l in range(len(chart['alerts'])):
                        if counter_alerts >= config.getint('tradingview', 'max_alerts') and config.getboolean('tradingview', 'clear_inactive_alerts'):
                            # try clean inactive alerts first
                            time.sleep(DELAY_CLEAR_INACTIVE_ALERTS)
                            wait_and_click(browser, css_selectors['btn_alert_menu'])
                            wait_and_click(browser, css_selectors['item_clear_inactive_alerts'])
                            wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                            time.sleep(DELAY_BREAK * 4)
                            # update counter
                            alerts = browser.find_elements_by_css_selector(css_selectors['item_alerts'])
                            if type(alerts) is list:
                                counter_alerts = len(alerts)

                        if counter_alerts >= config.getint('tradingview', 'max_alerts'):
                            log.warning("Maximum alerts reached. You can set this to a higher number in the kairos.cfg. Exiting program.")
                            return [counter_alerts, total_alerts]
                        try:
                            screenshot_url = ''
                            if config.has_option('logging', 'screenshot_timing') and config.get('logging', 'screenshot_timing') == 'alert':
                                screenshot_url = take_screenshot(browser, symbol, interval)[0]
                            create_alert(browser, chart['alerts'][l], timeframe, interval, symbols[k], screenshot_url)
                            counter_alerts += 1
                            total_alerts += 1
                        except Exception as err:
                            log.error("Could not set alert: " + symbols[k] + " " + chart['alerts'][l]['name'])
                            log.exception(err)

    except Exception as exc:
        log.exception(exc)
    return [counter_alerts, total_alerts]


def log_screenshot(browser, quit_program=False, name=''):
    if config.has_option('logging', 'screenshot_on_error') and config.getboolean('logging', 'screenshot_on_error'):
        filename = str(name) + datetime.datetime.now().strftime('%Y%m%d_%H%M') + '.png'
        if not os.path.exists('log'):
            os.mkdir('log')
        filename = os.path.join('log', filename)
        element = browser.find_element_by_css_selector('html')

        try:
            location = element.location
            size = element.size
            browser.save_screenshot(filename)
            offset_left, offset_right, offset_top, offset_bottom = [0, 0, 0, 0]
            if config.has_option('logging', 'screenshot_offset_left'):
                offset_left = config.getint('logging', 'screenshot_offset_right')
            if config.has_option('logging', 'screenshot_offset_right'):
                offset_right = config.getint('logging', 'screenshot_offset_top')
            if config.has_option('logging', 'screenshot_offset_top'):
                offset_top = config.getint('logging', 'screenshot_offset_left')
            if config.has_option('logging', 'screenshot_offset_bottom'):
                offset_bottom = config.getint('logging', 'screenshot_offset_bottom')
            x = location['x'] + offset_left
            y = location['y'] + offset_top
            width = location['x'] + size['width'] + offset_right
            height = location['y'] + size['height'] + offset_bottom
            im = Image.open(filename)
            im = im.crop((int(x), int(y), int(width), int(height)))
            im.save(filename)
            log.error('snapshot: ' + str(filename))
        except Exception as take_screenshot_error:
            log.exception(take_screenshot_error)
        if quit_program:
            exit(0)


def take_screenshot(browser, symbol, interval, retry_number=0):
    """
    Use selenium for a screenshot, or alternatively use TradingView's screenshot feature
    :param browser:
    :param symbol:
    :param interval:
    :param retry_number:
    :return:
    """
    screenshot_url = ''
    filename = ''

    try:

        if config.has_option('tradingview', 'tradingview_screenshot') and config.getboolean('tradingview', 'tradingview_screenshot'):
            html = browser.find_element_by_css_selector('html')
            html.send_keys(Keys.ALT + "s")
            time.sleep(DELAY_SCREENSHOT_DIALOG)
            input_screenshot_url = html.find_element_by_css_selector(css_selectors['dlg_screenshot_url'])
            screenshot_url = input_screenshot_url.get_attribute('value')
            html.send_keys(Keys.ESCAPE)
            log.debug(screenshot_url)

        elif screenshot_dir != '':
            chart_dir = ''
            match = re.search("^.*chart.(\\w+).*", browser.current_url)
            if re.Match:
                today_dir = os.path.join(screenshot_dir, datetime.datetime.today().strftime('%Y%m%d'))
                if not os.path.exists(today_dir):
                    os.mkdir(today_dir)
                chart_dir = os.path.join(today_dir, match.group(1))
                if not os.path.exists(chart_dir):
                    os.mkdir(chart_dir)
                chart_dir = os.path.join(chart_dir, )
            filename = symbol.replace(':', '_') + '_' + interval + '.png'
            filename = os.path.join(chart_dir, filename)
            elem_chart = browser.find_element_by_class_name('layout__area--center')
            time.sleep(DELAY_SCREENSHOT)

            location = elem_chart.location
            size = elem_chart.size
            browser.save_screenshot(filename)
            offset_left, offset_right, offset_top, offset_bottom = [0, 0, 0, 0]
            if config.has_option('logging', 'screenshot_offset_left'):
                offset_left = config.getint('logging', 'screenshot_offset_right')
            if config.has_option('logging', 'screenshot_offset_right'):
                offset_right = config.getint('logging', 'screenshot_offset_top')
            if config.has_option('logging', 'screenshot_offset_top'):
                offset_top = config.getint('logging', 'screenshot_offset_left')
            if config.has_option('logging', 'screenshot_offset_bottom'):
                offset_bottom = config.getint('logging', 'screenshot_offset_bottom')
            x = location['x'] + offset_left
            y = location['y'] + offset_top
            width = location['x'] + size['width'] + offset_right
            height = location['y'] + size['height'] + offset_bottom
            im = Image.open(filename)
            im = im.crop((int(x), int(y), int(width), int(height)))
            im.save(filename)

            log.debug(filename)

    except Exception as take_screenshot_error:
        log.exception(take_screenshot_error)
        [screenshot_url, filename] = retry_take_screenshot(browser, symbol, interval, retry_number)
    if screenshot_url == '' and filename == '':
        [screenshot_url, filename] = retry_take_screenshot(browser, symbol, interval, retry_number)

    return [screenshot_url, filename]


def retry_take_screenshot(browser, symbol, interval, retry_number=0):
    if retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('Trying again (' + str(retry_number + 1) + ')')
        browser.refresh()
        # Switching to Alert
        try:
            alert = browser.switch_to_alert()
            alert.accept()
            time.sleep(5)
        finally:
            return take_screenshot(browser, symbol, interval, retry_number + 1)
    else:
        log.error('Max retries reached.')


def create_alert(browser, alert_config, timeframe, interval, ticker_id, screenshot_url='', retry_number=0):
    """
    Create an alert based upon user specified yaml configuration.
    :param browser:         The webdriver.
    :param alert_config:    The config for this specific alert.
    :param timeframe:       Timeframe, e.g. 1 day, 2 days, 4 hours, etc.
    :param interval:        TV's short format, e.g. 2 weeks = 2W, 1 day = 1D, 4 hours =4H, 5 minutes = 5M.
    :param ticker_id:       Ticker / Symbol, e.g. COINBASE:BTCUSD.
    :param screenshot_url:  URL of TV's screenshot feature
    :param retry_number:    Optional. Number of retries if for some reason the alert wasn't created.
    :return: true, if successful
    """
    global alert_dialog

    try:
        html = browser.find_element_by_css_selector('html')
        html.send_keys(Keys.ALT + 'a')
        # wait_and_click(browser, css_selectors['btn_create_alert'])
        time.sleep(DELAY_BREAK)
        alert_dialog = browser.find_element_by_class_name(class_selectors['form_create_alert'])
        log.debug(str(len(alert_config['conditions'])) + ' yaml conditions found')

        # 1st row, 1st condition
        current_condition = 0
        css_1st_row_left = css_selectors['dlg_create_alert_first_row_first_item']
        try:
            wait_and_click(alert_dialog, css_1st_row_left)
        except Exception as alert_err:
            log.exception(alert_err)
            return retry(browser, alert_config, timeframe, interval, ticker_id, screenshot_url, retry_number)

        # time.sleep(DELAY_BREAK_MINI)
        el_options = alert_dialog.find_elements_by_css_selector(css_selectors['options_dlg_create_alert_first_row_first_item'])
        if not select(alert_config, current_condition, el_options, ticker_id):
            return False

        # 1st row, 2nd condition (if applicable)
        css_1st_row_right = css_selectors['exists_dlg_create_alert_first_row_second_item']
        if element_exists(browser, alert_dialog, css_1st_row_right, 0.5):
            current_condition += 1
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_first_row_second_item'])
            el_options = alert_dialog.find_elements_by_css_selector(css_selectors['options_dlg_create_alert_first_row_second_item'])
            if not select(alert_config, current_condition, el_options, ticker_id):
                return False

        # 2nd row, 1st condition
        current_condition += 1
        css_2nd_row = css_selectors['dlg_create_alert_second_row']
        wait_and_click(alert_dialog, css_2nd_row)
        el_options = alert_dialog.find_elements_by_css_selector(css_selectors['options_dlg_create_alert_second_row'])
        if not select(alert_config, current_condition, el_options, ticker_id):
            return False

        # 3rd+ rows, remaining conditions
        current_condition += 1
        i = 0
        while current_condition < len(alert_config['conditions']):
            time.sleep(DELAY_BREAK_MINI)
            log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
            # we need to get the inputs again for every iteration as the number may change
            inputs = alert_dialog.find_elements_by_css_selector(css_selectors['inputs_and_selects_create_alert_3rd_row_and_above'])
            while True:
                if inputs[i].get_attribute('type') == 'hidden':
                    i += 1
                else:
                    break

            if inputs[i].tag_name == 'select':
                elements = alert_dialog.find_elements_by_css_selector(css_selectors['dlg_create_alert_3rd_row_group_item'])
                if not ((elements[i].text == alert_config['conditions'][current_condition]) or ((not EXACT_CONDITIONS) and elements[i].text.startswith(alert_config['conditions'][current_condition]))):
                    elements[i].click()
                    time.sleep(DELAY_BREAK_MINI)

                    el_options = elements[i].find_elements_by_css_selector(css_selectors['options_dlg_create_alert_3rd_row_group_item'])
                    condition_yaml = str(alert_config['conditions'][current_condition])
                    found = False
                    for j in range(len(el_options)):
                        option_tv = str(el_options[j].get_attribute("innerHTML")).strip()
                        if (option_tv == condition_yaml) or ((not EXACT_CONDITIONS) and option_tv.startswith(condition_yaml)):
                            wait_and_click(alert_dialog, css_selectors['selected_dlg_create_alert_3rd_row_group_item'].format(j + 1))
                            found = True
                            break
                    if not found:
                        log.error("Invalid condition (" + str(current_condition+1) + "): '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
                        return False
            elif inputs[i].tag_name == 'input':
                copy2paste(inputs[i], str(alert_config['conditions'][current_condition]).strip())

            # give some time
            current_condition += 1
            i += 1

        # Options (i.e. frequency)
        wait_and_click(alert_dialog, css_selectors['checkbox_dlg_create_alert_frequency'].format(str(alert_config['options']).strip()))
        # Expiration
        set_expiration(alert_dialog, alert_config)

        # Show popup
        checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_show_popup'])
        if is_checkbox_checked(checkbox) != alert_config['show_popup']:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_show_popup'])

        # Sound
        checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_play_sound'])
        if is_checkbox_checked(checkbox) != alert_config['sound']['play']:
            wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_play_sound'])
        if is_checkbox_checked(checkbox):
            # set ringtone
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_ringtone'])
            el_options = alert_dialog.find_elements_by_css_selector(css_selectors['options_dlg_create_alert_ringtone'])
            for i in range(len(el_options)):
                if str(el_options[i].text).strip() == str(alert_config['sound']['ringtone']).strip():
                    el_options[i].click()
            # set duration
            wait_and_click(alert_dialog, css_selectors['dlg_create_alert_sound_duration'])
            el_options = alert_dialog.find_elements_by_css_selector(css_selectors['options_dlg_create_alert_sound_duration'])
            for i in range(len(el_options)):
                if str(el_options[i].text).strip() == str(alert_config['sound']['duration']).strip():
                    el_options[i].click()

        # Communication options
        # Send Email
        try:
            checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_send_email'])
            if is_checkbox_checked(checkbox) != alert_config['send']['email']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email'])
            # Send Email-to-SMS (the checkbox is indeed called 'send-sms'!)
            checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_email_to_sms'])
            if is_checkbox_checked(checkbox) != alert_config['send']['email-to-sms']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_email_to_sms'])
            # Send SMS (only for premium members)
            checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_send_sms'])
            if is_checkbox_checked(checkbox) != alert_config['send']['sms']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_sms'])
            # Notify on App
            checkbox = alert_dialog.find_element_by_name(name_selectors['checkbox_dlg_create_alert_send_push'])
            if is_checkbox_checked(checkbox) != alert_config['send']['notify-on-app']:
                wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_send_push'])

            # Construct message
            textarea = alert_dialog.find_element_by_name('description')
            generated = textarea.text
            chart = browser.current_url + '?symbol=' + ticker_id
            show_multi_chart_layout = False
            try:
                show_multi_chart_layout = alert_config['show_multi_chart_layout']
            except KeyError:
                log.warn('charts: multichartlayout not set in yaml, defaulting to multichartlayout = no')
            if type(interval) is str and len(interval) > 0 and not show_multi_chart_layout:
                chart += '&interval=' + str(interval)
            text = str(alert_config['message']['text'])
            text = text.replace('%TIMEFRAME', ' ' + timeframe)
            text = text.replace('%SYMBOL', ' ' + ticker_id)
            text = text.replace('%NAME', ' ' + alert_config['name'])
            text = text.replace('%CHART', ' ' + chart)
            text = text.replace('%SCREENSHOT', ' ' + screenshot_url)
            text = text.replace('%GENERATED', generated)
            try:
                screenshot_urls = []
                for i in range(len(alert_config['include_screenshots_of_charts'])):
                    screenshot_urls.append(alert_config['include_screenshots_of_charts'][i]+'?symbol='+ticker_id)
                text += ' screenshots_to_include: ' + str(screenshot_urls).replace("'", "")
            except ValueError as value_error:
                log.exception(value_error)
            except KeyError:
                log.warn('charts: include_screenshots_of_charts not set in yaml, defaulting to default screenshot')
            copy2paste(textarea, text)
        except Exception as alert_err:
            log.exception(alert_err)
            return retry(browser, alert_config, timeframe, interval, ticker_id, screenshot_url, retry_number)

        # Submit the form
        element = browser.find_element_by_css_selector(css_selectors['btn_dlg_create_alert_submit'])
        element.click()

        time.sleep(DELAY_SUBMIT_ALERT)

    except Exception as exc:
        log.exception(exc)
        # on except, refresh and try again
        return retry(browser, alert_config, timeframe, interval, ticker_id, screenshot_url, retry_number)

    return True


def import_watchlist(filepath, filename):

    browser = create_browser(False)
    login(browser)

    try:
        wait_and_click(browser, css_selectors['btn_calendar'])
        wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-tabs > div > div > div > div > div:nth-child(1)')
        time.sleep(0.5)
        wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
        time.sleep(0.5)

        el_options = browser.find_elements_by_css_selector('div.charts-popup-list > a.item.special')
        for j in range(len(el_options)):
            if str(el_options[j].text).startswith('Import Watchlist'):
                el_options[j].click()
                time.sleep(2)
                pyautogui.typewrite(r"" + filepath, interval=DELAY_KEYSTROKE)
                pyautogui.press('enter')
                time.sleep(1)
                log.info('watchlist imported')
                break

        # After a watchlist is imported, TV opens it. Since we cannot delete a watchlist while opened, we can safely assume that any watchlist of the same name that can be deleted is old and should be deleted
        wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
        time.sleep(0.5)
        el_options = browser.find_elements_by_css_selector('div.charts-popup-list > a.item.first:not(.active-item-backlight)')
        time.sleep(0.5)
        j = 0
        while j < len(el_options):
            try:
                if str(el_options[j].text) == str(filename).replace('.txt', ''):
                    btn_delete = el_options[j].find_element_by_class_name('icon-delete')
                    time.sleep(0.5)
                    browser.execute_script("arguments[0].setAttribute('style','visibility:visible;');", btn_delete)
                    time.sleep(0.5)
                    btn_delete.click()
                    # handle confirmation dialog
                    wait_and_click(browser, 'div.js-dialog__action-click.js-dialog__no-drag.tv-button.tv-button--success')
                    log.info('existing watchlist ' + str(filename).replace('.txt', '') + ' deleted')
                    # give TV time to remove the watchlist
                    time.sleep(0.5)
                    # open the watchlists menu again and update the options to prevent 'element is stale' error
                    wait_and_click(browser, 'body > div.layout__area--right > div > div.widgetbar-pages > div.widgetbar-pagescontent > div.widgetbar-page.active > div.widgetbar-widget.widgetbar-widget-watchlist > div.widgetbar-widgetheader > div.widgetbar-headerspace > a')
                    time.sleep(0.5)
                    el_options = browser.find_elements_by_css_selector('div.charts-popup-list > a.item.first:not(.active-item-backlight)')
                    time.sleep(0.5)
                    j = 0
            except Exception as e:
                log.exception(e)
            j = j + 1

    except Exception as e:
        log.info('Cannot import watchlist')
        log.info('If you are running OS X make sure you have pyobjc installed:')
        log.info('\tpip3 install pyobjc')
        log.info('If you have problems installing pyobjc on OS X El Capitain, try this instead:')
        log.info('\tMACOSX_DEPLOYMENT_TARGET=10.11 pip install pyobjc')
        log.exception(e)
    finally:
        destroy_browser(browser)


def select(alert_config, current_condition, el_options, ticker_id):
    log.debug('setting condition {0} to {1}'.format(str(current_condition + 1), alert_config['conditions'][current_condition]))
    value = str(alert_config['conditions'][current_condition])

    if value == "%SYMBOL":
        value = ticker_id.split(':')[1]

    found = False
    for i in range(len(el_options)):
        option_tv = str(el_options[i].get_attribute("innerHTML")).strip()
        if (option_tv == value) or ((not EXACT_CONDITIONS) and option_tv.startswith(value)):
            el_options[i].click()
            found = True
            break
    if not found:
        log.error("Invalid condition (" + str(current_condition+1) + "): '" + alert_config['conditions'][current_condition] + "' in yaml definition '" + alert_config['name'] + "'. Did the title/name of the indicator/condition change?")
    return found


def clear(element):
    element.clear()
    element.send_keys(MODIFIER_KEY + 'a')
    element.send_keys(Keys.BACKSPACE)
    time.sleep(DELAY_BREAK_MINI * 0.5)


def send_keys(element, string, interval=DELAY_KEYSTROKE):
    for i in range(len(string)):
        element.send_keys(string[i])
        time.sleep(interval)


def copy2paste(element, string):
    pyperclip.copy(string)
    clear(element)
    pyperclip.paste()
    if OS == 'macos':
        element.send_keys(Keys.SHIFT + Keys.INSERT)
    else:
        element.send_keys(Keys.CONTROL + 'v')


def retry(browser, alert_config, timeframe, interval, ticker_id, screenshot_url, retry_number):
    if retry_number < config.getint('tradingview', 'create_alert_max_retries'):
        log.info('Trying again (' + str(retry_number+1) + ')')
        browser.refresh()
        # Switching to Alert
        alert = browser.switch_to_alert()
        alert.accept()
        time.sleep(5)
        # change symbol
        input_symbol = browser.find_element_by_css_selector(css_selectors['input_symbol'])
        try:
            copy2paste(input_symbol, ticker_id)
        except Exception as err:
            log.debug('Can\'t find ' + str(ticker_id) + ' in list of symbols:')
            log.exception(err)
        input_symbol.send_keys(Keys.ENTER)
        time.sleep(DELAY_CHANGE_SYMBOL)
        return create_alert(browser, alert_config, timeframe, interval, ticker_id, screenshot_url, retry_number + 1)
    else:
        log.error('Max retries reached.')
        return False


def is_checkbox_checked(checkbox):
    checked = False
    try:
        checked = checkbox.get_attribute('checked') == 'true'
    finally:
        return checked


def set_expiration(_alert_dialog, alert_config):
    max_minutes = 86400
    datetime_format = '%Y-%m-%d %H:%M'

    exp = alert_config['expiration']
    if type(exp) is int:
        alert_config['expiration'] = dict()
        alert_config['expiration']['time'] = exp
        alert_config['expiration']['open-ended'] = False
    else:
        if 'time' not in alert_config['expiration']:
            alert_config['expiration']['time'] = exp
        if 'open-ended' not in alert_config['expiration']:
            alert_config['expiration']['open-ended'] = False

    checkbox = alert_dialog.find_element_by_css_selector(css_selectors['checkbox_dlg_create_alert_open_ended'])
    if is_checkbox_checked(checkbox) != alert_config['expiration']['open-ended']:
        wait_and_click(alert_dialog, css_selectors['clickable_dlg_create_alert_open_ended'])

    if alert_config['expiration']['open-ended'] or str(alert_config['expiration']['time']).strip() == '' or str(alert_config['expiration']['time']).strip().lower().startswith('n') or type(alert_config['expiration']['time']) is None:
        return
    elif type(alert_config['expiration']['time']) is int:
        target_date = datetime.datetime.now() + datetime.timedelta(minutes=float(alert_config['expiration']['time']))
    elif type(alert_config['expiration']['time']) is str and len(str(alert_config['expiration']['time']).strip()) > 0:
        target_date = datetime.datetime.strptime(str(alert_config['expiration']['time']).strip(), datetime_format)
    else:
        return

    max_expiration = datetime.datetime.now() + datetime.timedelta(minutes=float(max_minutes - 1440))
    if target_date > max_expiration:
        target_date = max_expiration
    date_value = target_date.strftime('%Y-%m-%d')
    time_value = target_date.strftime('%H:%M')

    input_date = _alert_dialog.find_element_by_name('alert_exp_date')
    time.sleep(DELAY_BREAK_MINI)
    copy2paste(input_date, date_value)
    input_time = _alert_dialog.find_element_by_name('alert_exp_time')
    time.sleep(DELAY_BREAK_MINI)
    copy2paste(input_time, time_value)


def login(browser):
    url = 'https://www.tradingview.com'
    uid = config.get('tradingview', 'username')
    pwd = config.get('tradingview', 'password')
    browser.get(url)

    # if logged in under a different username or not logged in at all log out and then log in again
    elem_username = browser.find_element_by_css_selector(css_selectors['username'])
    if type(elem_username) is WebElement and elem_username.text != '' and elem_username.text == uid:
        wait_and_click(browser, css_selectors['username'])
        wait_and_click(browser, css_selectors['signout'])

    wait_and_click(browser, css_selectors['signin'])

    # put credentials in if defined
    if uid and pwd:
        input_username = browser.find_element_by_css_selector(css_selectors['input_username'])
        input_password = browser.find_element_by_css_selector(css_selectors['input_password'])
        clear(input_username)
        input_username.send_keys(config.get('tradingview', 'username'))
        clear(input_password)
        input_password.send_keys(config.get('tradingview', 'password'))
    # if there are no user credentials and it is run in the background, then exit
    elif config.getboolean('webdriver', 'run_in_background'):
        log.warn("You are running Kairos in the background but haven't set your TV credentials. Please, do so in the config file or don't run Kairos in the background so you can manually enter your TV credentials on login.")
        exit(0)
    # otherwise give user time to set
    else:
        input_username = browser.find_element_by_css_selector(css_selectors['input_username'])
        input_password = browser.find_element_by_css_selector(css_selectors['input_password'])
        clear(input_password)
        clear(input_username)
        log.info("Please finish setting your credentials within 60 seconds. No need to press the login button (doing so will slow down Kairos).")
        time.sleep(60)
    try:
        wait_and_click(browser, css_selectors['btn_login'])
    finally:
        time.sleep(DELAY_BREAK * 5)


def create_browser(run_in_background):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=' + RESOLUTION)
    options.add_argument('--disable-notifications')
    prefs = {'profile.default_content_setting_values.notifications': 2}
    options.add_experimental_option('prefs', prefs)
    # fix gpu_process_transport)factory.cc(980) error on Windows when in 'headless' mode, see:
    # https://stackoverflow.com/questions/50143413/errorgpu-process-transport-factory-cc1007-lost-ui-shared-context-while-ini
    if OS == 'windows':
        options.add_argument('--disable-gpu')
    # run chrome in the background
    if run_in_background:
        options.add_argument('headless')
    browser = None

    chromedriver_file = r"" + str(config.get('webdriver', 'path'))
    if not os.path.exists(chromedriver_file):
        log.error("File " + chromedriver_file + " does not exist. Did setup your kairos.cfg correctly?")
        raise FileNotFoundError
    chromedriver_file.replace('.exe', '')

    try:
        browser = webdriver.Chrome(executable_path=chromedriver_file, options=options)
        browser.implicitly_wait(WAIT_TIME_IMPLICIT)
    except WebDriverException as web_err:
        log.exception(web_err)
        browser.close()
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return browser


def run(file):
    """
        TODO:   multi threading
    """
    counter_alerts = 0
    total_alerts = 0
    browser = None
    tv = None
    has_charts = False

    try:
        if len(file) > 1:
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), file)
        else:
            file = r"" + os.path.join(config.get('tradingview', 'settings_dir'), config.get('tradingview', 'settings'))
        if not os.path.exists(file):
            log.error("File " + str(file) + " does not exist. Did you setup your kairos.cfg and yaml file correctly?")
            raise FileNotFoundError

        # get the user defined settings file
        try:
            with open(file, 'r') as stream:
                try:
                    tv = yaml.safe_load(stream)
                    has_charts = 'charts' in tv
                except yaml.YAMLError as err_yaml:
                    log.exception(err_yaml)
        except FileNotFoundError as err_file:
            log.exception(err_file)
        except OSError as err_os:
            log.exception(err_os)

        if has_charts:
            browser = create_browser(config.getboolean('webdriver', 'run_in_background'))
            login(browser)

            # do some maintenance on the alert list (removing or restarting)
            try:
                if config.getboolean('tradingview', 'clear_alerts'):
                    wait_and_click(browser, css_selectors['btn_calendar'])
                    wait_and_click(browser, css_selectors['btn_alerts'])
                    wait_and_click(browser, css_selectors['btn_alert_menu'])
                    wait_and_click(browser, css_selectors['item_clear_alerts'])
                    wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                    time.sleep(DELAY_BREAK * 2)
                else:
                    if config.getboolean('tradingview', 'restart_inactive_alerts'):
                        wait_and_click(browser, css_selectors['btn_calendar'])
                        wait_and_click(browser, css_selectors['btn_alerts'])
                        wait_and_click(browser, css_selectors['btn_alert_menu'])
                        wait_and_click(browser, css_selectors['item_restart_inactive_alerts'])
                        wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                        time.sleep(DELAY_BREAK * 2)
                    elif config.getboolean('tradingview', 'clear_inactive_alerts'):
                        wait_and_click(browser, css_selectors['btn_calendar'])
                        wait_and_click(browser, css_selectors['btn_alerts'])
                        wait_and_click(browser, css_selectors['btn_alert_menu'])
                        wait_and_click(browser, css_selectors['item_clear_inactive_alerts'])
                        wait_and_click(browser, css_selectors['btn_dlg_clear_alerts_confirm'])
                        time.sleep(DELAY_BREAK * 2)
                    # count the number of existing alerts
                    alerts = browser.find_elements_by_css_selector(css_selectors['item_alerts'])
                    if type(alerts) is not None:
                        counter_alerts = len(alerts)
            except Exception as e:
                log.exception(e)
            # iterate over all items that have an 'alerts' property
            for file, items in tv.items():
                if type(items) is list:
                    for i in range(len(items)):
                        if 'alerts' in items[i]:
                            [counter_alerts, total_alerts] = open_chart(browser, items[i], counter_alerts, total_alerts)

            summary(total_alerts)
            destroy_browser(browser)
    except Exception as exc:
        log.exception(exc)
        summary(total_alerts)
        destroy_browser(browser)


def summary(total_alerts):
    if total_alerts > 0:
        elapsed = timing.clock() - timing.start
        avg = '%s' % float('%.5g' % (elapsed / total_alerts))
        log.info(str(total_alerts) + " alerts set with an average process time of " + avg + " seconds")
    elif total_alerts == 0:
        log.info("No alerts set")


def destroy_browser(browser):
    if type(browser) is webdriver.Chrome:
        close_all_popups(browser)
        browser.close()
        browser.quit()
