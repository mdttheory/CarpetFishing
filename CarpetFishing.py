##################################################################
#  Written by Mark Wittekind
##################################################################
import sys
import random
import math
#import itertools
from PyQt4 import QtGui,QtCore

## To install PyQt4:
## http://www.riverbankcomputing.com/software/pyqt/download

#TODO:
## Display lock timer
## Put caught fish in inventory
## Report the number of fish in inventory on main screen? Value of fish inventory, even?
## Check for PEP 8; Flake 8 Lint
## Find random items when fishing
## Use gaussian distribution for fish spawns centered on player level
## Vary catch probability
## Finish boat stats
## Buy/sell price modifiers
## Clean up repetition in Player class
## Item classes
## Procedurally fill store with items list
## Create purchase/sell classes
## Re-write with pygame?  Timers jacked...
## Better water images (can use gifs and other animations in pygame)
## Allow expandable water subgrid

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Player(QtCore.QObject):    
    ## Player state signals ##
    xp_changed = QtCore.pyqtSignal(int)
    xp_to_next_level_changed = QtCore.pyqtSignal(int)
    level_changed = QtCore.pyqtSignal(int)
    
    def __init__(self, level=1, cash=0, xp=0):
        """
        Initialize object of type Player.
        """
        super(Player, self).__init__()
        self.cash = cash 
        self.inventory = []
        self._xp = xp 
        self.level = level
        self._recalculate_xp()
        
    def _recalculate_xp(self):
        """
        Figure new xp after xp gain.
        """
        self.xp_to_next_level = 25*(self.level**self.level)/math.factorial(self.level)**1.3
        self.xp_to_next_level_changed.emit(self.xp_to_next_level)  # Send signal to GUI
        
    def _level_up(self):
        """
        Set new Player level.
        """
        if self.level==20: #Limit to level 20
            pass
        else:
            self.level += 1
            self.level_changed.emit(self.level)  # Send current level signal to GUI
            self._recalculate_xp()

    def catch_chance(self):
        """
        Chance to catch fish on encounter.
        """
        modifier = 1
        for item in self.inventory:  # Look for catch_chance modifiers in inventory
            modifier *= item.catch_chance_modifier
        self.catch_chance = (15+.25*self.level)*4.75*modifier/100
    
    @property
    def spawn_modifier(self):
        """
        Modify rate of spawn.
        """
        modifier = 1
        for item in self.inventory:
            modifier *= item.spawn_modifier
        return modifier
    
    @property
    def xp_modifier(self):
        """
        Modify xp per catch.
        """
        modifier = 1
        for item in self.inventory:
            modifier *= item.xp_modifier
        return modifier

    @property
    def buy_price_modifier(self):
        """
        Modify item purchase prices.
        """
        modifier = 1
        for item in self.inventory:
            modifier *= item.xp_modifier
        return modifier
        
    @property
    def xp(self):
        """
        Get player xp.
        """
        return self._xp
    
    @xp.setter
    def xp(self, xp):
        """
        Set player xp.
        """
        #if xp < self._xp:
            #raise ValueError("Can't subtract XP!")
            
        xp_modifier = 1
        for item in self.inventory: # Add up xp
            xp_modifier *= item.xp_modifier
        
        xp += (xp - self._xp) * xp_modifier
        self._xp = xp
        
        while self._xp > self.xp_to_next_level:
            self._xp -= self.xp_to_next_level
            self._level_up()
            
        self.xp_changed.emit(self._xp)  # Send xp signal to GUI

class Item(object):
    def __init__(self, name="", description="", 
            price=0, xp_modifier=1.0, spawn_modifier=1.0, level_modifier=1.0,
            sell_price_modifier=1.0, buy_price_modifier=1.0, required_level=0,
            maximum=0,catch_chance_modifier=1.0):
        """
        Initilialize object of type Item.
        """                
        self.name = name
        self.description = description
        self.price = int(price)
        self.xp_modifier = float(xp_modifier)
        self.spawn_modifier = float(spawn_modifier)
        self.level_modifier = float(level_modifier)
        self.sell_price_modifier = float(sell_price_modifier)
        self.buy_price_modifier = float(buy_price_modifier)
        self.required_level = int(required_level)
        self.maximum = int(maximum)
        self.catch_chance_modifier = float(catch_chance_modifier)

    def __str__(self):
        return "{name}: {description}".format(name=self.name, description=self.description)

class Fish(Item):
    pass

class Pole(Item):
    pass


class Boat(Item):
    pass


class Lure(Item):
    pass


class NotEnoughMoney(Exception):
    pass


class NotEnoughXP(Exception):
    pass

class Store(QtGui.QWidget):
    def __init__(self):
        """
        Initialize object of type Store
        """
        super(Store, self).__init__()

        items = [
            Pole("Beginner's Pole", "A pole for beginners.", price=10, spawn_modifier=1, required_level=0), 
            Pole("Journeyman's Pole", "A better pole than before.", price=50, spawn_modifier=1.1, required_level=2),
            Pole("Sturdy Pole", "This won't break easily, and because it isn't bright orange the fish aren't easily scared off!", price=125, spawn_modifier=1.2, required_level=4),
            Pole("Great Pole", "Wow, this pole is great!", price=250, spawn_modifier=1.5,required_level=7),
            Pole("Amazing Pole", "Who keeps making these?", price=750, spawn_modifier=2, required_level=10),
            Pole("Master Pole", "This was crafted by a monk who spent 8 years on it, though he did maintain various side projects", price=2000, spawn_modifier=2.75, required_level=13),
            Pole("North Pole", "How are you even fishing with that?!", price=10000, spawn_modifier=5, required_level=16), #rofl
            Pole("Polished Polish Pole", "There's that thing about Polish pole-making industries...", price=20000, spawn_modifier=10, required_level=20),
            Pole("Debug Pole", "Huge spawn rate modifier for testing", spawn_modifier=1000, price=0, required_level=0),
            Boat("Old Boat", "This thing may have once been a boat, but it is now primarily duct tape.", price=10, spawn_modifier=1, required_level=0),
            Boat("Used Boat", "This thing is loud as heck, but it doesn't scare off the fishies as much as before.", price=50, spawn_modifier=1.2, required_level=2),
            Boat("Speed Boat", "This thing is fast as the wind, but unfortunately there's only a light breeze.", price=125, spawn_modifier=1.4, required_level=4),
            Boat("Pontoon Boat", "This is probably what you should have been driving all along."),
            Boat("Sail Boat", "We'll take the rhumb line."),
            Boat("Trawler", "Catch ALL the things!"),
            Boat("Japanese Destroyer", "For some reason, the manual contains pictures of anime girls.", price=20000, spawn_modifier=6, required_level=10)
                ]
        # Define the tab structure
        store_tab_widget = QtGui.QTabWidget()
        pole_tab = QtGui.QWidget()
        boat_tab = QtGui.QWidget()
        sell_tab = QtGui.QWidget()
        tab_layout = QtGui.QVBoxLayout()
        store_tab_widget.addTab(pole_tab, "Poles")
        store_tab_widget.addTab(boat_tab, "Boats")
        store_tab_widget.addTab(sell_tab, "Sell")
        # Put the tabs in the container
        mainLayout = QtGui.QVBoxLayout(self)
        mainLayout.addWidget(store_tab_widget)
        self.setLayout(mainLayout)
        # Add lists to the tab
        poles_list = QtGui.QListWidget
        boats_list = QtGui.QListWidget()
        inventory_list = QtGui.QListWidget()
        # Add buttons to the tabs TODO
        
 

    def item_price(self, player, item):
        """
        Updates and item's price based on player modifiers.
        """
        return item.price * player.buy_price_modifier
        
    def buy(self, player, item):
        """
        Take money from Player and add selected item to Inventory.
        """
        price = self.item_price(player, item)
        
        if self.player.cash < price:
            raise NotEnoughMoney()
        
        if self.player.level < item.required_level:
            raise NotEnoughXP()
        
        player.cash -= price
        player.inventory.add(item)
        
    def sell(self, player, item):
        pass
        
    
class Main_GUI(QtGui.QWidget):
    
    def __init__(self):
        """
        Initialize object of type Main_GUI
        """
        super(Main_GUI, self).__init__()

        self.player = Player()

        self.move_lock_timer = QtCore.QTimer()
        self.move_lock_timer.setSingleShot(True)  # Lock user from moving for time
       
        self.initUI()  # Initialize the GUI
        
        # Create instance of fish_Spawn_Timer
        self.fish_Spawn_Timer = QtCore.QTimer()
        self.fish_Spawn_Timer.timeout.connect(self.spawn_fish)
        self.fish_Spawn_Timer.start(100)

        # Different items you can catch
        self.fish_dict={
            0:[Fish("Grandpa's boots", price=1)], 
            1:[Fish("Bluegill", price=2),Fish("Pumpkinseed", price=2)],
            2:[Fish("Yellow Perch", price=2)],
            3:[Fish("Golden Shiner", price=3),Fish("Flathead Minnow", price=3)],
            4:[Fish("Creek Chub", price=3)],
            5:[Fish("Gizzard Shad", price=5),Fish("Redbreasted Sunfish", price=5),Fish("Green Sunfish", price=5)],
            6:[Fish("Greenside Darter", price=5),Fish("Striped Shiner", price=5)],
            7:[Fish("Black Crappie", price=10),Fish("Largemouth Bass", price=10),Fish("Hybrid Striped Bass", price=10),Fish("Fender American Standard Bass", price=10), Fish("White Perch", price=10)],
            8:[Fish("Brown Bullhead Catfish", price=15),Fish("American Channel Catfish", price=15)],
            9:[Fish("American Eel", price=15)],
            10:[Fish("Yellow Bullhead Catfish", price=50),Fish("Common Carp", price=30)],
            11:[Fish("Walleye", price=50)],
            12:[Fish("Brown Trout", price=80),Fish("Rainbow Trout", price=100),Fish("Cutthroat Trout", price=55)],
            13:[Fish("Lake Trout", price=50),Fish("Kokanee Salmon", price=100)],
            14:[Fish("Grouper", price=160)],
            15:[Fish("Tuna", price=200)],
            16:[Fish("Nurse Shark", price=1000)],
            17:[Fish("Hammerhead Shark", price=2000)],
            18:[Fish("Marlin", price=3000)],
            19:[Fish("Great White Shark", price=18000),Fish("Finding Nemo: Final Boss", price=100)],
            20:[Fish("Blue Whale", price=20000)]}
            
        self.selected_tile = (-1, -1) # Avoid AttributeErrors
        
    def initUI(self):
        """
        'Initialize' the GUI object for Main_GUI
        """
        # Define the pieces
        experience_label = QtGui.QLabel("Experience:", self)
        #level_label = QtGui.QLabel("Level:", self)
        experience_bar = QtGui.QProgressBar()
        recent_fish_tag = QtGui.QLabel("Recent Catch: ")
        self.recent_fish_label = QtGui.QLabel("")

        # Update experience bar when we gain xp
        self.player.xp_changed.connect(experience_bar.setValue)
        
        experience_bar.setMaximum(self.player.xp_to_next_level)
        self.player.xp_to_next_level_changed.connect(experience_bar.setMaximum)
        
        level_output = QtGui.QLabel("Level: 1/20", self) # Default starting/max
        self.player.level_changed.connect(lambda x: level_output.setText("Level: "+str(x)+"/20"))  # Update level

        directions_button = QtGui.QPushButton("Instructions", self)
        directions_button.setFixedSize(100, 23)
        #PyQt4.QtCore.Qt.Alignment
        directions_button.clicked.connect(self.directions_clicked)

        store_button = QtGui.QPushButton("Store", self)
        store_button.clicked.connect(self.store_clicked)

        # Debug values
        self.move_lock_time = 10000
        self._fish_ttl = 5000
        self.fish_ttl_stddev = 2500
        self.fish_spawn_chance = 1.8

        # Create the main grid
        grid = QtGui.QGridLayout()
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(30)
        
        # Place the pieces
        grid.addWidget(experience_label, 1, 0)
        grid.addWidget(experience_bar, 1, 1)
        #grid.addWidget(level_label, 2, 0)
        grid.addWidget(level_output, 2, 0)
        grid.addWidget(store_button, 3, 0)
        grid.addWidget(directions_button, 2, 1)
        grid.addWidget(recent_fish_tag, 4, 0)
        grid.addWidget(self.recent_fish_label, 4, 1)
        
        # Create the water subgrid
        self.subgrid = QtGui.QGridLayout()
        self.subgrid.setSpacing(1)
        grid.addLayout(self.subgrid, 5, 0, 1, 2)  # row, column, rowspan, colspan

        water = QtGui.QIcon(QtGui.QPixmap(_fromUtf8("water.png")))
        water_selected = QtGui.QIcon(QtGui.QPixmap(_fromUtf8("water 2.png")))
        fish_in_square = QtGui.QIcon(QtGui.QPixmap(_fromUtf8("fishies.png")))
        fish_in_square_selected = QtGui.QIcon(QtGui.QPixmap(_fromUtf8("fishies active.png")))
        
        for grid_x in range(4):
            for grid_y in range(4):
                button = QPushButtonImageChange("", self, grid_x, grid_y, 
                    water, water_selected, fish_in_square, fish_in_square_selected)
                button.tile_selected.connect(self.select_tile)
                self.subgrid.addWidget(button, grid_x, grid_y)
                
                self.move_lock_timer.timeout.connect(lambda button=button: button.setEnabled(True))

        # Let there be light!
        self.setLayout(grid)
        self.setFixedSize(300, 300)
        self.setWindowTitle("Cubicle Fishing")    
        self.show()

    def directions_clicked(self):
        """
        Direction button action -> open Directions window
        """
        self.directions_window=Directions()
        self.directions_window.setGeometry(300, 300, 265, 200)
        self.directions_window.setWindowTitle("Directions")   
        self.directions_window.show()

    def store_clicked(self):
        """
        Store button action -> open Store window
        """
        self.store_window=Store()
        self.store_window.setGeometry(300, 300, 265, 200)
        self.store_window.setWindowTitle("Mark's Fishing Emporium")   
        self.store_window.show()

    def spawn_fish(self):
        """
        Spawns fish into the water subgrid.
        """
        chance = self.player.spawn_modifier * random.gauss(1, .4)  # Gauss distribution for spawn time
        if chance >= self.fish_spawn_chance: # Random grid
            rand_x = random.randrange(0, 4)
            rand_y = random.randrange(0, 4)
            ttl = abs(random.gauss(self._fish_ttl, self.fish_ttl_stddev))
            self.subgrid.itemAtPosition(rand_x, rand_y).widget().put_fish_in_tile(ttl)
        self.check_fish()
    
    def check_fish(self):
        """
        Finds fish in player's current grid if available and updates Player and GUI
        """
        selected_tile = self.subgrid.itemAtPosition(*self.selected_tile)
        if selected_tile and selected_tile.widget().fish_in_tile:
            possible_fish = []
            for level in range(1, self.player.level + 1):
                for fish in self.fish_dict[level]:
                    possible_fish.extend(fish for _ in range(int((20 - level) ** 1.5)))
            
            caught_fish=random.choice(possible_fish)
            self.player.inventory.append(caught_fish)
            #print(str(caught_fish)[:-2])
            
            self.player.xp += 10
            selected_tile.widget().remove_fish()
            display_fish=str(str(caught_fish) + " $" + str(caught_fish.price) + ".00")
            self.recent_fish_label.setText(display_fish)
        

    def select_tile(self, x, y):
        """
        User selects water subgrid tile, we check for first, lock user in
        """
        self.selected_tile = (x, y)
        self.check_fish()
        for grid_x in range(4):
            for grid_y in range(4):
                self.subgrid.itemAtPosition(grid_x, grid_y).widget().setEnabled(False)
        self.move_lock_timer.start(self.move_lock_time)

class Directions(QtGui.QWidget):
    def __init__(self):
        """
        Initialize object of type Directions
        """
        super(Directions, self).__init__()
        self.directions_browser = QtGui.QTextBrowser(self)
        dir_str="""Select a plot of water to being fishing.
You will continue fishing as long as you are on that plot.
Feel free to move, but remember... once you select a plot you are locked into that plot for a certain amount of time.

Watch out for schools of fish in other tiles.
You might be able to catch them if you get there before they move on.

You gain experience for every fish you catch.
Having a higher level allows you to catch better fish.
The fish type and the associated value are displayed each time you catch something.
In later versions you will be able to sell your fish to a store for money.
Mark's Fishing Emporium is empty for now, sorry!
        """
        self.directions_browser.append(dir_str)

class QPushButtonImageChange(QtGui.QPushButton):
    """ 
    Override QPushButton's click() function
    """
    tile_selected = QtCore.pyqtSignal(int, int) 
    
    def __init__(self, text, parent=None, x=None, y=None, image=None, image_clicked=None, image_fish=None, image_fish_clicked=None):
        """
        Initialize object of type QPushButtonImageChange
        """
        super(QPushButtonImageChange, self).__init__(text, parent)
        self.x = x
        self.y = y
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setFlat(True)
        self.image = image
        self.image_clicked = image_clicked
        self.image_fish = image_fish
        self.image_fish_clicked = image_fish_clicked
        self.setIcon(self.image)  
        self.setIconSize(QtCore.QSize(80,74))
        self.toggled.connect(self.do_toggled)
        self.fish_in_tile = False
        self.fishRemovalTimer = QtCore.QTimer()
        self.fishRemovalTimer.setSingleShot(True)
        self.fishRemovalTimer.timeout.connect(self.remove_fish)
        self._fish_ttl = 5000
        
    def do_toggled(self, checked):
        """
        Changes images based on user action and fish presence
        """
        if checked:
            if self.fish_in_tile:
                self.setIcon(self.image_fish_clicked)
            else:
                self.setIcon(self.image_clicked)
            self.tile_selected.emit(self.x, self.y)
        else:
            if self.fish_in_tile:
                self.setIcon(self.image_fish)
            else:
                self.setIcon(self.image)

    def put_fish_in_tile(self, time_to_live):
        """
        Places fish into a tile and starts fish life timer for removal
        """
        if self.isChecked(): 
            self.setIcon(self.image_fish_clicked)
        else:
            self.setIcon(self.image_fish)
        self.fish_in_tile = True
        self.fishRemovalTimer.start(time_to_live)
        
    def remove_fish(self):
        """
        Removes fish from tile and updates image
        """
        self.fish_in_tile = False
        if self.isChecked():
            self.setIcon(self.image_clicked)
        else:
            self.setIcon(self.image)
                
    @property
    def position(self):
        """
        Position getter
        """
        return self.x, self.y

    @position.setter
    def position(self, x, y):
        """
        Position setter
        """
        if not self.parent.itemAtPosition(x, y) is self:
            raise ValueError("The coordinates provided do not match the parent.")
        self.x = x
        self.y = y  

def main():

    app = QtGui.QApplication(sys.argv)
    GUI = Main_GUI()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
