class UrTSex:
    Male = 0
    Female = 1

class UrTGear:
    # Side arms/pistols
    Beretta = "beretta"
    Desert_Eagle = "desert_eagle"
    Glock = "glock"
    Colt = "colt"
    Magnum = "magnum"

    # Shotguns
    SPAS = "spas"
    Benelli = "benelli"

    # Submachine guns
    MAC11 = "mac11"
    MP5K = "mp5k"
    UMP45 = "ump45"


    # Rifles & Machine guns
    G36 = "g36"
    AK103 = "ak103"
    LR300 = "lr300"
    PSG = "psg"
    FRF1 = "frf1"
    SR8 = "sr8"
    Negev = "negev"
    M4A1 = "m4a1"
    P90 = "p90"

    # Miscellaneous
    HK69 = "hk69"
    HE = "he"
    Smoke = "smoke"
    Kevlar = "kevlar"
    Helmet = "helmet"
    Silencer = "silencer"
    Laser = "laser"
    Medkit = "medkit"
    NVG = "night_vision"
    Ammo = "extra_ammo"
    Null = "null/empty" # empty


# https://urbanterror.fandom.com/wiki/Gear_Codes
gear_codes = {
    "A": UrTGear.Null,
    
    # Side arms/pistols
    "F": UrTGear.Beretta,
    "G": UrTGear.Desert_Eagle,
    "f": UrTGear.Glock,
    "g": UrTGear.Colt,
    "l": UrTGear.Magnum,

    # Rifles & Machine guns
    "M": UrTGear.G36,
    "a": UrTGear.AK103,
    "L": UrTGear.LR300,
    "N": UrTGear.PSG,
    "Z": UrTGear.SR8,
    "c": UrTGear.Negev,
    "e": UrTGear.M4A1,
    "i": UrTGear.FRF1,
    "k": UrTGear.P90,

    # Shotguns
    "H": UrTGear.SPAS,
    "j": UrTGear.Benelli,

    # Submachine guns
    "I": UrTGear.MP5K,
    "h": UrTGear.MAC11,
    "J": UrTGear.UMP45,

    # Miscellaneous
    "K": UrTGear.HK69,
    "O": UrTGear.HE,
    "Q": UrTGear.Smoke,
    "R": UrTGear.Kevlar,
    "W": UrTGear.Helmet,
    "U": UrTGear.Silencer,
    "V": UrTGear.Laser,
    "T": UrTGear.Medkit,
    "S": UrTGear.NVG,
    "X": UrTGear.Ammo
}

class UrTPlayer:
    def __init__(self, name, sex, gear):
        self.name = name
        self.sex = sex
        self.gear = [gear_codes[x] for x in gear]

        self.kills = 0
        self.deaths = 0

class UrTGameModes:
    LastManStanding = 1
    FreeForAll = 2
    TeamDeathMatch = 3
    TeamSurvivor = 4
    FollowTheLeader = 5
    CaptureAndHold = 6
    CaptureTheFlag = 7
    BombAndDefuse = 8
    JumpMode = 9
    FreezeTag = 10
    GunGame = 11


class UrTParser:
    "Parses the Quake3 log format."

    def __init__(self, log_location = None, max_players = 16):
        self.log_location = log_location
        self.players = [None] * max_players # Every player connected, with their characteristics.
        self.usernames = [None] * max_players # Usernames oly
        
        self.server = {} # Server information

        self.on_newmap = None
        self.on_newround = None


    def parse_quakestring(self, string):
        """Parses the \\key1\\value1\\key2\\value2 ... format used by Quake 3 Arena"""
        returned = {}

        tokens = string.split("\\")[1:]

        for i in range(0, len(tokens), 2):
            try:
                returned[tokens[i]] = tokens[i + 1]
            except IndexError:
                break

        return returned

    
    def parse_line(self, line):
        
        # Server information or new round?
        if ("InitGame" in line):
            # Clear scores or whatever

            online_players = []

            for player in self.players:
                if (player != None):
                    online_players.append(player)

            # If enabled, call this callback when a new round occurs (for archival purposes).
            if (self.on_newround != None):
                self.on_newround(self, online_players)


            for player in online_players:
                player.kills = 0
                player.deaths = 0

            data = self.parse_quakestring(line.split("InitGame:")[1].lstrip())

            # If enabled, call this callback when the map changes.
            if (self.on_newmap != None):
                try:
                    if (data["mapname"] != self.server["mapname"]):
                        self.on_newmap(self, data["mapname"])
                except KeyError:
                    self.on_newmap(self, data["mapname"])

            self.server = data

        # Player information
        elif ("ClientUserinfo:" in line):
            afterwards = line.split("ClientUserinfo: ")[1]

            index = int(afterwards.split("\\")[0].rstrip())
            info = self.parse_quakestring(line.lstrip(str(index)).lstrip())

            self.players[index] = UrTPlayer(info["name"], UrTSex.Female if info["sex"] == "female" 
                else UrTSex.Male, [] if "gear" not in info else info["gear"])
                                  # ^^^^^^ 'gear' is not always guaranteed.
            
            self.usernames[index] = info["name"]

        
        elif ("Kill:" in line and "MOD_CHANGE_TEAM" not in line):
                
            
            afterwards = line.split("Kill: ")[1]
            
            killer = int(afterwards.split(" ")[0])
            victim = int(afterwards.split(" ")[1])

            self.players[killer].kills += 1
            self.players[victim].deaths += 1


        # Player disconnected
        elif ("ClientDisconnect:" in line):
            index = int(line.split("ClientDisconnect: ")[1])
            self.players[index] = None
            self.usernames[index] = None

            



