# Bot

## Librerie github
[Tapo](https://github.com/fishbigger/TapoP100)
[Telegram](https://github.com/eternnoir/pyTelegramBotAPI/)

## Prerequisiti
Si presume che tu abbia ottenuto un token API con [@BotFather](https://core.telegram.org/bots#botfather). Chiameremo questo token TOKEN.

## Ini file
In tapo_lib creare il file tapo.ini
```ini
[Credentials]
email=EMAIL
password=PWD
ip=IP_DEVICE
```
con le credenziali dell'account Tapo TpLink, l'ip del device può essere trovato nell'app in Impostazioni > Informazioni Dispositivo > Indirizzo IP

Nella cartella principale creare il file bot.ini
```ini
[Bot]
key=TOKEN
id_admin=-1
```

## Librerie
Installare un virtualenv, aprire il cmd nella cartella principale 
```cmd
virtualenv venv
```
Ora dovrebbe apparire la scritta (venv) davanti alla linea di comando, altrimenti chiudere e riaprire il cmd.
Insallare le dipendenze:
```cmd
pip install -r requirements.txt
```

## Tapo Device
Vedi dovumentazione [fishbigger Tapo](https://github.com/fishbigger/TapoP100)

## Telegram
Vedi documentazione [Telegram Api](https://core.telegram.org/) e [eternnoir Telegram Bot Api](https://github.com/eternnoir/pyTelegramBotAPI/)

## Start
```cmd
python iot_bot.py
```
