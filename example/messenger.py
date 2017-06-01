"""# coding: utf-8"""
# -*- coding: utf-8 -*-
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import json
from example.config import CONFIG
from fbmq import Attachment, Template, QuickReply, NotificationType
from example.fbpage import page

USER_SEQ = {}



@page.handle_optin
def received_authentication(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_auth = event.timestamp

    pass_through_param = event.optin.get("ref")

    print("Received authentication for user %s and page %s with pass "
          "through param '%s' at %s" % (sender_id, recipient_id, pass_through_param, time_of_auth))

    page.send(sender_id, "Authentication successful")


@page.handle_echo
def received_echo(event):
    message = event.message
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")
    print("page id : %s , %s" % (page.page_id, page.page_name))
    print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))


@page.handle_message
def received_message(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_message = event.timestamp
    message = event.message
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    seq = message.get("seq", 0)
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    seq_id = sender_id + ':' + recipient_id
    if USER_SEQ.get(seq_id, -1) >= seq:
        print("Ignore duplicated request")
        return None
    else:
        USER_SEQ[seq_id] = seq







#    if quick_reply:
#        quick_reply_payload = quick_reply.get('payload')
#        print("quick reply for message %s with payload %s" % (message_id, quick_reply_payload))
#
#        page.send(sender_id, "Quick reply tapped")









    if message_text:
        send_message(sender_id, message_text)


    elif message_attachments:
        print('-------------------------------message_attachments-------------------------------------')
        print('message with attachments')
        #page.send(sender_id, "Message with attachment received")
        page.send(sender_id, "Lo siento, por ahora solo reconozco texto")
        page.send(sender_id, "Prueba con un hola ;)")


@page.handle_delivery
def received_delivery_confirmation(event):
    delivery = event.delivery
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)


@page.handle_postback
def received_postback(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_postback = event.timestamp

    payload = event.postback_payload
    print('-------------------------postback_payload----------------------------------------')
    print(payload)

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))
    






    if payload == 'hoteles_playa':
        page.send(sender_id, "Tengo dos promociones para ti")
        page.send(sender_id, Template.Generic([
        Template.GenericElement("Hotel Cancún",
                                subtitle="Reserva ahora tu hotel en Cancún",
                                item_url="http://www.mariachi.io/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_cancun.jpg",
                                buttons=[
                                    Template.ButtonPostBack("reservar", "hotel_cancun")
                                ]),
        Template.GenericElement("Hotel Cabo",
                                subtitle="Reserva ahora tu hotel en los Cabos",
                                item_url="http://www.mariachi.io/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_cabo.jpg",
                                buttons=[
                                    Template.ButtonPostBack("reservar", "hotel_cabo")
                                ])
        ]))
        page.send(sender_id, "La cuarta noche es gratis si reservas desde el chatbot!!!")

    elif payload == 'hotel_cancun' or payload == 'hotel_cabo':
        page.send(sender_id, "Reservación exitosa!!")


    elif payload == 'hotel_ibis' or payload == 'hotel_francia':
        page.send(sender_id, Template.Buttons("Selecciona tu método de pago", [
        Template.ButtonWeb("Tarjeta crédito", "https://akrocard.com/wp-content/uploads/2015/05/tarjeta-pvc-chip-CPU.png"),
        Template.ButtonWeb("Tarjeta débito", "https://akrocard.com/wp-content/uploads/2015/05/tarjeta-pvc-chip-CPU.png")
    ]))

    elif payload == 'reservar_habitacion':
        page.send(sender_id, "Por favor indícame separando con comas, ciudad, estado, fecha de llegada y fecha de partida iniciando por día, mes y año (01, 02, 17)")
   
    elif payload == 'hoteles_cercanos':
        page.send(sender_id, "Claro que sí, será un placer hospedarte.")
        page.send(sender_id, "Compartir ubicacion?",
              quick_replies=[QuickReply(title="compartir", payload="compartir"),
                             QuickReply(title="en otro momento", payload="en otro momento")],
              metadata="DEVELOPER_DEFINED_METADATA")


    elif payload == 'servicios_hotel':
        page.send(sender_id, "Hola, tambien puedo ayudarte con servicio directo a tu habitación")
        page.send(sender_id, "En que te podemos servir?")

    else:
        page.send(sender_id, "Postback called")








@page.handle_read
def received_message_read(event):
    watermark = event.read.get("watermark")
    seq = event.read.get("seq")

    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))


@page.handle_account_linking
def received_account_link(event):
    sender_id = event.sender_id
    status = event.account_linking.get("status")
    auth_code = event.account_linking.get("authorization_code")

    print("Received account link event with for user %s with status %s and auth code %s "
          % (sender_id, status, auth_code))


def send_message(recipient_id, text):
    # If we receive a text message, check to see if it matches any special
    # keywords and send back the corresponding example. Otherwise, just echo
    # the text we received.
    special_keywords = {
        "Image": send_image,
        "Gif": send_gif,
        "Audio": send_audio,
        "Video": send_video,
        "File": send_file,
        "Button": send_button,
        "Generic": send_generic,
        "Receipt": send_receipt,
        "Quick reply": send_quick_reply,
        "Read receipt": send_read_receipt,
        "Typing on": send_typing_on,
        "Typing off": send_typing_off,
        "Account linking": send_account_linking,

        "Hi": send_menu,
        "Holi": send_menu,
        "Hola": send_menu,
        "Hola papu": send_menu,
        "Hola bot": send_menu,
        "Holi bot": send_menu,

        "Quiero reservar una habitación": send_reservacion,
        "Reservar habitación": send_reservacion,
        "Quiero reservar una habitacion": send_reservacion,
        "Reservar habitacion": send_reservacion,
        "quiero reservar una habitacion": send_reservacion,
        "reservar habitacion": send_reservacion,


        "Aguascalientes, Aguascalientes, 04/04/17, 06/04/17": send_Aguascalientes,
        "Aguascalientes": send_Aguascalientes,

        "Quiero conocer hoteles cerca de mi": send_hoteles_cercanos,
        "Quiero conocer hoteles cercanos a mi": send_hoteles_cercanos,
        "Hoteles cercanos": send_hoteles_cercanos,

        "Quisiera ordenar una hamburguesa con queso a la habitación 506": send_hambuerguesa,
        "Quiero una hamburguesa con queso": send_hambuerguesa,
        "Quiero una hamburguesa": send_hambuerguesa,
        "Raymundo Castellanos, cargo a la cuenta de la habitación": send_solicitud,
        "Raymundo Castellanos, cargo a la cuenta de la habitación 506": send_solicitud,
        "Raymundo Castellanos con cargo a mi cuenta": send_solicitud,
        "Raymundo Castellanos": send_solicitud,
        "Raymundo":send_solicitud,
        "Me gustaría agregar papas fritas a mi orden": send_papas,
        "Me gustaría agregar papas fritas a la orden": send_papas,
        "Con papas": send_papas,
        "Con queso": send_papas,


        "Ubicación": send_location,
        "compartir": send_location,
        "en otro momento": send_no_compartir
    }

    if text in special_keywords:
        special_keywords[text](recipient_id)
    else:
        #page.send(recipient_id, text, callback=send_text_callback, notification_type=NotificationType.REGULAR)
        page.send(recipient_id, "Aun no tengo redes neuronales :(")
        page.send(recipient_id, "Pero puedo copiar lo que dices :)")
        page.send(recipient_id, text, callback=send_text_callback, notification_type=NotificationType.REGULAR)
        #page.send(recipient_id, ";P")


def send_text_callback(payload, response):
    print("SEND CALLBACK")





def send_menu(recipient_id):
    print('-----------------------------------------HOLI------SEND_MENU------------------------------------------------------')
    page.send(recipient_id, "Hola, soy hotelbot y estoy para servirte ;)")
    page.send(recipient_id, "Estos son los servicios con los que puedo ayudarte:")
    page.send(recipient_id, Template.Generic([
        Template.GenericElement("Promociones hoteles playa",
                                subtitle="Disfruta de unas vacaciones en el mar",
                                image_url=CONFIG['SERVER_URL'] + "/assets/playa5.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "hoteles_playa")
                                ]),
        Template.GenericElement("Promociones hoteles ciudad",
                                subtitle="Goza de un tour por la ciudad",
                                image_url=CONFIG['SERVER_URL'] + "/assets/city3.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "hoteles_ciudad")
                                ]),
        Template.GenericElement("Reservar una habitación",
                                subtitle="Descansa en una habitación de lujo",
                                image_url=CONFIG['SERVER_URL'] + "/assets/habitacion.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "reservar_habitacion")
                                ]),
        Template.GenericElement("Conocer hoteles cerca de ti",
                                subtitle="Encuentra un hotel a la medida",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "hoteles_cercanos")
                                ]),
        Template.GenericElement("Solicitar servicios dentro del hotel",
                                subtitle="Disfruta de nuestros servicios",
                                image_url=CONFIG['SERVER_URL'] + "/assets/servicioshotel.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "servicios_hotel")
                                ])
    ]))


def send_reservacion(recipient):
    print('----------------------------------RESERVAR----HABITACION--------------------------------------')
    page.send(recipient, "Por favor indícame separando con comas, ciudad, estado, fecha de llegada y fecha de partida iniciando por día, mes y año (01, 02, 17)")

def send_Aguascalientes(recipient):
    page.send(recipient, "¿En cuál de nuestros hoteles te gustaría hospedarte?")
    page.send(recipient, Template.Generic([
        Template.GenericElement("Hotel Ibis",
                                subtitle="Haz tu reservación en Hotel Ibis",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_ibis_aguascalientes.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "hotel_ibis")
                                ]),
        Template.GenericElement("Hotel Francia Aguascalientes",
                                subtitle="Haz tu reservación en Hotel Francia",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_francia_aguascalientes.jpg",
                                buttons=[
                                    Template.ButtonPostBack("seleccionar", "hotel_francia")
                                ])
    ]))


def send_hambuerguesa(recipient):
    print('------------------------------SERVICIO---A----HABITACION----------------------------------------')
    page.send(recipient, "Por favor indique nombre de la persona que se registró en esta habitación y método de pago.")

def send_solicitud(recipient):
    page.send(recipient, "Su solicitud está siendo atendida por nuestro personal, en breve recibirá la orden en su habitación.")

def send_papas(recipient):
    page.send(recipient, "Confirmado, su solicitud está siendo atendida por nuestro personal, en breve recibirá la orden en su habitación.")
    page.send(recipient, "Es un placer servirle")


def send_location(recipient):
    print('-----------------------------enviar---ubicacion-------------------------------------------------')
    page.send(recipient, "Estos son los resultados que encontramos")
    page.send(recipient, Template.Generic([
        Template.GenericElement("Hotel San Francisco",
                                subtitle="Haz tu reservación",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_san_francisco.jpg",
                                buttons=[
                                    Template.ButtonWeb("Ruta", "https://www.google.com.mx/maps/dir/19.2963254,-99.1855357/Hotel+San+Francisco+Centro+Hist%C3%B3rico,+Luis+Moya,+Cuauht%C3%A9moc,+Ciudad+de+M%C3%A9xico,+CDMX/@19.3615022,-99.2475501,12z/data=!3m1!4b1!4m9!4m8!1m1!4e1!1m5!1m1!1s0x85d1fa2819fbd205:0x459bfda439d1d2aa!2m2!1d-99.1449614!2d19.434211")
                                ]),
        Template.GenericElement("Grand Hotel Ciudad de Mexico",
                                subtitle="Haz tu reservación",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_ciudad_mexico.jpg",
                                buttons=[
                                    Template.ButtonWeb("Ruta", "https://www.google.com.mx/maps/dir/19.2963254,-99.1855357/Gran+Hotel+Ciudad+de+M%C3%A9xico,+Av.+16+de+Septiembre+82,+Centro,+06000+Cuauht%C3%A9moc,+CDMX/@19.3610787,-99.246697,12z/data=!3m1!4b1!4m9!4m8!1m1!4e1!1m5!1m1!1s0x85ce0157191d1341:0xd6e6ab909104fb4c!2m2!1d{{longitude}}!2d{{latitude}}")
                                ]),
        Template.GenericElement("Hotel Isabel la Catolica",
                                subtitle="Haz tu reservación",
                                image_url=CONFIG['SERVER_URL'] + "/assets/hotel_isabel.jpg",
                                buttons=[
                                    Template.ButtonWeb("Ruta", "https://www.google.com.mx/maps/dir/19.2961852,-99.1855789/Hotel+Isabel,+Isabel+la+Cat%C3%B3lica+63,+Centro+Hist%C3%B3rico,+Centro,+06000+Ciudad+de+M%C3%A9xico,+CDMX/@19.3593533,-99.2125291,13z/data=!3m1!4b1!4m9!4m8!1m1!4e1!1m5!1m1!1s0x85d1fed2ef819f19:0x65f5a7cded682f87!2m2!1d{{longitude}}!2d{{latitude}}")])
    ]))

def send_no_compartir(recipient):
    print('----------------------------send_no_compartir------------------------------------------------')
    page.send(recipient, "En que mas te puedo ayudar?")


def send_hoteles_cercanos(recipient):
    print('------------------------------HOTELES----CERCANOS-----------------------------------------------')
    page.send(recipient, "Claro que sí, será un placer hospedarte.")
    page.send(recipient, "Compartir ubicacion?",
          quick_replies=[QuickReply(title="compartir", payload="compartir"),
                         QuickReply(title="en otro momento", payload="en otro momento")],
          metadata="DEVELOPER_DEFINED_METADATA")

#    page.send(recipient, "What's your favorite movie genre?",
#              quick_replies=[QuickReply(title="Action", payload="PICK_ACTION"),
#                             QuickReply(title="Comedy", payload="PICK_COMEDY")],
#              metadata="DEVELOPER_DEFINED_METADATA")
























def send_image(recipient):
    print('00000000000000000000000000000000000000000000000000000000000000')
    print(recipient)
    print('00000000000000000000000000000000000000000000000000000000000000')
    #page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "https://www.qa.dineroexpress.com.mx/img/137435869.jpg"))
    page.send(recipient, Attachment.Image("https://www.qa.dineroexpress.com.mx/img/137435869.jpg"))

def send_gif(recipient):
    page.send(recipient, Attachment.Image(CONFIG['SERVER_URL'] + "/assets/instagram_logo.gif"))


def send_audio(recipient):
    page.send(recipient, Attachment.Audio(CONFIG['SERVER_URL'] + "/assets/sample.mp3"))


def send_video(recipient):
    page.send(recipient, Attachment.Video(CONFIG['SERVER_URL'] + "/assets/allofus480.mov"))


def send_file(recipient):
    #page.send(recipient, Attachment.File(CONFIG['SERVER_URL'] + "/assets/test.txt"))
    page.send(recipient, Attachment.File("https://www.qa.dineroexpress.com.mx/img/137435869.jpg"))


def send_button(recipient):
    """
    Shortcuts are supported
    page.send(recipient, Template.Buttons("hello", [
        {'type': 'web_url', 'title': 'Open Web URL', 'value': 'https://www.oculus.com/en-us/rift/'},
        {'type': 'postback', 'title': 'tigger Postback', 'value': 'DEVELOPED_DEFINED_PAYLOAD'},
        {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
    ]))
    """
    page.send(recipient, Template.Buttons("hello", [
        Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
        Template.ButtonPostBack("trigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
        Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
    ]))


@page.callback(['DEVELOPED_DEFINED_PAYLOAD'])
def callback_clicked_button(payload, event):
    print(payload, event)


def send_generic(recipient):
    page.send(recipient, Template.Generic([
        Template.GenericElement("rift",
                                subtitle="Next-generation virtual reality",
                                item_url="https://www.oculus.com/en-us/rift/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                                buttons=[
                                    Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                                    Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                                    Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                                ]),
        Template.GenericElement("touch",
                                subtitle="Your Hands, Now in VR",
                                item_url="https://www.oculus.com/en-us/touch/",
                                image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                                buttons=[
                                    {'type': 'web_url', 'title': 'Open Web URL',
                                     'value': 'https://www.oculus.com/en-us/rift/'},
                                    {'type': 'postback', 'title': 'tigger Postback',
                                     'value': 'DEVELOPED_DEFINED_PAYLOAD'},
                                    {'type': 'phone_number', 'title': 'Call Phone Number', 'value': '+16505551234'},
                                ])
    ]))


def send_receipt(recipient):
    receipt_id = "order1357"
    element = Template.ReceiptElement(title="Oculus Rift",
                                      subtitle="Includes: headset, sensor, remote",
                                      quantity=1,
                                      price=599.00,
                                      currency="USD",
                                      image_url=CONFIG['SERVER_URL'] + "/assets/riftsq.png"
                                      )

    address = Template.ReceiptAddress(street_1="1 Hacker Way",
                                      street_2="",
                                      city="Menlo Park",
                                      postal_code="94025",
                                      state="CA",
                                      country="US")

    summary = Template.ReceiptSummary(subtotal=698.99,
                                      shipping_cost=20.00,
                                      total_tax=57.67,
                                      total_cost=626.66)

    adjustment = Template.ReceiptAdjustment(name="New Customer Discount", amount=-50)

    page.send(recipient, Template.Receipt(recipient_name='Peter Chang',
                                          order_number=receipt_id,
                                          currency='USD',
                                          payment_method='Visa 1234',
                                          timestamp="1428444852",
                                          elements=[element],
                                          address=address,
                                          summary=summary,
                                          adjustments=[adjustment]))


def send_quick_reply(recipient):
    """
    shortcuts are supported
    page.send(recipient, "What's your favorite movie genre?",
                quick_replies=[{'title': 'Action', 'payload': 'PICK_ACTION'},
                               {'title': 'Comedy', 'payload': 'PICK_COMEDY'}, ],
                metadata="DEVELOPER_DEFINED_METADATA")
    """
    page.send(recipient, "What's your favorite movie genre?",
              quick_replies=[QuickReply(title="Action", payload="PICK_ACTION"),
                             QuickReply(title="Comedy", payload="PICK_COMEDY")],
              metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['PICK_ACTION'])
def callback_picked_genre(payload, event):
    print(payload, event)


def send_read_receipt(recipient):
    page.mark_seen(recipient)


def send_typing_on(recipient):
    page.typing_on(recipient)


def send_typing_off(recipient):
    page.typing_off(recipient)


def send_account_linking(recipient):
    page.send(recipient, Template.AccountLink(text="Welcome. Link your account.",
                                              account_link_url=CONFIG['SERVER_URL'] + "/authorize",
                                              account_unlink_button=True))


def send_text_message(recipient, text):
    page.send(recipient, text, metadata="DEVELOPER_DEFINED_METADATA")
