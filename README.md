Olá!

Esse script substitui o script original do Fastnetmon:

/etc/fastnetmon.conf
----
# This script executed for ban, unban and attack detail collection
#notify_script_path = /usr/local/bin/notify_about_attack.sh
----

Esse Script notifica o cliente via E-Mail consultando o cadastro no PHPIPAM:

Cadastro no PHPIPAM:

“Section” - cadastrar o ASN do cliente;
“Description” - Cadastrar o E-MAIL do cliente;

Esse há possibilidade de personalizar o HTML do E-Mail.

editando o arquivo: email-template.html

Integração ao Telegram:

Adicionar o Token e o Chat_ID.

"Que a força esteja com voces!"
