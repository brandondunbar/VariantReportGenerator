"""

Brandon Dunbar
Group Manager
Saves/Loads user defined groups

"""

import _pickle as pickle
import os


def _make_paths():
    """
    Creates the required directory and pickle file if they don't exist.
    """

    # Create PersistentData directory if it doesn't exist
    if not os.path.isdir('PersistentData'):
        os.makedirs('PersistentData')

    # Create pickle file if it doesn't exist
    if not os.path.exists('PersistentData/serial_groups.pickle'):

        with open('PersistentData/serial_groups.pickle', 'wb') as pickle_out:
            pickle.dump({}, pickle_out)


def load_groups():
    """
    Deserializes the group dictionary object

    :return:
    Group dictionary object
    """

    with open('PersistentData/serial_groups.pickle', "rb") as file_object:
        groups = pickle.load(file_object)
        return groups


def save_groups(groups):
    """
    Takes in a group dictionary in the format:
    {'Group Name': [['Gene Name', 'RS#', '23 Wild', '23 Var', 'Anc Wild',
                     'Anc Var', 'Red', 'Yellow', 'Green'], ], }
    :param groups:
    The groups dictionary to be saved
    """

    # Serialize
    file_name = "PersistentData/serial_groups.pickle"
    with open(file_name, "wb") as file_object:
        pickle.dump(groups, file_object)


_make_paths()
