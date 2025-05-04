from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from threading import Thread

import backend

Window.size = (450, 500)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 18
        self.background_color = (0.2, 0.6, 1, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.size_hint_y = None
        self.height = 50
        with self.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MicButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 20
        self.background_normal = 'mic.png'
        self.background_down = 'mic.png'
        self.background_color = (1, 1, 1, 1)
        self.color = (0, 0, 0, 1)
        self.size_hint = (None, None)
        self.size = (50, 50)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.circle = RoundedRectangle(size=self.size, pos=self.pos, radius=[25])
        self.bind(pos=self.update_circle, size=self.update_circle)
        self.anim = None

    def update_circle(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size

    def start_pulse(self):
        self.anim = Animation(size=(60, 60), duration=0.5) + Animation(size=(50, 50), duration=0.5)
        self.anim.repeat = True
        self.anim.start(self)

    def stop_pulse(self):
        Clock.schedule_once(self._stop_pulse_main_thread)

    def _stop_pulse_main_thread(self, dt):
        self.size = (50, 50)
        self.circle.size = self.size

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=20, padding=20, **kwargs)

        Window.clearcolor = (1, 1, 1, 1)

        self.title_label = Label(
            text="Inventory Assistant",
            font_size=26,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.title_label)

        self.subtitle_label = Label(
            text="How can I assist you today?",
            font_size=18,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.subtitle_label)

        self.card = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint=(1, None), height=450)
        with self.card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.card_bg = RoundedRectangle(size=self.card.size, pos=self.card.pos, radius=[20])
        self.card.bind(size=self.update_card_bg, pos=self.update_card_bg)

        self.image = Image(source='use.png', size_hint_y=None, height=120)
        self.card.add_widget(self.image)

        self.response_label = Label(
            text="I'm ready to help you!",
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, None),
            height=100,
            halign='center',
            valign='middle'
        )
        self.response_label.bind(size=self.response_label.setter('text_size'))
        self.card.add_widget(self.response_label)

        input_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)

        self.user_input = TextInput(
            hint_text="Enter your command...",
            font_size=16,
            multiline=False
        )
        self.user_input.bind(on_text_validate=self.on_enter)

        self.mic_button = MicButton()
        self.mic_button.bind(on_press=self.activate_mic)

        input_layout.add_widget(self.user_input)
        input_layout.add_widget(self.mic_button)
        self.card.add_widget(input_layout)

        self.add_widget(self.card)

        button_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)

        self.check_stock_btn = RoundedButton(text="Check Stock")
        self.check_stock_btn.bind(on_press=self.check_stock)
        button_grid.add_widget(self.check_stock_btn)

        self.update_stock_btn = RoundedButton(text="Update Stock")
        self.update_stock_btn.bind(on_press=self.update_stock)
        button_grid.add_widget(self.update_stock_btn)

        self.view_report_btn = RoundedButton(text="View Today's Report")
        self.view_report_btn.bind(on_press=self.view_report)
        button_grid.add_widget(self.view_report_btn)

        self.reset_db_btn = RoundedButton(text="View Database")
        self.reset_db_btn.bind(on_press=self.reset_database)
        button_grid.add_widget(self.reset_db_btn)

        self.add_widget(button_grid)

        self.db_label = Label(
            text="Connected to database",
            font_size=12,
            color=(0, 0.6, 0, 1),
            size_hint_y=None,
            height=20
        )
        self.add_widget(self.db_label)

    def update_card_bg(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def on_enter(self, instance):
        command = self.user_input.text.strip()
        if command:
            self.process_command(command)

    def activate_mic(self, instance=None):
        def listen_thread():
            self.response_label.text = "Listening..."
            self.mic_button.start_pulse()
            command = backend.speech_input()
            self.mic_button.stop_pulse()
            if command:
                Clock.schedule_once(lambda dt: self.process_command(command))

        Thread(target=listen_thread).start()

    def process_command(self, command):
        self.response_label.text = "Assistant is typing..."
        Clock.schedule_once(lambda dt: self.get_tempCodeRunnerFile_response(command), 1)

    def get_tempCodeRunnerFile_response(self, command):
        response = backend.get_response(command)
        self.response_label.text = f"You: {command}\n\nAssistant: {response}"
        backend.speak_response(response)
        self.user_input.text = ""

    def check_stock(self, instance):
        self.response_label.text = "Fetching stock details..."
        Clock.schedule_once(lambda dt: self.call_view_stock(), 0.5)

    def update_stock(self, instance):
        self.response_label.text = "Preparing to update stock..."
        Clock.schedule_once(lambda dt: self.call_update_stock(), 0.5)

    def view_report(self, instance):
        self.response_label.text = "Generating today's sales report..."
        Clock.schedule_once(lambda dt: self.call_today_report(), 0.5)

    def reset_database(self, instance):
        self.response_label.text = "Opening full database view..."
        Clock.schedule_once(lambda dt: self.call_view_dataset(), 0.5)

    def call_view_stock(self):
        try:
            backend.view_stock()
            self.response_label.text = "Stocks checked!"
        except Exception as e:
            self.response_label.text = f"Error: {e}"

    def call_update_stock(self):
        try:
            backend.update_stock()
            self.response_label.text = "Updated the stock!"
        except Exception as e:
            self.response_label.text = f"Error: {e}"

    def call_today_report(self):
        try:
            backend.today_report()
            self.response_label.text = "Today's report generated!"
        except Exception as e:
            self.response_label.text = f"Error: {e}"

    def call_view_dataset(self):
        try:
            backend.view_dataset()
            self.response_label.text = "Database displayed!"
        except Exception as e:
            self.response_label.text = f"Error: {e}"

class InventoryAppMain(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    InventoryAppMain().run()
