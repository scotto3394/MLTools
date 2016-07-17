import os
import zipfile
import tarfile
from pymongo import MongoClient
import sys
import csv
import subprocess

#==============================================================================
# Helper Functions
#==============================================================================
def getDatabase(database):
    '''
    Initialize connection to database (local MongoDB server).

    Args: 
        database: Name of database to use.
    
    Returns:
        db: pymongo database object
    
    Note: Functionality is extremely limited for this function at the moment.
    '''
    client = MongoClient()
    db = client[database]

    return db

def smallFile(compressedFile, targetFile, dbCollection):
    '''
    File to insert small compressed files into a specified MongoDB database collection (via 10000 line batches)

    Args:
        compressedFile: The compressed file were the data is.
        targetFile: The specific file, inside the compressed file, which we are inserting.
        dbCollection: The pymongo collection object we are inserting into.

    Returns:
        cnt: Number of lines inserted from the file into the database collection.
    '''

    with compressedFile.open(targetFile,'r') as f: #Look into compressed File
        r = csv.DictReader(f)
        insertList = []
        cnt = 0
        # Run through file, inserting mini-batches
        for line in r:
            insertList.append(line)
            cnt += 1
            if cnt % 10000 == 0:
                dbCollection.insert_many(insertList, ordered = False)
                insertList = []
        dbCollection.insert_many(insertList, ordered = False)
    return cnt

def largeFile(compressedFile, targetFile, dbCollection):
    '''
    File to larger compressed files into a specified MongoDB database collection (via decompressing and large batch insert)

    Args:
        compressedFile: The compressed file were the data is.
        targetFile: The specific file, inside the compressed file, which we are inserting.
        dbCollection: The pymongo collection object we are inserting into.

    Returns:
        cnt: Number of lines inserted from the file into the database collection.
    '''
    collectionString = str(dbCollection.name)
    dbString = str(dbCollection.database.name)

    # Extract the file
    print("Extracting file...")
    compressedFile.extract(targetFile)
    print("Checking document size...")
    cnt = subprocess.check_output(['wc','-l',targetFile])

    # Use mongoinsert to insert in bulk
    print("Inserting document... (This may take a while)")
    subprocess.call(['mongoimport','-d',dbString, '-c', collectionString, '--type','csv','--file',targetFile,'--headerline'])

    # Clean up
    print("Cleaning up...")
    os.remove(targetFile)

    return cnt

def cleanDB(condition, collectionObject):
    '''
    Pymongo interface to remove all the documents from a collection that meet a certain condition.

    Args:
        condition (JSON): removal condition for the documents
        collectionObject: pymongo collection object we are removing documents from

    Returns:
        result: object containing information about the size/success of the deletion
    '''
    result = collectionObject.delete_many(condition)
    return result
#===============================================================================
# Extraction Methods
#===============================================================================
def extractCSV(fileName, folder = False, verbose = True, Override = False):
    '''
    Extract a compressed .csv file (from zip/tar).

    Args:
        fileName: Name of the file/folder you are decompressing.
        folder (Bool): Flag indicating whether you are extracting a file or a folder full of files.
        verbose (Bool): Flag indicating whether you want verbose output.
        Override (Bool): Flag indcating whether you want to overwrite the file if already extracted.

    Returns:
        None
    '''

    # Folder vs File detection
    if folder:
        absFilePath = os.path.abspath(fileName)
        filePaths = [os.path.join(absFilePath,name) for name in os.listdir(absFilePath)]
    else:
        filePaths = [os.path.abspath(fileName)]

    for file in filePaths:
        dirname, basename = os.path.split(file)
        nameSplit = basename.split('.')

        # Check if file has already been processed (or doesn't need to be)
        if os.path.exists(os.path.join(dirname, nameSplit[0] + ".csv")) and ~Override:
            if verbose:
                print("{} already processed".format(nameSplit[0] + ".csv"))

            continue

        if verbose:
            print("Processing {}".format(basename))
        # Extract the file
        if nameSplit[-1] == "zip":
            zipF = zipfile.ZipFile(file,'r')
            if verbose:
                print("Extracting...")
            zipF.extractall(dirname)
            if verbose:
                print("Done!")
            zipF.close()
        if nameSplit[-1]  == "tar" or nameSplit[-1]  == "bz":
            tarF = tarfile.TarFile(file,'r')
            if verbose:
                print("Extracting...")
            tarF.extractall(dirname)
            if verbose:
                print("Done!")
            tarF.close()

def insertMongo(fileName, dbName, collectionPairs = {}, folder = False, verbose = True, Override = False):
    '''
    Extract data from a compressed .csv file (from zip/tar) and inserts into (local) MongoDB database.

    Args:
        fileName: Name of the file/folder you are decompressing.
        dbName: Name of the database to insert files into.
        collectionPairs (Dict): Information specifying what collection to insert the file information into, e.g. {fileName1: collectionName1, fileName2, collectionName2}. If not specified, user will be prompted on stdin.
        folder (Bool): Flag indicating whether you are extracting a file or a folder full of files.
        verbose (Bool): Flag indicating whether you want verbose output.
        Override (Bool): Flag indcating whether you want to overwrite the file if already extracted.

    Returns:
        None
    '''
    # Folder vs File detection, db setup
    if folder:
        absFilePath = os.path.abspath(fileName)
        filePaths = [os.path.join(absFilePath,name) for name in os.listdir(absFilePath)]
    else:
        filePaths = [os.path.abspath(fileName)]

    db = getDatabase(dbName)

    for file in filePaths:
        dirname, basename = os.path.split(file)
        nameSplit = basename.split('.')

        # Check if file has already been processed (or doesn't need to be)
        if db.processed.find({"filePath": {"$exists": "true", "$eq": os.path.join(dirname, nameSplit[0] + '.csv')}}).count() > 0 and ~ Override:
            if verbose:
                print("{} already in the database".format(basename))

            continue
        else:

            if verbose:
                print("Processing {}".format(basename))
            # Identify the file
            if nameSplit[-1] == "zip":
                smallF = zipfile.ZipFile(file,'r')
            elif nameSplit[-1]  == "tar" or nameSplit[-1]  == "bz":
                smallF = tarfile.TarFile(file,'r')
            else:
                continue

            if verbose:
                print("Extracting...")
            for subFile in smallF.namelist(): # Loop through contents of compressed file
                if subFile in collectionPairs:
                    collectionName = collectionPairs[subFile]
                else:
                    sys.stdout.flush()
                    collectionName = raw_input("Input Collection name for {}: ".format(subFile))

                collection = db[collectionName]

                # Need a large file protocol and a small file protocol
                if smallF.getinfo(subFile).file_size < 100000000:
                    cnt = smallFile(smallF,subFile,collection)
                else:
                    cnt = largeFile(smallF,subFile,collection)


                db.processed.insert_one({"filePath": os.path.join(dirname,subFile), "lineCount": cnt})
            if verbose:
                print("Done!")
            smallF.close()

def insertSQL(fileName):
    #only supports SQLite right now
    pass
