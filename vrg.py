"""

Brandon Dunbar
Variant Report Generator
GUI file

"""

from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import WidgetException

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
# Modules:
from os import path, startfile
from configparser import ConfigParser
# My files:
import group_mngr
from gene import Gene
import generate_pdf
from logger import log

config = ConfigParser()


# Stylized Widgets: ----------------------------------------------------------*

class CustomTextInput(TextInput):
    """Stylized TextInput to minimize boilerplate code."""

    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)

        self.background_active = ''
        self.background_normal = ''
        self.background_color = (.9, .9, .9, 1)


class CustomButton(Button):

    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)

        self.background_normal = ''
        self.background_color = (.9, .9, .9, 1)
        self.color = (0, .1, .25, .75)


class GlobalData:
    """
    Variables that need to be accessed globally, stored in a class to avoid
    naming conflicts.
    """

    def __init__(self):

        self.settings = self.load_settings()

        self.dna_dir = config['Default Directories']['dna dir']
        self.output_dir = config['Default Directories']['Output Dir']

        self.active_group = ''
        self.active_gene = ''

        self.groups = group_mngr.load_groups()

    def save_settings(self, settings):
        """
        Saves user settings.

        :param settings:
            The config file.
        """

        with open('PersistentData/settings.ini', 'w') as config_file:
            settings.write(config_file)

    def load_settings(self):
        """
        Loads user settings from config file.
        Failing that, creates one.

        :returns:
            settings: The config file
        """

        # Create a settings file if there isn't one
        if not path.isfile('PersistentData/settings.ini'):
            self.initialize_config()

        # Store it
        config.read('PersistentData/settings.ini')
        settings = config

        return settings

    def initialize_config(self):
        """
        Initializes the user settings.ini
        """

        # Config file set up
        config['Default Directories'] = {'DNA Dir': '',
                                         'Output Dir': ''}

        # Save config file
        self.save_settings(config)


class HomeButton(ButtonBehavior, Image):
    """An image that switches back to home (menu) screen."""

    def __init__(self, **kwargs):
        super(HomeButton, self).__init__(**kwargs)

        self.source = 'PersistentData/eg.jpg'
        self.size_hint = (1, .25)

    def on_press(self):

        global_data.active_gene = ''
        global_data.active_group = ''
        sm.current = 'menu'


class AlphaNumTextInput(CustomTextInput):
    """A TextInput object that only accepts alphanumeric characters."""

    def __init__(self, **kwargs):
        super(AlphaNumTextInput, self).__init__(**kwargs)

        self.input_filter = self.alphanum_filter

    def alphanum_filter(self, *args):
        """
        Returns character (string) if it is alphanumeric.

        :args[0]:
        Character to input

        :args[1]:
        If character is a result of undo
        """

        if len(args) > 0:
            if args[0].isalnum():
                return args[0]

            else:
                return ''


# Screens: -------------------------------------------------------------------*

class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        # Container
        menu = BoxLayout(orientation="vertical",
                         padding=[1])

        # *Empowered Logo------------------------------------------------------
        self.logo = HomeButton()
        menu.add_widget(self.logo)

        # *Main Menu Title-----------------------------------------------------
        menu.add_widget(Label(text='Main Menu',
                              size_hint=(1, .1),
                              color=(0, .1, .25, .75)))

        # *Edit Groups---------------------------------------------------------
        group_btn = CustomButton(text='Edit Groups',
                                 size_hint=(1, .25),
                                 id='group')
        group_btn.bind(on_press=self.switch_screen)
        menu.add_widget(group_btn)

        menu.add_widget(Label(text='',
                              size_hint=(1, .01)))  # Add some blank space

        # *Generate Report-----------------------------------------------------
        generate_btn = CustomButton(text='Generate Report',
                                    size_hint=(1, .25),
                                    id='setup')
        generate_btn.bind(on_press=self.switch_screen)
        menu.add_widget(generate_btn)

        # Pack
        self.add_widget(menu)

    def switch_screen(self, *args):
        """Switches to the screen specified in the button's id field"""
        sm.current = args[0].id


class GroupScreen(Screen):

    def __init__(self, **kwargs):
        super(GroupScreen, self).__init__(**kwargs)

        # Hold the widgets in a container
        screen_container = BoxLayout(orientation='vertical',
                                     padding=[1])

        # *Empowered Logo------------------------------------------------------
        self.logo = HomeButton()
        screen_container.add_widget(self.logo)

        # *Group Selection Title-----------------------------------------------
        screen_container.add_widget(Label(text='Group Selection',
                                          size_hint=(1, .1),
                                          color=(0, .1, .25, .75)))

        # *Dropdown Menu-------------------------------------------------------
        self.dropdown = DropDown()
        self.dropdown.bind(on_select=self.set_active_group)

        # On load, no group is active.
        global_data.active_group = ''
        # Store the drop down buttons for easy manipulation
        self.current_groups = {}

        #       Populate when top button hit
        self.mainbutton = CustomButton(text='Select a group',
                                       size_hint=(1, .2))

        # Populate drop down on select
        self.mainbutton.bind(on_release=self.load_groups)
        self.dropdown.bind(on_select=lambda instance, x:
                           setattr(self.mainbutton, 'text', x))
        # Place on screen
        screen_container.add_widget(self.mainbutton)

        # *Group Actions Title-------------------------------------------------
        # Declarations
        self.button_container = BoxLayout(orientation='horizontal')

        #       Edit Button
        self.edit_btn = CustomButton(text="Edit",
                                     size_hint=(.3, .3))
        self.edit_btn.bind(on_press=self.switch_screen)

        #       New Button
        self.new_btn = CustomButton(text="New",
                                    size_hint=(.3, .3))
        self.new_btn.bind(on_press=self.switch_screen)

        #       Delete Button
        self.delete_btn = CustomButton(text="Delete",
                                       size_hint=(.3, .3))
        self.delete_btn.bind(on_press=self.delete)

        # Put buttons in container
        self.button_container.add_widget(self.edit_btn)
        self.button_container.add_widget(self.new_btn)
        self.button_container.add_widget(self.delete_btn)

        # Add container to screen container
        screen_container.add_widget(self.button_container)
        # Package screen container
        self.add_widget(screen_container)
        # Make sure drop down menu gets reset
        self.bind(on_enter=self.reset_menu)

    def set_active_group(self, *args):
        # args = (<DropDown obj>, 'Methylation Pathway')
        # Storing which group is selected for use in gene screen and deletion
        global_data.active_group = args[1]

    def switch_screen(self, *args):
        # Switch screens
        if args[0].text == "Edit" and global_data.active_group != '':
            sm.current = 'gene'
        elif args[0].text == "New":
            sm.current = 'newgroup'

    def delete(self, *args):

        def delete_group(*args):

            # Get the selected group
            active_group = global_data.active_group

            # Delete it from the group dictionary
            del global_data.groups[active_group]

            log(f"Group {active_group} deleted.")

            # Overwrite the existing groups with the modified group dictionary
            group_mngr.save_groups(global_data.groups)

            # Clear the selected group
            global_data.active_group = ''
            # Remove it from the drop down menu
            self.dropdown.remove_widget(self.current_groups[active_group])
            # Set drop down menu to default
            self.dropdown.select('Select a group')

            popup.dismiss()

        # If a group is selected and delete button hit, confirm deletion
        if global_data.active_group != '':

            # *Confirmation Popup----------------------------------------------
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=
                                     f"Delete {global_data.active_group}?"))

            # *Popup buttons---------------------------------------------------
            options = BoxLayout(orientation='horizontal', spacing=2)

            confirm_btn = CustomButton(text="Delete",  # Confirm delete button
                                       size_hint=(.3, .3))

            cancel_btn = CustomButton(text="Cancel",  # Cancel delete button
                                      size_hint=(.3, .3))
            options.add_widget(confirm_btn)
            options.add_widget(cancel_btn)
            content.add_widget(options)

            # *Popup Attributes------------------------------------------------
            popup = Popup(title="Delete?", content=content,
                          size_hint=(None, None), size=(400, 400),
                          separator_color=[1., 1., 1., 1.])

            confirm_btn.bind(on_press=delete_group)
            cancel_btn.bind(on_press=popup.dismiss)

            popup.open()

    def load_groups(self, *args):

        self.dropdown.clear_widgets()  # Clear any packaged buttons
        self.current_groups = {}  # Clear drop down button list

        groups = global_data.groups

        for group in groups:  # Iterating through groups and adding a button
            btn = CustomButton(text=group,  # Create button
                               size_hint_y=None,
                               height=44)
            btn.bind(on_release=lambda button:
            self.dropdown.select(button.text))  # Bind drop down functionality
            self.current_groups[group] = btn
            self.dropdown.add_widget(btn)  # Put in drop down menu

        self.dropdown.open(args[0])  # Called on clicking the default button

    def reset_menu(self, *args):
        # Need to make sure the menu text is defaulted when screen is entered
        self.dropdown.select('Select a group')
        global_data.active_group = ''
        global_data.active_gene = ''


class NewGroupScreen(Screen):

    def __init__(self, **kwargs):
        super(NewGroupScreen, self).__init__(**kwargs)
        # Widget Container
        screen_container = BoxLayout(orientation='vertical',
                                     padding=[1])

        # *Logo----------------------------------------------------------------
        self.logo = HomeButton()
        screen_container.add_widget(self.logo)

        # *New Group Title-----------------------------------------------------
        screen_container.add_widget(Label(text='New Group',
                                          size_hint=(1, .1),
                                          color=(0, .1, .25, .75)))

        #   Blank Buffer to maintain widget scale
        screen_container.add_widget(Label(text="",
                                          size_hint=(1, .3)))

        # *Group Name Input----------------------------------------------------
        self.name_ti = CustomTextInput(hint_text='Name of group...',
                                       multiline=False,
                                       size_hint=(1, .1),
                                       on_text_validate=self.create)
        screen_container.add_widget(self.name_ti)

        #   Buffer
        screen_container.add_widget(Label(text="",
                                          size_hint=(1, .6)))

        # *Create button-------------------------------------------------------
        self.create_btn = CustomButton(text='Create',
                                       size_hint=(1, .2))
        screen_container.add_widget(self.create_btn)
        self.create_btn.bind(on_press=self.create)

        # Pack
        self.add_widget(screen_container)

    def create(self, *args):
        group_name = self.name_ti.text  # Get the group name

        if group_name not in global_data.groups.keys() and \
                group_name.strip() != '':
            self.name_ti.text = ''  # Clear input
            global_data.active_group = group_name  # Set group name as active
            global_data.groups[group_name] = []  # Add new group to group dict
            group_mngr.save_groups(global_data.groups)  # Save group dictionary
            log(f"Group {group_name} created.")
            sm.current = 'editgene'  # Switch screens

        else:

            # Popup Widget Container
            popup_container = BoxLayout(orientation="vertical",
                                        spacing=75,
                                        size_hint_y=.75)

            # Warning label
            if group_name.strip() != '':
                warning = 'Group name taken! Group not created.'

            else:
                warning = 'Group field empty!'
            popup_container.add_widget(Label(text=warning))

            # Dismiss Button
            dismiss_btn = Button(text='Dismiss')
            popup_container.add_widget(dismiss_btn)

            # Popup Widget
            popup = Popup(title='Warning!',
                          content=popup_container,
                          size_hint=(None, None), size=(400, 400))

            # Bind button
            dismiss_btn.bind(on_release=lambda button: popup.dismiss())

            # Open popup
            popup.open()

    def switch_screen(self, *args):
        if args[0].text == "Create" and global_data.active_group != '':
            sm.current = 'editgene'


class GeneScreen(Screen):

    def __init__(self, **kwargs):
        super(GeneScreen, self).__init__(**kwargs)

        # Widget Container
        screen_container = BoxLayout(orientation='vertical',
                                     padding=[1])

        # *Logo----------------------------------------------------------------
        self.logo = HomeButton()
        screen_container.add_widget(self.logo)

        # *Gene Selection Title------------------------------------------------
        screen_container.add_widget(Label(text='Gene Selection',
                                          size_hint=(1, .1),
                                          color=(0, .1, .25, .75)))

        # *Drop Down Menu------------------------------------------------------
        self.dropdown = DropDown()
        self.dropdown.bind(on_select=self.set_gene)
        self.dd_btns = []  # A list of drop down buttons for easy deletion

        #       Populate when top button hit
        self.mainbutton = CustomButton(text='Select a gene',
                                       size_hint=(1, .2))
        self.mainbutton.bind(on_release=self.load_genes)  # Populate dropdown
        self.dropdown.bind(on_select=lambda instance, x:
                           setattr(self.mainbutton, 'text', x))
        #       Place on screen
        screen_container.add_widget(self.mainbutton)

        # *Gene Buttons--------------------------------------------------------
        #       Declarations
        self.button_holder = BoxLayout(orientation='horizontal')

        #       Edit Button
        self.edit_btn = CustomButton(text="Edit",
                                     size_hint=(.3, .3))
        self.edit_btn.bind(on_release=self.switch_screen)

        #       New Button
        self.new_btn = CustomButton(text="New",
                                    size_hint=(.3, .3))
        self.new_btn.bind(on_release=self.switch_screen)

        #       Delete Button
        self.delete_btn = CustomButton(text="Delete",
                                       size_hint=(.3, .3))
        self.delete_btn.bind(on_release=self.delete)

        #       Placement
        self.button_holder.add_widget(self.edit_btn)
        self.button_holder.add_widget(self.new_btn)
        self.button_holder.add_widget(self.delete_btn)
        screen_container.add_widget(self.button_holder)  # Place Container
        #       Pack all widgets
        self.add_widget(screen_container)

        # Reset drop down when screen is loaded
        self.bind(on_enter=self.reset_menu)

    def load_genes(self, *args):
        """Called when drop down is opened"""

        self.dropdown.clear_widgets()  # Clear any packaged buttons
        del self.dd_btns[:]  # Clear drop down button list

        # Grab relevant genes
        genes = global_data.groups[global_data.active_group]

        for gene in genes:
            btn = CustomButton(text=gene.name,
                               size_hint_y=None,
                               height=self.height/9)

            btn.bind(on_release=lambda button:
                     self.dropdown.select(button.text))
            self.dropdown.add_widget(btn)  # Add button to menu
            self.dd_btns.append(btn)  # Store button in delety-list

        self.dropdown.open(args[0])

    def set_gene(self, *args):
        # Storing which group is selected for use in gene screen
        global_data.active_gene = args[1]  # args[1] - Name of gene

    def delete(self, *args):

        def delete_gene():
            group = global_data.active_group  # Get active group
            gene = global_data.active_gene  # Get active gene

            # Iterate through genes because we need to check the name of each
            for index, _gene in enumerate(global_data.groups[group]):

                if _gene.name == gene:

                    # Delete the gene
                    del global_data.groups[group][index]
                    # Remove from drop down
                    self.dropdown.remove_widget(self.dd_btns[index])
                    log(f"Gene {gene} deleted.")
                    break

            group_mngr.save_groups(global_data.groups)  # Save the groups

            global_data.active_gene = ''  # No active gene
            self.dropdown.select('Select a gene')

            popup.dismiss()

        if global_data.active_gene != '':

            # *Deletion Confirmation-------------------------------------------
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text=f"Delete "
                                     f"{global_data.active_gene}?"))

            # *Confirmation Buttons--------------------------------------------
            options = BoxLayout(orientation='horizontal',
                                spacing=2)

            confirm_btn = CustomButton(text="Delete",  # Confirm button
                                       size_hint=(.3, .3))

            cancel_btn = CustomButton(text="Cancel",  # Cancel button
                                      size_hint=(.3, .3))
            #       Add Widgets to container
            options.add_widget(confirm_btn)
            options.add_widget(cancel_btn)
            content.add_widget(options)

            # *Popup Settings--------------------------------------------------
            popup = Popup(title="Delete?",
                          content=content,
                          size_hint=(None, None),
                          size=(400, 400),
                          separator_color=[1., 1., 1., 1.])

            confirm_btn.bind(on_press=delete_gene)
            cancel_btn.bind(on_press=popup.dismiss)

            popup.open()

    def switch_screen(*args):

        if args[1].text == "New":
            sm.current = 'editgene'

        elif args[1].text == "Edit":
            if global_data.active_gene != '':
                sm.current = 'editgene'

    def reset_menu(self, *args):
        # Need to make sure the menu text is defaulted when screen is entered
        self.dropdown.select('Select a gene')
        global_data.active_gene = ''


class EditGeneScreen(Screen):

    def __init__(self, **kwargs):
        super(EditGeneScreen, self).__init__(**kwargs)
        # *Widget Container
        screen_container = BoxLayout(orientation="vertical",
                                     padding=[1])

        # *Logo----------------------------------------------------------------
        self.logo = HomeButton()
        screen_container.add_widget(self.logo)

        # *New Gene Title------------------------------------------------------
        screen_container.add_widget(Label(text='New Gene',
                                          size_hint=(1, .1),
                                          color=(0, .1, .25, .75)))

        # *Form Container------------------------------------------------------
        form = GridLayout(cols=2, spacing=[0, 2], padding=[2])

        #       Display the entry fields
        attributes = ["Gene: ",
                      "RS#: ",
                      "23&me Wild: ",
                      "23&me Var: ",
                      "AncestryDNA Wild: ",
                      "AncestryDNA Var: ",
                      "Red Notes: ",
                      "Yellow Notes: ",
                      "Green Notes: "]
        self.entries = []  # List of entry boxes for easy grabbing

        for attribute in attributes:
            label = Label(text=attribute,
                          color=(0, .1, .25, .75),
                          size_hint=(.4, 1))

            entry = CustomTextInput(multiline=False,
                                    on_text_validate=self.save,  # Enter = save
                                    write_tab=False  # Allows switching via tab
                                    )

            # Put in form
            form.add_widget(label)
            form.add_widget(entry)
            # Add to list of entries
            self.entries.append(entry)

        screen_container.add_widget(form)  # Add form to screen container

        # *Save button
        save_btn = CustomButton(text="Save",
                                size_hint=(1, .3))
        save_btn.bind(on_press=self.save)

        # *Placement-----------------------------------------------------------
        screen_container.add_widget(save_btn)  # Add Save button to screen
        self.add_widget(screen_container)  # Pack screen
        self.bind(on_enter=self.load)

    def save(self, *args):

        attributes = []  # A list of the attributes that make up the gene

        # Iterating through entries twice, I don't want to clear some,
        # find an empty entry and then user has fill in the cleared ones again

        any_empty = False
        for entry in self.entries:  # Check for any empty entries

            if entry.text.strip() == '':
                any_empty = True

        if not any_empty:

            for entry in self.entries:  # Build the list
                attributes.append(entry.text)
                entry.text = ''  # Clear the entries

            # Shorten active group and gene references
            active_group = global_data.active_group
            active_gene = global_data.active_gene

            if active_gene:

                for index, _gene in enumerate(
                        global_data.groups[active_group]):

                    if _gene.name == active_gene:  # Gene object found

                        gene_obj = global_data.groups[active_group][index]
                        gene_obj.set_attributes(attributes)

                        log(f"Gene {active_gene} updated.")

                        break

            else:

                new_gene = Gene(attributes)  # Create new gene object

                # Add it to the group
                global_data.groups[global_data.active_group].append(new_gene)
                group_mngr.save_groups(global_data.groups)  # Save group
                log(f"Gene {new_gene.name} saved.")

            sm.current = 'gene'  # Switch to gene selection

        else:

            # Popup Widget Container
            popup_container = BoxLayout(orientation="vertical",
                                        spacing=75,
                                        size_hint_y=.75)

            # Warning label
            popup_container.add_widget(Label(text='Empty entry fields! '
                                                  'Gene not created.'))

            # Dismiss Button
            dismiss_btn = Button(text='Dismiss')
            popup_container.add_widget(dismiss_btn)

            # Popup Widget
            popup = Popup(title='Warning!',
                          content=popup_container,
                          size_hint=(None, None),
                          size=(400, 400))

            # Bind button
            dismiss_btn.bind(on_release=lambda button: popup.dismiss())

            # Open popup
            popup.open()

    def switch_screen(self, *args):
        if args[1].text == "Save":
            sm.current = 'gene'

    def load(self, *args):

        # Shorten active group and gene references
        active_group = global_data.active_group
        active_gene = global_data.active_gene

        if active_gene:  # True if this is an edit

            for index, _gene in enumerate(global_data.groups[active_group]):

                if _gene.name == active_gene:  # Gene object found

                    gene_obj = global_data.groups[active_group][index]
                    attributes = gene_obj.get_attributes()

                    for i, entry in enumerate(self.entries):

                        entry.text = attributes[i]

                    break


class SetupScreen(Screen):

    def __init__(self, **kwargs):
        super(SetupScreen, self).__init__(**kwargs)

        # *Widget Container
        self.screen_container = BoxLayout(orientation='vertical', padding=[1])

        # *Logo---------------------------------------------------------------*
        self.logo = HomeButton()
        self.screen_container.add_widget(self.logo)

        # *Set Up Title-------------------------------------------------------*
        self.screen_container.add_widget(Label(text='Report Set Up',
                                               size_hint=(1, .1),
                                               color=(0, .1, .25, .75)))

        # *Content Container--------------------------------------------------*
        self.form = BoxLayout(orientation="vertical",
                              spacing=2)

        # *DNA Container------------------------------------------------------*
        self.anc_container = BoxLayout(orientation="horizontal")
        #       Definitions----------------------------------------------------
        dna_lbl = Label(text="DNA File Path:",
                        color=(0, .1, .25, .75),
                        size_hint=(.5, 1))

        dna_browse = CustomButton(text="Browse",
                                  size_hint=(.3, 1))
        self.dna_path_lbl = Label(text='',
                                  size_hint=(1, 1),
                                  color=[0, 0, 0, 1],
                                  id='DNA')

        self.dna_path = ''  # Create a path attribute

        dna_browse.bind(on_release=lambda x:
                        self.choose_file(self.dna_path_lbl, self.dna_path))

        #       Placement------------------------------------------------------
        self.anc_container.add_widget(dna_lbl)
        self.anc_container.add_widget(dna_browse)
        self.anc_container.add_widget(self.dna_path_lbl)
        #           Add box to layout
        self.form.add_widget(self.anc_container)

        # *Output-------------------------------------------------------------*
        self.output_container = BoxLayout(orientation="horizontal")
        #       Definitions
        output_lbl = Label(text="Output Folder:",
                           color=(0, .1, .25, .75),
                           size_hint=(.5, 1))

        output_browse = CustomButton(text="Browse",
                                     size_hint=(.3, 1))

        self.output_path_lbl = Label(text='',
                                     size_hint=(1, 1),
                                     color=[0, 0, 0, 1],
                                     id='Output Folder')

        self.output_path = ''

        output_browse.bind(on_release=lambda x: self.choose_file(
            self.output_path_lbl, self.output_path, x))
        #       Placement------------------------------------------------------
        self.output_container.add_widget(output_lbl)
        self.output_container.add_widget(output_browse)
        self.output_container.add_widget(self.output_path_lbl)
        #           Add box to layout
        self.form.add_widget(self.output_container)

        # *File Name----------------------------------------------------------*
        self.filename = AlphaNumTextInput(hint_text="Name of report...",
                                          multiline=False,
                                          write_tab=False,
                                          size_hint_y=.35,)
        self.form.add_widget(self.filename)

        # *Header-------------------------------------------------------------*
        self.header = CustomTextInput(hint_text="Insert document header...",
                                      multiline=True)

        self.form.add_widget(self.header)

        # Loading window
        self.loading_bar = ProgressBar(max=100)
        self.loading_popup = Popup(title='Generating...',
                                   content=self.loading_bar,
                                   size_hint=(1, .25))

        # *Generate Button----------------------------------------------------*
        self.generate_btn = CustomButton(text="Generate and Open Report")

        self.generate_btn.bind(on_press=self.loading_popup.open)
        self.generate_btn.bind(on_release=self.generate_report)

        self.form.add_widget(self.generate_btn)

        # *Placement----------------------------------------------------------*
        self.screen_container.add_widget(self.form)  # Add form to screen
        self.add_widget(self.screen_container)  # Pack screen

        # *Browse-------------------------------------------------------------*
        self.active = self.dna_path_lbl  # The label to store path from browse

        #       Declarations
        self.container = BoxLayout(orientation='vertical')  # Browse container
        self.file_chooser = FileChooserListView()
        self.choose_btn = Button(text='Choose', size_hint=(1, .2))

        #       Browse window
        self.browse = Popup(title='Browse',
                            content=self.container,
                            size_hint=(.9, .9))

    def open(self, _path, filename):
        # *File selection-----------------------------------------------------*
        if len(filename) > 0:

            if len(filename[0]) > 30:  # If the file name is too long
                # Only show the last 30 characters
                self.active.text = "..." + filename[0][-30:]

            else:
                self.active.text = filename[0]

            self.dna_path = filename[0]  # Store the path

            active_dir = ''
            for directory in filename[0].split("\\")[:-1]:
                active_dir += directory + "\\"

            config['Default Directories']['DNA Dir'] = active_dir
            global_data.save_settings(config)

        # *Folder selection---------------------------------------------------*
        elif len(filename) == 0:
            if len(_path) > 30:  # If path too long to display
                self.active.text = "..." + _path[-30:]
            else:
                self.active.text = _path

            self.output_path = _path  # Store output directory path

            config['Default Directories']['Output Dir'] = _path
            global_data.save_settings(config)

        self.browse.dismiss()

    def choose_file(self, *args):

        self.active = args[0]  # Store the button pressed

        if len(args) > 2:  # If output button is pressed

            # Browse directories
            self.file_chooser = FileChooserListView(filters=[self.is_dir])

            # Check for default directory
            default_dir = config['Default Directories']['Output Dir']
            if default_dir != '':
                self.file_chooser.path = default_dir

        else:  # If DNA path is selected
            # Browse txt files
            self.file_chooser = FileChooserListView(filters=['*.txt',
                                                             self.is_dir])
            # Check for default directory
            default_dir = config['Default Directories']['DNA Dir']
            if default_dir != '':
                self.file_chooser.path = default_dir

        self.container.clear_widgets()

        # Bind Choose Button to Open method
        self.choose_btn.bind(on_release=lambda x:
                             self.open(self.file_chooser.path,
                                       self.file_chooser.selection))

        try:  # Exception thrown if browse is clicked twice
            self.container.add_widget(self.file_chooser)
            self.container.add_widget(self.choose_btn)

        except WidgetException:
            pass

        self.browse.title = args[0].id
        self.browse.open()

    def is_dir(self, directory, filename):
        return path.isdir(path.join(directory, filename))

    def generate_report(self, *args):
        """
        Generates the report in PDF format using pre-made groups and given
        DNA txt file.

        Args:
            0 = Button object automatically passed.
        """

        # self.loading_popup.open()

        try:

            doc = generate_pdf.generate(self.dna_path,
                                        self.header.text,
                                        self.filename.text,
                                        self.output_path,
                                        self.loading_bar)

            log(f"Report '{self.filename.text}' created in {self.output_path} "
                f"from {self.dna_path}.")

            self.loading_bar.value = 100
            startfile(doc, 'open')
            self.loading_popup.dismiss()

            # Clear form
            self.dna_path_lbl.text = ''
            self.output_path_lbl.text = ''
            self.filename.text = ''
            self.header.text = ''

            # Switch screens
            sm.current = 'menu'

        except ValueError as error:  # Called when invalid file is given

            log(error)

            warning_label = Label(text='File is not recognized as AncestryDNA'
                                       ' or 23&Me file!')

            warning = Popup(title='Error!',
                            content=warning_label,
                            size_hint=(1, .25))
            self.loading_popup.dismiss()
            warning.open()


global_data = GlobalData()

# Create the screen manager
sm = ScreenManager(transition=NoTransition())
screens = [MenuScreen(name='menu'),
           GroupScreen(name='group'),
           GeneScreen(name='gene'),
           EditGeneScreen(name='editgene'),
           NewGroupScreen(name='newgroup'),
           SetupScreen(name='setup')]

for screen in screens:
    sm.add_widget(screen)


class GeneratorApp(App):

    def build(self):
        self.icon = 'PersistentData/eg.ico'
        self.title = 'Variant Report Generator'
        Window.clearcolor = (1, 1, 1, 1)  # I want a white window bg
        Window.size = (500, 550)  # Set window size
        return sm  # Return screen manager, runs app


if __name__ == '__main__':
    GeneratorApp().run()
