import re
import os
import subprocess
import string
import pandas as pd

#  OBTAININGE TAXON ID FROM USER


def gettaxonid():
    # saving the users home directory path as a variable
    home_dir = "."
    userchoice = input('\nPlease input the taxonomic group\n').strip().lower()
    print('\n')
    # Creating a list of numbers 0-9 and a list of the letter of the alphabet to check against the users input
    nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    letters = list(string.ascii_lowercase)
    checkletters = any(ele in userchoice for ele in letters)
    checknums = any(ele in userchoice for ele in nums)
    # Checks if user input was alphabetical, and then perform esearch
    if checkletters == True and checknums == False:
        print('\n')
        print('esearch results are displayed below:\n')
        # Displays esearch results in genebank format
        subprocess.call("esearch -db taxonomy -query %s | efetch -format Gb" %
                        (userchoice), shell=True)
        print('\n')
        output = subprocess.check_output("esearch -db taxonomy -query %s | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
        outputdecode = output.decode("utf-8").strip()
        # a list containing the taxon and taxonIDs from esearch results is created
        taxonidlist = re.split(r"[\t\n]", outputdecode)
    # Checks if user input was numerical, and then performs esearch
    elif checkletters == False and checknums == True:
        print('\n')
        print('esearch results are displayed below:\n')
        # Displays esearch results in genebank format
        subprocess.call("esearch -db taxonomy -query %s[UID] | efetch -format Gb" % (userchoice), shell=True)
        print('\n')
        output = subprocess.check_output("esearch -db taxonomy -query %s[UID] | efetch -format xml | xtract -pattern Taxon -element ScientificName -element TaxId" % (userchoice), shell=True)
        outputdecode = output.decode("utf-8").strip()
        # a list containing the taxon and taxonIDs from esearch results is created
        taxonidlist = re.split(r"[\t\n]", outputdecode)
    else:
        print('\nInput requires only taxonID or taxonomy, Either "8782" or "aves")')
        taxonidlist = gettaxonid()
    # Checking if the esearch had valid output.
    if len(taxonidlist) == 1:
        print('\nThe esearch for %s taxonomy found no results.' % (userchoice))
        taxonidlist = gettaxonid()
    return taxonidlist, home_dir


#  CHECKING FOR MULTIPLE RESULTS


def checktaxid(idlist):
    # If length of list is greater than 3, the Taxon esearch generated more than one output
    if len(idlist) > 3:
        # Asks the user to input one of the available options from the esearch
        choice = input('\nPlease type the name of the desired output\n').strip().lower().capitalize()
        if choice in idlist:
            for item in idlist:
                # If the input matched an element from the list, 
                # items apart from the users choice will be deleted from the list
                if item == choice:
                    index = idlist.index(item)
                    del idlist[:index]
                    del idlist[index + 2:]
        # If theinput was not one of the available options on the list, the function will restart
        else:
            print('\nYou did not input one of the available choices')
            idlist = checktaxid(idlist)
    # taxonIDs get updated, this creates a list, with 3 elements, Taxon name, TaxonID new, TaxonID old.
    # the old taxon ID will be deleted
    elif len(idlist) == 3:
        del idlist[2:]
    # If list length is 2, this Taxon esearch generated a single taxon.
    elif len(idlist) == 2:
        return idlist
    return idlist

#  OBTAINING WORK DIRECTORY NAME

def get_available_name(base_name, existing_folders):
    number = 1
    new_name = base_name
    while new_name in existing_folders:
        number += 1
        new_name = f"{base_name}_{number}"
    return new_name


def create_folder(folder_name):
    try:
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
        return folder_name
    except FileExistsError:
        return None


def get_folder_name():
    default_folder = 'data'
    folder_name = input(f"Enter data folder name (default: {default_folder}): ").strip() or default_folder
    return folder_name


def getworkpath():
    while True:
        folder_name = get_folder_name()
        if (created_folder := create_folder(folder_name)) is not None:
            return created_folder
        else:
            user_response = input(f"Folder '{folder_name}' already exists.\n"
                                  "Do you want to\n1. Remove it\n2. Rename it\n3. Choose a different name?\nEnter the number:\n")

            if user_response == '1':
                try:
                    subprocess.call('rm -fr %s' % (folder_name), shell=True)
                    print(f"Folder '{folder_name}' removed.")
                except OSError as e:
                    print(f"Error removing folder: {e}")
            elif user_response == '2':
                new_name = get_available_name(folder_name, os.listdir())
                print(f"Suggested new name: '{new_name}'")
                return create_folder(new_name)
            elif user_response == '3':
                print("Operation canceled. Please choose a different folder name.")
                continue
            else:
                print("Invalid option. Please choose 1, 2, or 3.")
    

# OTAINING NAME OF PROTEIN

def getprotein (idlist):
    # Ask the user to input the protein of interest
	protchoice = input('\nPlease specify your family of Protein of interest for the %s taxon\n' % (idlist[0])).strip().lower()
	return protchoice

#  CREATING SPECIES, TAXID, ACCESSION AND PROTEIN LENGTH LISTS FROM ESEARCH RESULTS #


def listmaker(workpath):
    # Creating the list of species names 
    tempcmd = "cat %s/docsum.txt | xtract -pattern Organism -element Organism" % (workpath)
    protspecies = subprocess.check_output(tempcmd, shell=True)
    protspeciesdec = protspecies.decode("utf-8").strip()
    protspecieslist = re.split(r"[\n]", protspeciesdec)
    # Creating the list of taxonIDS
    protspeciestaxid = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element TaxId" % (workpath), shell=True)
    protspeciestaxiddec = protspeciestaxid.decode("utf-8").strip()
    protspeciestaxidlist = protspeciestaxiddec.split()
    # Creating the list of Protein Accession numbers 
    protspeciesaccession = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element AccessionVersion" % (workpath), shell=True)
    protspeciesaccessiondec = protspeciesaccession.decode("utf-8").strip()
    protspeciesaccessionlist = protspeciesaccessiondec.split()
    # Creating the list of Protein lengths
    protlength = subprocess.check_output("cat %s/docsum.txt | xtract -pattern DocumentSummary -element Slen" % (workpath), shell=True)
    protlengthdec = protlength.decode("utf-8").strip()
    protlengthlist = protlengthdec.split()
    # Converting protein length list from a string to integers
    protlengthlistint = list(map(int, protlengthlist))
    return protspecieslist, protspeciestaxidlist, protspeciesaccessionlist, protlengthlistint

# CHECKING SEQUENCES WITH TAXID AND PROTEIN  #


def checkseq(idlist, protchoice, workpath):
     
    # performing esearch
    equery = "esearch -db protein -query 'txid%s[Organism:exp] AND %s NOT PARTIAL' | efetch -format docsum > %s/docsum.txt" % (idlist[1], protchoice, workpath)
    print("Searching ...\n")
    subprocess.call(equery, shell=True)
    # Running previous function will make all lists required to create the panda dataframe from results   
    protspecieslist, protspeciestaxidlist, protspeciesaccessionlist, protlengthlistint = listmaker(workpath)
    # generating panda dataframe using the lists created with function 4.0
    s1 = pd.Series(protspecieslist)
    s2 = pd.Series(protspeciestaxidlist)
    s3 = pd.Series(protspeciesaccessionlist)
    s4 = pd.Series(protlengthlistint)
    # These are the dataframe columns: Species Name, Species TaxID, Protein Accession, Protein length
    df = pd.DataFrame({'Species Name' : s1, 'Species TaxID' : s2, 'Prot Accession' : s3, 'Prot Length' : s4})
    # Obtaining the total number of sequences by using the first index of the df.shape
    totalseq = df.shape[0]
    # Obaining the total number of unique species
    uniquespecies = len(df.drop_duplicates('Species Name'))
    # the following will occur if the total number of sequences found from the esearch is less than 10
    if totalseq < 10:
        print('fewer than 10 sequences were found\n')
        choices = input('Are you sure to do new search? y/n\n').strip().lower()
        # continue search with other protein name
        if choices == "y":
            print('\n')
            checkseq(idlist, workpath)
        # stop search
        elif choices == "n":
            print('\nStop search\n')
            exit(0)
        else:
            print('\nINVALID INPUT PLEASE TRY AGAIN')
    # the following will occur if the total number of unique sequences found	from the esearch is less than 10
    if uniquespecies < 5:
        print('\n')
        print('Fewer than 5 unique sequences were found:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseq, uniquespecies))
        choices = input('Are you sure to do new search? y/n\n').strip().lower()
        # continue search with other protein name
        if choices == "y":
            print('\n')
            checkseq(idlist, workpath)
        # stop search
        elif choices == "n":
            print('\nStop search\n')
            exit(0)
        else:
            print('\nINVALID INPUT PLEASE TRY AGAIN')
    # Prints esearch output summary: total number of sequences, number of unique species
    print('\n')
    print('Results from the esearch are displayed below:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseq, uniquespecies))
    print('\n')
    # Creating a list of species names
    protspeciesl = df['Species Name'].tolist()
    # Creating a dictionary of Species : Sequence counts)
    numberoffasta = dict((x, protspecieslist.count(x)) for x in set(protspecieslist))
    # Printing the top 3 most represented species. 
    # Achieved bysorting the dictionary from highest to loweres and appending the top 3 to a list
    print('The top 3 most species are displayed below:\n')
    highestkey = sorted(numberoffasta, key=numberoffasta.get, reverse=True)[:3]
    highestvalue = []
    for item in highestkey:
        value = numberoffasta.get(item)
        highestvalue.append(value)
    print('\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\n' % (highestkey[0], highestvalue[0], highestkey[1], highestvalue[1], highestkey[2], highestvalue[2]))
    print('\n')
    print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
    print('\n')
    # view = input('\nWould you like to view the full list of species and their respective number of FASTA sequences? y/n\n')
    # Print the key of the dictionary (species), followed by the count (value) will be printed to the user
    for key, value in numberoffasta.items():
        print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
    return protchoice, protspeciesl, df, workpath


# DETERMINING IF THE OUTPUT IS THE DESIRED OUTPUT  #


def change(idlist, protchoice, df, workpath):
    # While True loop acts as an error trap
    while True:
        finalanswer = input('\nWould you like to soldier on with the analsis? y/n\n').strip().lower()
        # Creating the list of available options for the user
        changelist = ['1', '2', '3']
        print('\n\n')
        # If finalanswer == 'y', the function ends
        if finalanswer == 'y':
            return protchoice, idlist, df, workpath
        # If final answer == 'n', the script will ask the user which of the available esearch inputs they would like to use.
        elif finalanswer == 'n':
            print('\n')
            print('your current search parameters are:\n\n1: [Taxon] %-25s [TaxonID] %-10s\n2: [Protein] %s\n' % (idlist[0], idlist[1], protchoice))
            print('\n')
            # While true loop acts as an error trap.
            while True:
                tochange = input('\nWhich would you like to change?\nEnter the digit:\n\t1 : To change Taxon,\n\t2 : To change Protein,\n\t3 : To change Taxon + Protein.\n').strip()
                # Checks user input against the earlier created list ['1', '2', '3']
                # if the user input is 1, the following will occur
                if tochange == changelist[0]:
                    subprocess.call('rm -fr %s' % (workpath), shell=True)
                    idlist, home_dir = gettaxonid()
                    idlist = checktaxid(idlist)
                    protchoice, protspecieslist, df, workpath = checkseq(idlist, protchoice, workpath)
                    protchoice, idlist, df, workpath = change(idlist, protchoice, df, workpath)
                    return protchoice, idlist, df, workpath
                # If input is 2, the following will occur
                elif tochange == changelist[1]:
                    subprocess.call('rm -fr %s' % (workpath), shell=True)
                    protchoice = getprotein(idlist)
                    protchoice, protspecieslist, df, workpath = checkseq(idlist, protchoice, workpath)
                    protchoice, idlist, df, workpath  = change(idlist, protchoice, df, workpath)
                    return protchoice, idlist, df, workpath
                # If input is 3, the following will occur
                elif tochange == changelist[2]:
                    subprocess.call('rm -fr %s' % (workpath), shell=True)
                    idlist, home_dir = gettaxonid()
                    idlist = checktaxonid(idlist)
                    protchoice  = getprotein(idlist)
                    protchoice, protspecieslist, df, workpath = checkseq(idlist, protchoice, workpath)
                    protchoice, idlist, df, workpath = change(idlist, protchoice, home_dir, df, workpath)
                    return protchoice, idlist, df, workpath
                else:
                    print('INVALID INPUT')
        else:
            print('please try again')
            return protchoice, idlist, df, workpath

# WARNING THE USER OF THE PRESENCE OF SEQUENCES WITH LOW/HIGH STANDARD DEVIATIONS


def checkingstandarddeviation(df):

    # first step is to obtain the shortest length protein from the dataframe, this is saved as a variable called min
    min = df['Prot Length'].min()
    # next the longest protein must be obtained and saved as a variable called max
    max = df['Prot Length'].max()
    # then we must get the mean length of proteins within the data frame and save this as a variable
    mean =df['Prot Length'].mean()
    # using the above three variables, the standard deviation of each of the lengths of proteins within the dataframe can be calculated
    std = df['Prot Length'].std()
    # the mean, standard deviation and the min and max of each protein sequence is then displayed to the user
    print('\n')
    print('Protein Length Statistics:\n\n\tMinimum Length:                  %s\n\tMaximum Length:                  %s\n\tMean Length:                     %.2f\n\tStandard Deviation:             %.2f' % (min, max, mean, std))
    # if the max sequence length is found to be >1 std above or below the mean, the following will be displayed to the user
    if max > (mean + std) or min < (mean - std):
        print('\nATTENTION')
        print('\nthe max or min length protein is >1 std from the mean')
        print('\nif this is the case, then there is a possibility of the presence of an outlier')
        print('\nYou may want to consider removing certain sequences')
    return min, max, mean, std

# DISPLAYING TO THE USER THE NUMBER OF SEQUENCES WHOSE STDs ARE ABOVE THE MEAN AND ALLOWING THEIR REMOVAL


def standarddeviationabove(df, min, max, mean, std):
    # while loop here acts as an error trap, this is here if the user does not enter one of the required inputs
    while True:
        # if the largest protein length if more than 1 std above the mean, the following will occur:		
        if max > (mean + std):
            print("\nMAXIMUM LENGTH SEQUENCE IS >1 STD ABOVE THE MEAN\n")
            print('\n\t-Choice-\t-Action-')
            print('\t0\t:\t[DO NOT REMOVE]    any sequences')
            stdabovecheck = mean
            n = 1
            # another while loop which looks for sequences with std above the mean protein length
            # with each time this loop goes around the number of stds will increases, unless zero standard deviations are found or if it reaches the value of 5
            while stdabovecheck < max and n <= 5:
                stdabovecheck = mean + std*n
                stdabove = df[df.apply( lambda x : x['Prot Length'] > (mean + std*n), axis=1 )].shape[0]
                if stdabove == 0:
                    break
                print('\t%s\t:\t[REMOVE SEQUENCES] %s Sequences     that are     %s Standard Deviations above the Mean' % (n, stdabove, n))
                totalabove = n
                n += 1
            # the user will be faced with a decision based on information obtained from the above commands
            # the user will be asked to provide the script with a digit
            choice = input('\nplease input a digit of your choosing, the sequences to be removed will be displayed after your choice has been made\n').strip()
            # a list containing options for the user must is created
            a = range(0, totalabove + 1)
            stdabovelist = list(map(str, a))
            # the list is referenced to the user to check if the user input was valid
            check = any(item in choice for item in stdabovelist)
            if check:
                # the input of the user determines the number of sequences that the user wants to remove
                # if the input is 0, the following will occur
                if choice == "0":
                    print('\n')
                    return df
                else:
                    # if the user input is not 0, the actual number of stds above the mean have been inputted by the user
                    # the user input must be converted into an integer
                    choice = int(choice)
                    # the script will then go on to locate the sequence that need to be removed
                    # once these sequence have been identified they are saved into a new dataframe, once this has occured the index is reset
                    stdaboveremove = df[df.apply( lambda x : x['Prot Length'] > (mean + std*choice), axis=1 )]
                    stdaboveremove.reset_index(drop=True, inplace=True)
                    # these particular sequences are now to be removed from the dataframe and saved to a new one
                    newdf = df[~df.apply( lambda x : x['Prot Length'] > (mean + std*choice), axis=1 )]
                    print('\n')
                    # the dataframe containing the sequences that are to be removed is displayed to the user
                    # the user is asked if they are happy with the removal of these sequences
                    print(stdaboveremove)
                    choices = input('\nyou have chosen for these sequences to be removed from the dataframe, are you happy with this decision? y/n\n').strip().lower()
                    # if the user is happy with their decision and inputs y, the datafram is saved with the selected sequences removed, the function ends
                    if choices == "y":
                        print('\n')
                        return newdf
                    # if the user is not happy with their decision and inputs n, the function will restart
                    elif choices == "n":
                        print('\nlets try that again, please select the sequences to be removed again\n')
                    else:
                        print('\nINVALID INPUT PLEASE TRY AGAIN')
            else:
                print('\n')
                print('INVALID INPUT, PLEASE TRY AGAIN')

# DISPLAYING TO THE USER THE NUMBER OF SEQUENCES WHOSE STDs ARE BELOW THE MEAN AND ALLOWING THEIR REMOVAL


def standarddeviationbelow(df, min, max, mean, std):
    # while loop here acts as an error trap, this is here if the user does not enter one of the required inputs
    while True:
        # if the smallest  protein length is more than 1 std below the mean, the following will occur:
        if min < (mean - std):
            print("\nMINIMUM LENGTH SEQUENCE IS >1 STD BELOW THE MEAN\n")			
            print('\n\t-Choice-\t-Action-')
            print('\t0\t:\t[DO NOT REMOVE]    any sequences')
            stdbelowcheck = mean
            n = 1
            # another while loop which looks for sequences with std below the mean
            # with each time this loop goes around the number of stds will increases, unless zero standard deviations are found or if it reaches the value of 5
            while stdbelowcheck > min and n <= 5:
                stdbelowcheck = mean - std*n
                stdbelow = df[df.apply( lambda x : x['Prot Length'] < (mean - std*n), axis=1 )].shape[0]
                if stdbelow == 0:
                    break
                print('\t%s\t:\t[REMOVE SEQUENCES] %s Sequences     that are     %s Standard Deviations below the Mean' % (n, stdbelow, n))
                totalbelow = n
                n += 1
            # the user will be faced with a decision based on information obtained from the above commands
            # the user will be asked to provide the script with a digit
            choice = input('\nplease input a digit of your choosing, the sequences to be removed will be displayed after your choice has been made\n').strip()
            # a list containing options for the user must is created
            b = range(0, totalbelow + 1)
            stdbelowlist = list(map(str, b))
            # the list is referenced to the user to check if the user input was valid
            check = any(item in choice for item in stdbelowlist)
            if check == True:
                # the input of the user determines the number of sequences that the user wants to remove
                # if the input is 0, the following will occur
                if choice == "0":
                    print('\n')
                    return df
                # if the user input is not 0, the actual number of stds below the mean have been inputted by the user
                # the user input must be converted into an integer
                else:
                    choice = int(choice)
                    # the script will then go on to locate the sequence that need to be removed
                    # once these sequence have been identified they are saved into a new dataframe, once this has occured the index is reset
                    stdbelowremove = df[df.apply( lambda x : x['Prot Length'] < (mean - std*choice), axis=1 )]
                    stdbelowremove.reset_index(drop=True, inplace=True)
                    # these particular sequences are now to be removed from the dataframe and saved to a new one
                    newdf = df[~df.apply( lambda x : x['Prot Length'] < (mean - std*choice), axis=1 )]
                    print('\n')
                    # the dataframe containing the sequences that are to be removed is displayed to the user
                    # the user is asked if they are happy with the removal of these sequences
                    print(stdbelowremove)
                    choices = input('\nyou have chosen for these sequences to be removed from the dataframe, are you happy with this decision? y/n\n').strip().lower()
                    # if the user is happy with their decision and inputs y, the datafram is saved with the selected sequences removed, the function ends
                    if choices == "y":
                        print('\n')
                        return newdf
                    # if the user is not happy with their decision and inputs n, the function will restart
                    elif choices == "n":
                        print('\nlets try that again, please select the sequences to be removed again\n')
                    else:
                        print('\nINVALID INPUT PLEASE TRY AGAIN')
            else:
                print('\n')
                print('INVALID INPUT, PLEASE TRY AGAIN')

# UPDATING THE DATAFRAME AND DISPLAYING THE NEW DATAFRAME TO THE USER


def updatedataframe(df, idlist, protchoice, workpath):
    # function will starting my counting the number of sequences and also the number of unique species within the dataframe
    total = df.shape[0]
    unique = len(df.drop_duplicates('Species Name'))
    # function will then create a list containing the different species within the dataframe
    specieslist = df['Species Name'].tolist()
    # the function will now display a summary of the info within the dataframe
    print('\n')
    print('A summary of the search results are displayed below:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, total, unique))
    # the function will then go on to create a dictionary of species : sequence counts
    numberoffasta = dict((x, specieslist.count(x)) for x in set(specieslist))
    print('\n')
    # function will then procede to show the user the 3 species with the highest number of sequences
    highestkey = sorted(numberoffasta, key=numberoffasta.get, reverse=True)[:3]
    highestvalue = []
    for item in highestkey:
        value = numberoffasta.get(item)
        highestvalue.append(value)
    print('\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\n' % (highestkey[0], highestvalue[0], highestkey[1], highestvalue[1], highestkey[2], highestvalue[1]))
    print('\n')
    print('The results contain redundant sequences.\nFASTA sequences will be downloaded later, and redundant sequences will be removed.')
    print('\n')
    # the function will ask the user if they want to view the list of species and the number of sequences for each species
    view = input('\nWould you like to view the full list of species and their respective number of FASTA sequences? y/n\n')
    if view == "y":
        # if the user decides that they want the view the list of species and their number of fasta sequences and inputs y, the following loop will occur
        for key, value in numberoffasta.items():
            print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
    # the function will then go on to ask the user if they wish to procede with the analysis
    choicex = 'empty'
    while True:
        choice = input('\ndo you want to procede with the analysis of this set of data? y/n\n').strip().lower()
        if choice == "y":
            return choicex, workpath
        # the user may not want to go ahead with the analysis of this data set, if this is the case the user will be given some options of datasets to procede with 
        elif choice == "n":
            choicex = input('\n\n\nWhich set of data would you like to analyse??\n\n\t1 : Start again, change TaxID and Protein\n\t2 : Revert to dataset before removal of sequences standarded deviations that are above/below mean\n\nPlease input one of the digits above\n').strip()
            # if the user inputs 1, the following will occur:
            if choicex == "1":
                # the main output foler will be deleted and the users choice of data set will be displayed to them
                subprocess.call("rm -fr %s" % (workpath), shell=True)
                print('lets try this again!')
                return choicex, workpath
            # if the user inputs 2, the following will	occur:
            elif choicex == "2":
                print('\nthe script will procede with analysis on the set of data containing the sequences whose standard deviations are considerably above or below the mean')
                return choicex, workpath
            else:
                ('\nINVALID INPUT, PLEASE INPUT EITHER 1 OR 2')
        else:
            print('\nINVALID INPUT, PLEASE TRY AGAIN')

# DOWNLOAD FAST SEQUENCES


def downloadfasta(idlist, protchoice, workpath):
    # a new folder is created for the storage of the downloaded fasta files
    os.mkdir('%s/fastafiles' % (workpath))
    print('\n\nDOWNLOADING FASTA FILES PLEASE WAIT')
    subprocess.call("esearch -db protein -query 'txid%s[Organism:exp] AND %s NOT PARTIAL' | efetch -format fasta > %s/fastafiles/unfiltered.fasta" % (idlist[1], protchoice, workpath), shell=True)


# GENERATING FASTA FILES FOR EACH SPECIES IN A NEW FOLDER AND CREATE FASTA FILE FOR NON REDUNDANT SEQUENCES WITHIN SPECIES USING SKIPREDUNDANT


def nonredundantfastafile(df, workpath):
    # while loop acting as an error trap 
    while True:
        # making a list of the required use inputs for this function to work
        choices = ["y", "n"]
        # the user will be asked if they want to remove non-redundant sequences
        choice = input("would you like non-redundant sequences within species to be removed?\nthis will aid in reducing the bias of the consensus sequence\nplease enter either y or n:\n").strip().lower()  
        if choice in choices:
            break
        else:
            print("INVALID INPUT, PLEASE TRY AGAIN")
    # lists containing the species TAXID and accession numbers will be created from items in the dataframe
    protspeciesl = df['Species TaxID'].tolist()
    acclist = df['Prot Accession'].tolist()
    # a new dictionary will now be created using these newly created lists, keys and values are appended to the dictionary 
    # if a particular already exists within the dictionary then the value will append to this existing key creating a list of accession numbers for each species
    sadict = {}
    for ele in range(0, len(protspeciesl)):
        x = protspeciesl[ele]
        y = acclist[ele]
        try:
            sadict[x] += [y]
        except:
            sadict[x] = [y]
    # if the user wishes to remove non redundant sequences and inputs y, the user will be asked to select either 95% threshold for redundancy or 100% threshold for redundancy 
    if choice == "y":
    # a while loop is set up to act as an error trap if the user does not input one of the required inputs
        while True:
            # asks the user if they would like to select either 95% or 100% threshold for redundancy 
            options = input("\n would your rather \n\n\t 1 : 95% redundancy threshold\n\t 2 : 100% redundancy threshold\n please enter either 1 or 2\n")
            # if the user decides that they want to filter non-redundant sequences with 95% redundancy threshold the following will occur:
            if options == "1":
                # a new folder for the fasta files that have undergone 95% skip redundancy will be created
                os.mkdir('%s/fastafiles/species' % (workpath))	
                # the sadict dictionary will be used to name new files with the species taxID and write the corresponding accession numbers to these newly created files
                for species in sadict.keys():
                    accs = sadict[species]
                    file = open('%s/fastafiles/species/%s_accession.txt' % (workpath, species), 'w')
                    for accs in accs:
                        file.write(accs + "\n")
                    file.close()
                    # new fasta files are generated using pullseq, fasta sequences are extracted from the main fasta file into the new fasta files
                    subprocess.call("./pullseq -i '%s/fastafiles/unfiltered.fasta' -n '%s/fastafiles/species/%s_accession.txt' > '%s/fastafiles/species/%s.fa'" % (workpath, workpath, species, workpath, species), shell=True)
                    # once these new fasta files have been created, the script will perform skip redundant on all fasta files and move the results into the newly created fasta files
                    subprocess.call("skipredundant -sequences '%s/fastafiles/species/%s.fa' -threshold 95.0 -auto Y -outseq '%s/fastafiles/species/%s.nr'" % (workpath, species, workpath, species), shell=True)
                # once skip redundant has been performed, these results need to be merged into a single file
                subprocess.call("find %s/fastafiles/species -name '*.nr' | xargs -I {} cat {} >> %s/fastafiles/filtered.fasta" % (workpath, workpath), shell=True)
                return sadict, choice
            # if the user decide that they want to perform skip redundant with 100% threshold, then a very similar process to above will occur
            elif options == "2":
                # a new folder for the fasta files that have undergone 100% skip redundancy will be created
                os.mkdir('%s/fastafiles/species' % (workpath))
                # the sadict dictionary will be used to name new files with the species taxID and	write the corresponding	accession numbers to these newly created files
                for species in sadict.keys():
                    accs = sadict[species]
                    file = open('%s/fastafiles/species/%s_accession.txt' % (workpath, species), 'w')
                    for accs in accs:
                        file.write(accs	+ "\n")
                    file.close()
                    #	new fasta files	are generated using pullseq, fasta sequences are extracted from the main fasta file into the new fasta files
                    subprocess.call("./pullseq -i '%s/fastafiles/unfiltered.fasta' -n '%s/fastafiles/species/%s_accession.txt' > '%s/fastafiles/species/%s.fa'" % (workpath, workpath, species, workpath, species), shell=True)
                    # once these new fasta files have been created, the script will perform skip redundant on all fasta files and move the results into the newly created fasta files
                    subprocess.call("skipredundant -sequences '%s/fastafiles/species/%s.fa' -threshold 100.0 -auto Y -outseq '%s/fastafiles/species/%s.nr'" % (workpath, species, workpath, species), shell=True)
                # once skip redundant has been performed, these results need to be merged into a single file
                subprocess.call("find %s/fastafiles/species -name '*.nr' | xargs -I {} cat {} >> %s/fastafiles/filtered.fasta" % (workpath, workpath), shell=True)
                return sadict, choice
            else:
                print('\nINVALID INPUT, PLEASE INPUT EITHER 1 OR 2')
    # if the user does not wish to remove non redundant sequences and inputs n, the following will occur:
    else:
        # a new folder will be created for the containment of all fasta sequences that are to be produced
        os.mkdir('%s/fastafiles/species' % (workpath))
        # the sadict dictionary will be used to name new files with the species taxID and write the corresponding accession numbers to these newly created files
        for species in sadict.keys():
            accs = sadict[species]
            file = open('%s/fastafiles/species/%s_accession.txt' % (workpath, species), 'w')
            for accs in accs:
                file.write(accs + "\n")
            file.close()
            # new fasta files are generated using pullseq, fasta sequences are extracted from the main fasta file into the new fasta files
            subprocess.call("./pullseq -i '%s/fastafiles/unfiltered.fasta' -n '%s/fastafiles/species/%s_accession.txt' > '%s/fastafiles/species/%s.fa'" % (workpath, workpath, species, workpath, species), shell=True)
        # these results need to be merged into a single file
        subprocess.call("find %s/fastafiles/species -name '*.fa' | xargs -I {} cat {} >> %s/fastafiles/filtered.fasta" % (workpath, workpath), shell=True)
    return sadict, choice



# DISPLAYS THE RESULTS OF SKIP REDUNDANT TO THE USER, DISPLAYING THE TOTAL NO, OF SPEQUENCES FOR EACH OF THE UNIQUE SEQUENCES


def nonredundantsequencecheck(idlist, protchoice, workpath):
    # the function will start by opening the file containing the filtered fasta sequences and determines the names of each of the species using regular expression
    with open('%s/fastafiles/filtered.fasta' % (workpath), 'r') as file:
        filer = file.read().strip()
        numofprotspecies = re.findall(r'\[(.*?)]', filer)
        file.close()
    # the total number of sequences, as well as the number of unique species are obtained from numofspecies
    totalseqs = len(numofprotspecies)
    uniquespecies = len(set(numofprotspecies))
    print('\n')
    # the function will display to the user the taxonID, the family of protein, the total number of sequences and species
    print('Here are the filtered esearch results\n\t-These results are non-redundant:\n\nTaxon          :   %s\nProtein Family :   %s\nTotal sequences:   %s\nNo. of Species :   %s' % (idlist[0], protchoice, totalseqs, uniquespecies))
    print('\n')
    # the function will then go on to create a dictionary of species : sequence counts
    numberoffasta = dict((x, numofprotspecies.count(x)) for x in set(numofprotspecies))
    print('Here are the 3 most represented species:\n')
    highestkey = sorted(numberoffasta, key=numberoffasta.get, reverse=True)[:3]
    highestvalue = []
    for item in highestkey:
        value = numberoffasta.get(item)
        highestvalue.append(value)
    # the three most represented species will then be displayed to the user
    print('\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\nSpecies: %-40s Sequences: %s\n' % (highestkey[0], highestvalue[0], highestkey[1], highestvalue[1], highestkey[2], highestvalue[2]))
    print('\n')
    view = input('\nWould you like to view the full list of species and their respective number of FASTA sequences? y/n\n')
    # if the user does want to view the list of species and their number of sequences, the dictionary created earlier is used to print the species (key) and the number of sequences (value)
    if view == "y":
        for key, value in numberoffasta.items():
            print('Species: %-40s' 'Number of FASTA sequences: %s' %(key, numberoffasta[key]))
            # print('\n')
    # this while loop will act as an error trap, for when/if the user does not input either y or n
    while True:
        choicex = 0
        # the user will be asked to make a decision on whether they would like to contiunue with the analysis of the just displayed list of species and number of sequences
        choice = input('\ndo you want to procede with the analysis of this set of data? y/n\n').strip().lower()
        # if the user decides that they are happy to continue, the function will come to an end and the user will be shown choicex and totalseqs
        if choice == "y":
            return choicex, totalseqs
        # if the user is not happy to continue with the analysis, then the user will be asked which data set they would like to procede with 
        elif choice == "n":
            # user will hev 3 options:
            # 1: change to taxon +protein dataset
            # 2: change to the dataset that had not been filtered for redundancies
            # 3: change to the dataset before the removal of sequences whose std were a certain level above or below the mean
            choicex = input('Which dataset would you like to revert to?\n\t1 : Start again, change TaxID and Protein\n\t2 : Continue with the dataset prior to filtering for redundancy\n\t 3 : Continue with the dataset before removal of sequences whose standarded deviations are above/below mean\nPlease input one of the digits\n')
            # if the user inputs one, the following will occur:
            if choicex == "1":
                subprocess.call("rm -fr %s" % (workpath), shell=True)
                # the main output directory will be deleted because the script will essentially be starting again
                print('Lets start again')
                return choicex, totalseqs
            # if th e user input is 2, the following will occur:
            elif choicex == "2":
                subprocess.call("rm -fr %s/fastafiles" % (workpath), shell=True)
                # the folder containing the fastafiles will be removed and fasta sequences will be redownloaded
                print('We shall continue with the dataset that had not been filtered for redundancies')
                return choicex, totalseqs
            # if the user input is 3, the following will occur:
            elif choicex == "3":
                # the folder containing the fasta files will be removed and the fasta sequences will be redownloaded
                subprocess.call("rm -fr %s/fastafiles" % (workpath), shell=True)
                print('we shall continue with the data set that had not had sequences with std of a certain level above or below the mean removed')
                return choicex, totalseqs
            else:
                print('INVALID INPUT, PLEASE TRY AGAIN')
        else:
            print('INVALID INPUT, PLEASE TRY AGAIN')
            return choicex, totalseqs

# CREATING THE CONSENSUS SEQUENCES USING TH E FASTA FILE


def consensusseq (workpath):
    # the function will firstly use clastalo to perform multiple alignment on the most recently created file containing fasta sequences
	print('\nMultiple alignment is underway, please wait')
	subprocess.call("clustalo -i '%s/fastafiles/filtered.fasta' -o '%s/fastafiles/multialign.fasta'" % (workpath, workpath), shell=True)
    # the function will then go on to use the results from the multiple alignment to create the consensus sequence using "cons"
	print('\nCurrently generating the consensus sequence, please wait')
	subprocess.call("cons -sequence '%s/fastafiles/multialign.fasta' -outseq '%s/fastafiles/consensus.fasta'" % (workpath, workpath), shell=True)
    # next step is to make a new directory for the containment of the blast results and database
	os.mkdir('%s/fastafiles/blast' % (workpath))
    # once the new directory is made the function wil go on to use the fasta file to make the blast database
	subprocess.call("makeblastdb -dbtype 'prot' -in '%s/fastafiles/filtered.fasta' -out '%s/fastafiles/blast/fastadatabase'" % (workpath, workpath), shell=True)
    # the function will then go on to run the blast of the newly created consensus sequenes against the newly created blast database
	print('\nRunning the BLAST of the consensus sequence against the database, please wait')
	subprocess.call("blastp -query '%s/fastafiles/consensus.fasta' -db '%s/fastafiles/blast/fastadatabase' -num_threads '20' -outfmt 6 -max_hsps 1 -out '%s/fastafiles/blast/blastresult.blastp.out.txt'" % (workpath, workpath, workpath), shell=True)


# ASKING THE USER HOW MANY SEQUENCES HE/SHE WOULD LIKE THE CONSEERVATION PLOT TO BE PERFROMED ON AND SETTING A LIMIT OF 250 SEQUENCES

def conservationplot (totalseqs, home_dir, idlist, protein, workpath, df):
    # the function will first of all make a new directory for the storage of fasta files to be plotted
	os.mkdir('%s/fastafilesplot' % (workpath))
    # function will then make another directory for the storage of the image of the conservation plot
	os.mkdir('%s/conservationplot' % (workpath))
    # while loop is present to allow mulitple conservation plots to be performed by the user 
	while True:
        # the maximum number of sequences to be plotted is the total number of sequences, if there are fewer sequences, the user will be asked how many he/she would like to plot the minimum number of sequences to be plotted will be set to 10
		if totalseqs < 250:
			while True:
				numofseqs = input('\n\nHow many sequences would you like to use  for the  conservation analysis ?\n\n\tMinimum number : 10\n\tMaximum Number : %s\n\nInput a number between the above listed numbers\n' % (totalseqs))
				numofseqs = int(numofseqs)
				if numofseqs >= 10 and numofseqs <= totalseqs:
					break
				else:
					print('INVALID INPUT, PLEASE TRY AGAIN')
        # the maximum number of sequences to be plotted is 250, if there are fewer sequences, the user will be asked how many he/she would like to plot
        # the minimum number of sequence to be plotted will be 10
		else:
			while True:
				numofseqs = input('How many sequences would you like for the conservation analysis on?\n\n\tMinimum number : 10\n\tMaximum Number : 250\n\nPlease input a number between the above listed numbers\n')
				numofseqs = int(numofseqs)
				if numofseqs >= 10 and numofseqs <= 250:
					break
				else:
					print('INVALID INPUT, PLEASE TRY AGAIN')
        # if the user input it valid, i.e less than 250, less than total number of seqs and more than 10, the function will continue, if this is not the case, the function will restart
		if (numofseqs <= totalseqs or numofseqs <= 250) and numofseqs >= 10:
            # the file cotaining the blast results will be used to create a list
			seqslist = []
			with open('%s/fastafiles/blast/blastresult.blastp.out.txt' % (workpath), 'r') as file:
				n = 1
                # the line in file is split and elemts and index postion will then be appended. this will end when the value of n exceeds the value of numofseqs
                # only the desired sequences will be appended onto the list
				for line in file:
					if n > numofseqs:
						break
					seqs = line.split()
					seqslist.append(seqs[1])
					n += 1
			file.close()
            # the function will then go on to create another file for the containment of the accession numbers of each of the seqeunces the user selected for the conservation plot analysis
			with open ('%s/fastafilesplot/selectedaccessionnumbers.txt' % (workpath), 'w') as file:
				n = 1
				for item in seqslist:
					file.write('%s\n' % (item))
			file.close()
            # the accession numbers within the file are used alongside pullseq to pull the sequences
            # this also pulls the accession numbers from the fasta file containing the mulltiple alignments
			subprocess.call("./pullseq -i '%s/fastafiles/multialign.fasta' -n '%s/fastafilesplot/selectedaccessionnumbers.txt' > '%s/fastafilesplot/selectedfastas.fa'" % (workpath, workpath, workpath), shell=True)
            # this sequences will now be plotted!, this is done using plotcon
			subprocess.call("plotcon -sequence '%s/fastafilesplot/selectedfastas.fa' -graph svg -gtitle 'Conservation plot of %s protein in %s taxonomy' -gxtitle 'Amino Acid Position' -gytitle 'Conservation' -gdirectory '%s/conservationplot' -goutfile 'ConservationPlot' -auto Y" % (workpath, protein, idlist[0], workpath), shell=True)
            # an image of the conservation plots is saved to the conservation plot directory created at the beginnning of the function
			# subprocess.call("display '%s/conservationplot/ConservationPlot.svg' &" % (workpath), shell=True)
            # the while loop here acts as an errror trap in case the users input is invalid (not y or n)
			while True:
                # the user will be asked if they want to create another conservation plot
                # if the user decides they do and inputs y, the loop will start again
                # if the user decides they dont want to do this again and inputs n, the function will end
				choice = input('Would you like to perform conservation analysis with another set of data? y/n\n').strip()
				if choice == "y":
					break
				if choice == "n":
                    # the data frame will be updated such that it contains only the sequences that the user decided to perform conservation analysis on
					accessionlist = open('%s/fastafilesplot/selectedaccessionnumbers.txt' % (workpath)).read().splitlines()
					df = df[df['Prot Accession'].isin(accessionlist)]
                    # the updated dataframe will be saved into a file for the users viewing. this file will contain information on the sequences that were plotted as well as other information
					with open('%s/conservationplot/PlottedProteinDataFrame.txt' % (workpath), 'a') as file:
						file.write('Here is the dataframe of the protein sequences plotted in the protein conservation plot:\n\n')
						file.write(df.to_string())
					file.close()
					return df
			else:
				print('INVALID INPUT, PLEASE TRY AGAIN')


# SCANNING PROTEIN WITH MOTIFS FROM THE PROSITE DATABASE TO DETERMINE IF THERE ARE ANY KNOWN MOTIFS ASSOCIATED WITH THE SUBSET OF SEQUENCEs

def findmotifs(workpath, df):
    # first of all the function will make a new folder for the containment of the results from the motif analysis
	os.mkdir('%s/motifsofplotted' % (workpath))
    # the function will then go on to create a list containing the accession numbers of all the protein sequences in the plot from the datadframe
	plottedaccsl = df['Prot Accession'].tolist()
    # function will then make a new folder for the containment of the fasta sequences that are to undergo motif analysis
	os.mkdir('%s/motifsofplotted/fastafiles' % (workpath))
    # next is to create a new file containing all of the accession numbers of the protein sequences, pullseq will be used on this to obtain the sequences
	for item in plottedaccsl:
		with open('%s/motifsofplotted/fastafiles/%s.txt' % (workpath, item), 'w') as file:
			file.write('%s\n' % (item))
		file.close()
    # the function will then go onto to use pullseq to get and store each the plotted protein sequnences into their own file
	print('Searching for plotted proteins with motifs from the PROSITE database, to find out if any known motifs are associated with the subset of sequences in the dataset\n')
	for item in plottedaccsl:
		subprocess.call("./pullseq -i '%s/fastafiles/multialign.fasta' -n '%s/motifsofplotted/fastafiles/%s.txt' > '%s/motifsofplotted/fastafiles/%s.fa'" % (workpath, workpath, item, workpath, item), shell=True)
		subprocess.call("patmatmotifs -sequence '%s/motifsofplotted/fastafiles/%s.fa' -auto Y -outfile '%s/motifsofplotted/fastafiles/%s_motif.txt'" % (workpath, item, workpath, item), shell=True)
    # function will go on to create a single file of motifs using all the individual motif files
	subprocess.call("find %s/motifsofplotted/fastafiles -name '*motif.txt' | xargs -I {} cat {} > %s/motifsofplotted/Plottedmotifs.txt" % (workpath, workpath), shell=True)
	print('motif analysis was completed successfully')
	print('\n')
    # obtaining the number of motif hits for each sequence, 
    # ahcieved by using grep each of the hit counts lines
	motifhits = subprocess.check_output("cat %s/motifsofplotted/Plottedmotifs.txt | grep 'HitCount'" % (workpath), shell=True)
	motifs = motifhits.decode("utf-8").strip()
    # a list of motifs is then created
	motifslist = motifs.split()
	plotted = df.shape[0]
    # starting from the third position (2nd index) and moving in steps of 3
	seqswithmotif = motifslist[2::3]
    # gettting the total number of sequences that were plotted
	totalplotted = len(seqswithmotif)
    # function procedes to remove all of the sequences that had zero motif hit count
	seqswithmotifs = [x for x in seqswithmotif if x != "0"]
    # functio then gets the total number of which corresponds to the total number of sequences with motifs
    # this needs to be converted into an integer
	numofmotifseqs = len(seqswithmotifs)
	numofmotifs = [int(a) for a in seqswithmotifs]
    # the function the obtains the total number of motifs found by adding up the list of integers
	totalnumofmotifs = sum(numofmotifs)
    # function will now create a list of each of the unique motifs that were found
	uniquemotif = subprocess.check_output("cat '%s/motifsofplotted/Plottedmotifs.txt' | grep 'Motif =' | uniq" % (workpath), shell=True)
	uniquemotifs = uniquemotif.decode("utf-8").strip()
    # paths to the files containing the outputdata are then shown to the user if they wish to take a look at them
	print('Motif analysis summary:\n\nTotal number of sequences analysed/plotted: %s\nTotal number of motifs: %s\nTotal number of Sequences with Motifs: %s\nMotifs found: %s' % (totalplotted, totalnumofmotifs, numofmotifseqs, uniquemotifs))
	print('\nFor further analysis of the sequences and motifs, please analyse the motif analysis output file. The path to this file are displayed below')
	print('\n')
	print('Location of the files generated by this script are:')
	print('\nConservation Plot Image:\n\t%s/conservationplot/ConservationPlot.svg' % (workpath))
	print('\nPlotted Sequence dataframe:\n\t%s/conservationplot/PlottedProteinDataFrame.txt' % (workpath))
	print('\nMotif analysis output:\n\t%s/motifsofplotted/Plottedmotifs.txt' % (workpath))
	print('\n')
	print('\n END OF SCRIPT, HOPE THIS WAS USEFUL')
	print('\nCheerio!')


# FUNCTION WHICH RUNS ALL FUNCTIONS


def runallfunctions():
    taxonidlist, home_dir = gettaxonid()
    newidlist = checktaxid(taxonidlist)
    workpath = getworkpath()
    protein = getprotein(newidlist)
    checkprotein, specieslist, df, workpath = checkseq(newidlist, protein, workpath)
    newprot, updatedidlist, df1, workpath = change (newidlist, protein, df, workpath)

    def stdfunctions (workpath):
        min, max, means, stds = checkingstandarddeviation(df1)
        df2 = standarddeviationabove (df1, min, max, means, stds)
        df3 = standarddeviationbelow(df2, min, max, means, stds)
        resetchoice, workpath =  updatedataframe (df3, updatedidlist, newprot, workpath)
        if resetchoice == "1":
            return runallfunctions()
        elif resetchoice == "2":
            min, max, means, stds, df3, resetchoice, workpath = stdfunctions(workpath)
        return min, max, means, stds, df3, resetchoice, workpath
    parameters = stdfunctions(workpath)

    def nonredundantfunctions(parameters):
        mins, max, means, stds, df3, resetchoice, workpath = parameters
        downloadfasta(newidlist, newprot, workpath)
        proteindict, redundancychoice = nonredundantfastafile(df3, workpath)
        resetchoice2, totalseq = nonredundantsequencecheck(newidlist, newprot, workpath)
        if resetchoice2 == "1":
            return runallfunctions()
        elif resetchoice2 == "2":
            proteindict, redundancychoice, resetchoice2, totalseq, df3 = nonredundantfunctions(parameters)
        elif resetchoice2 == "3":
            min, max, means, stds, df3, resetchoice, workpath = stdfunctions(workpath)
            proteindict, redundancychoice, resetchoice2, totalseq, df3 = nonredundantfunctions(parameters)
        return proteindict, redundancychoice, resetchoice2, totalseq, df3
    proteindict, redundancychoice, resetchoice2, totalseq, df3 = nonredundantfunctions(parameters)
    consensusseq (workpath)
    plotteddf3 = conservationplot (totalseq, home_dir, newidlist, newprot, workpath, df3)
    findmotifs(workpath, plotteddf3)

runallfunctions()
