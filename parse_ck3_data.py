#! /usr/bin/env python3

import time
import sys
import dash
import visdcc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


traits = ["education_intrigue_1","education_intrigue_2","education_intrigue_3","education_intrigue_4","education_diplomacy_1","education_diplomacy_2","education_diplomacy_3","education_diplomacy_4","education_stewardship_1","education_stewardship_2","education_stewardship_3","education_stewardship_4","education_martial_1","education_martial_2","education_martial_3","education_martial_4","education_learning_1","education_learning_2","education_learning_3","education_learning_4","diplomat","family_first","august","reveler_1","reveler_2","reveler_3","blademaster_1","blademaster_2","blademaster_3","hunter_1","hunter_2","hunter_3","strategist","overseer","gallant","architect","administrator","avaricious","schemer","seducer","torturer","whole_of_body","scholar","theologian","mystic_1","mystic_2","mystic_3","physician_1","physician_2","physician_3","lifestyle_herbalist","lifestyle_gardener","lustful","chaste","gluttonous","temperate","greedy","generous","lazy","diligent","wrathful","calm","patient","impatient","arrogant","humble","deceitful","honest","craven","brave","shy","gregarious","ambitious","content","arbitrary","just","cynical","zealous","paranoid","trusting","compassionate","callous","sadistic","stubborn","fickle","vengeful","forgiving","rowdy","charming","curious","pensive","bossy","drunkard","hashishiyah","rakish","reclusive","irritable","flagellant","profligate","improvident","contrite","comfort_eater","inappetetic","journaller","confider","athletic","pregnant","depressed_1","depressed_genetic","lunatic_1","lunatic_genetic","possessed_1","possessed_genetic","ill","pneumonic","great_pox","early_great_pox","lovers_pox","leper","wounded_1","wounded_2","wounded_3","maimed","one_eyed","one_legged","disfigured","infirm","incapable","gout_ridden","consumption","cancer","typhus","bubonic_plague","smallpox","sickly","scarred","eunuch","blind","beauty_bad_1","beauty_bad_2","beauty_bad_3","beauty_good_1","beauty_good_2","beauty_good_3","intellect_bad_1","intellect_bad_2","intellect_bad_3","intellect_good_1","intellect_good_2","intellect_good_3","physique_bad_1","physique_bad_2","physique_bad_3","physique_good_1","physique_good_2","physique_good_3","pure_blooded","fecund","strong","shrewd","clubfooted","hunchbacked","lisping","stuttering","dwarf","giant","inbred","weak","dull","impotent","spindly","scaly","albino","wheezing","bleeder","infertile","celibate","pilgrim","excommunicated","devoted","sayyid","saoshyant","saoshyant_descendant","savior","divine_blood","blood_of_prophet","faith_warrior","saint","order_member","berserker","shieldmaiden","varangian","poet","bastard","legitimized_bastard","disputed_heritage","child_of_concubine_female","child_of_concubine_male","wild_oat","bastard_founder","twin","kinslayer_1","kinslayer_2","kinslayer_3","deviant","cannibal","sodomite","incestuous","adulterer","fornicator","murderer","born_in_the_purple","augustus","viking","reincarnation","adventurer","heresiarch","peasant_leader","witch","disinherited","denounced","logistician","military_engineer","aggressive_attacker","unyielding_defender","forder","flexible_leader","desert_warrior","jungle_stalker","reaver","reckless","holy_warrior","open_terrain_expert","rough_terrain_expert","forest_fighter","cautious_leader","organizer","winter_soldier","crusader_king","chakravarti","greatest_of_khans","paragon","consecrated_blood","education_martial_prowess_1","education_martial_prowess_2","education_martial_prowess_3","education_martial_prowess_4","diplomatic_court_1","diplomatic_court_2","warlike_court_1","warlike_court_2","administrative_court_1","administrative_court_2","intrigue_court_1","intrigue_court_2","scholarly_court_1","scholarly_court_2"]

app = dash.Dash()

def split_subobjects_list(s):
    bracket_depth = 1
    subobjects = []
    inside_token = False
    current_subobject_start = 0
    for i, char in enumerate(s[1:]):
        if char == '{':
            bracket_depth += 1
        if char == '}':
            bracket_depth -= 1

        if bracket_depth == 0:
            break
        
        if bracket_depth == 1 or (bracket_depth == 2 and char == '{'): #not inside a subobject
            if char.isspace() and inside_token:
                subobjects.append(s[current_subobject_start:i+1])
                inside_token = False
            if (not char.isspace()) and (not inside_token):
                inside_token = True
                current_subobject_start = i

    return subobjects

class CK3Date(object):
    def __init__(self,string):
        if string.count('.') != 2:
            raise ValueError("not date string: {}".format(string))
        else:
            year, month,day = string.split('.')
            self.year = int(year)
            self.month = int(month)
            self.day = int(day)
    def __repr__(self):
        return "{}.{}.{}".format(self.year, self.month, self.day)
    

def parse_dict(s):
    bracket_depth = 0

    equals_sign_indexes = []
    quote_depth = 0
    
    for i, char in enumerate(s):
        if char == '{':
            bracket_depth += 1
        if char == '}':
            bracket_depth -= 1
        if char == '"':
            quote_depth ^= 1
            
        if bracket_depth == 1 and char == '=' and quote_depth == 0:
            equals_sign_indexes.append(i)
    d = {}
    for idx in equals_sign_indexes:
        key = s[:idx].rsplit(maxsplit=1)[-1]
        end_index = None
        if s[idx+1] == '{':            
            bracket_depth = 0
            for k in range(idx+1, len(s)):
                if s[k] == '{':
                    bracket_depth += 1
                if s[k] == '}':
                    bracket_depth -= 1
                if bracket_depth == 0:
                    end_index = k
                    break
        else:
            for k in range(idx+1, len(s)):
                if s[k].isspace():
                    end_index = k
                    break
        if end_index == None:
            end_index = len(s) - 1
        value = parse_tag(s[idx+1:end_index+1])
        d[key] = value
    return d
        
                    
        
        

def parse_list(s):
    subobjs = split_subobjects_list(s)
    return [parse_tag(token) for token in subobjs]


def parse_tag(s):
    s = s.strip()
    #attempt to parse a single tag
    # input s should be a string containing the complete object

    #multi line objects always start with a '{' character
    
    if s[0] == '{':
        #either a list or a dict
        #if theres an equals sign before we enter another object its a dict
        #otherwise its a list

        bracket_depth = 0
        closing_bracket_idx = None

        for i, char in enumerate(s):
            if char == '{':
                bracket_depth += 1
            elif char == '}':
                bracket_depth -= 1

            if bracket_depth == 0:
                closing_bracket_idx = i
                break
        if closing_bracket_idx == None:
            raise ValueError("unbalanced object {}".format(s))
        
        s = s[0:closing_bracket_idx+1]
        pre_next_open_bracket_part = s[1:].split('{')[0]

        if pre_next_open_bracket_part.find('=') >= 0:
            # we find an equals sign so dict
            return parse_dict(s)
        else:
            #no equals sign so list
            return parse_list(s)

        
    else:
        s = s.strip()

        if s.lstrip("-").isdecimal() :
            return int(s)
        else:
            if s == "yes":
                return True
            elif s == "no":
                return False
            
            decimal_count = s.count('.')
            if decimal_count == 1 and s.lstrip("-").replace('.','').isdecimal():
                return float(s)
            elif decimal_count == 2 and s.replace('.', '').isdecimal:
                return s
            else:
                return s
    
        

def str_for_one_character(f):
    bracket_depth = 0

    lines = []
    for line in f:
        if not (len(line) == 0) and (not line.isspace()):
            lines.append(line)
        bracket_depth += line.count('{')
        bracket_depth -= line.count('}')

        if bracket_depth == 0:
            break
    
    return ''.join(lines)



def iterate_over_chars(filename):
    bracket_depth = 0
    characters = []
    lines_for_current_char = []
    current_char_id = None
    
    within_character = False
    character_count = 0
    char_zone = False

    relevant_ids = []
    sigurdr_id = 7611
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("living=") or line.startswith("dead_unprunable=") or line.startswith("	dead_prunable={") or line.startswith("dead_prunable="):
                char_zone = True
            if char_zone:
                bracket_depth += line.count('{')
                bracket_depth -= line.count('}')
                if bracket_depth == 2 and (not within_character) and line.find('=') >= 0:                
                    character_count += 1
                    idx = line.find("=")
                    current_char_id = int(line[:idx].rsplit(maxsplit=1)[-1].strip())
                    lines_for_current_char = [line[idx+1:]]
                    within_character = True
                    
                elif within_character:
                    lines_for_current_char.append(line)

                if bracket_depth == 1 and within_character:
                    yield current_char_id, ''.join(lines_for_current_char)                                       
                    within_character = False
                    lines_for_current_char = None                                
                
                if bracket_depth == 0:
                    char_zone = False




def iterate_over_secrets(filename):
    bracket_depth = 0
    characters = []
    lines_for_current_secret = []
    current_secret_id = None
    
    within_secret = False
    secret_count = 0
    secrets_zone = False

    with open(filename, "r") as f:
        for line in f:
            if line.startswith("	secrets="):
                secrets_zone = True
            if secrets_zone:
                bracket_depth += line.count('{')
                bracket_depth -= line.count('}')
                
                if bracket_depth == 2 and (not within_secret) and line.find('=') >= 0:                
                    secret_count += 1
                    idx = line.find("=")
                    current_secret_id = int(line[:idx].rsplit(maxsplit=1)[-1].strip())
                    lines_for_current_secret = [line[idx+1:]]
                    within_secret = True
                    
                elif within_secret:
                    lines_for_current_secret.append(line)

                if bracket_depth == 1 and within_secret:
                    yield current_secret_id, ''.join(lines_for_current_secret)                                       
                    within_secret = False
                    lines_for_current_secret = None                                
                
                if bracket_depth == 0:
                    break

def iterate_over_active_opinions(filename):

    bracket_depth = 0
    characters = []
    lines_for_current_opinion = []
    current_opinion_id = None
    
    within_opinion = False
    opinions_zone = False
    start_line = False
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("	active_opinions="):
                
                opinions_zone = True
                start_line = True
                
            if opinions_zone:
                #print(line)
                bracket_depth += line.count('{')
                bracket_depth -= line.count('}')

                if start_line:
                    start_line = False
                    lines_for_current_opinion = ["{"]
                    within_opinion = True
                else:
                    if bracket_depth == 2 and (not within_opinion) and line.find('{') >= 0:
                        idx = line.find("{")
                        #current_opinion_id = int(line[:idx].rsplit(maxsplit=1)[-1].strip())
                        lines_for_current_opinion = [line[idx:]]
                        within_opinion = True
                    
                    elif within_opinion:
                        lines_for_current_opinion.append(line)

                    if bracket_depth == 1 and within_opinion:
                        yield ''.join(lines_for_current_opinion)                                       
                        within_opinion = False
                        lines_for_current_opinion = None                                
                
                if bracket_depth == 0:
                    break
                
def iterate_over_active_jobs(filename):
    bracket_depth = 0
    lines_for_current_job = []
    current_job_id = None
    
    within_job = False
    job_count = 0
    job_zone = False
    active_job_zone = False

    with open(filename, "r") as f:
        for line in f:
            if line.startswith("council_task_manager={"):
                job_zone = True
            if job_zone and line.startswith("	active={"):
                active_job_zone = True
            if active_job_zone:
                bracket_depth += line.count('{')
                bracket_depth -= line.count('}')
                
                if bracket_depth == 2 and (not within_job) and line.find('=') >= 0:                
                    job_count += 1
                    idx = line.find("=")
                    current_job_id = int(line[:idx].rsplit(maxsplit=1)[-1].strip())
                    lines_for_current_job = [line[idx+1:]]
                    within_job = True
                    
                elif within_job:
                    lines_for_current_job.append(line)

                if bracket_depth == 1 and within_job:
                    yield current_job_id, ''.join(lines_for_current_job)                                       
                    within_job = False
                    lines_for_current_job = None                                
                
                if bracket_depth == 0:
                    break
                


def recursively_add_family(filename, members,deleted_chars):
    count = 0
    print("initial members: ", len(members))
    while True:
        
        count += 1
        new_members = []
        
        for char_id in members:
            if 'child' in members[char_id]['family_data']:
                for child_id in members[char_id]['family_data']['child']:
                    if not child_id in members and not child_id in deleted_chars:
                        new_members.append(child_id)

        print("recursion_level:", count, "found {} new characters, total characters {}".format(len(new_members), len(members)+len(new_members)))
        if len(new_members) == 0:
            break
        if len(new_members) == 1:
            print(new_members)
                
        with open(filename, "r") as f:    
            for char_id, string in iterate_over_chars(filename):
                if char_id in new_members:
                    members[char_id] = parse_tag(string)
                    new_members.remove(char_id)
        print(new_members)
                
sigurdr_id = 7611
relevant_ids = []
filename = "gamestate"

# characters_zone = False
# with open(filename, "r") as f:
#     bracket_depth = 0
#     for line in f:
#         if line.startswith("characters={"):
#             characters_zone = True
#         if characters_zone:
#             bracket_depth += line.count('{')
#             bracket_depth -= line.count('}')
#             if (bracket_depth == 2 and "=" in line) or (bracket_depth == 1 and "=" in line and not "{" in line):
#                 print(line)
#             if bracket_depth == 0:
#                 break
                
        
#         #if bracket_depth == 0 and "=" in line and not "triggered_event={" in line:
#         #    print(line, end="")

# #exit()

deleted_chars = set()
deleted_chars_zone = False
deleted_chars_lines = None
bracket_depth = 0
with open(filename, "r") as f:
    for line in f:
        first_line = False
        if line.startswith("deleted_characters={"):
            deleted_chars_zone = True
            idx = line.find("=")
            deleted_chars_lines = [line[idx+1:]]
            first_line = True
        if deleted_chars_zone:
            bracket_depth += line.count('{')
            bracket_depth -= line.count('}')
            if not first_line:
                deleted_chars_lines.append(line)
            if bracket_depth == 0:
                break

deleted_chars = set(parse_tag("".join(deleted_chars_lines)))
print(deleted_chars)                

nodes = []
edges = []



#net.add_node(sigurdr_id, "Sigurdr", colour="blue")

relevant_chars = {}
concubine_ids = []

council_job_ids = []
council_jobs = {}
for char_id, string in iterate_over_chars(filename):
    if char_id == sigurdr_id:        
        char_data = parse_tag(string)        
        relevant_chars[char_id] = char_data
        
        #relevant_ids.append(char_data['family_data']['spouse'])
        relevant_ids.append(char_data['family_data']['concubine'])
        council_job_ids += char_data['landed_data']['council']
        
    if "concubinist=7611" in string:
        concubine_ids.append(char_id)
        relevant_chars[char_id] = parse_tag(string)



for job_id, string in iterate_over_active_jobs(filename):
    if job_id in council_job_ids:
        council_jobs[job_id] = parse_tag(string)
    if len(council_jobs) > 5:
        break


for key in council_jobs:
    relevant_ids.append(council_jobs[key]['owner'])
        
for char_id, string in iterate_over_chars(filename):
    if char_id in relevant_ids and not char_id in relevant_chars:        
        char_data = parse_tag(string)
        relevant_chars[char_id] = char_data


recursively_add_family(filename, relevant_chars, deleted_chars)        


relevant_opinions = []
for i, string in enumerate(iterate_over_active_opinions(filename)):
    opinion = parse_tag(string)
    if opinion["owner"] in relevant_chars and opinion["target"] == opinion["owner"]: #in relevant_chars :
        #relevant_opinions.append(opinion)
        print("*******")
        print(opinion)
        print("*******")
# {'owner': 16798161, 'target': 16799695, 'scripted_relations': {'best_friend': [0]}}
# {'owner': 36394, 'target': 8068, 'scripted_relations': {'friend': [0]}}
# {'owner': 8168, 'target': 32504, 'scripted_relations': {'rival': [0]}}
exit()
for opinion in relevant_opinions:
    if 'opinions_data' in relevant_chars[opinion['owner']]:
        relevant_chars[opinion['owner']]['opinions_data'].append(opinion)
    else:
        relevant_chars[opinion['owner']]['opinions_data'] = [opinion]
    

spouse_id = relevant_chars[sigurdr_id]["family_data"]["spouse"]

string_dict = {}

def person_to_node(char_id,data):
    strings = [str(char_id)]
    for key in data:
        if key != "dna":
            if key == "traits":
                strings.append("{}: {}".format(key, str([traits[idx] for idx in data['traits']])))                
            else:
                strings.append("{}: {}".format(key, str(data[key])))
                
    string_dict[char_id] = "\n".join(strings)
    node = {'id': char_id, 'label': data["first_name"].replace('_','').replace('"','').capitalize(), 'shape':'dot', 'size':7}
    if char_id == sigurdr_id:
        node['color'] = "blue"
    elif char_id in concubine_ids:
        node['color'] = "pink"
    elif char_id == spouse_id:
        node['color'] = "red"
    else:
        node['color'] = "green"
    if 'dead_data' in data:
        node['color'] = "grey"
    if 'secret_data' in data:
        node['color'] = {'background':node['color'], 'border':'red'}
    return node

secret_ids = set()  
for char_id in relevant_chars:
    if 'alive_data' in relevant_chars[char_id] and 'targeting_secrets' in relevant_chars[char_id]['alive_data']:
        for secret_id in relevant_chars[char_id]['alive_data']['targeting_secrets']:
            secret_ids.add(secret_id)
    if 'alive_data' in relevant_chars[char_id] and 'secrets' in relevant_chars[char_id]['alive_data']:
        for secret_id in relevant_chars[char_id]['alive_data']['secrets']:
            secret_ids.add(secret_id)

relevant_secrets = {}        
for secret_id, string in iterate_over_secrets(filename):
    if secret_id in secret_ids:
        relevant_secrets[secret_id] = parse_tag(string)
        
#print(relevant_secrets)
for char_id in relevant_chars:
    if 'alive_data' in relevant_chars[char_id] and 'targeting_secrets' in relevant_chars[char_id]['alive_data']:
        for secret_id in relevant_chars[char_id]['alive_data']['targeting_secrets']:
            if 'secret_data' in relevant_chars[char_id]:
                relevant_chars[char_id]['secret_data'].append(relevant_secrets[secret_id])
            else:
                relevant_chars[char_id]['secret_data'] = [relevant_secrets[secret_id]]
                
    if 'alive_data' in relevant_chars[char_id] and 'secrets' in relevant_chars[char_id]['alive_data']:
        for secret_id in relevant_chars[char_id]['alive_data']['secrets']:
            if 'secret_data' in relevant_chars[char_id]:
                relevant_chars[char_id]['secret_data'].append(relevant_secrets[secret_id])
            else:
                relevant_chars[char_id]['secret_data'] = [relevant_secrets[secret_id]]
        



for char_id in relevant_chars:
    if 'traits' in relevant_chars[char_id]:        
        relevant_chars[char_id]['traits'] = [traits[idx] for idx in relevant_chars[char_id]['traits']]
        
import json    
with open("ck3_data_with_opinions.json", "w") as f:
    json.dump({'char_data': relevant_chars, 'job_data': council_jobs},fp=f)
    
exit()

added_chars = set()
for char_id in relevant_chars:
    if not char_id in added_chars:
        nodes.append(person_to_node(char_id, relevant_chars[char_id]))
        added_chars.add(char_id)
        
    if "child" in relevant_chars[char_id]["family_data"]:
        for child_id in relevant_chars[char_id]["family_data"]["child"]:
            if not child_id in added_chars:
                nodes.append(person_to_node(child_id, relevant_chars[child_id]))
                added_chars.add(child_id)
            edges.append({'id': "{}__{}".format(char_id,child_id), 'from':char_id, 'to':child_id, 'label':'child', 'arrows':{'to': True}})
                
# for child_id in relevant_chars[spouse_id]["family_data"]["child"]:
#     edges.append({'id': "{}__{}".format(spouse_id,child_id), 'from':spouse_id, 'to':child_id, 'label':'child'})

#print(council_jobs)
for job_id in council_jobs:
    edges.append({'id': "{}_c_{}".format(council_jobs[job_id]['court_owner'],council_jobs[job_id]['owner']), 'from':council_jobs[job_id]['court_owner'], 'to':council_jobs[job_id]['owner'], 'label':council_jobs[job_id]['type'],'color':'grey', 'dashes':True, 'physics':False})

app.layout = html.Div(className="row",children=[
    dcc.Store(id='memory',data=string_dict),
    html.Div(children=[visdcc.Network(id = "net", data={'nodes':nodes, 'edges':edges}, options={'height':'600px', 'width': '600px'})], style={'display': 'inline-block'}),
    html.Div(
        children=dcc.Textarea(
            id='textarea',
            #value='Textarea content initialized\nwith multiple lines of text',
            style={'width': '900px', 'height': '600px'},
            disabled=True,
            readOnly=True,
        ), style={'display': 'inline-block'}
    )
    ])



app.clientside_callback(
    """
    function(x,data) {
        if(x && x.hasOwnProperty('nodes') ){
            return data[x['nodes'][0]];
        }else{
            return "";
        }
    }
    """,
    Output('textarea', 'value'),
    Input('net', 'selection'),
    Input('memory', 'data')    
)


# @app.callback(
#     Output('textarea', 'value'),
#     [Input('net', 'selection')])
# def myfun(x): 
#     #s = 'Selected nodes : '
#     #if len(x['nodes']) > 0 : s += str(x['nodes'][0])
    
#     if x and 'nodes' in x and len(x['nodes']) > 0:
#         return x['nodes'][0]
    
#         #strings = [str(x['nodes'][0])]
#         # for key in relevant_chars[x['nodes'][0]]:
#         #     if key != 'dna':
#         #         #if key == "traits":
#         #         #    strings.append("{}: {}".format(key, str([traits[idx] for idx in relevant_chars[x['nodes'][0]][key]])))
#         #         #else:
#         #         strings.append("{}: {}".format(key, str(relevant_chars[x['nodes'][0]][key])))
        
#         return "\n".join(strings)
#     else:
#         return ""

    
    
# def myFun(x):
#     return {'nodes': {'color':x}}
if __name__ == "__main__":
    app.run_server(debug=False)




        
    
    
#net.add_node(, relevant_chars[char]["first_name"])

    # secrets = []

# for char_id, string in iterate_over_chars(filename):
#     if char_id == 22761:
#         char_data = parse_tag(string) # grunhildr
#         print(char_data)
#         secrets += char_data['alive_data']['secrets']


# print(secrets)


# for secret_id, string in iterate_over_secrets(filename):
#     if secret_id in secrets:
#         secret = parse_tag(string)
#         print(secret)

        
