""" Module for Address table."""
import sqlite3
from fastapi import HTTPException


def setup_address():
    """ Creates the database and table if they're not yet existing."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS address(longitude, latitude, name)')
    con.commit()


def is_empty():
    """ Checks if the address table is empty."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM address')
    return cur.fetchone() is None


def insert_sample_addresses():
    """ Inserts sample data into the address table"""
    sample_data = [
        {'longitude': 14.652014090305315, 'latitude': 121.03239208494593, 'name': 'MRT-3 North Avenue Station'},
        {'longitude': 14.646571274698536, 'latitude': 121.03774575390592, 'name': 'MRT-3 Quezon Avenue Station'},
        {'longitude': 14.63559453870884, 'latitude': 121.04326675579757, 'name': 'MRT-3 GMA Kamuning Station'},
        {'longitude': 14.62021503109602, 'latitude': 121.05126478009082, 'name': 'MRT-3 Cubao Station'},
        {'longitude': 14.607646761214939, 'latitude': 121.05665079304319, 'name': 'MRT-3 Santolan-Anapolis Station'},
        {'longitude': 14.588013323020583, 'latitude': 121.05658510797447, 'name': 'MRT-3 Ortigas Station'},
        {'longitude': 14.581579958048176, 'latitude': 121.05408022421689, 'name': 'MRT-3 Shaw Boulevard Station'},
        {'longitude': 14.5738587523626, 'latitude': 121.0480101360587, 'name': 'MRT-3 Boni Station'},
        {'longitude': 14.56686874135519, 'latitude': 121.04540040332779, 'name': 'MRT-3 Guadalupe Station'},
        {'longitude': 14.554885349456182, 'latitude': 121.03453663135889, 'name': 'MRT-3 Buendia Station'},
        {'longitude': 14.549130558531793, 'latitude': 121.02710455167781, 'name': 'MRT-3 Ayala Station'},
        {'longitude': 14.541939162522192, 'latitude': 121.01945389330639, 'name': 'MRT-3 Magallanes Station'},
        {'longitude': 14.537887098300516, 'latitude': 121.00126586520338, 'name': 'MRT-3 Taft Avenue Station'},
    ]

    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    cur.executemany('INSERT INTO address VALUES(:longitude, :latitude, :name)', sample_data)
    con.commit()


def get_all_addresses():
    """ Gets all addresses."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    cur.execute('SELECT longitude, latitude, name FROM address')

    return {
        'results': [
            {
                'longitude': longitude,
                'latitude': latitude,
                'name': name,
            }
            for longitude, latitude, name
            in cur.fetchall()
        ]
    }


def get_address(address_name: str):
    """ Gets a specific address."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    data = {'name': address_name}
    try:
        cur.execute('SELECT longitude, latitude, name FROM address WHERE name = :name', data)
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    address = cur.fetchone()
    if address is None:
        raise HTTPException(status_code=404, detail='address not found')

    longitude, latitude, name = address
    return {
        'longitude': longitude,
        'latitude': latitude,
        'name': name,
    }


def update_address(address_name: str, longitude: float, latitude: float):
    """ Updates a specific address."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    data = {
        'longitude': longitude,
        'latitude': latitude,
        'name': address_name,
    }
    try:
        execute = cur.execute('''
            UPDATE address
            SET longitude = :longitude, latitude = :latitude
            WHERE name = :name
        ''', data)
        con.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    if execute.rowcount == 0:
        raise HTTPException(status_code=404, detail='address not found')

    return get_address(address_name)


def create_address(address_name: str, longitude: float, latitude: float):
    """ Creates a new address."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    try:
        address = get_address(address_name)
        if address is not None:
            raise HTTPException(status_code=409, detail='address already exists')
    except HTTPException as error:
        if error.detail != 'address not found':
            raise error from error

    data = {
        'longitude': longitude,
        'latitude': latitude,
        'name': address_name,
    }
    try:
        execute = cur.execute('''
            INSERT INTO address VALUES (:longitude, :latitude, :name)      
        ''', data)
        con.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    if execute.rowcount == 0:
        raise HTTPException(status_code=500)

    return get_address(address_name)


def delete_address(address_name: str):
    """ Deletes a specific address."""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    address = get_address(address_name)

    data = {'name': address_name}
    try:
        execute = cur.execute('''
            DELETE FROM address
            WHERE name = :name
        ''', data)
        con.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    if execute.rowcount == 0:
        raise HTTPException(status_code=500)

    return address


def delete_all():
    """ Deletes all addresses"""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    addresses = get_all_addresses()

    try:
        cur.execute('DELETE FROM address')
        con.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    return addresses


def get_addresses_in_range(
    source_longitude: float,
    source_latitude: float,
    distance: float
):
    """ Gets address that are within a given distance"""
    con = sqlite3.connect('address_book.db')
    cur = con.cursor()
    data = {
        'source_longitude': source_longitude,
        'source_latitude': source_latitude,
        'distance': distance,
    }
    try:
        cur.execute('''
            SELECT longitude, latitude, name
            FROM address
            WHERE (
                ((longitude - :source_longitude) * (longitude - :source_longitude))
                + ((latitude - :source_latitude) * (latitude - :source_latitude))
            ) <= (:distance * :distance)
        ''', data)
    except sqlite3.Error as error:
        raise HTTPException(status_code=500) from error

    return {
        'results': [
            {
                'longitude': longitude,
                'latitude': latitude,
                'name': name,
            }
            for longitude, latitude, name
            in cur.fetchall()
        ]
    }
