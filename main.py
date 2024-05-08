""" Main function for FastAPI."""
from fastapi import FastAPI
from pydantic import BaseModel

import setup_sqlite
import address_table

setup_sqlite.setup_database()


class Address(BaseModel):
    """ Model of an Address."""
    name: str
    longitude: float
    latitude: float


class Coordinates(BaseModel):
    """ Model of Coordinates."""
    longitude: float
    latitude: float


app = FastAPI()


@app.get('/address/')
def get_all():
    """ Gets all addresses."""
    return address_table.get_all_addresses()

@app.get('/address/{address_name}')
def get_address(address_name: str):
    """ Gets a specific address."""
    return address_table.get_address(address_name)

@app.put('/address/{address_name}')
def update_address(address_name: str, coords: Coordinates):
    """ Updates a specific address."""
    return address_table.update_address(address_name, coords.longitude, coords.latitude)

@app.post('/address/')
def create_address(address: Address):
    """ Creates a new address."""
    return address_table.create_address(address.name, address.longitude, address.latitude)

@app.delete('/address/{address_name}')
def delete_address(address_name: str):
    """ Deletes a specific address."""
    return address_table.delete_address(address_name)

@app.get('/address-range')
def get_addresses_in_range(longitude: float, latitude: float, distance: float):
    """ Gets address that are within a given distance"""
    return address_table.get_addresses_in_range(longitude, latitude, distance)

@app.delete('/address/')
def delete_all():
    """ Deletes all addresses"""
    return address_table.delete_all()
