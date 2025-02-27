from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ThermiaOnlineAPI.const import DATETIME_FORMAT


@dataclass
class CalendarSchedule:
    """
    CalendarSchedule class represents a schedule with various attributes such as start time, end time, recurrence, and status indicators.

    Methods:
        __init__(self, functionId: int, start: datetime, end: datetime, installationId: int = 0, isRunning: Optional[bool] = None, isFaulty: Optional[bool] = None, id: Optional[int] = None, recurringType: int = 0, recurringOccurrence: int = 1, value: Optional[float] = None, isPaused: Optional[bool] = None):
            Initializes a CalendarSchedule object with the provided attributes.
        toJSON(self) -> dict:
        fromJSON(data: dict) -> CalendarSchedule:
    """

    __isRunning: Optional[bool]
    __isFaulty: Optional[bool]
    __id: Optional[int]
    __installationId: int
    __functionId: int
    __start: datetime
    __end: datetime
    __recurringType: int
    __recurringOccurrence: int
    __value: Optional[float]
    __isPaused: Optional[bool]

    def __init__(
        self,
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
        isPaused: Optional[bool] = None,
    ):
        """
        Initialize a Schedule object.

        Args:
            functionId (int): The ID of the function.
            start (datetime): The start time of the schedule.
            end (datetime): The end time of the schedule.
            installationId (int, optional): The ID of the installation. Defaults to 0.
            isRunning (Optional[bool], optional): Indicates if the schedule is currently running. Defaults to None.
            isFaulty (Optional[bool], optional): Indicates if the schedule is faulty. Defaults to None.
            id (Optional[int], optional): The ID of the schedule. Defaults to None.
            recurringType (int, optional): The type of recurrence. Defaults to 0.
            recurringOccurrence (int, optional): The occurrence of the recurrence. Defaults to 1.
            value (Optional[float], optional): The value associated with the schedule. Defaults to None.
            isPaused (Optional[bool], optional): Indicates if the schedule is paused. Defaults to None.
        """
        self.__isRunning = isRunning
        self.__isFaulty = isFaulty
        self.__id = id
        self.__installationId = installationId
        self.__functionId = functionId
        self.__start = start
        self.__end = end
        self.__recurringType = recurringType
        self.__recurringOccurrence = recurringOccurrence
        self.__value = value
        self.__isPaused = isPaused

    @property
    def isRunning(self) -> Optional[bool]:
        """
        Indicates if the schedule is currently running.
        Only available for schedules fetched from the API.
        """
        return self.__isRunning

    @property
    def isFaulty(self) -> Optional[bool]:
        """
        Indicates if there is a fault in the schedule.
        Only available for schedules fetched from the API.
        """
        return self.__isFaulty

    @property
    def id(self) -> Optional[int]:
        """
        Unique identifier for the schedule.
        Only available for schedules fetched from the API.
        """
        return self.__id

    @property
    def installationId(self) -> int:
        """
        Identifier for the installation associated with the schedule.
        """
        return self.__installationId

    @property
    def functionId(self) -> int:
        """
        Identifier for the function associated with the schedule.
        functionID refers to CAL_FUNCTION_XXX constants in const.py
        """
        return self.__functionId

    @property
    def start(self) -> datetime:
        """
        The start time of the schedule.
        """
        return self.__start

    @property
    def end(self) -> datetime:
        """
        The end time of the schedule.
        """
        return self.__end

    @property
    def recurringType(self) -> int:
        """
        Type of recurrence for the schedule (e.g., daily, weekly).
        """
        return self.__recurringType

    @property
    def recurringOccurrence(self) -> int:
        """
        Occurrence of the recurrence (e.g., every 2 days).
        """
        return self.__recurringOccurrence

    @property
    def value(self) -> Optional[float]:
        """
        The value associated with the schedule (e.g., temperature setpoint for CAL_FUNCTION_REDUCED_HEATING_EFFECT).
        """
        return self.__value

    @property
    def isPaused(self) -> Optional[bool]:
        """
        Indicates if the schedule is currently paused.
        Only available for schedules fetched from the API.
        """
        return self.__isPaused

    def set_installationId(self, installationId: int):
        """
        Set the installation ID for the schedule.

        Args:
            installationId (int): The installation ID to set.
        """
        self.__installationId = installationId

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
        return CalendarSchedule(
            isRunning=data.get("isRunning"),
            isFaulty=data.get("isFaulty"),
            id=data.get("id"),
            installationId=data["installationId"],
            functionId=data["functionId"],
            start=(
                datetime.strptime(data["start"], DATETIME_FORMAT)
                if data.get("start")
                else None
            ),
            end=(
                datetime.strptime(data["end"], DATETIME_FORMAT)
                if data.get("end")
                else None
            ),
            recurringType=data["recurringType"],
            recurringOccurrence=data["recurringOccurrence"],
            value=data.get("value"),
            isPaused=data.get("isPaused"),
        )
