from ThermiaOnlineAPI import Thermia
from ThermiaOnlineAPI.exceptions import AuthenticationException
from credentials import USERNAME, PASSWORD
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from flask import Flask, Response
import prometheus_client

app = Flask(__name__)

custom_registry = CollectorRegistry()

prometheus_metrics = {}

wanted_metrics = {
    'outdoor_temperature': {'path': ['_ThermiaHeatPump__status', 'outdoorTemperature'], 'description': 'Outdoor Temperature of the heat pump'},
    'hot_water_temperature': {'path': ['_ThermiaHeatPump__status', 'hotWaterTemperature'], 'description': 'Hot Water Temperature of the heat pump'},
    'supply_line_temperature': {'path': ['_ThermiaHeatPump__group_temperatures', 1, 'registerValue'], 'description': 'Supply Line Temperature of the heat pump'},
    'return_line_temperature': {'path': ['_ThermiaHeatPump__group_temperatures', 2, 'registerValue'], 'description': 'Return Line Temperature of the heat pump'},
    'brine_in_temperature': {'path': ['_ThermiaHeatPump__group_temperatures', 3, 'registerValue'], 'description': 'Brine In Temperature of the heat pump'},
    'brine_out_temperature': {'path': ['_ThermiaHeatPump__group_temperatures', 4, 'registerValue'], 'description': 'Brine Out Temperature of the heat pump'},
    'heating_effect': {'path': ['_ThermiaHeatPump__status', 'heatingEffect'], 'description': 'Heating Effect of the heat pump'},
    'compressor_operational_time': {'path': ['_ThermiaHeatPump__group_operational_time', 2, 'registerValue'], 'description': 'Compressor Operational Time in hours'},
    'hot_water_operational_time': {'path': ['_ThermiaHeatPump__group_operational_time', 3, 'registerValue'], 'description': 'Hot Water Operational Time in hours'},
    'desired_supply_line_temperature': {'path': ['_ThermiaHeatPump__group_temperatures', 6, 'registerValue'], 'description': 'Desired Supply Line Temperature of the heat pump'}
}

thermia = None

def init_thermia():
    global thermia
    if thermia is None:
        thermia = Thermia(USERNAME, PASSWORD)

def reauthenticate():
    global thermia
    thermia = Thermia(USERNAME, PASSWORD)

def collect_data():
    if not USERNAME or not PASSWORD:
        return "Error: USERNAME and PASSWORD must be set in credentials.py"
    
    try:
        init_thermia()
        heat_pumps = thermia.fetch_heat_pumps()

        for hp in heat_pumps:
            heat_pump_name = hp.__dict__.get('_ThermiaHeatPump__info', {}).get('name', 'unknown')

            for metric, details in wanted_metrics.items():
                value = hp.__dict__
                for key in details['path']:
                    if isinstance(value, dict):
                        value = value.get(key)
                    elif isinstance(value, list):
                        value = value[key]

                if isinstance(value, (int, float)):
                    print(f"Registering {metric}: {value} for {heat_pump_name}")
                    if metric not in prometheus_metrics:
                        prometheus_metrics[metric] = Gauge(metric, details['description'], ['heat_pump_name'], registry=custom_registry)
                    prometheus_metrics[metric].labels(heat_pump_name=heat_pump_name).set(value)

        return None

    except AuthenticationException as auth_error:
        print("Authentication error detected, re-authenticating...")
        reauthenticate()
        return collect_data()

    except Exception as e:
        return f"Error while collecting data: {str(e)}"

@app.route('/metrics')
def metrics():
    collection_status = collect_data()
    if collection_status:
        return Response(collection_status, status=500, mimetype='text/plain')
    
    return Response(generate_latest(custom_registry), mimetype='text/plain')