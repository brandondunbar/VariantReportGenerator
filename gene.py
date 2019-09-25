"""

Brandon Dunbar
Gene Class
A script to hold the Gene class

"""


class Gene:
    def __init__(self, attributes):
        self.name = attributes[0]
        self.rs_id = attributes[1]
        self.tt_wild = attributes[2]
        self.tt_var = attributes[3]
        self.anc_wild = attributes[4]
        self.anc_var = attributes[5]
        self.red_notes = attributes[6]
        self.yellow_notes = attributes[7]
        self.green_notes = attributes[8]

    def __repr__(self):
        return self.rs_id

    def __str__(self):
        return self.rs_id

    def get_attributes(self):
        """
        Returns a list of gene attributes.

        :returns:
        attributes: A list of the class attributes
        """

        attributes = [self.name,
                      self.rs_id,
                      self.tt_wild,
                      self.tt_var,
                      self.anc_wild,
                      self.anc_var,
                      self.red_notes,
                      self.yellow_notes,
                      self.green_notes]

        return attributes

    def set_attributes(self, attributes):
        """
        Sets
        :param attributes:
        A list of values to set class attributes to.
        """

        self.name = attributes[0]
        self.rs_id = attributes[1]
        self.tt_wild = attributes[2]
        self.tt_var = attributes[3]
        self.anc_wild = attributes[4]
        self.anc_var = attributes[5]
        self.red_notes = attributes[6]
        self.yellow_notes = attributes[7]
        self.green_notes = attributes[8]
