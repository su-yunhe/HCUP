import datetime,json,os,pathlib
from hypium import UiDriver
base=pathlib.Path(__file__).resolve().parent
os.chdir(base)
driver=UiDriver.connect(device_sn='127.0.0.1:11245')
result=driver.swipe_to_recent_task()
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'action':'UiDriver.swipe_to_recent_task','result':str(result)},ensure_ascii=False))
