""" Module for setting up sqlite"""
import address_table

def setup_database():
    """ Sets up database related resources."""
    address_table.setup_address()
    if address_table.is_empty():
        address_table.insert_sample_addresses()
