@echo off
chcp 65001
setx Backup_HOME "C:\Program Files\mysql\MySQL Enterprise Backup 8.0\bin" /M
setx Path "%Path%;%Backup_HOME%" /M
echo 环境变量设置完成
