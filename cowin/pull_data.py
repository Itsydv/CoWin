from cowin.base_api import BaseApi
from cowin.config import Constants
import datetime

def today() -> str:
    return datetime.datetime.now().strftime(Constants.DD_MM_YYYY)

class CoWinAPI(BaseApi):

    def get_states(self):
        url = Constants.states_list
        return self._call_api(url)

    def get_districts(self, state_id: str):
        url = f"{Constants.districts_list}/{state_id}"
        return self._call_api(url)

    def get_availability_by_district(self, district_id: str, date: str = today()):
        url = f"{Constants.availability_by_district}?district_id={district_id}&date={date}"
        return self._call_api(url)
    
    def get_availability_by_district_week(self, district_id: str, date: str = today()):
        url = f"{Constants.availability_by_district_week}?district_id={district_id}&date={date}"
        return self._call_api(url)

    def get_availability_by_pincode(self, pin_code: str, date: str = today()):
        url = f"{Constants.availability_by_pincode}?pincode={pin_code}&date={date}"
        return self._call_api(url)
    
    def get_availability_by_pincode_week(self, pin_code: str, date: str = today()):
        url = f"{Constants.availability_by_pincode_week}?pincode={pin_code}&date={date}"
        return self._call_api(url)
    
    def download_certificate(self, beneficiary_reference_id: str):
        url = f"{Constants.download_cert}?beneficiary_reference_id={beneficiary_reference_id}"
        return self._call_api(url)