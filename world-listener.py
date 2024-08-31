import time

from screeps.screeps import Connection

from dotenv import load_dotenv
from store import Store
import os
import json
import traceback

load_dotenv()

store = Store()
world_state = {}


def report_cpu(message):
    store.write_point('system', {}, message)


def report_room(message):
    game_time = message.get('gameTime')
    print(game_time)
    energy_harvested = 0
    for id, entity_update in message['objects'].items():
        if entity_update is None:
            continue
        if id not in world_state:
            world_state[id] = entity_update
        entity = world_state[id]
        match entity.get('type'):
            case 'source':
                energy_difference = entity.get('energy') - entity_update.get('energy')
                energy_harvested += 0 if energy_difference < 0 else energy_difference
            case 'mineral':
                store.write_point('mineral', {'id': entity_update.get('_id'), 'type': entity.get('mineralType')}, {
                    'amount': entity_update.get('mineralAmount')
                })
            case 'constructedWall':
                pass
            case 'road':
                pass
            case 'energy':
                pass
            case 'creep':
                pass
            case 'container':
                pass
            case 'extension':
                pass
            case 'rampart':
                pass
            case 'tower':
                pass
            case 'controller':
                progress_difference = entity_update.get('progress') - entity.get('progress')
                
                store.write_point('controller', {'id': id}, {
                    'progress': entity_update.get('progress'),
                    'progress_difference': progress_difference,
                    'level': entity_update.get('level') or entity.get('level'),
                    'safeModeAvailable': entity_update.get('safeModeAvailable')
                })
            case 'spawn':
                pass
            case 'tombstone':
                creep_name = entity.get('name')
                if creep_name:
                    for creep_id, creep in world_state.items():
                        if creep.get('type') == 'creep' and creep.get('name') == creep_name:
                            del world_state[creep_id]
                            break  
                pass
            case 'constructionSite':
                pass
            case _:
                print(f"Unknown element type: {entity.get('type')}")

        for key, value in entity_update.items():
            entity[key] = value
    
    total_dropped_energy = 0
    for id, entity in world_state.items():
        if entity.get('type') == 'energy':
            total_dropped_energy += entity.get('energy', 0)
    

    spawn_energy = 0
    spawn_energy_capacity = 0
    for id, entity in world_state.items():
        if entity.get('type') == 'spawn' or entity.get('type') == 'extension':            
            spawn_energy += entity.get('store').get('energy')
            spawn_energy_capacity += entity.get('storeCapacityResource').get('energy')


    stored_energy = 0
    stored_energy_capacity = 0
    for id, entity in world_state.items():
        if entity.get('type') == 'spawn' or entity.get('type') == 'container':            
            stored_energy += entity.get('store').get('energy')
            stored_energy_capacity += entity.get('storeCapacity') or entity.get('storeCapacityResource').get('energy')

    tower_energy = 0
    tower_energy_capacity = 0
    for id, entity in world_state.items():
        if entity.get('type') == 'tower':
            tower_energy += entity.get('store').get('energy')
            tower_energy_capacity += entity.get('storeCapacityResource').get('energy')

    creeps = 0
    for id, entity in world_state.items():
        if entity.get('type') == 'creep':
            creeps+=1;

    store.write_point('energy', {}, {
        'creeps': creeps,
        'dropped_energy': total_dropped_energy,
        'stored_energy': stored_energy,
        'stored_energy_capacity': stored_energy_capacity,
        'spawn_energy': spawn_energy,
        'spawn_energy_capacity': spawn_energy_capacity,
        'energy_harvested': energy_harvested,
        'tower_energy': tower_energy,
        'tower_energy_capacity': tower_energy_capacity,
    })



def sysout(message):
    try:
        parsed_message = json.loads(message)
        if parsed_message[0].startswith('room:shard'):
            report_room(parsed_message[1])
        elif parsed_message[0].endswith('/cpu'):
            report_cpu(parsed_message[1])
    except json.JSONDecodeError:
        print(f"Failed to parse message as JSON: {message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("Stacktrace:")
        traceback.print_exc()


while True:
    try:
        conn = Connection(os.getenv('SCREEPS_USERNAME'), os.getenv('SCREEPS_PASSWORD'), 'shard3/W48N55')
        conn.startWebSocket(sysout)
    except Exception as e:
        print(f"Connection lost: {str(e)}")
        print("Attempting to reconnect in 5 seconds...")
        time.sleep(5)
    else:
        break
