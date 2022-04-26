""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
"""
from pip._vendor import requests
import shutil
import sqlite3
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
import os.path
import os
from os import path
from os.path import exists
import ctypes
import hashlib
from urllib import response



from requests import request
import requests

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = download_apod_image(apod_info_dict)
    image_msg = download_apod_image
    h = hashlib.sha256(image_url.encode())
    image_sha256 = str(h.digest())
    image_path = get_image_path(image_url, image_dir_path)
    image_size = len(image_path)
  

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    filename = image_url.split("/")[-1]
    wallpaper = os.path.join(image_path,filename)
    set_desktop_background_image(wallpaper)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    
    filename = image_url.split("/")[-1]
    full_path = os.path.join(dir_path, filename)
    print(full_path)
    return full_path

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    nasa_api = 'https://api.nasa.gov/planetary/apod?api_key='
    my_key = 'NQPZ8KD9a3Cx6p8cIKx8sQGwsh1v1x6F3h7MBAIc'
    print("Getting APOD Information... ")

    parameters = (nasa_api + my_key + "&date=" + date)
      
    response = requests.get(parameters)

    if response.status_code == 200:
        
        print('Response:',response.status_code, '🎉🎉🎉', '\n')
        print("Success APOD Obtained")
        info =response.json() 
        info_dict= dict(info)
        
        return info_dict
        
    else:
        print('Failed. Response code:',response.status_code)
        return None

    

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """    
    print("The URL of the APOD is " + image_url)
    print("The full path of the APOD is " + image_path)
    print("The APOD size is ", image_size, " KB" )
    print("The Hash for the file is ", image_sha256)

def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    picture = image_url['url']
    pic_info = requests.get(picture)
    if pic_info.status_code == 200: 
        print('Response:',pic_info.status_code, '🎉🎉🎉', '\n')
        print("Success connection")
        return picture

    else:
        print('Failed to download APOD',pic_info.status_code)
        return None

def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    URL = image_msg
    req = requests.get(URL, stream=True)

    if req.status_code == 200:
        print('Response:',req.status_code, '🎉🎉🎉', '\n')
        print("Save Succesfull")
             
    else:
        print('Failed to download APOD',req.status_code)

    get_filename = image_msg.split("/")[-1]
    full_path = os.path.join(image_path,get_filename)
    req.raw.decode_content = True
    with open(full_path,'wb') as f:
        shutil.copyfileobj(req.raw, f)
    
    return None
    

def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """

    file_path = db_path
    file_exist = exists(file_path)
    if file_exist == False:
        db_path = sqlite3.connect(file_path)
        cursor = db_path.cursor()

        cursor.execute("""CREATE TABLE "NASA APOD"(
            image path text,
            image_url text,
            image_size integer,
            image_sha256 text
        )
            """) 
        db_path.commit()
        db_path.close()
    return None

def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO 'NASA APOD' (image_path, image_url, image_size, image_sha256) VALUE (?,?,?,?"), (db_path, image_path, image_size, image_sha256)
    connection.commit()
    connection.commit()
    return None

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT 'image_sha256' FROM 'NASA APOD'")
    get_hash = cursor.fetchall()
    cursor.close()
    if image_sha256 in get_hash:
        return True
    else: 
        return False

def set_desktop_background_image(wallpaper):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    ctypes.windll.user32.SystemParametersInfoW(20,0,wallpaper,3)
    return None
main()