"""

Brandon Dunbar
File Parser
Extract and sort data from DNA files

"""


def _pull(path):
    """
    pull()
    :param path:
    Path of the file to be returned
    :return:
    A generator object of the file, returning lists
    """

    with open(path, "r") as file:

        for line in file:

            if not line.startswith("#"):

                yield [i.strip() for i in line.split("\t")]


def parse(groups, dna_path, service):
    """
    Sorts through the provided gene text files and returns the relevant
    genes

    :param groups:
    The dictionary of groups and their gene objects
    :param dna_path:
    The path to the DNA txt file
    :param service:
    23&Me or AncestryDNA
    :return:
    A list of shared SNPs
    """

    # Get the genes from the group file----------------------------------------
    needed_genes = [gene.rs_id for group in groups.values() for gene in group]

    if needed_genes:  # If there are any genes to search for-------------------

        # Dictionaries from files in the format:
        # {rs#: [chromosome, position, allele1, allele2], ...}

        if service == "AncestryDNA":
            genes = {_gene[0]: _gene[1:]
                     for _gene in _pull(dna_path)
                     if _gene[0] in needed_genes}

            return genes

        elif service == "23&Me":
            # 23&me has the last two alleles together with no space separating
            # them, we need to work around this.
            genes = {_gene[0]: _gene[1:-1] + [_gene[-1][0], _gene[-1][1]]
                     for _gene in _pull(dna_path)
                     if _gene[0] in needed_genes}

            return genes

    else:
        return {}

