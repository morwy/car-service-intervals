#!/usr/bin/python

# --------------------------------------------------------------------------------------------------
#
# Imports.
#
# --------------------------------------------------------------------------------------------------
import json
import os
from dataclasses import dataclass, field

from dacite import from_dict


# --------------------------------------------------------------------------------------------------
#
# Global variables.
#
# --------------------------------------------------------------------------------------------------
@dataclass
class MaintenanceItem:
    interval_km: int = 0
    description: str = ""


@dataclass
class KilometrageActions:
    kilometrage: int = 0
    actions: list[str] = field(default_factory=list)


@dataclass
class KilometrageInstruction:
    kilometrage_items: list[KilometrageActions] = field(default_factory=list)

    def create_checkbox_list(self) -> str:
        checkbox_list = ""

        for kilometrage_item in self.kilometrage_items:
            checkbox_list += (
                str(kilometrage_item.kilometrage).rjust(7)
                + " :\t[ ]\t"
                + kilometrage_item.actions[0]
                + "\n"
            )

            if len(kilometrage_item.actions) > 1:
                for action in kilometrage_item.actions[1:]:
                    checkbox_list += "\t\t\t[ ]\t" + action + "\n"

        return checkbox_list

    def save(self, filepath: str) -> None:
        checkbox_list = self.create_checkbox_list()
        with open(file=filepath, mode="w", encoding="utf-8") as file:
            file.write(checkbox_list)


# --------------------------------------------------------------------------------------------------
#
# Class definition.
#
# --------------------------------------------------------------------------------------------------
class KilometrageInstructionBuilder:

    def __init__(self, filepath: str) -> None:
        self.__filepath = filepath
        self.__maintenance_items = self.__read_maintenance_items_from_file(
            filepath=filepath
        )

    def __read_maintenance_items_from_file(self, filepath: str) -> list:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: '{filepath}'.")

        with open(file=filepath, mode="r", encoding="utf-8") as file:
            json_data = json.load(file)

        maintenance_items = []
        for item in json_data:
            maintenance_item = from_dict(data_class=MaintenanceItem, data=item)
            maintenance_items.append(maintenance_item)

        maintenance_items.sort(
            key=lambda maintenance_item: maintenance_item.interval_km
        )

        return maintenance_items

    def build(
        self, min_kilometrage=0, max_kilometrage=300000, kilometrage_step=1000
    ) -> KilometrageInstruction:
        instruction: KilometrageInstruction = KilometrageInstruction()

        for kilometrage in range(min_kilometrage, max_kilometrage, kilometrage_step):
            if kilometrage == 0:
                continue

            kilometrage_actions: KilometrageActions = KilometrageActions(
                kilometrage=kilometrage
            )

            for maintenance_item in self.__maintenance_items:
                if kilometrage % maintenance_item.interval_km == 0:
                    kilometrage_actions.actions.append(maintenance_item.description)

            if len(kilometrage_actions.actions) > 0:
                instruction.kilometrage_items.append(kilometrage_actions)

        return instruction


# --------------------------------------------------------------------------------------------------
#
# Entry point.
#
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    manual_filepath = os.path.join(os.getcwd(), "example.json")
    instruction_builder = KilometrageInstructionBuilder(filepath=manual_filepath)
    instruction = instruction_builder.build()
    kilometrage_instruction_filepath = os.path.join(os.getcwd(), "example.txt")
    instruction.save(filepath=kilometrage_instruction_filepath)
