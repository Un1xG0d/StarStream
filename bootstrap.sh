chmod +x /home/admin/StarStream/boot.sh
echo -e "@reboot /home/admin/StarStream/boot.sh" |sudo tee -a /etc/crontab
crontab /etc/crontab