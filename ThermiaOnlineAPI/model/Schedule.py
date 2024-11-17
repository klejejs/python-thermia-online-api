from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ThermiaOnlineAPI.const import DATETIME_FORMAT

@dataclass
class Schedule:
    """
    A class used to represent a Schedule for a Heat Pump.

    Attributes
    ----------
    isRunning : bool
        Indicates if the schedule is currently running.
        Only available for schedules fetched from the API.
    isFaulty : bool
        Indicates if there is a fault in the schedule.
        Only available for schedules fetched from the API.
    id : int
        Unique identifier for the schedule.
        Only available for schedules fetched from the API.
    installationId : int
        Identifier for the installation associated with the schedule.
    functionId : int
        Identifier for the function associated with the schedule.
        functionID refers to CAL_FUNCTION_XXX constants in const.py
    start : datetime
        The start time of the schedule.
    end : datetime
        The end time of the schedule.
    recurringType : int
        Type of recurrence for the schedule (e.g., daily, weekly).
    recurringOccurrence : int
        Occurrence of the recurrence (e.g., every 2 days).
    value : Optional[float]
        The value associated with the schedule (e.g., temperature setpoint for CAL_FUNCTION_REDUCED_HEATING_EFFECT).
    isPaused : bool
        Indicates if the schedule is currently paused.
        Only available for schedules fetched from the API.
    """
    isRunning: Optional[bool]
    isFaulty: Optional[bool]
    id: Optional[int]
    installationId: int
    functionId: int
    start: datetime
    end: datetime
    recurringType: int
    recurringOccurrence: int
    value: Optional[float]
    isPaused: Optional[bool]
    
    def __init__(self, 
                 functionId: int,
                 start: datetime, 
                 end: datetime, 
                 installationId: int = 0, 
                 isRunning: Optional[bool] = None, 
                 isFaulty: Optional[bool] = None, 
                 id: Optional[int] = None, 
                 recurringType: int = 0, 
                 recurringOccurrence: int = 1, 
                 value: Optional[float] = None, 
                 isPaused: Optional[bool] = None):
        self.isRunning = isRunning
        self.isFaulty = isFaulty
        self.id = id
        self.installationId = installationId
        self.functionId = functionId
        self.start = start
        self.end = end
        self.recurringType = recurringType
        self.recurringOccurrence = recurringOccurrence
        self.value = value
        self.isPaused = isPaused

    def toJSON(self):
        """
        Convert the Schedule object to a JSON-serializable dictionary.

        Returns:
        dict: A dictionary representation of the Schedule object.
        """
        json_dict = {
            "installationId": self.installationId,
            "functionId": self.functionId,
            "start": self.start.strftime(DATETIME_FORMAT) if self.start else None,
            "end": self.end.strftime(DATETIME_FORMAT) if self.end else None,
            "recurringType": self.recurringType,
            "recurringOccurrence": self.recurringOccurrence,
        }
        if self.isRunning is not None:
            json_dict["isRunning"] = self.isRunning
        if self.isFaulty is not None:
            json_dict["isFaulty"] = self.isFaulty
        if self.id is not None:
            json_dict["id"] = self.id
        if self.value is not None:
            json_dict["value"] = self.value
        if self.isPaused is not None:
            json_dict["isPaused"] = self.isPaused
        return json_dict
    
    @staticmethod
    def fromJSON(data: dict):
        """
        Create a Schedule object from a JSON-serializable dictionary.

        Args:
            data (dict): A dictionary representation of the Schedule object.

        Returns:
            Schedule: A Schedule object created from the dictionary.
        """
        return Schedule(
            isRunning=data.get("isRunning"),
            isFaulty=data.get("isFaulty"),
            id=data.get("id"),
            installationId=data["installationId"],
            functionId=data["functionId"],
            start=datetime.strptime(data["start"], DATETIME_FORMAT) if data.get("start") else None,
            end=datetime.strptime(data["end"], DATETIME_FORMAT) if data.get("end") else None,
            recurringType=data["recurringType"],
            recurringOccurrence=data["recurringOccurrence"],
            value=data.get("value"),
            isPaused=data.get("isPaused"),
        )
