# DragRaceSim.py  — single-file Kivy app (updated)
import sys
import os
import json
import random
import math

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '1000')
Config.set('graphics', 'minimum_height', '700')
Config.set('graphics', 'fullscreen', 'auto')  # open full screen automatically

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import (
    Color, RoundedRectangle, Line, Ellipse,
    StencilPush, StencilUse, StencilUnUse, StencilPop
)
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.core.image import Image as CoreImage

# ------------------------------------------------------------------------
# Data paths
# ------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEENS_FILE = os.path.join(BASE_DIR, "queens", "queens.json")
IMAGES_DIR = os.path.join(BASE_DIR, "queens", "images")
SEASONS_FILE = os.path.join(BASE_DIR, "queens", "seasons.json")

def get_image_path(image_name):
    if not image_name:
        return ""
    p = os.path.join(IMAGES_DIR, image_name)
    return p if os.path.exists(p) else ""

def load_queens_data():
    if not os.path.exists(QUEENS_FILE):
        return []
    try:
        with open(QUEENS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("queens", []) if isinstance(data, dict) else data
    except Exception as e:
        print("JSON Error:", e)
        return []

def load_seasons_data():
    # seasons.json expected format example:
    # { "USA": [{"season":"S1","queens":["A","B",...]}, ...], "All Stars":[...], "UK":[... ] }
    if not os.path.exists(SEASONS_FILE):
        # fallback sample data
        return {
            "USA": [
                {"season":"S1", "franchise":"USA", "queens":["BeBe Zahara Benet","Nina Flowers","Rebecca Glasscock"]},
                {"season":"S2", "franchise":"USA", "queens":["Tyra Sanchez","Raven","Jujubee"]}
            ],
            "All Stars": [
                {"season":"AS1", "franchise":"All Stars", "queens":["Chad Michaels","Raven","Shangela"]},
            ],
            "UK": [
                {"season":"UK1", "franchise":"UK", "queens":["The Vivienne","Divina De Campo","Baga Chipz"]}
            ]
        }
    try:
        with open(SEASONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print("Seasons JSON Error:", e)
        return {}

# ------------------------------------------------------------------------
# KV
# ------------------------------------------------------------------------
KV = """
#:import utils kivy.utils

#:set C_BG_LIGHT   utils.get_color_from_hex('#E7F7F3')
#:set C_MINT_MAIN  utils.get_color_from_hex('#4DB6AC')
#:set C_MINT_DARK  utils.get_color_from_hex('#00695C')
#:set C_MINT_ACCENT utils.get_color_from_hex('#B2DFDB')
#:set C_WHITE      (1, 1, 1, 1)
#:set C_TEXT_DARK  utils.get_color_from_hex('#063F36')

<RoundedButton@Button>:
    background_normal: ''
    background_color: C_MINT_MAIN if self.state=='normal' else C_MINT_DARK
    color: C_WHITE
    bold: True
    font_size: '15sp'
    canvas.before:
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [14,]

<GhostButton@Button>:
    background_normal: ''
    background_color: C_MINT_ACCENT if self.state=='normal' else C_MINT_MAIN
    color: C_MINT_DARK
    bold: True
    canvas.before:
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]

<StyledSpinner@Spinner>:
    background_normal: ''
    background_color: 1,1,1,1
    color: C_TEXT_DARK
    font_size: '14sp'
    canvas.before:
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8,]
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 8)
            width: 1

<QueenChip>:
    orientation: 'horizontal'
    size_hint: None, None
    size: 200, 44
    padding: [12, 5, 12, 5]
    spacing: 5
    canvas.before:
        Color:
            rgba: 1,1,1,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [14,]
        Color:
            rgba: 0.3019608, 0.7137255, 0.6745098, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 14)
            width: 1

    Label:
        text: root.text
        color: C_TEXT_DARK
        font_size: '14sp'
        bold: True
        shorten: True
        text_size: self.size
        halign: 'left'
        valign: 'middle'
        size_hint_x: 1

    Button:
        text: "✕"
        size_hint: None, None
        size: 24, 24
        pos_hint: {'center_y': 0.5}
        background_normal: ''
        background_color: 0,0,0,0
        color: utils.get_color_from_hex('#e57373')
        on_release: root.remove_self()

<StartScreen>:
    canvas.before:
        Color:
            rgba: C_BG_LIGHT
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: 18
        spacing: 12

        # Pre-defined Casts button (curved, mint background) above main card
        BoxLayout:
            size_hint_y: None
            height: 56
            padding: [6,0]
            RoundedButton:
                id: btn_predefined_top
                text: "Pre-defined Casts"
                size_hint_x: None
                width: 260
                background_normal: ''
                background_color: C_MINT_MAIN
                color: C_WHITE
                on_release: app.root.current = 'predefined'

            Widget:

        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            padding: 20

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 0.95, 0.9
                spacing: 30
                padding: 30
                canvas.before:
                    Color:
                        rgba: (1,1,1,0.92)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [22,]
                    Color:
                        rgba: C_MINT_MAIN
                    Line:
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 22)
                        width: 2

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.55
                    spacing: 14

                    Label:
                        text: "Configure Season"
                        color: C_MINT_DARK
                        font_size: '24sp'
                        bold: True
                        size_hint_y: None
                        height: 48
                        halign: 'left'
                        text_size: self.size

                    TextInput:
                        id: search_input
                        hint_text: "Search Queen..."
                        multiline: False
                        size_hint_y: None
                        height: 44
                        background_normal: ''
                        background_active: ''
                        background_color: (0.95, 0.95, 0.95, 1)
                        foreground_color: C_TEXT_DARK
                        padding_y: [10, 10]
                        on_text: root.filter_queens(self.text)

                    ScrollView:
                        size_hint_y: None
                        height: 100
                        canvas.before:
                            Color:
                                rgba: (0,0,0,0.03)
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [8,]
                        GridLayout:
                            id: suggestions_grid
                            cols: 1
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 6

                    BoxLayout:
                        size_hint_y: None
                        height: 48
                        spacing: 10
                        RoundedButton:
                            text: "Add Random"
                            on_release: root.add_single_random()
                        RoundedButton:
                            text: "Clear Cast"
                            on_release: root.clear_selection()

                    Label:
                        text: f"Cast Size: {len(root.selected_queens)}"
                        color: C_MINT_DARK
                        size_hint_y: None
                        height: 28
                        halign: 'left'
                        text_size: self.size

                    ScrollView:
                        size_hint_y: None
                        height: 80
                        BoxLayout:
                            id: chips_box
                            orientation: 'horizontal'
                            size_hint_x: None
                            width: self.minimum_width
                            spacing: 8

                    GridLayout:
                        cols: 2
                        spacing: 12
                        size_hint_y: None
                        height: 150

                        Label:
                            text: "Season Format:"
                            color: C_TEXT_DARK
                            halign: 'left'
                            text_size: self.size
                        StyledSpinner:
                            id: spin_season
                            text: 'Regular'
                            values: ['Regular', 'All Stars (Legacy)', 'All Stars (Assassin)']

                        Label:
                            text: "Finale Format:"
                            color: C_TEXT_DARK
                            halign: 'left'
                            text_size: self.size
                        StyledSpinner:
                            id: spin_finale
                            text: 'Top 3'
                            values: ['Top 3', 'Top 4', 'Top 2']

                        Label:
                            text: "Returning Format:"
                            color: C_TEXT_DARK
                            halign: 'left'
                            text_size: self.size
                        StyledSpinner:
                            id: spin_returning
                            text: 'None'
                            values: ['None', 'Random Return', 'Choose Return']

                    RoundedButton:
                        text: "START THE SEASON"
                        size_hint_y: None
                        height: 56
                        font_size: '16sp'
                        on_release: root.start_simulation()

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.45
                    padding: [36, 36]

                    BoxLayout:
                        orientation: 'vertical'
                        padding: 18
                        canvas.before:
                            Color:
                                rgba: C_MINT_MAIN
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]

                        Image:
                            source: 'queens/images/logo.png'
                            allow_stretch: True
                            keep_ratio: True

<PredefinedScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 8

        BoxLayout:
            size_hint_y: None
            height: 56
            spacing: 8
            RoundedButton:
                text: "Back"
                size_hint_x: None
                width: 120
                on_release: app.root.current = 'start'
            Label:
                text: "Pre-defined Casts"
                bold: True
                color: C_MINT_DARK

        BoxLayout:
            size_hint_y: None
            height: 44
            spacing: 8
            Button:
                text: "USA"
                on_release: root.set_tab('USA')
            Button:
                text: "All Stars"
                on_release: root.set_tab('All Stars')
            Button:
                text: "UK"
                on_release: root.set_tab('UK')
            Widget:

        ScrollView:
            GridLayout:
                id: seasons_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: 6

<SimulationScreen>:
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [0,]

    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            size_hint_y: None
            height: 64
            padding: [18, 6]
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 0.92)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [0,]

            Label:
                id: header_label
                text: root.title_text
                color: C_MINT_DARK
                font_size: '20sp'
                bold: True
                halign: 'left'
                text_size: self.size

            RoundedButton:
                text: "Track Record"
                size_hint_x: None
                width: 120
                on_release: root.toggle_track_record()

            Widget:
                size_hint_x: None
                width: 10

            RoundedButton:
                text: "Exit"
                size_hint_x: None
                width: 84
                background_normal: ''
                background_color: 1,1,1,0
                canvas.before:
                    Color:
                        rgba: utils.get_color_from_hex('#e57373')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10,]
                on_release: root.exit_sim()

        AnchorLayout:
            id: main_stage
            anchor_x: 'center'
            anchor_y: 'center'

        BoxLayout:
            size_hint_y: None
            height: 84
            padding: 14
            canvas.before:
                Color:
                    rgba: (1,1,1,0.62)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [0,]

            Widget:
            RoundedButton:
                id: btn_proceed
                text: root.button_text
                size_hint_x: None
                width: 220
                on_release: root.proceed_stage()
            Widget:

<TrackRecordPopup>:
    title: "Season Progress"
    title_color: C_TEXT_DARK
    background: ''
    background_color: C_BG_LIGHT
    separator_color: C_MINT_MAIN
    size_hint: 0.9, 0.9
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        ScrollView:
            GridLayout:
                id: grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 2
        Button:
            text: "Close"
            size_hint_y: None
            height: 50
            background_normal: ''
            background_color: C_MINT_DARK
            on_release: root.dismiss()
"""

# ------------------------------------------------------------------------
# Python UI components
# ------------------------------------------------------------------------
class QueenChip(BoxLayout):
    text = StringProperty("")
    def __init__(self, name, remove_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = name
        self.callback = remove_callback
    def remove_self(self):
        self.callback(self.text)

class QueenCircle(BoxLayout):
    """
    Circular portrait with border and label.
    Uses stencil instructions so the portrait is actually clipped to a circle.
    """
    text = StringProperty("")
    source = StringProperty(None)
    border_color = ListProperty([0.8, 0.8, 0.8, 1])

    def __init__(self, text="", source=None, border_color=None, **kwargs):
        super().__init__(orientation='vertical', size_hint=(None, None), spacing=6, **kwargs)
        self.size = (120, 160)
        self.text = text
        if border_color:
            self.border_color = border_color

        # Anchor to hold the image centered (ensure vertical centering by giving room)
        self.anchor = AnchorLayout(size_hint=(1, None), height=120)
        self.img = Image(source=source or '', size_hint=(None, None), size=(110, 110), allow_stretch=True, keep_ratio=True)
        self.img.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.anchor.add_widget(self.img)

        self.lbl = Label(text=self.text, font_size='13sp', color=get_color_from_hex('#063F36'),
                         bold=True, halign='center', valign='top', size_hint=(1, None), height=30)
        self.lbl.bind(size=lambda inst, *a: setattr(inst, 'text_size', inst.size))

        # update label when text property changes
        self.bind(text=lambda inst, val: setattr(self.lbl, 'text', val))

        self.add_widget(self.anchor)
        self.add_widget(self.lbl)

        # stencil clip for circular image
        with self.canvas.before:
            StencilPush()
            self.clip = Ellipse(pos=(0, 0), size=(0, 0))
            StencilUse()

        with self.canvas.after:
            StencilUnUse()
            StencilPop()
            self._border_color_instr = Color(*self.border_color)
            self._border_line = Line(circle=(0, 0, 0), width=3)

        # Bind to update clip when image moves/resizes
        self.img.bind(pos=self._update_clip, size=self._update_clip)
        self.anchor.bind(pos=self._update_clip, size=self._update_clip)
        self.bind(pos=self._update_clip, size=self._update_clip)
        self.bind(border_color=self._update_border_color)
        self.source = source or ''
        self.bind(source=self._on_source_change)
        self._on_source_change(None, self.source)

    def _on_source_change(self, instance, value):
        if value:
            try:
                if os.path.exists(value):
                    self.img.source = value
                    try:
                        CoreImage(value).texture
                    except Exception:
                        pass
                else:
                    self.img.source = ''
            except Exception:
                self.img.source = ''
        else:
            self.img.source = ''

    def _update_clip(self, *a):
        img_x, img_y = self.img.pos
        img_w, img_h = self.img.size
        try:
            self.clip.pos = (img_x, img_y)
            self.clip.size = (img_w, img_h)
        except Exception:
            pass
        try:
            cx = img_x + img_w / 2.0
            cy = img_y + img_h / 2.0
            r = min(img_w, img_h) / 2.0
            self._border_line.circle = (cx, cy, r)
        except Exception:
            pass

    def _update_border_color(self, *a):
        try:
            self._border_color_instr.rgba = tuple(self.border_color)
        except Exception:
            pass

class TrackRecordPopup(Popup):
    pass

# ------------------------------------------------------------------------
# Screens
# ------------------------------------------------------------------------
class StartScreen(Screen):
    all_queens = ListProperty([])
    selected_queens = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_queens = load_queens_data()
        self.predefined_casts = {
            "Season 1 (Sample)": ["BeBe Zahara Benet", "Nina Flowers", "Rebecca Glasscock"],
            "Season 2 (Sample)": ["Tyra Sanchez", "Raven", "Jujubee"],
            "All Stars Classics": ["Raven", "Chad Michaels", "Jinkx Monsoon"],
            "Random Quick 6": random.sample([q['name'] for q in self.all_queens], min(6, len(self.all_queens))) if self.all_queens else []
        }

    def filter_queens(self, query):
        grid = self.ids.suggestions_grid
        grid.clear_widgets()
        if not query:
            return
        qlow = query.lower()
        matches = [q for q in self.all_queens if qlow in q['name'].lower()]
        for q in matches[:6]:
            btn = Button(text=q['name'], size_hint_y=None, height=38, background_normal='', background_color=(1,1,1,1), color=get_color_from_hex('#00695C'))
            with btn.canvas.before:
                Color(1,1,1,0.92)
                rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[6])
            btn.bind(pos=lambda inst, *a, r=rect: setattr(r, 'pos', inst.pos))
            btn.bind(size=lambda inst, *a, r=rect: setattr(r, 'size', inst.size))
            btn.bind(on_release=lambda inst, name=q['name']: self.add_queen(name))
            grid.add_widget(btn)

    def add_queen(self, name):
        if name in self.selected_queens:
            return
        self.selected_queens.append(name)
        chip = QueenChip(name, self.remove_queen)
        self.ids.chips_box.add_widget(chip)
        self.ids.search_input.text = ""
        self.ids.suggestions_grid.clear_widgets()

    def remove_queen(self, name):
        if name in self.selected_queens:
            self.selected_queens.remove(name)
            self.ids.chips_box.clear_widgets()
            for q in self.selected_queens:
                self.ids.chips_box.add_widget(QueenChip(q, self.remove_queen))

    def add_single_random(self):
        available = [q for q in self.all_queens if q['name'] not in self.selected_queens]
        if available:
            pick = random.choice(available)
            self.add_queen(pick['name'])

    def clear_selection(self):
        self.selected_queens = []
        try:
            self.ids.chips_box.clear_widgets()
        except Exception:
            pass

    def start_simulation(self):
        if len(self.selected_queens) < 4:
            p = Popup(title="Too few queens", content=Label(text="Pick at least 4 queens to start a season."), size_hint=(0.5, 0.34))
            p.open()
            return
        app = App.get_running_app()
        sim_screen = app.root.get_screen('simulation')
        config = {
            'season': self.ids.spin_season.text,
            'finale': self.ids.spin_finale.text,
            'returning': self.ids.spin_returning.text
        }
        full_cast = [q for q in self.all_queens if q['name'] in self.selected_queens]
        sim_screen.initialize_game(full_cast, config)
        app.root.current = 'simulation'

class PredefinedScreen(Screen):
    seasons_data = ObjectProperty(None)
    current_tab = StringProperty('USA')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seasons_data = load_seasons_data()
        # populate when screen opens — kv will call on_pre_enter
    def on_pre_enter(self):
        self.populate_seasons()

    def set_tab(self, tab):
        self.current_tab = tab
        self.populate_seasons()

    def populate_seasons(self):
        grid = self.ids.seasons_grid
        grid.clear_widgets()
        tab = self.current_tab
        items = self.seasons_data.get(tab, [])
        if not items:
            lbl = Label(text="No seasons available.", size_hint_y=None, height=40)
            grid.add_widget(lbl)
            return
        for s in items:
            row = BoxLayout(size_hint_y=None, height=64, padding=[8,6], spacing=6)
            left = BoxLayout(orientation='vertical', size_hint_x=0.6)
            left.add_widget(Label(text=f"{s.get('season','Unknown')} — {s.get('franchise','')}", bold=True, halign='left'))
            left.add_widget(Label(text=f"{len(s.get('queens',[]))} queens", halign='left'))
            row.add_widget(left)
            btn_preview = Button(text="Preview", size_hint_x=0.2, on_release=lambda inst, ss=s: self.preview_season(ss))
            btn_load = Button(text="Load", size_hint_x=0.2, on_release=lambda inst, ss=s: self.load_season(ss))
            row.add_widget(btn_preview)
            row.add_widget(btn_load)
            grid.add_widget(row)

    def preview_season(self, season_dict):
        qlist = season_dict.get('queens', [])
        text = "\n".join(qlist) if qlist else "No queens"
        Popup(title=f"Preview {season_dict.get('season','')}", content=Label(text=text), size_hint=(0.6,0.6)).open()

    def load_season(self, season_dict):
        # load queens into StartScreen selection (only names present in queens.json)
        app = App.get_running_app()
        start = app.root.get_screen('start')
        start.clear_selection()
        names = [n for n in season_dict.get('queens', []) if any(q['name'] == n for q in start.all_queens)]
        for n in names:
            start.add_queen(n)
        Popup(title="Loaded", content=Label(text=f"Loaded {len(names)} queens."), size_hint=(0.5,0.3)).open()
        # Optionally return to start screen:
        app.root.current = 'start'

class SimulationScreen(Screen):
    # states
    STATE_IDLE = 0
    STATE_INTRO = 1
    STATE_PERFORMANCE = 2
    STATE_JUDGING = 3
    STATE_WINNER = 4
    STATE_LIPSYNC = 5
    STATE_ELIMINATION = 6
    STATE_FINALE = 7

    title_text = StringProperty("Workroom")
    button_text = StringProperty("Start Episode")
    bg_color = ListProperty([0.95, 0.97, 0.96, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_state = self.STATE_IDLE
        self.episode = 1
        self.queens_data = {}
        self.eliminated_names = []
        self.config = {}
        self.current_results = {}
        self.current_challenge = ""

    def initialize_game(self, cast, config):
        self.config = config
        self.episode = 1
        self.eliminated_names = []
        self.queens_data = {}
        for q in cast:
            q_copy = q.copy()
            q_copy['history'] = []
            q_copy['stats'] = {
                'perform': random.randint(3, 10),
                'comedy': random.randint(3, 10),
                'runway': random.randint(3, 10),
                'charisma': random.randint(3, 10),
                'lipsync': random.randint(3, 10)
            }
            self.queens_data[q['name']] = q_copy
        self.show_workroom_grid()

    def get_active_queens(self):
        return [q for n, q in self.queens_data.items() if n not in self.eliminated_names]

    def _card_wrap(self, widget, radius=12, bg=(1, 1, 1, 0.98), border=(0.82, 0.94, 0.92, 1)):
        wrapper = BoxLayout(orientation='vertical', padding=10)
        with wrapper.canvas.before:
            Color(*bg)
            rect = RoundedRectangle(pos=wrapper.pos, size=wrapper.size, radius=[radius])
            Color(*border)
            line = Line(rounded_rectangle=(wrapper.x, wrapper.y, wrapper.width, wrapper.height, radius), width=1.2)
        wrapper.bind(pos=lambda inst, *a, r=rect, l=line: (setattr(r, 'pos', inst.pos), setattr(l, 'rounded_rectangle', (inst.x, inst.y, inst.width, inst.height, radius))))
        wrapper.bind(size=lambda inst, *a, r=rect, l=line: (setattr(r, 'size', inst.size), setattr(l, 'rounded_rectangle', (inst.x, inst.y, inst.width, inst.height, radius))))
        wrapper.add_widget(widget)
        return wrapper

    # Workroom grid
    def show_workroom_grid(self):
        stage = self.ids.main_stage
        stage.clear_widgets()
        self.bg_color = [0.95, 0.97, 0.96, 1]
        self.title_text = f"Episode {self.episode} - The Workroom"
        self.button_text = "Start Episode"

        active = self.get_active_queens()
        if not active:
            stage.add_widget(Label(text="No cast selected.", color=[0, 0, 0, 0.6]))
            return

        count = len(active)
        cols = min(4, max(1, count))
        spacing = 18
        cell_w, cell_h = 140, 180
        rows = math.ceil(count / cols)

        grid = GridLayout(cols=cols, spacing=spacing, size_hint=(None, None))
        grid.width = cols * (cell_w + spacing)
        grid.height = rows * (cell_h + spacing)
        grid.padding = [8, 8]

        for q in active:
            qc = QueenCircle(text=q['name'], source=get_image_path(q.get('image')), border_color=[0.28, 0.68, 0.46, 1])
            grid.add_widget(qc)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
        anchor.add_widget(grid)
        scroll = ScrollView(size_hint=(0.95, 0.88))
        scroll.add_widget(anchor)
        stage.add_widget(scroll)

    # Show a centered text/event with optional subject(s)
    def show_text_event(self, title, message, subject=None, subject2=None, text_color=None):
        stage = self.ids.main_stage
        stage.clear_widgets()

        outer = BoxLayout(orientation='vertical', padding=18, spacing=12)

        title_card = BoxLayout(size_hint_y=None, height=70, padding=8)
        with title_card.canvas.before:
            Color(1, 1, 1, 0.98)
            trect = RoundedRectangle(pos=title_card.pos, size=title_card.size, radius=[10])
            Color(*get_color_from_hex('#4DB6AC'))
            tline = Line(rounded_rectangle=(title_card.x, title_card.y, title_card.width, title_card.height, 10), width=1.2)
        title_card.bind(pos=lambda inst, *a, r=trect, l=tline: (setattr(r, 'pos', inst.pos), setattr(l, 'rounded_rectangle', (inst.x, inst.y, inst.width, inst.height, 10))))
        title_card.bind(size=lambda inst, *a, r=trect, l=tline: (setattr(r, 'size', inst.size), setattr(l, 'rounded_rectangle', (inst.x, inst.y, inst.width, inst.height, 10))))
        title_card.add_widget(Label(text=title, font_size='20sp', bold=True, color=[0, 0.2, 0.17, 1]))
        outer.add_widget(title_card)

        if subject and not subject2:
            content = BoxLayout(orientation='vertical', spacing=12)
            anchor_q = AnchorLayout(size_hint_y=None, height=220)
            qc = QueenCircle(text=subject.get('name', ''), source=get_image_path(subject.get('image')), border_color=[0.95, 0.8, 0.15, 1])
            anchor_q.add_widget(qc)
            content.add_widget(anchor_q)

            msg_text = message or "Condragulations, you are the winner of this week's challenge."
            lbl = Label(text=msg_text, font_size='16sp', halign='center', valign='middle', color=text_color or [0, 0.15, 0.12, 1])
            lbl.text_size = (self.width * 0.7, None)
            content.add_widget(lbl)
            outer.add_widget(self._card_wrap(content, radius=10))
        else:
            content = BoxLayout(orientation='horizontal', spacing=12)
            if subject:
                left = BoxLayout(orientation='vertical', size_hint_x=None, width=180)
                left.add_widget(QueenCircle(text=subject.get('name', ''), source=get_image_path(subject.get('image')), border_color=[0.9, 0.7, 0.1, 1]))
                left.add_widget(Label(text=subject.get('role', ''), size_hint_y=None, height=20, color=[0, 0, 0, 0.7]))
                content.add_widget(left)

            msg_box = BoxLayout(orientation='vertical')
            msg_lbl = Label(text=message, font_size='16sp', halign='center', valign='middle', text_size=(self.width * 0.5, None), color=text_color or [0, 0.15, 0.12, 1])
            msg_box.add_widget(msg_lbl)
            content.add_widget(msg_box)

            if subject2:
                right = BoxLayout(orientation='vertical', size_hint_x=None, width=180)
                right.add_widget(QueenCircle(text=subject2.get('name', ''), source=get_image_path(subject2.get('image')), border_color=[0.8, 0.2, 0.2, 1]))
                right.add_widget(Label(text=subject2.get('role', ''), size_hint_y=None, height=20, color=[0, 0, 0, 0.7]))
                content.add_widget(right)

            outer.add_widget(self._card_wrap(content, radius=10))

        stage.add_widget(outer)

    # Performance screen — show grid of performance cards for each active queen
    def show_performance_groups(self):
        stage = self.ids.main_stage
        stage.clear_widgets()
        self.title_text = f"Episode {self.episode} - Performances"
        self.button_text = "Judges Critiques"

        main = BoxLayout(orientation='vertical', padding=12, spacing=8)
        main.add_widget(Label(text=f"Episode {self.episode} — Performances", size_hint_y=None, height=44, bold=True, color=[0, 0.2, 0.17, 1]))

        active = self.get_active_queens()
        if not active:
            main.add_widget(Label(text="No performances yet.", color=[0,0,0,0.6]))
            stage.add_widget(main)
            return

        cols = min(3, max(1, len(active)))  # make large cards, 3 columns max
        grid = GridLayout(cols=cols, spacing=12, size_hint=(None, None))
        card_w, card_h = 320, 200
        rows = math.ceil(len(active) / cols)
        grid.width = cols * (card_w + 12)
        grid.height = rows * (card_h + 12)
        grid.padding = [8,8]

        for q in active:
            # performance card: portrait + name + last history + stats
            card = BoxLayout(orientation='vertical', padding=8, spacing=6, size_hint=(None,None), size=(card_w, card_h))
            # portrait centered
            qc = QueenCircle(text=q['name'], source=get_image_path(q.get('image')), border_color=[0.28,0.68,0.46,1])
            qc.size = (120,160)
            # stats text
            stats = q.get('stats', {})
            hist = q.get('history', [])[-5:] if q.get('history') else []
            stat_text = f"Stats — P:{stats.get('perform',0)} C:{stats.get('comedy',0)} R:{stats.get('runway',0)} L:{stats.get('lipsync',0)}"
            hist_text = "History: " + ", ".join(hist) if hist else "History: —"
            card.add_widget(AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,None), height=120, children=[qc]))
            card.add_widget(Label(text=stat_text, size_hint_y=None, height=22))
            card.add_widget(Label(text=hist_text, size_hint_y=None, height=20))
            grid.add_widget(card)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,1))
        anchor.add_widget(grid)
        scroll = ScrollView(size_hint=(0.95,0.85))
        scroll.add_widget(anchor)
        main.add_widget(scroll)
        stage.add_widget(main)

    # Judging critiques (centered)
    def show_judging(self):
        stage = self.ids.main_stage
        stage.clear_widgets()
        self.title_text = "Main Stage - Critiques"
        self.button_text = "Proceed"

        outer = BoxLayout(orientation='vertical', padding=14, spacing=12)
        header = BoxLayout(size_hint_y=None, height=44, padding=[8,0])
        with header.canvas.before:
            Color(0.18,0.6,0.48,0.08)
            rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[8])
        header.bind(pos=lambda inst,*a: setattr(rect,'pos', inst.pos))
        header.bind(size=lambda inst,*a: setattr(rect,'size', inst.size))
        header.add_widget(Label(text="Critiques — Main Stage", bold=True, color=[0,0.18,0.15,1]))
        outer.add_widget(header)

        top2 = self.current_results.get('top2', [])
        high = self.current_results.get('high', [])
        low = self.current_results.get('low', [])
        btm2 = self.current_results.get('btm2', [])
        winner = self.current_results.get('winner')
        safe = self.current_results.get('safe', [])

        focus = []
        if winner: focus.append(winner)
        focus.extend(top2)
        focus.extend(high)
        focus.extend(low)
        focus.extend(btm2)

        seen = set(); ordered = []
        for q in focus:
            if not q: continue
            if q['name'] not in seen:
                ordered.append(q); seen.add(q['name'])

        if not ordered:
            outer.add_widget(Label(text="No critique data.", color=[0,0,0,0.5]))
            stage.add_widget(self._card_wrap(outer, radius=10, border=(0.2,0.6,0.45,1)))
            return

        cols = min(6, max(1, len(ordered)))
        cw, ch = 140, 180
        rows = math.ceil(len(ordered)/cols)
        grid = GridLayout(cols=cols, spacing=10, size_hint=(None, None))
        grid.width = cols * (cw + 10)
        grid.height = rows * (ch + 10)

        for q in ordered:
            grid.add_widget(QueenCircle(text=q['name'], source=get_image_path(q.get('image')), border_color=[0.06,0.2,0.16,1]))

        anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,1))
        anchor.add_widget(grid)
        outer.add_widget(anchor)

        if safe:
            safe_names = ", ".join([s['name'] for s in safe])
            outer.add_widget(Label(text=f"Also safe: {safe_names}", color=[0,0,0,0.6], size_hint_y=None, height=22))

        stage.add_widget(self._card_wrap(outer, radius=10, border=(0.2,0.6,0.45,1)))

    # Lip sync screen — pair centered vertically and horizontally
    def show_lipsync(self):
        stage = self.ids.main_stage
        stage.clear_widgets()
        self.title_text = "Lip Sync"
        self.button_text = "Proceed"
        self.bg_color = [0.18, 0.58, 0.51, 1]

        if self.config.get('season') == 'All Stars (Legacy)':
            pair = self.current_results.get('top2', [])
            q1 = pair[0] if len(pair) >= 1 else None
            q2 = pair[1] if len(pair) >= 2 else None
        else:
            btm = self.current_results.get('btm2', [])
            q1 = btm[0] if len(btm) >= 1 else None
            q2 = btm[1] if len(btm) >= 2 else None

        if not q1:
            active = self.get_active_queens()
            q1 = active[0] if active else {'name': 'Unknown', 'image': None}
        if not q2:
            active = self.get_active_queens()
            q2 = active[1] if len(active) > 1 else {'name': 'Unknown', 'image': None}

        outer = BoxLayout(orientation='vertical', padding=18, spacing=10)
        # Use flexible vertical centering: spacer, pair, spacer
        outer.add_widget(Label(size_hint_y=1))  # spacer

        pair_box = BoxLayout(orientation='horizontal', spacing=28, size_hint=(None,None))
        pair_box.width = 520; pair_box.height = 240
        pair_box.add_widget(QueenCircle(text=q1['name'], source=get_image_path(q1.get('image')), border_color=[1,1,1,1]))
        pair_box.add_widget(QueenCircle(text=q2['name'], source=get_image_path(q2.get('image')), border_color=[1,1,1,1]))

        holder = AnchorLayout(size_hint_y=None, height=260)
        holder.add_widget(pair_box)
        outer.add_widget(holder)

        msg = "The time has come... lip sync for your life!"
        outer.add_widget(Label(text=msg, font_size='16sp', color=[1,1,1,1], size_hint_y=None, height=30))

        outer.add_widget(Label(size_hint_y=1))  # spacer
        stage.add_widget(outer)

    # Elimination outcome screen (centered, formatted)
    def show_elimination_view(self, winner_keep, eliminated, message):
        stage = self.ids.main_stage
        stage.clear_widgets()

        outer = BoxLayout(orientation='vertical', padding=16, spacing=10)

        # Title at top
        title_card = BoxLayout(size_hint_y=None, height=56, padding=8)
        with title_card.canvas.before:
            Color(1,1,1,0.98)
            trect = RoundedRectangle(pos=title_card.pos, size=title_card.size, radius=[8])
            Color(*get_color_from_hex('#4DB6AC'))
            tline = Line(rounded_rectangle=(title_card.x, title_card.y, title_card.width, title_card.height, 8), width=1.2)
        title_card.bind(pos=lambda inst,*a: setattr(trect,'pos', inst.pos))
        title_card.bind(size=lambda inst,*a: setattr(trect,'size', inst.size))
        title_card.add_widget(Label(text="Elimination", font_size='20sp', bold=True, color=[0,0.18,0.15,1]))
        outer.add_widget(title_card)

        # Result lines (centered)
        line_box = BoxLayout(orientation='vertical', size_hint_y=None, height=72, spacing=6, padding=[10,0])
        q1_line = Label(text=f"{winner_keep['name']} — Shantay You Stay", font_size='16sp', color=[0,0,0,0.85], size_hint_y=None, height=30)
        q2_line = Label(text=f"{eliminated['name']} — Sashay Away", font_size='16sp', color=[0,0,0,0.85], size_hint_y=None, height=30)
        line_box.add_widget(q1_line); line_box.add_widget(q2_line)
        outer.add_widget(self._card_wrap(line_box, radius=10))

        # Pictures side-by-side centered
        pics_holder = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=240)
        pics = BoxLayout(orientation='horizontal', spacing=30, size_hint=(None, None))
        pics.width = 480; pics.height = 180
        pics.add_widget(QueenCircle(text=winner_keep['name'], source=get_image_path(winner_keep.get('image')), border_color=[0.16,0.5,0.38,1]))
        pics.add_widget(QueenCircle(text=eliminated['name'], source=get_image_path(eliminated.get('image')), border_color=[0.85,0.25,0.25,1]))
        pics_holder.add_widget(pics)
        outer.add_widget(pics_holder)

        outer.add_widget(Label(text=message, font_size='15sp', color=[0,0,0,0.7], size_hint_y=None, height=28))

        stage.add_widget(outer)
        self.button_text = "Next Episode"

    # Flow logic (unchanged)
    def proceed_stage(self):
        active = self.get_active_queens()
        stop_count = {'Top 2': 2, 'Top 3': 3, 'Top 4': 4}.get(self.config.get('finale'), 3)

        if len(active) <= stop_count and self.current_state == self.STATE_IDLE:
            self.current_state = self.STATE_FINALE
            self.run_finale()
            return

        if self.current_state == self.STATE_IDLE:
            self.current_challenge = random.choice(['Acting', 'Comedy', 'Design', 'Ball', 'Snatch Game', 'Rusical'])
            self.show_text_event(f"Episode {self.episode}", f"The challenge is: {self.current_challenge}!")
            self.button_text = "Perform"
            self.current_state = self.STATE_INTRO
            return

        if self.current_state == self.STATE_INTRO:
            self.calculate_placements()
            self.show_performance_groups()
            self.current_state = self.STATE_PERFORMANCE
            self.button_text = "Judges Critiques"
            return

        if self.current_state == self.STATE_PERFORMANCE:
            self.show_judging()
            self.current_state = self.STATE_JUDGING
            self.button_text = "Proceed"
            return

        if self.current_state == self.STATE_JUDGING:
            if 'All Stars' in self.config.get('season', ''):
                if 'Legacy' in self.config.get('season', ''):
                    t = self.current_results.get('top2', [])
                    names = " and ".join([q['name'] for q in t[:2]])
                    self.show_text_event("The Tops", f"The Top 2 of the week are {names}!")
                else:
                    winner = self.current_results.get('winner')
                    if winner:
                        self.show_text_event("The Winner", "", subject=winner)
                    else:
                        self.show_text_event("The Winner", "A winner has been chosen!")
            else:
                winner = self.current_results.get('winner')
                if winner:
                    winner_display = winner.copy()
                    winner_display['role'] = "Winner"
                    self.show_text_event("Results", "", subject=winner_display)
                else:
                    self.show_text_event("Results", "A winner has been chosen!")
            self.title_text = "Lip Sync"
            self.button_text = "Proceed"
            self.current_state = self.STATE_WINNER
            return

        if self.current_state == self.STATE_WINNER:
            self.show_lipsync()
            self.current_state = self.STATE_LIPSYNC
            return

        if self.current_state == self.STATE_LIPSYNC:
            self.decide_elimination()
            self.current_state = self.STATE_ELIMINATION
            return

        if self.current_state == self.STATE_ELIMINATION:
            self.episode += 1
            self.show_workroom_grid()
            self.current_state = self.STATE_IDLE
            self.button_text = "Start Episode"
            return

        if self.current_state == self.STATE_FINALE:
            self.exit_sim()
            return

    # Scoring functions (unchanged)
    def calculate_placements(self):
        active = self.get_active_queens()
        scores = []
        stat_map = {'Acting': 'perform', 'Comedy': 'comedy', 'Snatch Game': 'comedy', 'Rusical': 'perform', 'Design': 'runway', 'Ball': 'runway'}
        main_stat = stat_map.get(self.current_challenge, 'charisma')

        for q in active:
            base = q['stats'].get(main_stat, 5)
            score = base + random.uniform(-2, 3)
            scores.append((score, q))
        scores.sort(key=lambda x: x[0], reverse=True)

        fmt = self.config.get('season', 'Regular')
        res = {'winner': None, 'top2': [], 'high': [], 'safe': [], 'low': [], 'btm2': []}
        n = len(scores)

        if n > 6:
            highs = scores[:3]
            lows = scores[-3:]
            res['winner'] = highs[0][1]
            res['high'] = [h[1] for h in highs[1:]]
            res['low'] = [lows[0][1]]
            res['btm2'] = [lows[1][1], lows[2][1]]
            if 'Legacy' in fmt:
                res['top2'] = [highs[0][1], highs[1][1]]
        else:
            if fmt == 'All Stars (Legacy)':
                if n >= 2:
                    res['top2'] = [scores[0][1], scores[1][1]]
                if n >= 2:
                    res['btm2'] = [scores[-1][1], scores[-2][1]]
                if n >= 3:
                    res['high'] = [scores[2][1]] if n >= 3 else []
                if n >= 4:
                    res['low'] = [scores[-3][1]] if n >= 4 else []
            elif fmt == 'All Stars (Assassin)':
                if n >= 1:
                    res['winner'] = scores[0][1]
                if n >= 6:
                    res['btm2'] = [scores[-1][1], scores[-2][1], scores[-3][1]]
                elif n >= 2:
                    res['btm2'] = [scores[-1][1], scores[-2][1]]
                if n >= 3:
                    res['high'] = [scores[1][1], scores[2][1]] if n >= 3 else []
            else:
                if n >= 1:
                    res['winner'] = scores[0][1]
                if n >= 6:
                    res['high'] = [scores[1][1], scores[2][1]]
                    res['low'] = [scores[-3][1]]
                    res['btm2'] = [scores[-1][1], scores[-2][1]]
                elif n == 5:
                    res['high'] = [scores[1][1]]
                    res['low'] = [scores[-3][1]]
                    res['btm2'] = [scores[-1][1], scores[-2][1]]
                elif n == 4:
                    res['high'] = [scores[1][1]]
                    res['btm2'] = [scores[-1][1], scores[-2][1]]
                elif n == 3:
                    res['btm2'] = [scores[-1][1], scores[-2][1]]

        taken = []
        if res.get('winner'): taken.append(res['winner'])
        taken.extend(res.get('top2', []))
        taken.extend(res.get('high', []))
        taken.extend(res.get('low', []))
        taken.extend(res.get('btm2', []))

        if n <= 6:
            res['safe'] = []
        else:
            res['safe'] = [s[1] for s in scores if s[1] not in taken]

        res['great'] = []
        if res.get('winner'): res['great'].append(res['winner'])
        res['great'].extend(res.get('top2', []))
        res['great'].extend(res.get('high', []))
        res['good'] = res.get('safe', [])
        res['bad'] = []
        res['bad'].extend(res.get('low', []))
        res['bad'].extend(res.get('btm2', []))

        self.current_results = res
        self.record_results_to_history()

    def record_results_to_history(self):
        res = self.current_results
        if res.get('winner'): self.queens_data[res['winner']['name']]['history'].append("WIN")
        for q in res.get('top2', []): self.queens_data[q['name']]['history'].append("TOP2")
        for q in res.get('high', []): self.queens_data[q['name']]['history'].append("HIGH")
        for q in res.get('safe', []): self.queens_data[q['name']]['history'].append("SAFE")
        for q in res.get('low', []): self.queens_data[q['name']]['history'].append("LOW")
        for q in res.get('btm2', []): self.queens_data[q['name']]['history'].append("BTM")

    def decide_elimination(self):
        fmt = self.config.get('season', 'Regular')
        eliminated = None
        survivor = None
        msg = ""

        if fmt == 'All Stars (Legacy)':
            top2 = self.current_results.get('top2', [])
            ls_winner = random.choice(top2) if top2 else None
            btm = self.current_results.get('btm2', [])
            eliminated = random.choice(btm) if btm else None
            if ls_winner and eliminated:
                msg = f"{ls_winner['name']} wins the lip sync and chops {eliminated['name']}!"
                survivor = None
        elif fmt == 'All Stars (Assassin)':
            if random.random() > 0.5:
                btm = self.current_results.get('btm2', [])
                eliminated = random.choice(btm) if btm else None
                if eliminated:
                    msg = f"{self.current_results.get('winner', {'name':'Winner'})['name']} beats the Assassin and eliminates {eliminated['name']}!"
            else:
                btm = self.current_results.get('btm2', [])
                eliminated = random.choice(btm) if btm else None
                if eliminated:
                    msg = f"The Assassin wins! The group has voted to eliminate {eliminated['name']}."
        else:
            btm = self.current_results.get('btm2', [])
            if len(btm) >= 2:
                q1, q2 = btm[0], btm[1]
            elif len(btm) == 1:
                q1 = btm[0]; q2 = {'name': 'Challenger', 'image': None}
            else:
                active = self.get_active_queens()
                q1 = active[0] if active else {'name': 'Unknown', 'image': None}
                q2 = active[1] if len(active) > 1 else {'name': 'Unknown', 'image': None}
            s1 = q1.get('stats', {}).get('lipsync', 5) + random.uniform(0, 5)
            s2 = q2.get('stats', {}).get('lipsync', 5) + random.uniform(0, 5)
            if s1 > s2:
                eliminated = q2; survivor = q1
            else:
                eliminated = q1; survivor = q2
            msg = f"Shantay, you stay {survivor['name']}. {eliminated['name']}, sashay away."

        eliminated = eliminated or {'name': 'Unknown', 'image': None}
        survivor = survivor or {'name': 'Unknown', 'image': None}

        if eliminated and eliminated.get('name'):
            if eliminated['name'] not in self.eliminated_names:
                self.eliminated_names.append(eliminated['name'])
            hist = self.queens_data.get(eliminated['name'], {}).get('history', [])
            if hist:
                hist[-1] = "ELIM"
            else:
                if eliminated['name'] in self.queens_data:
                    self.queens_data[eliminated['name']]['history'].append("ELIM")

            self.show_elimination_view(survivor, eliminated, msg)
            self.button_text = "Next Episode"
        else:
            self.show_text_event("Elimination", "No elimination this episode.")
            self.button_text = "Next Episode"

    def run_finale(self):
        active = self.get_active_queens()
        if not active:
            self.show_text_event("Finale", "No contestants left.")
            return
        winner = random.choice(active)
        winner_display = winner.copy()
        winner_display['role'] = "Crowned Winner"
        self.show_text_event("THE CROWNING", f"The winner of Drag Race is... {winner['name']}!", subject=winner_display)
        self.button_text = "Return to Menu"

    def toggle_track_record(self):
        popup = TrackRecordPopup()
        popup.ids.grid.clear_widgets()
        for name, data in self.queens_data.items():
            row = BoxLayout(size_hint_y=None, height=36, padding=[8, 0])
            status = " [ELIM]" if name in self.eliminated_names else ""
            lbl1 = Label(text=name + status, color=[0, 0, 0, 1], size_hint_x=0.4, halign='left')
            lbl1.text_size = (lbl1.width, None)
            row.add_widget(lbl1)
            hist = " | ".join(data['history'])
            lbl2 = Label(text=hist, color=[0, 0.4, 0.3, 1], size_hint_x=0.6)
            row.add_widget(lbl2)
            popup.ids.grid.add_widget(row)
        popup.open()

    def exit_sim(self):
        app = App.get_running_app()
        app.root.current = 'start'

# ------------------------------------------------------------------------
# App entry
# ------------------------------------------------------------------------
class DragRaceSimulatorApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(PredefinedScreen(name='predefined'))
        sm.add_widget(SimulationScreen(name='simulation'))
        return sm

if __name__ == '__main__':
    DragRaceSimulatorApp().run()
