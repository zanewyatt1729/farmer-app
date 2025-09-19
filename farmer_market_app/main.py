from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import requests
import json
from kivy.uix.boxlayout import BoxLayout

# Load UI from ui.kv
Builder.load_file('ui.kv')

class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        response = requests.post('http://localhost:5000/api/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            data = response.json()
            self.manager.current = 'main'
            self.manager.role = data['role']
        else:
            self.ids.error_label.text = 'Login failed'

class RegisterScreen(Screen):
    def register(self):
        username = self.ids.username.text
        password = self.ids.password.text
        role = self.ids.role.text
        response = requests.post('http://localhost:5000/api/register', json={'username': username, 'password': password, 'role': role})
        if response.status_code == 201:
            self.manager.current = 'login'
        else:
            self.ids.error_label.text = 'Registration failed'

class MainScreen(Screen):
    def on_enter(self):
        self.load_products()

    def load_products(self):
        response = requests.get('http://localhost:5000/api/products')
        if response.status_code == 200:
            products = response.json()
            self.ids.product_list.clear_widgets()
            for p in products:
                self.ids.product_list.add_widget(ProductItem(product=p))

class ProductItem(BoxLayout):
    def __init__(self, product, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.ids.name.text = product['name']
        self.ids.description.text = product['description']
        self.ids.price.text = str(product['price'])

class ChatScreen(Screen):
    def send_message(self):
        content = self.ids.message_input.text
        other_user_id = 1  # Placeholder, need to select user
        response = requests.post(f'http://localhost:5000/api/messages/{other_user_id}', json={'content': content})
        if response.status_code == 201:
            self.ids.message_input.text = ''
            self.load_messages()

    def load_messages(self):
        other_user_id = 1
        response = requests.get(f'http://localhost:5000/api/messages/{other_user_id}')
        if response.status_code == 200:
            messages = response.json()
            self.ids.chat_list.clear_widgets()
            for m in messages:
                self.ids.chat_list.add_widget(ChatItem(message=m))

class ChatItem(BoxLayout):
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        self.ids.content.text = message['content']

class OrderScreen(Screen):
    def on_enter(self):
        self.load_orders()

    def load_orders(self):
        response = requests.get('http://localhost:5000/api/orders')
        if response.status_code == 200:
            orders = response.json()
            self.ids.order_list.clear_widgets()
            for o in orders:
                self.ids.order_list.add_widget(OrderItem(order=o))

class OrderItem(BoxLayout):
    def __init__(self, order, **kwargs):
        super().__init__(**kwargs)
        self.ids.product_id.text = str(order['product_id'])
        self.ids.quantity.text = str(order['quantity'])
        self.ids.status.text = order['status']

class FarmerMarketApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(OrderScreen(name='orders'))
        return sm

if __name__ == '__main__':
    FarmerMarketApp().run()
