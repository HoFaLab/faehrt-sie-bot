from dataclasses import dataclass
import datetime as dt

@dataclass
class DepartureInfo():
    station: str
    destination: str
    datetime: str
    delay: str  = "0" # e.g "5"
    cancelled: bool  = False
    matching_argentina_dep = None

    @property
    def effective_dep_time(self) -> dt.datetime:
        return dt.datetime.strptime(self.datetime, "%H:%M").replace(
            day=dt.datetime.now().day,
            month=dt.datetime.now().month,
            year=dt.datetime.now().year
        )    
    
    @property
    def effective_dep_time_str(self) -> dt.datetime:
        return self.effective_dep_time.strftime('%H:%M')  
    
    @property
    def effective_delay_min(self) -> int:
        return (self.effective_dep_time - self.schedule_departure_time).total_seconds() / 60
    
    @property
    def schedule_departure_time(self) -> dt.datetime:
        return self.effective_dep_time - dt.timedelta(minutes=int(self.delay))
    
    @property
    def schedule_departure_time_str(self) -> str:
        return self.schedule_departure_time.strftime("%H:%M")

    