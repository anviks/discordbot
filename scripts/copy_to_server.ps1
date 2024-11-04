$Path = 'scripts'

scp -r -P 8022 "..\$Path" "localhost@192.168.1.165:/data/data/com.termux/files/home/discordbot/$Path"
