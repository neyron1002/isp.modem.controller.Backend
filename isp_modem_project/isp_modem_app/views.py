from django.shortcuts import render
import requests
import urllib.parse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Modem, ACServer
import json

class CheckConnectionView(APIView):
    def get(self, request, ip, id_company):
        server_ip, server_port = get_server_details(id_company)
        
        if not server_ip or not server_port:
            return Response({"errorCode": 10}, status=status.HTTP_200_OK)
           
        query_url = f"http://{server_ip}:{server_port}/devices/?query={{\"InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.ExternalIPAddress\": \"{ip}\"}}"
        query_response = requests.get(query_url)
        
        if query_response.status_code == 200:
            try:
                data = query_response.json()
                if isinstance(data, list) and data and '_id' in data[0]:
                    _id = data[0]['_id']
                    encoded_id = encode_id(_id)
                    post_url = f"http://{server_ip}:{server_port}/devices/{encoded_id}/tasks?connection_request"
                    post_payload = {
                        "name": "refreshObject",
                        "objectName": "test"
                    }
                    post_headers = {
                        "Content-Type": "application/json"
                    }
                    post_response = requests.post(post_url, headers=post_headers, json=post_payload)

                    if post_response.status_code == 200:
                        return Response({"errorCode": 0}, status=status.HTTP_200_OK)
                    elif post_response.status_code == 202:
                        return Response({"errorCode": 1}, status=status.HTTP_200_OK)
                    else:
                        return Response({"errorCode": 2}, status=status.HTTP_200_OK)
                else:
                    return Response({"errorCode": 3}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({"errorCode": 4}, status=status.HTTP_200_OK)
        else:
            return Response({"errorCode": 5}, status=status.HTTP_200_OK)

class GetSSIDsView(APIView):
    def get(self, request, ip, id_company):
        server_ip, server_port = get_server_details(id_company)
        
        if not server_ip or not server_port:
            return Response({"errorCode": 10}, status=status.HTTP_200_OK)
        
        url = f"http://{server_ip}:{server_port}/devices/?query={{\"InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.ExternalIPAddress\": \"{ip}\"}}"
        response = requests.get(url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and data:
                    device = data[0]
                    manufacturer = device.get('_deviceId', {}).get('_Manufacturer')
                    model = device.get('_deviceId', {}).get('_OUI')
                    product_class = device.get('_deviceId', {}).get('_ProductClass')

                    modem_data = get_modem_data(manufacturer, model, product_class)
                    if not modem_data:
                        return Response({"errorCode": 6}, status=status.HTTP_200_OK)
                    
                    ssid_paths = [modem_data['paths']['ssidPath']]
                    if modem_data.get('has5g'):
                        ssid_paths.append(modem_data['paths']['ssid5gPath'])
                    
                    ssids = get_ssids_from_device(device, ssid_paths)
                    
                    if ssids:
                        return Response({"ssids": ssids, "manufacturer": manufacturer, "model": model, "productClass": product_class, "errorCode": 0}, status=status.HTTP_200_OK)
                    else:
                        return Response({"errorCode": 7, "manufacturer": manufacturer, "model": model, "productClass": product_class}, status=status.HTTP_200_OK)
                else:
                    return Response({"errorCode": 3}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({"errorCode": 4}, status=status.HTTP_200_OK)
        else:
            return Response({"errorCode": 5}, status=status.HTTP_200_OK)

class UpdateSSIDView(APIView):
    def post(self, request):
        ip = request.data.get('ip')
        new_ssid = request.data.get('newSsid')
        new_pass = request.data.get('newPass')
        id_company = request.data.get('idCompany')

        if not all([ip, new_ssid, new_pass, id_company]):
            return Response({"errorCode": 8}, status=status.HTTP_200_OK)

        server_ip, server_port = get_server_details(id_company)
        
        if not server_ip or not server_port:
            return Response({"errorCode": 10}, status=status.HTTP_200_OK)

        get_url = f"http://{server_ip}:{server_port}/devices/?query={{\"InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.ExternalIPAddress\": \"{ip}\"}}"
        get_response = requests.get(get_url)

        if get_response.status_code == 200:
            try:
                data = get_response.json()
                if isinstance(data, list) and data and '_id' in data[0]:
                    device_id = data[0]['_id']
                    encoded_id = encode_id(device_id)
                    
                    device = data[0]
                    manufacturer = device.get('_deviceId', {}).get('_Manufacturer')
                    model = device.get('_deviceId', {}).get('_OUI')
                    product_class = device.get('_deviceId', {}).get('_ProductClass')
                    
                    modem_data = get_modem_data(manufacturer, model, product_class)
                    if not modem_data:
                        return Response({"errorCode": 6}, status=status.HTTP_200_OK)

                    payload = create_payload(modem_data, new_ssid, new_pass)

                    post_url = f"http://{server_ip}:{server_port}/devices/{encoded_id}/tasks?connection_request"
                    post_response = requests.post(post_url, json=payload)
                    
                    if post_response.status_code == 200:
                        return Response({"errorCode": 0}, status=status.HTTP_200_OK)
                    else:
                        return Response({"errorCode": 9}, status=status.HTTP_200_OK)
                else:
                    return Response({"errorCode": 3}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({"errorCode": 4}, status=status.HTTP_200_OK)
        else:
            return Response({"errorCode": 5}, status=status.HTTP_200_OK)

# Helper functions

def encode_id(id):
    if id is None:
        raise ValueError("El ID no puede ser None")
    return urllib.parse.quote(str(id), safe='')

def get_modem_data(manufacturer, oui, product_class):
    try:
        modem = Modem.objects.get(Manufacturer=manufacturer, Oui=oui, ProductClass=product_class)
        return json.loads(modem.JsonParameters)
    except Modem.DoesNotExist:
        return None

def get_ssids_from_device(device, ssid_paths):
    ssids = []
    for path in ssid_paths:
        ssid_value = device
        for key in path.split('.'):
            ssid_value = ssid_value.get(key, {})
        if '_value' in ssid_value:
            ssids.append(ssid_value['_value'])
    return ssids

def create_payload(modem_data, new_ssid, new_pass):
    parameter_values = [
        [modem_data['paths']['ssidPath'], new_ssid, "xsd:string"],
        [modem_data['paths']['passwordPath'], new_pass, "xsd:string"]
    ]
    if modem_data.get('has5g'):
        parameter_values.append([modem_data['paths']['ssid5gPath'], f"{new_ssid}_5G", "xsd:string"])
        parameter_values.append([modem_data['paths']['password5gPath'], new_pass, "xsd:string"])
    
    return {
        "name": "setParameterValues",
        "parameterValues": parameter_values
    }

def get_server_details(id_company):
    try:
        server = ACServer.objects.get(IdCompany=id_company, IsEnabled=True)
        return server.ServerAccessIp, server.Port
    except ACServer.DoesNotExist:
        return None, None