#!/usr/bin:env python

import json
import requests
from lxml import html
from collections import OrderedDict
import argparse
from datetime import datetime
import certifi
import urllib3


def parse_inputs():
    """
    Parses the command line input arguments.

    Parameters
    ----------

    None.

    Returns
    ----------

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package.
        Dictionary is keyed by the argument name (e.g., args['source_airport']).
    """

    parser = argparse.ArgumentParser()

    # Taken from
    # https://stackoverflow.com/questions/24180527/argparse-required-arguments-listed-under-optional-arguments
    # Normally `argparse` lists all arguments as 'optional'.  However some of
    # my arguments are required so this hack makes `parser.print_help()`
    # properly show that they are.

    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('--required_arg')

    required.add_argument("-s", "--source", dest="source_airport",
                          help="Airport code for the source city.",
                          type=str)

    required.add_argument("-d", "--destination", dest="dest_airport",
                          help="Airport code for the destination city.",
                          type=str)

    required.add_argument("-t", "--date", dest="date",
                          help="Date for leaving the source city. 'DD/MM/YYYY'",
                          type=str)

    args = parser.parse_args()
    args = vars(args)

    # We require a source/destination airport in addition to a date.
    if not (args["source_airport"] or args["dest_airport"] or args["date"]):
        parser.print_help()
        print("")
        raise RuntimeError


    try:
        dt = datetime.strptime(args["date"], "%d/%m/%Y")
    except ValueError:
        print("The date you entered does not fit the expected 'DD/MM/YYYY' "
              "format")

    return args


def scrape_airfares(source_airport, dest_airport, date):
    """
    Gets airfare prices from Expedia.

    This function was taken (essentially) whole from
    https://www.scrapehero.com/scrape-flight-schedules-and-prices-from-expedia/

    Parameters
    ----------

    source_airport: String. Required.
        The airport code where we're leaving from.    

    dest_airport: String. Required. 
        The airport code where we're arriving at. 
    
    date: String. Required. 
        The date we're scraping airfares for. Must be in 'DD/MM/YYYY' format. 

    Returns
    ----------

    flightlist: List.  Required.
        A list containing all the flight information from the source airport to
        the destination airport on the date specified.  This is eventually
        saved out as a .json file.
    """

    print("Scraping airfares from {0} to {1} on {2}".format(source_airport,
                                                            dest_airport,
                                                            date))

    # Expedia is an American website so need to use the date as 'MM/DD/YYYY'.
    dt = datetime.strptime(date, "%d/%m/%Y")
    date_string = "{0}/{1}/{2}".format(dt.month, dt.day, dt.year)

    http = urllib3.PoolManager(
           cert_reqs='CERT_REQUIRED',
           ca_certs=certifi.where())

    url="https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source_airport,dest_airport,date_string)

    print(url)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    response = requests.get(url, headers=headers, verify=False)
    parser = html.fromstring(response.text)
    json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")

    raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
    flight_data = json.loads(raw_json["content"])

    flight_info  = OrderedDict() 
    lists=[]

    for i in flight_data['legs'].keys():
        total_distance =  flight_data['legs'][i].get("formattedDistance",'')
        exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal','')

        departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportLongName','')
        departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
        departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
        
        arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportLongName','')
        arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
        arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
        airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
        
        no_of_stops = flight_data['legs'][i].get("stops","")
        flight_duration = flight_data['legs'][i].get('duration',{})
        flight_hour = flight_duration.get('hours','')
        flight_minutes = flight_duration.get('minutes','')
        flight_days = flight_duration.get('numOfDays','')

        if no_of_stops==0:
            stop = "Nonstop"
        else:
            stop = str(no_of_stops)+' Stop'

        total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days,flight_hour,flight_minutes)
        departure = departure_location_airport+", "+departure_location_city
        arrival = arrival_location_airport+", "+arrival_location_city
        carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
        plane = carrier.get('plane','')
        plane_code = carrier.get('planeCode','')
        formatted_price = "{0:.2f}".format(exact_price)

        if not airline_name:
            airline_name = carrier.get('operatedBy','')
        
        timings = []
        for timeline in  flight_data['legs'][i].get('timeline',{}):
            if 'departureAirport' in timeline.keys():
                departure_airport = timeline['departureAirport'].get('longName','')
                departure_time = timeline['departureTime'].get('time','')
                arrival_airport = timeline.get('arrivalAirport',{}).get('longName','')
                arrival_time = timeline.get('arrivalTime',{}).get('time','')
                flight_timing = {
                                    'departure_airport':departure_airport,
                                    'departure_time':departure_time,
                                    'arrival_airport':arrival_airport,
                                    'arrival_time':arrival_time
                }
                timings.append(flight_timing)

        flight_info={'stops':stop,
            'ticket price':formatted_price,
            'departure':departure,
            'arrival':arrival,
            'flight duration':total_flight_duration,
            'airline':airline_name,
            'plane':plane,
            'timings':timings,
            'plane code':plane_code
        }
        lists.append(flight_info)

    flightlist = sorted(lists, key=lambda k: k['ticket price'],reverse=False)

    return flightlist 



def save_json(data, source_airport, dest_airport, date):
    """
    Saves the scraped airfares as a .json file.

    Parameters
    ----------

    data: List. Required.        
        A list containing all the flight information from the source airport to
        the destination airport on the date specified.

    source_airport: String. Required. 
        The source airport code we scraped data for. 

    dest_airport: String. Required. 
        The destination airport code we scraped data for. 
    
    date: String. Required. 
        The date we scraped data for.  Must be in 'DD/MM/YYYY' format.

    Returns
    ----------

    None.  The .json file is saved as
    '<source_airport>_<dest_aiport>_<day>_<month>_<year>.json'
    """

    dt = datetime.strptime(args["date"], "%d/%m/%Y")

    fname = "{0}_{1}_{2}_{3}_{4}.json".format(args["source_airport"],
                                              args["dest_airport"],
                                              dt.day,
                                              dt.month,
                                              dt.year)

    with open(fname,'w') as fp:
        json.dump(scraped_data,fp,indent = 4)

    print("Saved data to {0}".format(fname))


if __name__ == '__main__':

    args = parse_inputs()

    scraped_data = scrape_airfares(args["source_airport"],
                                   args["dest_airport"],
                                   args["date"])
      
    save_json(scraped_data, args["source_airport"], args["dest_airport"],
              args["date"])
