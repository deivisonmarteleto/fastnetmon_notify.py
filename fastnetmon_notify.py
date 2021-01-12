#!/bin/python3

import sys
from sys import stdin
import logging
import telegram
import json
import requests
import time
import os
import ssl
import ipaddress
from ipwhois.net import Net
from ipwhois.asn import IPASN
from phpipam_client import PhpIpamClient, GET, PATCH
from datetime import datetime
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import redis

# VARIAVEIS
ACTION_BAN_STR = "ban"
ACTION_UNBAN_STR = "unban"
DIR_NET_LIST = '/opt/jobs/networks_list'
LOG_FILE_DIR = '/opt/jobs/mail_as.log'
LOG_LEVEL = logging.DEBUG
list_subnet = []


r = redis.StrictRedis(host="127.0.0.1", charset="utf-8", decode_responses=True, port=6379, db=0)

# API IPAM
ipam = PhpIpamClient(
    url='http://10.3.1.2:8008',
    app_id='app',
    token='TOKEN',
    username='api_user',
    password='SENHA',
    encryption=False,
)

logging.basicConfig(level = LOG_LEVEL, filename = LOG_FILE_DIR, format='%(asctime)s:%(lineno)d - %(message)s')

# FIM
def get_redis(arg1):
    ip_addr = str("ixdc_" + arg1 + "_flow_dump")
    results = r.get(ip_addr)
    return results


def telegram_bot_sendtext(bot_message):
    bot_token = 'TOKEN'
    bot_chatID = 'CHAT_ID'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


#Recebe o argv IP converte para AS

def get_whois(ipaddr):
        net = Net(ipaddr)
        obj = IPASN(net)
        results = obj.lookup()['asn']
        return results


## Consultar EMAIL


def coletar_mail_asn_ipam():
    a = ipam.get('/sections/')
    return [{'mail':i['description'],'asn':i['name']} for i in a]


def get_mail_ipam(asn1):
    asn_ipam = coletar_mail_asn_ipam()
    for i in range(0, len(asn_ipam)):
        asn = str(asn_ipam[i]['asn'])
        mail = str(asn_ipam[i]['mail'])
        if asn1 in asn:
            return mail


def send_mail(email):
    smtp_server = 'SMTP_SERVER'
    smtp_ssl_port = 465
    username = 'CONTA@MAIL.com'
    password = 'SENHA'
    from_addr = 'CONTA@MAIL.com.br'
    to_addrs = (email)
    html = open('/path/email-template.html')
    message = MIMEText(html.read(), 'html')
    message['Subject'] = '[DDoS Defense] Alerta de ataque DDoS'
    message['From'] = 'no-reply@mail.com.br'
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
        action = sys.argv[4]
        find_asn = get_whois(ip_addr)
        find_contato = get_mail_ipam(find_asn)
        on_redis = get_redis(ip_addr)
        logging.debug("starting with ip: " + ip_addr +" and action: " + action)
        if action == ACTION_BAN_STR:
            body = "".join(sys.stdin.readlines())
            telegram_bot_sendtext(f"Ataque identificado, AS: {find_asn} IP: {ip_addr} - Realizando anuncio do bloco para UPX Mitigation. {on_redis} ")
            contato_1 = str(find_contato)
            send_mail(contato_1)
            logging.debug("Mensagem enviada" + body )
            sys.exit(0)
        elif action == ACTION_UNBAN_STR:
            logging.debug("Mensagem unbam" )
            telegram_bot_sendtext(f"Fim do ataque, AS: {find_asn} IP: {ip_addr} - Bloco removido da UPX mitigation. ")
            sys.exit(0)
        else:
            logging.warning("None action matched with consts")

    except Exception as e:
        logging.critical(str(e))



