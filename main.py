import json
import os
import urllib.parse
import webbrowser
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

Window.clearcolor = (0.94, 0.95, 0.96, 1)
MY_WHATSAPP_NUMBER = "917383584862"
DATA_FILE = "medicines.json"


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
      return json.load(f)
  return []


class MedicineCard(BoxLayout):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(1, 1, 1, 1)
      self.rect = RoundedRectangle(
          pos=self.pos, size=self.size, radius=[dp(10)]
      )
    self.bind(pos=self._update_rect, size=self._update_rect)

  def _update_rect(self, instance, value):
    self.rect.pos = instance.pos
    self.rect.size = instance.size


class AmbicastorsApp(BoxLayout):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.orientation = "vertical"
    self.padding = 0
    self.spacing = 0
    self.medicines = load_data()
    self.selected_image_path = ""

    top_bar = BoxLayout(
        size_hint_y=None, height=dp(60), padding=[dp(15), dp(10)]
    )
    title_label = Label(
        text="[b][color=008055]Ambicastors[/color] [color=111111]Pharmacy[/color][/b]",
        markup=True,
        font_size="22sp",
        halign="left",
        valign="center",
    )
    title_label.bind(size=title_label.setter("text_size"))
    top_bar.add_widget(title_label)
    self.add_widget(top_bar)

    main_layout = BoxLayout(
        orientation="vertical", padding=dp(12), spacing=dp(12)
    )

    rx_banner = Button(
        text="[b]+ Upload Doctor Prescription[/b]\n[size=12sp]Get 100% Original Medicines Delivered Fast[/size]",
        markup=True,
        size_hint_y=None,
        height=dp(58),
        background_normal="",
        background_color=(0.05, 0.55, 0.35, 1),
    )
    rx_banner.bind(on_press=self.send_rx_whatsapp)
    main_layout.add_widget(rx_banner)

    admin_btn = Button(
        text="+ Add Medicine to Shop (Admin)",
        size_hint_y=None,
        height=dp(36),
        background_normal="",
        background_color=(0.2, 0.25, 0.3, 1),
        font_size="13sp",
    )
    admin_btn.bind(on_press=self.show_add_popup)
    main_layout.add_widget(admin_btn)

    list_title = Label(
        text="[b][color=333333]Popular Products[/color][/b]",
        markup=True,
        size_hint_y=None,
        height=dp(20),
        halign="left",
    )
    list_title.bind(size=list_title.setter("text_size"))
    main_layout.add_widget(list_title)

    self.scroll = ScrollView()
    self.list_layout = BoxLayout(
        orientation="vertical", size_hint_y=None, spacing=dp(12)
    )
    self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
    self.scroll.add_widget(self.list_layout)
    main_layout.add_widget(self.scroll)

    self.add_widget(main_layout)
    self.refresh_list()

  def refresh_list(self):
    self.list_layout.clear_widgets()
    for med in self.medicines:
      card = MedicineCard(
          size_hint_y=None, height=dp(105), padding=dp(10), spacing=dp(12)
      )

      if med.get("img") and os.path.exists(med["img"]):
        img = Image(
            source=med["img"],
            size_hint_x=None,
            width=dp(80),
            allow_stretch=True,
            keep_ratio=True,
        )
        card.add_widget(img)
      else:
        no_img = Label(
            text="[No Image]",
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=None,
            width=dp(80),
            font_size="12sp",
        )
        card.add_widget(no_img)

      details = Label(
          text=f"[b][size=16sp][color=111111]{med['name']}[/color][/size][/b]\n\n[size=15sp][color=008055][b]MRP {med['price']}[/b][/color][/size]",
          markup=True,
          halign="left",
          valign="center",
      )
      details.bind(size=details.setter("text_size"))
      card.add_widget(details)

      order_btn = Button(
          text="BUY NOW",
          size_hint_x=None,
          width=dp(90),
          background_normal="",
          background_color=(0.05, 0.55, 0.35, 1),
          bold=True,
          font_size="13sp",
      )
      order_btn.bind(on_press=lambda inst, m=med: self.ask_address_popup(m))
      card.add_widget(order_btn)

      self.list_layout.add_widget(card)

  def show_add_popup(self, instance):
    self.selected_image_path = ""
    content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

    self.name_in = TextInput(
        hint_text="Brand Name (e.g. Crocin 650)", multiline=False
    )
    self.price_in = TextInput(
        hint_text="Price (e.g. ₹30)", multiline=False
    )

    self.img_btn = Button(
        text="Choose Photo File", background_color=(0.2, 0.4, 0.7, 1)
    )
    self.img_btn.bind(on_press=self.open_file_chooser)

    save_btn = Button(
        text="Save Medicine", background_color=(0.1, 0.6, 0.3, 1), bold=True
    )
    save_btn.bind(on_press=self.save_medicine)

    content.add_widget(self.name_in)
    content.add_widget(self.price_in)
    content.add_widget(self.img_btn)
    content.add_widget(save_btn)

    self.add_popup = Popup(
        title="Add New Product", content=content, size_hint=(0.9, 0.65)
    )
    self.add_popup.open()

  def open_file_chooser(self, instance):
    file_content = BoxLayout(
        orientation="vertical", spacing=dp(10), padding=dp(10)
    )
    default_path = (
        "/sdcard/Download" if os.path.exists("/sdcard/Download") else "/sdcard"
    )

    self.file_chooser = FileChooserListView(
        path=default_path, filters=["*.jpg", "*.png", "*.jpeg"]
    )
    select_btn = Button(
        text="Select This Photo",
        size_hint_y=None,
        height=dp(45),
        background_color=(0.1, 0.6, 0.3, 1),
    )
    select_btn.bind(on_press=self.confirm_photo_selection)

    file_content.add_widget(self.file_chooser)
    file_content.add_widget(select_btn)

    self.chooser_popup = Popup(
        title="Select Medicine Photo",
        content=file_content,
        size_hint=(0.95, 0.85),
    )
    self.chooser_popup.open()

  def confirm_photo_selection(self, instance):
    if self.file_chooser.selection:
      self.selected_image_path = self.file_chooser.selection[0]
      self.img_btn.text = "Photo Selected!"
      self.chooser_popup.dismiss()

  def save_medicine(self, instance):
    name = self.name_in.text.strip()
    price = self.price_in.text.strip()
    if name and price:
      self.medicines.append(
          {"name": name, "price": price, "img": self.selected_image_path}
      )
      with open(DATA_FILE, "w") as f:
        json.dump(self.medicines, f)
      self.refresh_list()
      self.add_popup.dismiss()

  def ask_address_popup(self, med):
    content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

    name_input = TextInput(hint_text="Patient Name", multiline=False)
    addr_input = TextInput(
        hint_text="Full Address / Delivery Area", multiline=True
    )

    send_btn = Button(
        text="Confirm & Order via WhatsApp",
        background_color=(0.05, 0.55, 0.35, 1),
        bold=True,
    )
    send_btn.bind(
        on_press=lambda inst: self.send_to_whatsapp(
            med, name_input.text, addr_input.text, addr_popup
        )
    )

    content.add_widget(name_input)
    content.add_widget(addr_input)
    content.add_widget(send_btn)

    addr_popup = Popup(
        title=f"Order: {med['name']}", content=content, size_hint=(0.9, 0.55)
    )
    addr_popup.open()

  def send_to_whatsapp(self, med, name, addr, popup):
    msg = f"Hello Ambicastors Pharmacy,\nNew Order Request:\n- *Patient Name:* {name}\n- *Address:* {addr}\n- *Medicine:* {med['name']}\n- *Price:* {med['price']}"
    url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
    webbrowser.open(url)
    popup.dismiss()

  def send_rx_whatsapp(self, instance):
    msg = "Hello Ambicastors Pharmacy, mujhe Doctor ka Prescription bhej kar medicine order karni hai."
    url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
    webbrowser.open(url)


class MainApp(App):

  def build(self):
    return AmbicastorsApp()


if __name__ == "__main__":
  MainApp().run()
