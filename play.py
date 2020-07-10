import requests
import json
import yaml

# api-endpoint 
url = "https://api-v2.swissunihockey.ch"
season = "2020";

# API url
url_club_path = url+"/api/clubs"
url_club_teams = url+"/api/teams?mode=by_club&season="+season+"&club_id="
url_team_calendar = url+"/api/games?mode=team&season="+season+"&games_per_page=30&team_id="

clubs = {'sum': 45201, 'tiuh' : 435553}

aliases = {"SU Mendrisiotto" : "sum",
           "Ticino Unihockey": "tiuh",
           "Regazzi Verbano UH Gordola": "vuh",
           "UHC Lugano" : "luh",
           "UH Eagles Sementina" : "uhes",
           "Unihockey Collina d'Oro" : "uhcd",
           "SAM Massagno UH" : "sam",
           "Gambarognese UHC" : "guhc",
           "S.G. Concordia Giubiasco" : "cguh",
           "UHC Ascona" : "uhca",
           "Flippers-Tanachin S. Gottardo" : "flip",
           "UHT CSKA Lodrino" : "cska",
           "Blenio Stars Unihockey" : "blenio",
           "UH Vallemaggia Cavergno" : "maggia",
           }



class SUClient():

    def write_to_file(self, path, content):
        json_file = open(path,"w")
        json_file.write(content);
        json_file.close()


    def get_clubs_ids(self):
        r = requests.get(url = url_club_path, params = {}) 
        data_obj = json.loads(r.text)
        #print (data_obj)
        filtered_list = [x for x in data_obj['entries'] if x['text'] in aliases.keys()]
        mapping = {}
        for e in filtered_list:
            mapping[e['text']] = e['set_in_context']['club_id']
        return mapping

    def get_club_teams(self, club_id):
        r = requests.get(url = url_club_teams+str(club_id), params = {})
        data_obj = json.loads(r.text)
        mapping = {}
        for e in data_obj['entries']:
            mapping[e['text']] = e['set_in_context']['team_id']
        return mapping
    
    def generate_config(self):
        clubs_ids = self.get_clubs_ids()
        clubs_info = []
        for club, id in clubs_ids.items():
            club_info = {}
            club_info['name']  = club
            club_info['alias'] = aliases[club]
            club_info['id']    = id
            club_info['teams'] = self.get_club_teams(id)
            clubs_info.append(club_info)
        print(json.dumps(clubs_info, indent=2))
        write_to_file("conf/config.json", json.dumps(clubs_info, indent=2))

    def generate_team_calendar(self, team_id):
        r = requests.get(url = url_team_calendar+str(team_id), params = {})
        data_obj = json.loads(r.text)
        mapping = {}
        date_section = data_obj['data']['regions'][0]
        rows = date_section['rows']
        calendar = []
        for item in rows:
            crt_game_info = item['cells']
            game = {}
            game['date']     = crt_game_info[0]['text'][0]
            #game['location'] = crt_game_info[1]['text']
            game['team_home'] = crt_game_info[2]['text']
            game['team_away'] = crt_game_info[3]['text']
            #game['result'] = crt_game_info[4]['text']
            calendar.append(game)
        #print(json.dumps(calendar, indent=2))
        return calendar
    
    def generate_all_calenders(self):
        with open("conf/config.json") as json_file:
            data = json.load(json_file)
            for p in data:
                for team in p['teams'].keys():
                    filename = p['alias']+"_"+team.casefold().replace(".","").replace(" ","_").replace("/","")
                    data = self.generate_team_calendar(p['teams'][team]);
                    self.write_to_file("calendars/"+filename+".json", json.dumps(data, indent=2))



su_client = SUClient()


# Show json
#su_client.generate_config()
#su_client.get_club_teams(clubs['sum'])
#su_client.generate_team_calendar("428518")
su_client.generate_all_calenders()