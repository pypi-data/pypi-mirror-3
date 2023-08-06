#! /bin/env python
#

import configparser
import os

def defl_input(prompt, default):
  usr = input(prompt+"(%s)" % default);
  if len(usr):
    return (usr)
  else:
    return (default)

def main():
  print("Welcome to lastSoul's netSoul client configurator.")
  print("	!!! Beware, this tool will delete your old configuration !!!")
  input("	Press enter to proceed.")
  config = configparser.RawConfigParser()
  config.add_section("Connection")
  config.set("Connection", 'server', defl_input("NetSoul server IP/Hostname ? ", 'ns-server.epitech.net'))
  config.set("Connection", 'port', defl_input("NetSoul server port ? ", '4242'))
  config.add_section("Auth")
  config.set("Auth", 'login', defl_input("Login ? ", None))
  config.set("Auth", 'passwd', defl_input("Password socks ? ", None))
  config.add_section("Misc")
  config.set("Misc", 'userdata', defl_input("UserData ? ", "lastSoul v1.2"))
  config.set("Misc", 'location', defl_input("Location ? ", None))
  config.set("Misc", 'watch', defl_input("Watchlist (comma-separated) ? ", None))
  try:
    with open(os.environ['HOME'] + '/.lastsoul.cfg', 'wb') as configfile:
      config.write(configfile)
      print("Configuration saved.")
  except IOError as e:
    print("Error while saving config : %s" % e)

if __name__ == "__main__":
  main()
