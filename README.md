PhpIPAM and FNM INTEGRATION

The Script queries the ASN and E-MAIL of the customers registered in phpIPAM, and sends two types of notifications.

- Send personalized E-MAIL to the customer's ASN / CIDR registration.
- Sends a notification on Telegram to the NOC.

---------------------------------------------------------------------------------
PhpIPAM E-Mail / Subnet / ASN registration:

  >  “Section” - register the customer's ASN;
  >  “Description” - register the customer's EMAIL;
  >  “subnets” - register the customer's SUBNET IPv4/24 and IPv6/32;

source: https://phpipam.net/api/api_documentation/

----------------------------------------------------------------------------------

This script replaces the original Fastnetmon script:

"/etc/fastnetmon.conf
----
# This script executed for ban, unban and attack detail collection
#notify_script_path = /usr/local/bin/notify_about_attack.sh"
----


"Que a força esteja com voces!"
