from screeps.screeps import Connection

from dotenv import load_dotenv
from store import Store
import os
import json

load_dotenv()

store = Store()
old_vals = {}


def report_cpu(message):
    store.write_point('system', {}, message)


def report_room(message):
    game_time = message.get('gameTime')
    print(game_time)
    creeps = 0
    dropped_energy = 0
    stored_energy = 0
    stored_energy_capacity = 0
    spawn_energy = 0
    spawn_energy_capacity = 0
    for id, element in message['objects'].items():
        object_type = element.get('type')
        match object_type:
            case 'source':
                current_energy = element.get('energy')
                previous_energy = old_vals.get(id, current_energy)
                energy_difference = current_energy - previous_energy
                energy_difference = 0 if energy_difference < 0 else energy_difference
                
                store.write_point('source-energy', {'id': id}, {
                    'energy': current_energy,
                    'energy_harvested': energy_difference
                })
                
                old_vals[id] = current_energy
            case 'mineral':
                store.write_point('mineral', {'id': element.get('_id'), 'type': element.get('mineralType')}, {
                    'amount': element.get('mineralAmount')
                })
            case 'constructedWall':
                pass
            case 'road':
                pass
            case 'energy':
                dropped_energy += element.get('energy')
            case 'creep':
                creeps += 1
            case 'container':
                stored_energy += element.get('store').get('energy')
                stored_energy_capacity += element.get('storeCapacity')
            case 'extension':
                spawn_energy += element.get('store').get('energy')
                spawn_energy_capacity += element.get('storeCapacityResource').get('energy')
            case 'rampart':
                pass
            case 'tower':
                pass
            case 'controller':
                current_progress = element.get('progress')
                previous_progress = old_vals.get(id, current_progress)
                progress_difference = current_progress - previous_progress
                
                store.write_point('controller', {'id': id}, {
                    'progress': current_progress,
                    'progress_difference': progress_difference,
                    'level': element.get('level'),
                    'safeModeAvailable': element.get('safeModeAvailable')
                })
                
                old_vals[id] = current_progress
            case 'spawn':
                spawn_energy += element.get('store').get('energy')
                spawn_energy_capacity += element.get('storeCapacityResource').get('energy')
            case None:  # some junk, I haven't found what it means
                pass
            case 'tombstone':
                pass
            case _:
                print(f"Unknown element type: {object_type}")
    store.write_point('energy', {}, {
        'creeps': creeps,
        'dropped_energy': dropped_energy,
        'stored_energy': stored_energy,
        'stored_energy_capacity': stored_energy_capacity,
        'spawn_energy': spawn_energy,
        'spawn_energy_capacity': spawn_energy_capacity
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


conn = Connection(os.getenv('SCREEPS_USERNAME'), os.getenv('SCREEPS_PASSWORD'),'shard3/W48N55')
conn.startWebSocket(sysout)