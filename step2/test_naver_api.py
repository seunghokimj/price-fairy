import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from naver_api import call_naver_api

print(call_naver_api('닌텐도스위치'))
