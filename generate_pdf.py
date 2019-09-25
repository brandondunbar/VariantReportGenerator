"""

Brandon Dunbar
PDF Creator
Takes data and creates a PDF report

"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, \
    TableStyle, Spacer, Flowable
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from datetime import datetime

import group_mngr
import file_parser


def _detect_service(dna_path):
    """
    Detects whether file is AncestryDNA or 23&me

    :param dna_path:
    Path to dna file

    :return:
    String specifying active service
    """

    with open(dna_path, 'r') as file:

        first_line = file.readline()

        if "AncestryDNA" in first_line:
            return 'AncestryDNA'

        elif "23andMe" in first_line:
            return '23&Me'

        else:
            raise ValueError("Invalid file!")


def _log_not_found(not_found):
    """
    Logs the RS ids not found to a text file

    :param not_found:
    A list of genes not found
    """

    with open("PersistentData/not_founds.txt", "a") as file:
        file.write(f"{datetime.now()}:\n")
        for gene in not_found:
            file.write(str(gene) + "\n")


def format_group(genes, service, pulled_genes):
    """
    Takes group dictionary and reformats it to be written to the pdf.

    :param genes:
    The group dictionary to be converted

    :param service:
    AncestryDNA or 23&me

    :param pulled_genes:
    The genes pulled from the DNA files

    :return:
    A tuple to be passed directly to reportlab's Table object and fill the data
    parameter
    """

    """
    groups will be a dictionary with group names as keys, and a list of gene 
    objects as values
    {'Group Name': [<geneObject>, <geneObject>],}
    
    Gene objects will have the attributes: 
    gene_name, rsid, trait_wild, trait_var, red_notes, yellow notes, green notes
    """

    formatted_group = []
    yellow = []
    red = []
    green = []
    not_found = []

    for index, gene in enumerate(genes):

        # Declare variables for readability------------------------------------
        try:
            pulled_gene = pulled_genes[gene.rs_id]
            chromosome = pulled_gene[0]
            position = pulled_gene[1]
            trait_one = pulled_gene[2]
            trait_two = pulled_gene[3]

        except KeyError:
            trait_one, trait_two = 'X', 'X'

        # Get the target service-----------------------------------------------
        if service == "23&me":
            wild = gene.tt_wild
            variant = gene.tt_var

        else:
            wild = gene.anc_wild
            variant = gene.anc_var

        styles = getSampleStyleSheet()
        trait_pair = f"{trait_one}/{trait_two}"

        # Check green, red, or yellow------------------------------------------

        # Not Found:
        if trait_one == 'X' and trait_two == 'X':

            trait_result = Paragraph("Not found", styles['BodyText'])
            not_found.append(gene.rs_id)

        # Green:
        elif trait_one.upper() == wild.upper() and \
                trait_two.upper() == wild.upper():

            # Create paragraph object
            trait_result = Paragraph(gene.green_notes, styles['BodyText'])

            # Add to list of green genes
            green.append((3, index+1))

        # Red
        elif trait_one.upper() == variant.upper() and \
                trait_two.upper() == variant.upper():

            # Create paragraph object
            trait_result = Paragraph(gene.red_notes, styles['BodyText'])

            # Add to list of red genes
            red.append((3, index+1))

        # Yellow
        else:

            # Create paragraph object
            trait_result = Paragraph(gene.yellow_notes, styles['BodyText'])

            # Add to list of yellow genes
            yellow.append((3, index+1))

        # Format it for recording----------------------------------------------
        formatted_gene = [gene.name,
                          gene.rs_id,
                          trait_pair,
                          trait_result]
        formatted_group.append(formatted_gene)

    notes = [red, yellow, green]

    if not_found:
        _log_not_found(not_found)

    return formatted_group, notes


def write_report(groups, pulled_genes, filename, out_path, service,
                 header):
    """
    Creates the pdf file

    :param groups:
    The user defined groups

    :param pulled_genes:
    Genes pulled from DNA file

    :param filename:
    Name of the report upon creation

    :param out_path:
    Where to create the PDF

    :param service:
    23&Me or AncestryDNA?

    :param header:
    The top level paragraph

    :return:
    Path of created file
    """

    # Set up
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(f"{out_path}/{filename}.pdf",
                            pagesize=letter,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=18)

    # Declarations
    elements = []
    title = "Empowered Genetics Variant Report"
    logo = "PersistentData/eg.jpg"

    elements.append(Image(logo, 1.5*inch, 1.5*inch))  # Add the logo
    elements.append(Paragraph(f"<font color=#5A8782>{title}</font>",
                              styles["h1"]))  # Add the title
    elements.append(Paragraph(header, styles["df"]))  # Add the header
    elements.append(Spacer(width=0, height=20))

    #   Add Groups
    for group, genes in groups.items():

        elements.append(MCLine(500))
        elements.append(Spacer(width=0, height=5))

        # Get the group as a tuple to be added to the document
        formatted_group, gene_notes = format_group(genes,
                                                   service,
                                                   pulled_genes)

        if len(formatted_group) < 1:
            continue

        # Add group name
        elements.append(Paragraph(f"<font color=#516170><i>{group}</i></font>",
                                  styles["h2"]))

        # Nested tuple for table: main tuple is table, inner tuples rows, each
        # item in its own column
        table_legend = [("Gene", "RS#", "Wild/Var", "Result",), ]
        group_data = tuple(table_legend + formatted_group)

        group_table = Table(data=group_data,
                            colWidths=(75, 60, 50, 275,),
                            rowHeights=20)

        # Highlight the cells accordingly
        for index, color in enumerate(gene_notes):
            for cell in color:
                if index == 0:
                    cell_color = colors.red
                elif index == 1:
                    cell_color = colors.yellow
                else:
                    cell_color = colors.green

                group_table.setStyle(TableStyle([('BACKGROUND', cell, cell,
                                                  cell_color),
                                                 ('TEXTCOLOR', cell, cell,
                                                  colors.black)]))

        elements.append(group_table)
        elements.append(Spacer(width=0, height=20))

    # Build the elements
    doc.build(elements)

    return f"{out_path}/report.pdf"


def generate(dna_path, header, filename, output_path, loading_bar):
    """
    Pulls together numerous functions to generate the pdf report

    :param dna_path:
    Path to the DNA file

    :param header:
    Paragraph at the top of the document

    :param filename:
    Name of the file to be created

    :param output_path:
    Destination for the report

    :return:
    The path to the generated report
    """

    # Get the predefined groups
    groups = group_mngr.load_groups()

    loading_bar.value = 10

    # Create variable to hold the active service, assigned below
    service = _detect_service(dna_path)  # Returns "AncestryDNA" or "23&Me"

    loading_bar.value = 20

    # Get the genes from the provided file
    pulled_genes = file_parser.parse(groups, dna_path, service)

    loading_bar.value += 50

    # Create the pdf with given info
    write_report(groups, pulled_genes, filename, output_path, service,
                 header=header)

    loading_bar.value = 75

    # Return the path the file was saved to
    file_path = output_path + f"/{filename}.pdf"

    return file_path


class MCLine(Flowable):
    """
    Line flowable --- draws a line in a flowable
    http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
    """

    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def __repr__(self):
        return "Line(w=%s)" % self.width

    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)

