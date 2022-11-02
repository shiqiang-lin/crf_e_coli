"""
This py file is used to get random number of random genes from genome and compare the empiricals
of edges and vertices in the form of Pearson product-moment correlation coefficient. The sampling
was repeated for multiple times.
"""

import os
import shutil
from random import sample
from random import randint
import numpy as np
import pandas as pd





current_directory = os.getcwd()
os.chdir(current_directory)
os.chdir('gene_files')



def get_random_number_of_random_gene_files():
    number_of_random_genes = randint(430,4292)

    os.chdir(current_directory)
    file_names_list = os.listdir('gene_files')

    #get only the .txt files to list
    gene_file_names_list = []   
    for file_name in file_names_list:
        file_name_split = file_name.split('.')
        if file_name_split[1] == 'txt':
            gene_file_names_list.append(file_name)

    #get the N=number_of_random_genes gene file names from gene_file_names_list
    random_genes_list = sample(gene_file_names_list,number_of_random_genes)
    #print(len(random_genes_list))

    return random_genes_list




def get_empirical_features(random_genes_list):

    os.chdir(current_directory)
    #load dictionaries
    codon_to_amino_acid_dictionary = np.load('codon_to_amino_acid.dict.npy',allow_pickle=True).item()
    state_pair_dictionary = np.load('state_pair.dict.npy',allow_pickle=True).item()
    state_observation_pair_dictionary = np.load('state_observation_pair.dict.npy',allow_pickle=True).item()
    os.chdir('gene_files')
    
    gene_file_name = ''
    for i in range(len(random_genes_list)):   
        gene_file_name = random_genes_list[i]
        gene_file_name_f = open(gene_file_name)
        gene_file_name_content = gene_file_name_f.read()
        gene_file_name_f.close()

        gene_file_name_content = gene_file_name_content.strip()
        

        """
        first deal with the START start codon and the stop codon STOP,
        both are done manually.
        The additon of START and STOP makes the feature calculation
        consistent in terms of empirical and expected.
        """
        #1)the START and the start codon
        #The start codon of the gene is designated as codon_1, having 's'.
        
        codon_1 = gene_file_name_content[0:3]
        if codon_1 == 'ATG':
            amino_acid_1 = codon_to_amino_acid_dictionary[codon_1]
        else:
            amino_acid_1 = codon_to_amino_acid_dictionary[codon_1] + 's'
      
        observation_pair = "START" + amino_acid_1
        state_pair = "START" + codon_1
        state_pair_dictionary[observation_pair][state_pair][1] = \
                        state_pair_dictionary[observation_pair][state_pair][1] + 1
        
        #The codon_1 amino_acid_1 counts 1 in the state_observation_pair_dictionary.
        #Other codons are done in the for cycles.    
        state_observation_pair = codon_1 + amino_acid_1
        state_observation_pair_dictionary[state_observation_pair][1] = \
                        state_observation_pair_dictionary[state_observation_pair][1] + 1                                                               
       
        #2)the stop codon and STOP
        #The stop codon of the gene is designated as codon_n.
        codon_n = gene_file_name_content[-3:]
        amino_acid_n = codon_to_amino_acid_dictionary[codon_n]

        observation_pair = amino_acid_n + "STOP"
        state_pair = codon_n + "STOP"
        state_pair_dictionary[observation_pair][state_pair][1] = \
                        state_pair_dictionary[observation_pair][state_pair][1] + 1

        state_observation_pair = "STOP" + "STOP"
        state_observation_pair_dictionary[state_observation_pair][1] = \
                        state_observation_pair_dictionary[state_observation_pair][1] + 1
        
        #3)Then count the middle part of the gene.  
        """
        deal with the middle part of the gene, which consists of codon_1, codon_2, ..., codon_n

        codon_1      0,1,2
        codon_2      3,4,5
        codon_3      6,7,8
        codon_4      9,10,11
        codon_5      12,13,14
        ...          ...
        codon_i      3*i-3,3*i-2,3*i-1
                     [3*i-3:3*i]
        ...          ...
        codon_n-1    3*(n-1)-3,3*(n-1)-3+1,3*(n-1)-3+2
                     [3*n-6:3*n-3]
        codon_n      3*n-3,3*n-2,3*n-1
                     [3*n-3:3*n]          
        """                                                         
        gene_file_name_content_len = len(gene_file_name_content)
        codon_num = int(gene_file_name_content_len/3)

        for i in range(1,codon_num):
            left_codon = gene_file_name_content[3*i-3:3*i]
            right_codon = gene_file_name_content[3*i:3*i+3]
            
            if (i == 1) and (left_codon != 'ATG'):
                left_amino_acid = codon_to_amino_acid_dictionary[left_codon] + 's'            
            else:
                left_amino_acid = codon_to_amino_acid_dictionary[left_codon]                        
            right_amino_acid = codon_to_amino_acid_dictionary[right_codon]
            
            observation_pair = left_amino_acid + right_amino_acid
            state_pair = left_codon + right_codon
                   
            state_pair_dictionary[observation_pair][state_pair][1] = \
                        state_pair_dictionary[observation_pair][state_pair][1] + 1
            
            #state_observation_pair only considers the right_codon + right_amino_acid                                                                  
            state_observation_pair = right_codon + right_amino_acid
            
            state_observation_pair_dictionary[state_observation_pair][1] = \
                        state_observation_pair_dictionary[state_observation_pair][1] + 1
                    
    """
    check if there is any value 0 in the two dictionaries. If yes, change to a small number, try 1e-8
    """
    for observation_pair,state_pair_dict in state_pair_dictionary.items():
        for state_pair,value in state_pair_dict.items():
            if value[1] == 0:       
                #print("The %s %s has an empirical feature of zero." %(observation_pair,state_pair))
                state_pair_dictionary[observation_pair][state_pair][1] = 1e-8
    """               
    #This dictionary only has START, STOP with zero values, which do not need to set a small value.
    for state_observation, value in state_observation_pair_dictionary.items():
        if value[1] == 0:
            print("The %s %s has an empirical feature of zero." %(state_observation,value))
    """
    return  state_pair_dictionary,state_observation_pair_dictionary



"""
random_genes_list = get_random_number_of_random_gene_files()
state_pair_dictionary,state_observation_pair_dictionary = get_empirical_features(random_genes_list)        
"""
PPMCCs_of_state_pair_dictionary_list = []
PPMCCs_of_state_observation_pair_dictionary_list = []

N = 100

for i in range(N):
    
    random_genes_list_0 = get_random_number_of_random_gene_files()
    random_genes_list_1 = get_random_number_of_random_gene_files()

    state_pair_dictionary_0,state_observation_pair_dictionary_0 = get_empirical_features(random_genes_list_0)
    state_pair_dictionary_1,state_observation_pair_dictionary_1 = get_empirical_features(random_genes_list_1)

    #print(state_pair_dictionary_0['AC'])
    #print(state_pair_dictionary_1['AC'])

    state_pair_dictionary_0_values_to_list = []
    state_pair_dictionary_1_values_to_list = []
    state_observation_pair_dictionary_0_values_to_list = []
    state_observation_pair_dictionary_1_values_to_list = []

    for observation_pair in state_pair_dictionary_0.keys():
        for state_pair in state_pair_dictionary_0[observation_pair].keys():
            state_pair_dictionary_0_values_to_list.append(state_pair_dictionary_0[observation_pair][state_pair][1])
            state_pair_dictionary_1_values_to_list.append(state_pair_dictionary_1[observation_pair][state_pair][1])

    for state_observation in state_observation_pair_dictionary_0.keys():
        state_observation_pair_dictionary_0_values_to_list.append(state_observation_pair_dictionary_0[state_observation][1])
        state_observation_pair_dictionary_1_values_to_list.append(state_observation_pair_dictionary_1[state_observation][1])


    #get Pearson product-moment correlation coefficient
    A_0 = pd.Series(state_pair_dictionary_0_values_to_list)
    B_0 = pd.Series(state_pair_dictionary_1_values_to_list)
    """
    print(state_pair_dictionary_0_values_to_list[0:20])
    print(state_pair_dictionary_1_values_to_list[0:20])
    print(random_genes_list_0[0:20])
    print(random_genes_list_1[0:20])
    """
    corr_state_pair_dictionary = B_0.corr(A_0,method='pearson')
    #print(corr_state_pair_dictionary)
    PPMCCs_of_state_pair_dictionary_list.append(corr_state_pair_dictionary)



    A_1 = pd.Series(state_observation_pair_dictionary_0_values_to_list)
    B_1 = pd.Series(state_observation_pair_dictionary_1_values_to_list)
    """
    print(state_observation_pair_dictionary_0_values_to_list[0:20])
    print(state_observation_pair_dictionary_1_values_to_list[0:20])
    """
    corr_state_observation_pair_dictionary = B_1.corr(A_1,method='pearson')
    #print(corr_state_observation_pair_dictionary)
    PPMCCs_of_state_observation_pair_dictionary_list.append(corr_state_observation_pair_dictionary)





#plot the figure
import matplotlib.pyplot as plt


x = [i for i in range(len(PPMCCs_of_state_pair_dictionary_list))]
y1 = PPMCCs_of_state_pair_dictionary_list
plt.scatter(x,y1,c='royalblue',s=10)

y2 = PPMCCs_of_state_observation_pair_dictionary_list
plt.scatter(x,y2,c='darkorange',s=10)
plt.xlabel("No. of sampling")
plt.ylabel("PPMCC of dictionaries")
plt.title("E. coli")
plt.show()






