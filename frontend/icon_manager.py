from enum import Enum


class IconID(str, Enum):
    CHART_PIPE = "chart-pipe"
    MONEY_DOLLAR = "money-dollar"
    CHART_AVERAGE = "chart-average"

    TROPHY = "trophy"
    REPEAT = "repeat"
    LENS_SEARCH = "lens-search"
    TIME = "time"
    USER_PAYING = "user-paying"
    GENDERS = "genders"
    CART = "cart"
    CAKE = "cake"


class Icons:
    BASE_PATH = "/assets/icons/"
    DEFAULT_EXTENSION = ".svg"

    @staticmethod
    def get_icon(icon_id: IconID) -> str:
        """
        Generates the file path for an icon based on its identifier.

        This static method constructs a file path by joining the base path,
        the value of the icon identifier, and the default file extension for icons.

        :param icon_id: The identifier of the icon.
        :type icon_id: IconID
        :return: The full file path for the specified icon.
        :rtype: str
        """
        return f"{Icons.BASE_PATH}{icon_id.value}{Icons.DEFAULT_EXTENSION}"
