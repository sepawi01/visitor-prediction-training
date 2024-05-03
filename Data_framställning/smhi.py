import requests
import pandas as pd
from io import StringIO
import json
import gzip

class WeatherForecastAPI:
    def __init__(self):
        self.base_url = "https://opendata-download-metfcst.smhi.se"  # Ersätt med den faktiska bas-URL:en till API:et
        self.headers = {"Accept-Encoding": "gzip"}

    def get_point_forecast(self, category, version, longitude, latitude):
        """Hämta väderprognos för en specifik punkt."""
        # api/category/pmp3g/version/2/geotype/point/lon/16.158/lat/58.5812/data.json,
        url = f"{self.base_url}/api/category/{category}/version/{version}/geotype/point/lon/{longitude}/lat/{latitude}/data.json"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        sorted_weather = self.sort_and_print_weather(data)
        return 
    
    def sort_and_print_weather(self, data):
        weather_categories = {
            "msl": "Air pressure (hPa)",
        "t": "Air temperature (°C)",
        "vis": "Horizontal visibility (km)",
        "wd": "Wind direction (degrees)",
        "ws": "Wind speed (m/s)",
        "r": "Relative humidity (%)",
        "tstm": "Thunder probability (%)",
        "tcc_mean": "Mean total cloud cover (octas)",
        "lcc_mean": "Mean low level cloud cover (octas)",
        "mcc_mean": "Mean medium level cloud cover (octas)",
        "hcc_mean": "Mean high level cloud cover (octas)",
        "gust": "Wind gust speed (m/s)",
        "pmin": "Minimum precipitation intensity (mm/h)",
        "pmax": "Maximum precipitation intensity (mm/h)",
        "spp": "Percent of precipitation in frozen form (%)",
        "pcat": "Precipitation category",
        "pmean": "Mean precipitation intensity (mm/h)",
        "pmedian": "Median precipitation intensity (mm/h)",
        "Wsymb2": "Weather symbol (code)"
        }

        categorized_data = {}
        # Loopa igenom varje tidsserie och hämta parametrar och värden
        for entry in data['timeSeries']:
            valid_time = entry['validTime']
            parameters = entry['parameters']
            entry_data = {}
            # Loopa igenom parametrarna och spara dem i en dictionary
            for parameter in parameters:
                parameter_name = parameter['name']
                parameter_unit = parameter['unit']
                parameter_value = parameter['values'][0]
                parameter_description = weather_categories.get(parameter_name, "Unknown")
                entry_data[parameter_name] = {
                    'unit': parameter_unit,
                    'value': parameter_value,
                    'description': parameter_description
                }
            categorized_data[valid_time] = entry_data

        # Sortera den kategoriserade datan baserat på tid och skriv ut den
        sorted_data = sorted(categorized_data.items())
        for time, data_entry in sorted_data:
            print(f"At {time}:")
            for parameter, info in data_entry.items():
                print(f"  {parameter}: {info['value']} {info['unit']} - {info['description']}")

        return sorted_data

    def get_multipoint_forecast(self, category, version, validtime, parameter, leveltype, level, downsample=2, with_geo=False):
        """Hämta väderprognos för multipunkter."""
        url = f"{self.base_url}/category/{category}/version/{version}/geotype/multipoint/validtime/{validtime}/parameter/{parameter}/leveltype/{leveltype}/level/{level}/data.json"
        params = {
            "with-geo": str(with_geo).lower(),
            "downsample": downsample
        }
        
        response = requests.get(url, headers=self.headers, params=params)

        # Hantera GZIP-komprimerat svar
        if response.headers.get('Content-Encoding') == 'gzip':
            content = gzip.decompress(response.content)
            data = json.loads(content.decode('utf-8'))
        else:
            data = response.json()

        return data

    
class OpenDataMetobsReader:
    def __init__(self):
        self.metObsAPI = "https://opendata-download-metobs.smhi.se/api"

    def get_parameters(self):
        """Fetch and let the user choose a parameter, return the chosen parameter key."""
        response = requests.get(f"{self.metObsAPI}/version/latest.json")
        parameters = response.json()['resource']
        print("Tillgängliga parametrar:")
        for i, parameter in enumerate(parameters, 1):
            if parameter['title'] in ['Lufttemperatur','Nederbördsmängd','Molnbas','Molnmängd','Nederbörd','Nederbördsintensitet']:
                print(f"{i}. {parameter['title']},{parameter['summary']},({parameter['key']})")
            else:
                print(f"{i}. {parameter['title']}, ({parameter['key']})")

        search_query = input("Sök efter en parameter (lämna tomt för att visa alla): ").lower()
        if search_query:
            filtered_parameters = [parameter for parameter in parameters if search_query in parameter['title'].lower()]
            for i, parameter in enumerate(filtered_parameters, 1):
                if parameter['title'] in ['Lufttemperatur','Nederbördsmängd','Molnbas','Molnmängd','Nederbörd','Nederbördsintensitet']:
                    print(f"{i}. {parameter['title']},{parameter['summary']},({parameter['key']})")
                else:
                    print(f"{i}. {parameter['title']} ({parameter['key']})")
            if not filtered_parameters:
                print("Ingen parameter hittades med den söktermen. Visar alla parametrar igen.")
            else:
                parameters = filtered_parameters  

        choice = int(input("Välj en parameter genom att ange dess nummer: "))
        parameter_key = parameters[choice - 1]['key']
        return parameter_key
   

    def get_station_names(self, parameter_key):
        """Fetch stations for the chosen parameter and let the user choose one, return the chosen station id."""
        response = requests.get(f"{self.metObsAPI}/version/latest/parameter/{parameter_key}.json")
        stations = response.json()['station']

        print("Tillgängliga stationer:")
        for i, station in enumerate(stations, 1):
            print(f"{i}. {station['name']} ({station['key']})")

        # Lägg till sökfunktionalitet
        search_query = input("Sök efter en station (lämna tomt för att visa alla): ").lower()
        if search_query:
            filtered_stations = [station for station in stations if search_query in station['name'].lower()]
            for i, station in enumerate(filtered_stations, 1):
                print(f"{i}. {station['name']} ({station['key']})")
            if not filtered_stations:
                print("Ingen station hittades med den söktermen. Visar alla stationer igen.")
            else:
                stations = filtered_stations  # Använd den filtrerade listan för val

        # Låt användaren välja en station från den filtrerade listan
        choice = int(input("Välj en station genom att ange dess nummer: "))
        station_id = stations[choice - 1]['key']
        return station_id

    def get_period_names(self, parameter_key, station_key):
        response = requests.get(f"{self.metObsAPI}/version/latest/parameter/{parameter_key}/station/{station_key}.json")
        periods = response.json()['period']
        for i, period in enumerate(periods, 1):
            print(f"{i}. {period['key']}")
        choice = int(input("Välj en period genom att ange dess nummer: "))
        return periods[choice - 1]['key']

    def get_data(self, parameter_key, station_key, period_name):
        url = f"{self.metObsAPI}/version/latest/parameter/{parameter_key}/station/{station_key}/period/{period_name}/data.csv"
        response = requests.get(url)
        print(response.text)
        return response.text

    def display_csv_data(self, csv_data):
        """Anpassad visning av CSV-data och spara ner till fil med uppdaterade pandas-inställningar."""
        # Dela upp datan i rader och hitta datasektionen
        lines = csv_data.split('\n')
        data_section_started = False
        data_lines = []
        for line in lines:
            if line.startswith('Datum;Tid (UTC);') or line.startswith('Från Datum Tid (UTC)'):  # Start på datasektionen
                data_section_started = True
                data_lines.append(line)  # Lägg till kolumnrubriker
                continue
            if data_section_started and line.strip():  # Säkerställ att raden inte är tom
                data_lines.append(line)

        # Omvandla den extraherade datasektionen till en DataFrame och spara ner till en fil
        if data_lines:
            data_str = '\n'.join(data_lines)
            df = pd.read_csv(StringIO(data_str), sep=";", on_bad_lines='skip', low_memory=False)
            print(df)
            
            # Spara DataFrame till en CSV-fil
            df.to_csv('smhi_temp_2024.csv', index=False, sep=';')
            print("Data har sparats till 'smhi_weather_code.csv'.")
        else:
            print("Ingen data hittades i den angivna sektionen.")

if __name__ == "__main__":
    try:
        reader = OpenDataMetobsReader()
        
        choice = input("Vill du hämta (1) historisk data eller (2) väderprognos? Ange 1 eller 2: ")
        
        if choice == '1':
            parameter_key = reader.get_parameters()
            station_key = reader.get_station_names(parameter_key)
            period_key = reader.get_period_names(parameter_key, station_key)
            csv_data = reader.get_data(parameter_key, station_key, period_key)
        elif choice == '2':
            api = WeatherForecastAPI()
            # Använd korrekta parametrar för ditt API-anrop
            point_forecast = api.get_point_forecast("pmp3g", "2", "15.00", "60.00")  
            print("Point Forecast:", point_forecast)

            multipoint_forecast = api.get_multipoint_forecast("pmp3g", "2", "20230101T000000Z", "temperature", "surface", "0")
            print("MultiPoint Forecast:", multipoint_forecast)
        else:
            raise ValueError("Ogiltigt val. Ange antingen 1 eller 2.")
        
        # Visa den hämtade CSV-datan med pandas
        reader.display_csv_data(csv_data)
    except Exception as e:
        print(f"Ett fel inträffade: {e}")
