import shiv.cli

shiv.cli.main('-o delay-bot.pyz '
              '-p /usr/bin/python3 '
              '--compressed '
              '--site-packages dist '
              '-r requirements.txt '
              '-e delay-bot:run'.split(" "))
