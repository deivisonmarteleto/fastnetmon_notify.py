#!/usr/bin/python3
# Coded by Deivison Marteleto <dmarteleto@gmail.com>



import smtplib
import ssl
from sys import stdin
import optparse
import sys
import logging
import telegram
import json
import requests
import time
from ipwhois.net import Net
from ipwhois.asn import IPASN
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis


MAIL_LIST_DIR = "/opt/jobs/email.txt"
LOG_FILE = "/opt/jobs/fastnetmon-notify.log"
ACTION_BAN_STR = "ban"
ACTION_UNBAN_STR = "unban"

LOG_LEVEL = logging.DEBUG


r = redis.StrictRedis(host="127.0.0.1", charset="utf-8", decode_responses=True, port=6379, db=0)

logging.basicConfig(level = LOG_LEVEL, filename = LOG_FILE, format='%(asctime)s:%(lineno)d - %(message)s')

def get_redis(arg1):
    ip_addr = str("ixdc_" + arg1 + "_flow_dump")
    results = r.get(ip_addr)
    return results


def telegram_bot_sendtext(bot_message):
    bot_token = '*******'
    bot_chatID = '*******'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def get_whois(arg1):
        """ Verificando AS"""
        net = Net(arg1)
        obj = IPASN(net)
        results = obj.lookup()['asn']
        logging.debug("Descobrindo o AS: " + (results))
        return results


def get_contato(arg1):
    """ Selecionando Contato """
    with open(MAIL_LIST_DIR, 'r') as f:
        lista = [(l.split(' ')[0], (l.split(' ')[1].replace('\n', ''))) for l in f]
        selected_mail = [hop for hop in lista if arg1 in hop[0]]
        logging.debug("Selecionando email: " + str(selected_mail))
        if len(selected_mail) > 0:

             return selected_mail[0]
        else:
             raise Exception("Nao existe mail no txt.")


def get_mail(arg1):
    smtp_server = 'mail.******.com.br'
    smtp_ssl_port = 465
    username = '***@***.com.br'
    password = '****'
    from_addr = '******@***.com.br'
    to_addrs = (arg1)
    html = open('./email-template.html')
    message = MIMEText(html.read(), 'html')
    message['Subject'] = '[DDoS Defense] Alerta de ataque DDoS'
    message['From'] = 'no-reply@****.com.br'
    message['To'] = to_addrs
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_ssl_port, context=context) as server:
        server.login(username, password)
        server.sendmail(from_addr, to_addrs, message.as_string())
        logging.debug("Mensagem enviada com sucesso" )


if __name__ == "__main__":
    try:
        if len(sys.argv) != 5:
            logging.error("Miss some paramter")
            exit(3)
        ip_addr = sys.argv[1].replace('_', '.')
        on_redis = get_redis(ip_addr)
        action = sys.argv[4]
        find_asn = get_whois(ip_addr)
        find_contato = get_contato(find_asn)
        logging.debug("starting with ip: " + ip_addr +" and action: " + action )
        if action == ACTION_UNBAN_STR:
            telegram_bot_sendtext(f"Fim do ataque, AS: {find_asn} IP: {ip_addr} - Anuncio do bloco normalizado: ATM IX-Plus. ")
            sys.exit(0)
        elif action == ACTION_BAN_STR:
            body = "".join(sys.stdin.readlines())
            telegram_bot_sendtext(f"Ataque identificado, AS: {find_asn} IP: {ip_addr} - Anuncio do bloco removido: ATM IX-Plus. {on_redis} ")
            contato_1 = str(find_contato[1])
            get_mail(contato_1)
            logging.debug("Mensagem enviada" + body )
            sys.exit(0)
        else:
            logging.warning("None action matched with consts")

    except Exception as e:
        logging.critical(str(e))
