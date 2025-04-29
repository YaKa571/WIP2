from dash import callback, Output, Input, MATCH, State

from components.component_factory import DATASETS


class DataTableCallbacks:

    # A single pattern-match callback for _all_ create_data_table tables
    @staticmethod
    @callback(
        Output({"type": "data-table", "index": MATCH}, "data"),
        Input({"type": "data-table", "index": MATCH}, "page_current"),
        Input({"type": "data-table", "index": MATCH}, "page_size"),
        State({"type": "data-table", "index": MATCH}, "id")
    )
    def update_table(page_current: int, page_size: int, uid: dict) -> list[dict]:
        """
        Updates and returns a portion of a data table based on the current page,
        page size, and unique table identifier (uid). This function fetches
        a specific slice of the dataset corresponding to the given parameters.

        :param page_current: The current page index of the data table.
        :type page_current: int
        :param page_size: The number of rows displayed per page in the data table.
        :type page_size: int
        :param uid: A dictionary representing a unique identifier for the data table.
                     It contains metadata such as the index of the dataset.
        :type uid: dict
        :return: A list of dictionaries containing the selected rows of the dataset.
        :rtype: list[dict]
        """
        df = DATASETS[uid["index"]]
        start = page_current * page_size
        end = start + page_size
        return df.iloc[start:end].to_dict("records")
