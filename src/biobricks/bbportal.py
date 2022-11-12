import json

def BBtoken_exists(config):
  return 'BBToken' in config

def BBtoken_browser_update(config,CONFIG_FILE):
  print("\033[91m copy token from https://members.biobricks.ai/token\033[0m")
  config['BBTOKEN'] = input('paste token here: ')
  with open(CONFIG_FILE, 'w') as f:
    json.dump(config, f)
        
  