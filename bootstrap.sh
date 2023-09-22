chmod +x /home/admin/AutoARISS/boot.sh
echo -e "@reboot /home/admin/AutoARISS/boot.sh" |sudo tee -a /etc/crontab
crontab /etc/crontab