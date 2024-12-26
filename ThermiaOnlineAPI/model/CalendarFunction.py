from dataclasses import dataclass


@dataclass
class CalendarFunction:
    __id: int
    __name: str
    __recurringEnabled: bool
    __canBePaused: bool
    __hasFunctionBasedValue: bool
    __isTemperatureOverriden: bool
    __properties_type: str
    __properties_value: str

    def __init__(self, id: int, name: str, recurringEnabled: bool, canBePaused: bool, hasFunctionBasedValue: bool, isTemperatureOverriden: bool, properties_type:str, properties_value:str):
        """
        Initialize a CalendarFunction instance.

        Args:
            id (int): The unique identifier for the calendar function.
            name (str): The name of the calendar function.
            recurringEnabled (bool): Indicates if the function is recurring.
            canBePaused (bool): Indicates if the function can be paused.
            hasFunctionBasedValue (bool): Indicates if the function has a value based on its function.
            isTemperatureOverriden (bool): Indicates if the temperature is overridden.
            properties_type (str): The type of the properties associated with the calendar function.
            properties_value (str): The value of the properties associated with the calendar function.
        """
        self.__id = id
        self.__name = name
        self.__recurringEnabled = recurringEnabled
        self.__canBePaused = canBePaused
        self.__hasFunctionBasedValue = hasFunctionBasedValue
        self.__isTemperatureOverriden = isTemperatureOverriden
        self.__properties_type = properties_type
        self.__properties_value = properties_value

    @property
    def id(self) -> int:
        """Get the unique identifier for the calendar function."""
        return self.__id

    @property
    def name(self) -> str:
        """Get the name of the calendar function."""
        return self.__name

    @property
    def recurringEnabled(self) -> bool:
        """Check if the function is recurring."""
        return self.__recurringEnabled

    @property
    def canBePaused(self) -> bool:
        """Check if the function can be paused."""
        return self.__canBePaused

    @property
    def hasFunctionBasedValue(self) -> bool:
        """Check if the function has a value based on its function."""
        return self.__hasFunctionBasedValue

    @property
    def isTemperatureOverriden(self) -> bool:
        """Check if the temperature is overridden."""
        return self.__isTemperatureOverriden

    @property
    def properties_type(self) -> str:
        """Get the type of the properties associated with the calendar function."""
        return self.__properties_type

    @property
    def properties_value(self) -> str:
        """Get the value of the properties associated with the calendar function."""
        return self.__properties_value

   
    @staticmethod
    def fromJSON(data: dict):
        """
        Create a CalendarFunction instance from a JSON dictionary.

        Args:
            data (dict): A dictionary containing the CalendarFunction data.

        Returns:
            CalendarFunction: An instance of CalendarFunction created from the provided data.
        """
        return CalendarFunction(
            id=data['id'],
            name=data['name'],
            recurringEnabled=data['recurringEnabled'],
            canBePaused=data['canBePaused'],
            hasFunctionBasedValue=data['hasFunctionBasedValue'],
            isTemperatureOverriden=data['isTemperatureOverriden'],
            properties_type=data['properties']['type'],
            properties_value=data['properties']['value']
        )