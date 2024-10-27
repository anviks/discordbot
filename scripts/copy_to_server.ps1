$SourcePath = '.\translations'
$DestinationPath = ''

scp -r -P 8022 $SourcePath "localhost@192.168.1.165:/data/data/com.termux/files/home/discordbot/$DestinationPath"
