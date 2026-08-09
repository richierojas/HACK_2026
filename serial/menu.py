import oled
from sound.synth_presets import Synth_Presets

class MenuDataItem:
    def __init__(self, name : str, value, update_function = None ):
        """If value max is provided, draw() will show a bar with value's percentage by default"""
        self.name = name
        self.value = value
        self.update_function = update_function

class BarDataItem(MenuDataItem):
    DEFAULT_UPDATE_PERCENTAGE = 1
    def __init__(self, name : str, value, value_max, value_update_amount = None):
        """
        When calling valueup or down, changes by value_update_amount.
        By default, value_update_amount is set to 1% of the maximum
        """
        super().__init__(name, value)
        self.value_max = value_max
        self.value_update_amount = value_update_amount
        if self.value_update_amount is None:
            self.value_update_amount = self.value_max / 100 * BarDataItem.DEFAULT_UPDATE_PERCENTAGE

    def fraction(self):
        """Returns fraction of value to its maximum as a double"""
        return self.value / self.value_max

    def up(self):
        self.value = min(self.value + self.value_update_amount, self.value_max)

    def down(self):
        """Does not allow negative values"""
        self.value = max(self.value - self.value_update_amount, 0)

# * Assume only one item shown in the bar for now
# ! Does not handle empty arrays, passed arrays must be None or filled
class Menu:
    def __init__(self, name : str, data_items_array = None, bar_data_item : BarDataItem = None, submenus = None, items = None):
        self.name = name
        self.selected = 0
        self.submenus = submenus
        self.data_items = None
        if data_items_array is not None:
            self.data_items = { item.name : item for item in data_items_array }

        #Data item that is shown in the bar, should be in data_items to prevent undefined behavior
        #?Add print if not present in data_items?
        self.bar_data_item = bar_data_item

        if self.submenus is not None:
            for menu in self.submenus:
                menu.supermenu = self

        self.items = items
        self.supermenu = None

    def _entries(self):
        return self.submenus if self.submenus is not None else self.items

    def move_up(self):
        if self.selected > 0:
            self.selected -= 1

    def move_down(self):
        if self.selected < len(self._entries()) - 1:
            self.selected += 1

    #! Does not support multiple bar items
    def bar_up(self):
        self.bar_data_item.up()

    #! Does not support multiple bar itmes
    def bar_down(self):
        self.bar_data_item.down()

    def current(self):
        menu_array = self._entries()
        return menu_array[self.selected]

    #TODO: Add more bar options
    def draw(self, showBar = True):
        entries = self._entries()
        menu_items = [(entry.name if isinstance(entry, Menu) else entry) for entry in entries]

        supermenus = []
        supermenu = self.supermenu
        while supermenu is not None:
            supermenus.append(supermenu)    #stores in reverse order (supermost last)
            supermenu = supermenu.supermenu
        #TODO: finish displaying super menus and update selection above
        supermenu_string = ""
        for sm in reversed(supermenus):
            supermenu_string += f"\\{sm.name}"
        supermenu_string += f"\\{self.name}"


        oled.clear()

        # ===== Title =====
        oled.text(f"ARTEMIS AUDIO - {supermenu_string}", 12, 2)
        oled.line(0, 11, 127, 11)

        # Show 4 menu items
        start = max(0, self.selected - 1)

        if start > len(menu_items) - 4:
            start = max(0, len(menu_items) - 4)

        y = 16

        for i in range(start, min(start + 4, len(menu_items))):

            if i == self.selected:

                # Highlight bar
                oled.fill_rect(0, y - 1, 128, 9, 1)

                # Inverted text
                oled.text(menu_items[i], 6, y, 0)

            else:

                oled.text(menu_items[i], 6, y, 1)

            y += 10

        if showBar and self.bar_data_item is not None:
            bar_data = self.bar_data_item
            # ===== Bottom Bar =====
            oled.line(0, 53, 127, 53)

            oled.text(bar_data.name, 2, 56)

            # Volume outline
            oled.rect(24, 55, 70, 8)

            # Filled volume
            fill = int(68 * bar_data.fraction())

            if fill > 0:
                oled.fill_rect(25, 56, fill, 6)

            # Percentage
            oled.text(str(bar_data.fraction() * 100), 100, 56)

        oled.show()

volume = BarDataItem("VOL", 75, 100)
#TODO: Add functionality for menu options
instruments_menu = Menu("INSTRUMENTS", items=[Synth_Presets.PIANO, Synth_Presets.GUITAR, Synth_Presets.BASS, Synth_Presets.KICK])
volume_menu = Menu("VOLUME", items=["GLOBAL", "ACTIVE", "PLAYBACK"])
record_menu = Menu("RECORD", items=["RECORD", "PLAY-PAUSE"])
key_menu = Menu("KEY", items=["KEY LETTER", "QUALITY", "OCTAVE"])
#if time: chord_menu

main_menu = Menu("MAIN MENU", submenus=[instruments_menu, volume_menu, record_menu, key_menu], data_items_array=[volume], bar_data_item=volume)

_active = main_menu

def move_up():
    _active.move_up()

def move_down():
    _active.move_down()

def current():
    return _active.current()

def draw():
    _active.draw()

def volume_up():
    volume.up()

def volume_down():
    volume.down()

#TODO: Add behavior for selecting item options
def select():
    """Enter currently selected submenu. 
    Returns None if a submenu was selected, returns (menu, item string) if an item was selected"""
    global _active
    picked = _active.current()
    if isinstance(picked, Menu):
        _active = picked
        return None
    return (_active, picked)

def back():
    """moves to supermenu"""
    global _active
    if _active.supermenu is not None:
        _active = _active.supermenu


